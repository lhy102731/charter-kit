#!/usr/bin/env python3
"""Explicitly install optional Charter Kit provider skills.

This installer is intentionally NOT run automatically by a plugin. It reads
``dependencies.install.json`` and clones/copies only the providers the user
asks for, into the user's skill directory (``~/.agents/skills`` by default).

Usage examples::

    python scripts/install_dependencies.py --list
    python scripts/install_dependencies.py --dry-run
    python scripts/install_dependencies.py --yes
    python scripts/install_dependencies.py --only j-space grill-me
    python scripts/install_dependencies.py --target ~/.dsh/skills --yes --force
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable

DEFAULT_TARGET_TOKEN = "{home}/.agents/skills"
DEFAULT_MANIFEST = "dependencies.install.json"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=str(Path(__file__).resolve().parents[1] / DEFAULT_MANIFEST))
    parser.add_argument("--target", default="", help="destination skills directory (default ~/.agents/skills)")
    parser.add_argument("--only", nargs="*", default=[], help="install only these provider ids")
    parser.add_argument("--yes", action="store_true", help="confirm all installations without prompting")
    parser.add_argument("--force", action="store_true", help="replace existing skill directories")
    parser.add_argument("--dry-run", action="store_true", help="print actions without cloning or copying")
    parser.add_argument("--list", action="store_true", help="list manifest entries and exit")
    return parser.parse_args(argv)


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SystemExit(f"cannot read manifest {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid manifest {path}: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("entries"), list):
        raise SystemExit(f"manifest {path} must contain an entries array")
    return data


def expand_target(raw: str) -> Path:
    value = raw or DEFAULT_TARGET_TOKEN
    value = value.replace("{home}", str(Path.home()))
    return Path(value).expanduser()


def clone_checkout(repo: str, ref: str) -> tuple[tempfile.TemporaryDirectory[str], Path]:
    """Clone the repo into a temp dir; caller must call cleanup().

    ``ref`` may be a branch, tag, or full commit SHA. A shallow clone of the
    default branch is taken first, then the requested ref is fetched and
    checked out. This works for arbitrary commit SHAs, which ``git clone
    --branch`` cannot reliably target on every git version.
    """
    temp = tempfile.TemporaryDirectory(prefix="charter-kit-deps-")
    checkout = Path(temp.name)
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", "--single-branch", repo, str(checkout)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if ref:
            subprocess.run(
                ["git", "-C", str(checkout), "fetch", "--depth", "1", "origin", ref],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            subprocess.run(
                ["git", "-C", str(checkout), "checkout", "--detach", ref],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
    except subprocess.CalledProcessError as exc:
        temp.cleanup()
        raise SystemExit(f"git clone failed for {repo}@{ref}: {exc}") from exc
    return temp, checkout


def path_in_checkout(checkout: Path, source_path: str) -> Path:
    candidate = checkout / source_path
    if not candidate.exists():
        raise SystemExit(f"source path not found in checkout: {source_path}")
    return candidate


def confirm(question: str, default: bool = True) -> bool:
    suffix = " [Y/n] " if default else " [y/N] "
    answer = input(question + suffix).strip().lower()
    if not answer:
        return default
    return answer in {"y", "yes"}


def copy_tree(source: Path, destination: Path, force: bool) -> bool:
    if destination.exists():
        if not force:
            return False
        shutil.rmtree(destination)
    shutil.copytree(source, destination)
    return True


def apply_renames(destination: Path, rename_files: dict[str, str]) -> None:
    for old, new in (rename_files or {}).items():
        old_path = destination / old
        if old_path.exists() and old_path.name != new:
            old_path.rename(destination / new)


def install_entry(entry: dict[str, Any], target: Path, args: argparse.Namespace, dry_run: bool) -> str:
    provider_id = entry["id"]
    repo = entry["repo"]
    ref = entry.get("ref", "main")
    source_path = entry["sourcePath"]
    mode = entry.get("mode", "copyDir")
    dest_name = entry.get("destName")
    rename_files = entry.get("renameFiles", {})

    if mode == "copyChildren":
        destinations = [target]
    else:
        if not dest_name:
            raise SystemExit(f"entry {provider_id}: destName is required for mode {mode}")
        destinations = [target / dest_name]

    # Existing target handling before any network work.
    if not dry_run:
        for destination in destinations:
            if destination.exists() and not args.force:
                return f"skip {provider_id}: {destination} already exists (use --force to replace)"

    if not dry_run:
        temp, checkout = clone_checkout(repo, ref)
        try:
            source = path_in_checkout(checkout, source_path)
            copied: list[str] = []
            if mode == "copyChildren":
                for child in sorted(source.iterdir()):
                    if not child.is_dir():
                        continue
                    if copy_tree(child, target / child.name, args.force):
                        copied.append(child.name)
            else:
                destination = destinations[0]
                if copy_tree(source, destination, args.force):
                    apply_renames(destination, rename_files)
                    copied.append(destination.name)
            return f"installed {provider_id}: {', '.join(copied) or 'no new directories'}"
        finally:
            temp.cleanup()
    else:
        source_desc = f"{repo}@{ref}:{source_path}"
        if mode == "copyChildren":
            return f"would install children of {source_desc} into {target}"
        return f"would install {source_desc} into {target / (dest_name or '')}"


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    manifest = load_manifest(Path(args.manifest))
    target = expand_target(args.target)

    if args.list:
        for entry in manifest["entries"]:
            print(f"{entry['id']}\t{entry['repo']}@{entry.get('ref', 'main')}\t{entry['sourcePath']}")
        return 0

    entries = [e for e in manifest["entries"] if not args.only or e["id"] in args.only]
    if not entries:
        print("No matching provider entries to install.")
        return 0

    if args.dry_run:
        print(f"Target skills directory: {target}")
        for entry in entries:
            print(install_entry(entry, target, args, dry_run=True))
        return 0

    if not shutil.which("git"):
        print("ERROR: git is required to install dependencies.", file=sys.stderr)
        return 1

    target.mkdir(parents=True, exist_ok=True)

    for entry in entries:
        if not args.yes:
            ok = confirm(f"Install {entry['id']} from {entry['repo']}?")
            if not ok:
                print(f"skip {entry['id']}: declined")
                continue
        result = install_entry(entry, target, args, dry_run=False)
        print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())