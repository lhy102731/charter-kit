#!/usr/bin/env python3
"""Report intermediate artifacts that escaped the leaf's scratch root.

The leaf contract names one scratch root - .scratch unless the contract says
otherwise - and states that every file the leaf produces that is not a
deliverable belongs there. This check is the obligation behind that sentence: it
walks the deliverable tree and reports the artifacts that landed somewhere else.

Three things are reported, because they fail differently:

- an artifact version control already excludes is counted, not reported. It is
  local noise, and noise is what the scratch root exists to absorb;
- an artifact that version control would accept is reported. This is the case
  that grows a project, and it is reported before it happens rather than after;
- an artifact already committed is reported whichever ignore rule exists, since
  an ignore rule does not apply to a file someone already added.

The flagged set is deliberately closed: names that are never deliverables.
Interpreter caches, test and coverage output, editor backups, captured logs,
patch leftovers. A project-specific artifact type does not belong in this list;
it belongs in the scratch root.

When to run it: after the layer evidence this leaf will cite is in the record, and 
before closure is signed. Not after closing - no step runs then, and the artifacts 
would already have been integrated - and not before the evidence is taken, which 
deletes the proof the answer needs. Run it in CI as well: a rule that only runs at 
leaf boundaries is asleep for most of the work.

The check does not decide lifetimes. A fixture or golden file the suite must run 
against later is a deliverable that was left in the scratch root: promote it into 
the tree and name it under Allowed paths.

Usage:
    python scripts/check_scratch.py [project_dir] [--scratch PATH] [--json] [--init]

Exit codes: 0 clean, 1 artifacts found, 2 the check could not run.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

DEFAULT_SCRATCH = ".scratch"

JUNK_DIRECTORIES = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".hypothesis",
    ".tox",
    ".nox",
    "htmlcov",
}

# Host state and dependencies: never descended into. The scratch root is skipped
# by name at every level, because that is where the artifacts belong.
SKIPPED_DIRECTORIES = {
    ".charter",
    ".git",
    ".hg",
    ".idea",
    ".jspace",
    ".svn",
    ".superpowers",
    ".venv",
    ".vscode",
    "node_modules",
    "venv",
}

JUNK_SUFFIXES = (
    ".bak",
    ".orig",
    ".pstats",
    ".prof",
    ".pyc",
    ".pyo",
    ".rej",
    ".swo",
    ".swp",
    ".tmp",
)

JUNK_NAMES = {".DS_Store", "Thumbs.db"}

SCRATCH_LINE = re.compile(r"^- Scratch root:\s*(.+?)\s*$", re.MULTILINE)
TOKEN = re.compile(chr(96) + "([^" + chr(96) + "]+)" + chr(96))


def declared_scratch_root(project_dir: Path) -> str:
    """Read the scratch root from the leaf contract, falling back to the default."""

    try:
        text = (project_dir / ".charter" / "current-task.md").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return DEFAULT_SCRATCH
    match = SCRATCH_LINE.search(text)
    if not match:
        return DEFAULT_SCRATCH
    value = match.group(1).strip()
    tokens = TOKEN.findall(value)
    candidate = (tokens[0] if tokens else value.split()[0]).strip().rstrip("/")
    return candidate or DEFAULT_SCRATCH


def run_git(project_dir: Path, arguments: list[str], stdin: str = "") -> subprocess.CompletedProcess[str] | None:
    """Run one git command, returning None when git or the repository is absent."""

    try:
        return subprocess.run(
            ["git", "-C", str(project_dir), *arguments],
            input=stdin,
            capture_output=True,
            text=True,
            check=False,
        )
    except (OSError, ValueError):
        return None


def tracked_paths(project_dir: Path) -> set[str] | None:
    completed = run_git(project_dir, ["ls-files", "-z"])
    if completed is None or completed.returncode != 0:
        return None
    return {entry for entry in completed.stdout.split(chr(0)) if entry}


def ignored_paths(project_dir: Path, candidates: list[str]) -> set[str]:
    """Report which candidates version control already excludes."""

    if not candidates:
        return set()
    payload = "".join(f"{candidate}{chr(0)}" for candidate in candidates)
    completed = run_git(project_dir, ["check-ignore", "--stdin", "--no-index", "-z"], stdin=payload)
    if completed is None or completed.returncode not in (0, 1):
        return set()
    return {entry for entry in completed.stdout.split(chr(0)) if entry}


def covers_scratch(project_dir: Path, scratch: str) -> bool:
    completed = run_git(project_dir, ["check-ignore", "--no-index", "-z", f"{scratch}/"])
    if completed is not None and completed.returncode == 0 and completed.stdout.strip(chr(0)):
        return True
    try:
        text = (project_dir / ".gitignore").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    for line in text.splitlines():
        candidate = line.strip()
        if not candidate or candidate.startswith("#"):
            continue
        candidate = candidate.removeprefix("!").removeprefix("/")
        candidate = candidate.removesuffix("/**").removesuffix("/*").removesuffix("/")
        if candidate == scratch:
            return True
    return False


def candidates(project_dir: Path, scratch: str) -> list[tuple[str, str]]:
    """Walk the deliverable tree and collect (path, reason) junk candidates."""

    found: list[tuple[str, str]] = []
    scratch_name = Path(scratch).parts[0] if Path(scratch).parts else DEFAULT_SCRATCH

    for current, directories, files in os.walk(project_dir, topdown=True):
        here = Path(current)
        kept: list[str] = []
        for name in sorted(directories):
            if name in SKIPPED_DIRECTORIES or name == scratch_name:
                continue
            if name in JUNK_DIRECTORIES:
                relative = (here / name).relative_to(project_dir).as_posix()
                found.append((relative + "/", "generated state directory"))
                continue
            kept.append(name)
        directories[:] = kept

        for name in sorted(files):
            relative = (here / name).relative_to(project_dir).as_posix()
            if name in JUNK_NAMES:
                found.append((relative, "generated platform file"))
            elif name == ".coverage" or (name.startswith(".coverage.") and name != ".coverage.settings"):
                found.append((relative, "coverage data"))
            elif name.endswith(JUNK_SUFFIXES):
                found.append((relative, "build or editor leftover"))
            elif name.endswith(".log"):
                found.append((relative, "captured log"))
    return found


def classify(project_dir: Path, scratch: str) -> tuple[list[tuple[str, str]], int, bool]:
    """Split candidates into findings, an ignored count, and the repository flag."""

    tracked = tracked_paths(project_dir)
    found = candidates(project_dir, scratch)
    if tracked is None:
        return (
            [(path, reason + " (no version control here, so nothing filters it)") for path, reason in found],
            0,
            False,
        )

    ignored = ignored_paths(project_dir, [path.rstrip("/") for path, _ in found])
    ignored_prefixes = {entry.rstrip("/") for entry in ignored}
    findings: list[tuple[str, str]] = []
    excluded = 0
    for path, reason in found:
        bare = path.rstrip("/")
        is_tracked = bare in tracked or any(item.startswith(bare + "/") for item in tracked)
        if is_tracked:
            findings.append((path, reason + ", and already committed"))
        elif bare in ignored_prefixes:
            excluded += 1
        else:
            findings.append((path, reason + ", and nothing ignores it"))

    for relative in tracked:
        if relative == scratch or relative.startswith(scratch.rstrip("/") + "/"):
            findings.append((relative, "tracked file inside the scratch root"))
    if not covers_scratch(project_dir, scratch):
        findings.append((scratch.rstrip("/") + "/", "the scratch root is not ignored, so artifacts can be added by accident"))
    return findings, excluded, True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", nargs="?", default=".")
    parser.add_argument("--scratch", help="override the scratch root read from the contract")
    parser.add_argument("--json", action="store_true", help="print findings as JSON")
    parser.add_argument("--init", action="store_true", help="create the scratch root and exit")
    args = parser.parse_args(argv)

    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.is_dir():
        print(f"Scratch check: FAIL - not a directory: {project_dir}", file=sys.stderr)
        return 2

    scratch = (args.scratch or declared_scratch_root(project_dir)).strip().rstrip("/")
    scratch = scratch or DEFAULT_SCRATCH

    if args.init:
        try:
            (project_dir / scratch).mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            print(f"Scratch check: FAIL - could not create {scratch} ({exc.__class__.__name__})", file=sys.stderr)
            return 2
        print(f"Scratch root ready: {scratch}")
        return 0

    findings, excluded, repository = classify(project_dir, scratch)
    if args.json:
        print(
            json.dumps(
                {
                    "scratch": scratch,
                    "repository": repository,
                    "excluded": excluded,
                    "findings": [{"path": path, "reason": reason} for path, reason in findings],
                },
                indent=2,
            )
        )
    else:
        for path, reason in findings:
            print(f"JUNK {path} - {reason}")
        print(f"SCRATCH {scratch} excluded={excluded}")
        print(f"RESULT {'PASS' if not findings else f'FAIL({len(findings)})'}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
