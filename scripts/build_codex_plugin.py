#!/usr/bin/env python3
"""Build the self-contained Codex distribution for Charter Kit."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import sys
import tempfile
from pathlib import Path


PACKAGE_NAME = "charter-kit"
MANIFEST_RELATIVE = Path("targets") / "codex" / ".codex-plugin" / "plugin.json"
SKILL_RELATIVE = Path("skills") / "charter-workflow"
DISTRIBUTION_RELATIVE = Path("plugins") / PACKAGE_NAME
LEGACY_MANIFEST_RELATIVE = Path(".codex-plugin") / "plugin.json"
PACKAGE_ROOT_ITEMS = (
    "LICENSE",
    "README.md",
    "DEVELOPMENT_CHARTER.md",
    "DEPENDENCIES.md",
    "dependencies.json",
    "agentpack.yaml",
    "portable",
    "scripts",
)
IGNORED_TREE_NAMES = {"__pycache__", ".git", ".hg", ".svn", "plugins", "tests"}


def is_junction(path: Path) -> bool:
    check = getattr(path, "is_junction", None)
    if callable(check):
        return bool(check())
    path_check = getattr(os.path, "isjunction", None)
    if path_check is not None:
        return bool(path_check(path))
    if os.name == "nt":
        try:
            attributes = os.lstat(path).st_file_attributes
        except (AttributeError, FileNotFoundError, OSError):
            return False
        reparse_point = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x0400)
        return bool(attributes & reparse_point)
    return False


def is_link(path: Path) -> bool:
    return path.is_symlink() or is_junction(path)


def validate_no_traversal(path: Path, label: str) -> None:
    if any(part == ".." for part in path.parts):
        raise OSError(f"refusing {label} with traversal segments: {path}")


def validate_no_links(path: Path, label: str) -> None:
    current = path
    seen = [current, *current.parents]
    for candidate in seen:
        if candidate.exists() and is_link(candidate):
            raise OSError(f"refusing linked {label}: {candidate}")


def validate_source_tree(path: Path, label: str) -> None:
    validate_no_traversal(path, label)
    validate_no_links(path, label)
    if not path.exists():
        raise FileNotFoundError(f"missing {label}: {path}")
    if not path.is_dir():
        raise OSError(f"expected directory for {label}: {path}")
    for child in sorted(path.rglob("*")):
        if is_link(child):
            raise OSError(f"refusing linked {label} entry: {child}")


def validate_source_file(path: Path, label: str) -> None:
    validate_no_traversal(path, label)
    validate_no_links(path, label)
    if not path.is_file():
        raise FileNotFoundError(f"missing {label}: {path}")


def copy_file(source: Path, destination: Path) -> None:
    validate_no_links(destination, "destination")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def copy_tree(source: Path, destination: Path) -> None:
    validate_source_tree(source, "source tree")
    validate_no_traversal(destination, "destination")
    validate_no_links(destination, "destination")
    if destination.exists():
        if destination.is_file():
            raise OSError(f"expected directory destination: {destination}")
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)
    for child in sorted(source.iterdir(), key=lambda item: item.name):
        if child.name in IGNORED_TREE_NAMES or child.suffix == ".pyc":
            continue
        if is_link(child):
            raise OSError(f"refusing linked source entry: {child}")
        target = destination / child.name
        if child.is_dir():
            copy_tree(child, target)
        else:
            copy_file(child, target)


def tree_inventory(root: Path) -> list[tuple[str, str, bytes | None]]:
    if not root.exists():
        raise FileNotFoundError(f"missing distribution: {root}")
    if not root.is_dir():
        raise OSError(f"expected distribution directory: {root}")
    validate_no_links(root, "distribution")
    inventory: list[tuple[str, str, bytes | None]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        if is_link(path):
            raise OSError(f"refusing linked distribution entry: {path}")
        relative = path.relative_to(root).as_posix()
        if path.is_dir():
            inventory.append((relative, "dir", None))
        else:
            inventory.append((relative, "file", path.read_bytes()))
    return inventory


def build_stage(source_root: Path, stage_root: Path) -> None:
    manifest_source = source_root / MANIFEST_RELATIVE
    skill_source = source_root / SKILL_RELATIVE
    validate_source_file(manifest_source, "Codex manifest source")
    validate_source_tree(skill_source, "Charter skill source")
    stage_root.mkdir(parents=True, exist_ok=True)
    for relative in PACKAGE_ROOT_ITEMS:
        source = source_root / relative
        if source.is_dir():
            copy_tree(source, stage_root / relative)
        else:
            validate_source_file(source, f"package source {relative}")
            copy_file(source, stage_root / relative)
    copy_file(manifest_source, stage_root / ".codex-plugin" / "plugin.json")
    copy_tree(skill_source, stage_root / "skills" / "charter-workflow")


def sync_legacy_snapshot(source_root: Path, repository_root: Path) -> None:
    manifest_source = source_root / ".codex-plugin" / "plugin.json"
    skill_source = source_root / "skills" / "charter-workflow"
    legacy_manifest = repository_root / LEGACY_MANIFEST_RELATIVE
    legacy_skill = repository_root / SKILL_RELATIVE
    validate_source_file(manifest_source, "generated manifest")
    validate_source_tree(skill_source, "generated skill tree")
    validate_no_links(legacy_manifest.parent, "legacy manifest destination")
    validate_no_links(legacy_skill, "legacy skill destination")
    legacy_manifest.parent.mkdir(parents=True, exist_ok=True)
    copy_file(manifest_source, legacy_manifest)
    copy_tree(skill_source, legacy_skill)


def build_distribution(repository_root: Path, destination_root: Path) -> Path:
    validate_no_traversal(destination_root, "output")
    validate_no_links(destination_root, "output")
    destination_root.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f".{PACKAGE_NAME}-stage-", dir=destination_root.parent) as temp_dir:
        stage_root = Path(temp_dir) / PACKAGE_NAME
        build_stage(repository_root, stage_root)
        if destination_root.exists():
            if is_link(destination_root):
                raise OSError(f"refusing linked destination: {destination_root}")
            if destination_root.is_file():
                raise OSError(f"expected directory destination: {destination_root}")
            shutil.rmtree(destination_root)
        stage_root.replace(destination_root)
    return destination_root


def ensure_check_match(source_root: Path, destination_root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix=f".{PACKAGE_NAME}-check-") as temp_dir:
        stage_root = Path(temp_dir) / PACKAGE_NAME
        build_stage(source_root, stage_root)
        if not destination_root.exists():
            raise FileNotFoundError(f"missing distribution: {destination_root}")
        if tree_inventory(stage_root) != tree_inventory(destination_root):
            raise ValueError(f"{destination_root} differs from freshly generated bytes")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare the committed distribution against a fresh build",
    )
    parser.add_argument(
        "--output",
        default=str(DISTRIBUTION_RELATIVE),
        help="distribution directory to build or compare",
    )
    args = parser.parse_args(argv)

    repository_root = Path(__file__).resolve().parents[1]
    raw_output = Path(args.output).expanduser()
    validate_no_traversal(raw_output, "output")
    validate_no_links(raw_output, "output")
    if not raw_output.is_absolute():
        output_root = (Path.cwd() / raw_output).resolve(strict=False)
    else:
        output_root = raw_output.resolve(strict=False)

    try:
        if args.check:
            ensure_check_match(repository_root, output_root)
        else:
            distribution_root = build_distribution(repository_root, output_root)
            sync_legacy_snapshot(distribution_root, repository_root)
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"Charter Kit packager: FAIL: {exc}", file=sys.stderr)
        return 1

    if args.check:
        print(f"Charter Kit packager: PASS: {output_root}")
    else:
        print(f"Charter Kit packager: built {output_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
