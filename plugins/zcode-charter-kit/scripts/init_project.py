#!/usr/bin/env python3
"""Create the small .charter working set in a project directory.

This is an explicit, local-only convenience command. It never installs
dependencies or contacts the network. By default it refuses to overwrite
existing files; --add-missing only fills absent working-set files, while
--force creates a complete backup before replacing generated files. New
projects use the canonical runtime filenames, and existing projects keep any
legacy ``*-template.md`` files that are already present.

The one file it touches outside ``.charter/`` is ``.gitignore``: a single
``.jspace/`` entry is appended when no existing line already decides that
directory, so the session ledger stays out of version control by rule instead of
by discipline. No existing line is ever rewritten, and a failure here is
reported without failing initialization.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import stat
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from tempfile import mkdtemp, mkstemp


FILES = {
    "project-charter.md": "project.md",
    "roadmap.md": "roadmap.md",
    "leaf-task.md": "current-task.md",
    "reuse-discovery.md": "reuse-discovery.md",
    "handoff.md": "handoff.md",
    "decision.md": "decision.md",
    "review.md": "review.md",
    "evidence-receipt.md": "evidence-receipt.md",
}


# The session execution ledger lives beside the working set but is host state,
# not project history.  The handoff template records it as untracked, and a
# sentence in a document does not stop ``git add -A`` from committing it, so the
# initializer turns that assertion into a rule the repository itself carries.
LEDGER_DIRECTORY = ".jspace"
LEDGER_IGNORE_ENTRY = f"{LEDGER_DIRECTORY}/"
LEDGER_IGNORE_COMMENT = (
    "# Charter Kit: the session execution ledger is host state, not project history.\n"
    "# .charter/ carries the governance record and stays tracked; this directory does not.\n"
)


def covers_ledger(pattern: str) -> bool:
    """Report whether one .gitignore line already decides the ledger directory.

    This is a deliberately small subset of gitignore matching: the realistic
    spellings of a directory entry, plus negations, which are reported so an
    explicit user decision to track the ledger is never overwritten.
    """

    candidate = pattern.strip()
    if not candidate or candidate.startswith("#"):
        return False
    candidate = candidate.removeprefix("!").removeprefix("/")
    candidate = candidate.removesuffix("/**").removesuffix("/*").removesuffix("/")
    return candidate == LEDGER_DIRECTORY


def ensure_ledger_ignored(project_dir: Path) -> str:
    """Append the ledger ignore entry once, without rewriting user lines.

    Never raises: the working set matters more than this convenience, so every
    failure is reported as a status string and initialization continues.
    """

    gitignore = project_dir / ".gitignore"
    if not (project_dir / ".git").exists() and not gitignore.exists():
        return "SKIPPED - no repository or .gitignore in the project root"
    try:
        if is_link(gitignore):
            return "UNVERIFIED - refusing to write a linked .gitignore"
        if gitignore.exists() and not gitignore.is_file():
            return "UNVERIFIED - .gitignore is not a regular file"
        existing = gitignore.read_text(encoding="utf-8", errors="replace") if gitignore.is_file() else ""
        for line in existing.splitlines():
            if covers_ledger(line):
                if line.strip().startswith("!"):
                    return f"UNCHANGED - an explicit negation keeps {LEDGER_IGNORE_ENTRY} tracked"
                return f"UNCHANGED - {LEDGER_IGNORE_ENTRY} is already ignored"
        if not existing:
            prefix = ""
        elif existing.endswith("\n"):
            prefix = "\n"
        else:
            prefix = "\n\n"
        with gitignore.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(f"{prefix}{LEDGER_IGNORE_COMMENT}{LEDGER_IGNORE_ENTRY}\n")
        return f"ADDED - {LEDGER_IGNORE_ENTRY} appended to .gitignore"
    except OSError as exc:
        return f"UNVERIFIED - .gitignore could not be updated ({exc.__class__.__name__})"


def find_template_dir(package_root: Path) -> Path:
    """Find templates in either the full kit or the self-contained Skill.

    The package-root layout uses ``portable/templates``; an installed
    ``skills/charter-workflow`` snapshot carries the same files directly in
    ``templates``.  Keeping the lookup here lets both entry points bootstrap a
    project without depending on the other layer.
    """

    candidates = (package_root / "portable" / "templates", package_root / "templates")
    for candidate in candidates:
        if all((candidate / name).is_file() for name in FILES):
            return candidate
    missing = ", ".join(name for name in FILES if not any((candidate / name).is_file() for candidate in candidates))
    raise FileNotFoundError(f"missing package templates: {missing}")


def find_dependency_checker(package_root: Path) -> Path | None:
    """Return the local checker path when this layer ships one."""

    candidates = (package_root / "scripts" / "check_dependencies.py", package_root / "check_dependencies.py")
    return next((candidate for candidate in candidates if candidate.is_file()), None)


def append_diagnostic_fallback(log_path: Path, reason: str) -> None:
    """Record an explicit unverified/fallback result without leaking details."""

    safe_reason = reason.replace("\r", "?").replace("\n", "?")[:300]
    log_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with log_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(f"# Charter Kit dependency check {timestamp}\n")
        handle.write(
            "[UNVERIFIED] dependency-checker (required, capability) — "
            f"{safe_reason}; impact: automatic capability diagnosis was not confirmed; "
            "fallback: perform the documented local checks manually; "
            "action: review the dependency requirements and restore the checker explicitly\n"
        )
        handle.write(
            "[FALLBACK] dependency-checker (required, capability) — "
            "portable/manual dependency checklist is available; "
            "impact: automatic capability diagnosis was not confirmed; "
            "fallback: perform the documented local checks manually; "
            "action: continue only within the recorded limitation\n"
        )


def run_dependency_check(package_root: Path, project_dir: Path, evidence_dir: Path) -> int:
    """Run the bundled metadata-only checker and always leave a log.

    A missing or malformed checker must not erase a newly-created working set.
    The checker itself decides whether required capabilities make the project
    ``BLOCKED_TOOLING``; initialization still succeeds so the user can inspect
    and repair the record.
    """

    log_path = evidence_dir / "dependency-check.log"
    checker_path = find_dependency_checker(package_root)
    if checker_path is None:
        append_diagnostic_fallback(log_path, "bundled dependency checker was not found")
        return 1
    try:
        spec = importlib.util.spec_from_file_location("_charter_kit_dependency_checker", checker_path)
        if spec is None or spec.loader is None:
            raise RuntimeError("checker module could not be loaded")
        module = importlib.util.module_from_spec(spec)
        # Dataclasses and other standard-library decorators resolve the module
        # through ``sys.modules`` while it is being executed.  Register the
        # transient module before invoking its loader; this also keeps the
        # self-contained Skill copy independent of package imports.
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        arguments = ["--project", str(project_dir), "--log-file", str(log_path)]
        # Let the checker layer its package manifest with the project's own
        # ``.charter/dependencies.json``.  Passing the package file explicitly
        # would suppress automatic project discovery and make project-specific
        # required capabilities invisible during initialization.
        result = module.main(arguments)
        return int(result or 0)
    except Exception as exc:  # pragma: no cover - defensive host boundary
        append_diagnostic_fallback(log_path, f"checker could not run ({exc.__class__.__name__})")
        return 1


def backup_charter(target_dir: Path) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup_dir = target_dir.with_name(f"{target_dir.name}.backup-{timestamp}")
    staging_dir = Path(mkdtemp(prefix=f".{backup_dir.name}.tmp-", dir=target_dir.parent))
    try:
        shutil.copytree(target_dir, staging_dir, symlinks=True, dirs_exist_ok=True)
        os.replace(staging_dir, backup_dir)
    except Exception:
        shutil.rmtree(staging_dir, ignore_errors=True)
        raise
    return backup_dir


def is_link(path: Path) -> bool:
    """Detect symlinks and Windows junctions without following them."""
    if path.is_symlink():
        return True
    junction_check = getattr(path, "is_junction", None)
    if junction_check is not None and junction_check():
        return True
    path_check = getattr(os.path, "isjunction", None)
    if path_check is not None and path_check(path):
        return True
    if os.name == "nt":
        try:
            attributes = os.lstat(path).st_file_attributes
        except (AttributeError, FileNotFoundError, OSError):
            return False
        reparse_point = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x0400)
        return bool(attributes & reparse_point)
    return False


def find_link(path: Path) -> Path | None:
    """Return the first symlink or junction below path."""
    if is_link(path):
        return path
    if not path.is_dir():
        return None
    for child in path.iterdir():
        found = find_link(child)
        if found is not None:
            return found
    return None


def validate_target(target_dir: Path) -> None:
    if is_link(target_dir):
        raise OSError(f"refusing to use symlinked or junction .charter directory: {target_dir}")
    if target_dir.exists() and not target_dir.is_dir():
        raise OSError(f"refusing to use non-directory .charter path: {target_dir}")
    if target_dir.exists():
        linked = find_link(target_dir)
        if linked is not None:
            raise OSError(f"refusing to operate on .charter symlink or junction: {linked}")


def validate_destinations(target_dir: Path) -> None:
    """Validate every path that will be touched before any backup or replacement."""
    evidence_dir = target_dir / "evidence"
    if is_link(evidence_dir):
        raise OSError(f"refusing to use linked evidence directory: {evidence_dir}")
    if evidence_dir.exists() and not evidence_dir.is_dir():
        raise OSError(f"refusing to use non-directory evidence path: {evidence_dir}")
    for target_name in FILES.values():
        destination = target_dir / target_name
        if is_link(destination):
            raise OSError(f"refusing to overwrite linked charter file: {destination}")
        if destination.exists() and not destination.is_file():
            raise OSError(f"refusing to overwrite non-file charter path: {destination}")


def atomic_copy(source: Path, destination: Path) -> None:
    """Copy a template without following or truncating an existing destination link."""
    fd, temporary_name = mkstemp(prefix=f".{destination.name}.", dir=destination.parent)
    os.close(fd)
    temporary = Path(temporary_name)
    try:
        shutil.copyfile(source, temporary)
        os.replace(temporary, destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def init_project(
    package_root: Path,
    project_dir: Path,
    force: bool = False,
    add_missing: bool = False,
) -> tuple[list[Path], Path | None, str]:
    source_dir = find_template_dir(package_root)
    target_dir = project_dir.resolve() / ".charter"

    validate_target(target_dir)
    validate_destinations(target_dir)
    target_exists = target_dir.exists()
    existing_entries = list(target_dir.iterdir()) if target_exists else []
    if existing_entries and not force and not add_missing:
        names = ", ".join(str(path.relative_to(target_dir)) for path in existing_entries)
        raise FileExistsError(f"refusing to overwrite existing .charter files: {names}; use --force deliberately")

    backup_dir = backup_charter(target_dir) if target_exists and force else None

    target_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir = target_dir / "evidence"
    evidence_dir.mkdir(exist_ok=True)
    created: list[Path] = []
    for source_name, target_name in FILES.items():
        destination = target_dir / target_name
        if add_missing and destination.exists():
            continue
        atomic_copy(source_dir / source_name, destination)
        created.append(destination)
    # Diagnostics are evidence, not a second approval gate.  Even a required
    # capability miss leaves the working set available for inspection and is
    # represented in the log as BLOCKED_TOOLING by the workflow.
    run_dependency_check(package_root, project_dir.resolve(), evidence_dir)
    # Governance records belong in version control and the session ledger does
    # not.  Both halves of that rule are cheap to apply here and expensive to
    # discover later, when an untracked charter can no longer be cited as
    # authoritative history.
    ledger_status = ensure_ledger_ignored(project_dir.resolve())
    return created, backup_dir, ledger_status


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", help="project directory to receive .charter/")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--force",
        action="store_true",
        help="back up .charter, then overwrite the generated charter files",
    )
    mode.add_argument(
        "--add-missing",
        action="store_true",
        help="add only missing generated files; preserve all existing charter data",
    )
    args = parser.parse_args(argv)
    package_root = Path(__file__).resolve().parents[1]
    project_dir = Path(args.project_dir).expanduser()
    try:
        created, backup_dir, ledger_status = init_project(package_root, project_dir, args.force, args.add_missing)
    except (FileExistsError, FileNotFoundError, OSError) as exc:
        print(f"Charter project initialization: FAIL: {exc}", file=sys.stderr)
        return 1
    action = "updated missing files in" if args.add_missing else "initialized"
    print(f"Charter project {action}: {project_dir.resolve() / '.charter'}")
    if backup_dir is not None:
        print(f"Backup: {backup_dir}")
    for path in created:
        print(f"- {path.relative_to(project_dir.resolve())}")
    if args.add_missing and not created:
        print("- no missing generated files")
    print(f"Session ledger ignore rule: {ledger_status}")
    print("Next: fill .charter/project.md and .charter/roadmap.md, complete .charter/reuse-discovery.md, then approve the first bounded current-task.md.")
    print("Then commit .charter/ (project.md and reuse-discovery.md included) so the charter and the reuse gate carry auditable history.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
