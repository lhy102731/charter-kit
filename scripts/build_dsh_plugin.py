#!/usr/bin/env python3
"""Build the DSH plugin distribution for Charter Kit.

The builder copies the portable core and the DSH adapter source into
``plugins/dsh-charter-kit/`` and emits ``lib/index.js`` from the adapter entry.
It is read-only with respect to the source tree, rejects links/caches, and
supports ``--check`` for deterministic byte comparison.


"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from pathlib import PurePosixPath


PACKAGE_NAME = "@dsh-external/dsh-charter-kit"
TARGET_RELATIVE = Path("targets") / "dsh"
DISTRIBUTION_RELATIVE = Path("plugins") / "dsh-charter-kit"
TARGET_SKILL_RELATIVE = Path("skills") / "charter-workflow"
DISTRIBUTION_SKILL_RELATIVE = DISTRIBUTION_RELATIVE / "skills" / "charter-workflow"
DISTRIBUTION_ROOT_ITEMS = (
    "LICENSE",
    "README.md",
    "DEVELOPMENT_CHARTER.md",
    "DEPENDENCIES.md",
    "dependencies.json",
    "agentpack.yaml",
    "portable",
    "scripts/check_dependencies.py",
    "scripts/init_project.py",
)
TARGET_FILES = (
    "package.json",
    Path("src") / "index.js",
    Path("scripts") / "build.sh",
)
IGNORED_TREE_NAMES = {"__pycache__", ".git", ".hg", ".svn", "plugins", "targets"}


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


def path_exists(path: Path) -> bool:
    try:
        return os.path.lexists(os.fspath(path))
    except OSError:
        return False


def is_regular_file(path: Path) -> bool:
    try:
        return stat.S_ISREG(os.lstat(path).st_mode)
    except (FileNotFoundError, OSError):
        return False


def is_hardlink(path: Path) -> bool:
    return is_regular_file(path) and os.lstat(path).st_nlink > 1


def lexical_absolute(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path)))


def is_same_or_descendant(path: Path, parent: Path) -> bool:
    try:
        return os.path.commonpath(
            [os.path.normcase(os.fspath(path)), os.path.normcase(os.fspath(parent))]
        ) == os.path.normcase(os.fspath(parent))
    except ValueError:
        return False


def validate_no_traversal(path: Path, label: str) -> None:
    if any(part == ".." for part in path.parts):
        raise OSError(f"refusing {label} with traversal segments: {path}")


def validate_no_links(path: Path, label: str) -> None:
    current = path
    for candidate in [current, *current.parents]:
        if path_exists(candidate) and is_link(candidate):
            raise OSError(f"refusing linked {label}: {candidate}")


def validate_existing_tree(path: Path, label: str) -> None:
    if not path_exists(path):
        return
    validate_no_links(path, label)
    try:
        mode = os.lstat(path).st_mode
    except OSError as exc:
        raise OSError(f"cannot inspect {label}: {path} ({exc})") from exc
    if not stat.S_ISDIR(mode):
        raise OSError(f"expected directory for {label}: {path}")
    for child in sorted(path.rglob("*"), key=lambda item: item.as_posix()):
        if is_link(child):
            raise OSError(f"refusing linked {label} entry: {child}")
        try:
            child_mode = os.lstat(child).st_mode
        except OSError as exc:
            raise OSError(f"cannot inspect {label} entry: {child} ({exc})") from exc
        if stat.S_ISDIR(child_mode):
            continue
        if not stat.S_ISREG(child_mode):
            raise OSError(f"refusing special {label} entry: {child}")
        if is_hardlink(child):
            raise OSError(f"refusing hard-linked {label} entry: {child}")


def validate_source_tree(path: Path, label: str) -> None:
    validate_no_traversal(path, label)
    validate_no_links(path, label)
    if not path_exists(path):
        raise FileNotFoundError(f"missing {label}: {path}")
    if not stat.S_ISDIR(os.lstat(path).st_mode):
        raise OSError(f"expected directory for {label}: {path}")
    for child in sorted(path.rglob("*")):
        if is_link(child):
            raise OSError(f"refusing linked {label} entry: {child}")
        try:
            child_mode = os.lstat(child).st_mode
        except OSError as exc:
            raise OSError(f"cannot inspect {label} entry: {child} ({exc})") from exc
        if stat.S_ISDIR(child_mode):
            continue
        if not stat.S_ISREG(child_mode):
            raise OSError(f"refusing special {label} entry: {child}")
        if is_hardlink(child):
            raise OSError(f"refusing hard-linked {label} entry: {child}")


def validate_source_file(path: Path, label: str) -> None:
    validate_no_traversal(path, label)
    validate_no_links(path, label)
    if not path_exists(path) or not is_regular_file(path):
        raise FileNotFoundError(f"missing {label}: {path}")
    if is_hardlink(path):
        raise OSError(f"refusing hard-linked {label}: {path}")


def copy_file(source: Path, destination: Path) -> None:
    validate_no_links(destination, "destination")
    if path_exists(destination):
        if not is_regular_file(destination):
            raise OSError(f"refusing special destination: {destination}")
        if is_hardlink(destination):
            raise OSError(f"refusing hard-linked destination: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.",
        dir=destination.parent,
    )
    temporary = Path(temporary_name)
    try:
        os.close(fd)
        shutil.copyfile(source, temporary)
        os.replace(temporary, destination)
    finally:
        if path_exists(temporary):
            try:
                temporary.unlink()
            except OSError:
                pass


def copy_tree(source: Path, destination: Path) -> None:
    validate_source_tree(source, "source tree")
    validate_no_traversal(destination, "destination")
    validate_no_links(destination, "destination")
    validate_existing_tree(destination, "destination")
    if path_exists(destination):
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


def validate_output_boundary(repository_root: Path, destination_root: Path) -> None:
    repository_root = lexical_absolute(repository_root)
    destination_root = lexical_absolute(destination_root)
    canonical = repository_root / DISTRIBUTION_RELATIVE
    if destination_root == canonical:
        return
    if is_same_or_descendant(destination_root, repository_root):
        raise OSError(
            "refusing output that overlaps the repository source tree; "
            f"use the canonical output {canonical} or an external directory"
        )
    if is_same_or_descendant(repository_root, destination_root):
        raise OSError(
            "refusing output that contains the repository source tree; "
            "choose a disjoint external directory"
        )


def validate_output_for_build(repository_root: Path, destination_root: Path) -> None:
    validate_no_traversal(destination_root, "output")
    validate_no_links(destination_root, "output")
    validate_output_boundary(repository_root, destination_root)
    canonical = lexical_absolute(repository_root) / DISTRIBUTION_RELATIVE
    if path_exists(destination_root):
        validate_existing_tree(destination_root, "output")
        if lexical_absolute(destination_root) != canonical:
            raise OSError(
                "refusing to replace an existing external output; "
                "choose a new output directory"
            )


def tree_inventory(root: Path) -> list[tuple[str, str, bytes | None]]:
    if not path_exists(root):
        raise FileNotFoundError(f"missing distribution: {root}")
    if not stat.S_ISDIR(os.lstat(root).st_mode):
        raise OSError(f"expected distribution directory: {root}")
    validate_no_links(root, "distribution")
    inventory: list[tuple[str, str, bytes | None]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        if is_link(path):
            raise OSError(f"refusing linked distribution entry: {path}")
        relative = path.relative_to(root).as_posix()
        mode = os.lstat(path).st_mode
        if stat.S_ISDIR(mode):
            inventory.append((relative, "dir", None))
        elif stat.S_ISREG(mode):
            if is_hardlink(path):
                raise OSError(f"refusing hard-linked distribution entry: {path}")
            inventory.append((relative, "file", path.read_bytes()))
        else:
            raise OSError(f"refusing special distribution entry: {path}")
    return inventory


def validate_distribution_manifest(stage_root: Path) -> None:
    manifest_path = stage_root / "package.json"
    validate_source_file(manifest_path, "DSH package manifest")
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise OSError(f"invalid DSH package manifest: {manifest_path} ({exc})") from exc
    if not isinstance(payload, dict):
        raise OSError(f"DSH package manifest must be a JSON object: {manifest_path}")
    if payload.get("name") != PACKAGE_NAME:
        raise OSError(f"DSH package manifest name must be {PACKAGE_NAME}")
    if payload.get("main") != "./lib/index.js":
        raise OSError("DSH package manifest main must be ./lib/index.js")


def build_stage(repository_root: Path, stage_root: Path) -> None:
    target_root = repository_root / TARGET_RELATIVE
    validate_source_tree(target_root, "DSH target source")
    for relative in DISTRIBUTION_ROOT_ITEMS:
        source = repository_root / relative
        if source.is_dir():
            copy_tree(source, stage_root / relative)
        else:
            validate_source_file(source, f"package source {relative}")
            copy_file(source, stage_root / relative)
    for relative in TARGET_FILES:
        source = target_root / relative
        validate_source_file(source, f"DSH target {relative}")
        copy_file(source, stage_root / relative)
    copy_tree(repository_root / TARGET_SKILL_RELATIVE, stage_root / "skills" / "charter-workflow")

    lib_dir = stage_root / "lib"
    lib_dir.mkdir(parents=True, exist_ok=True)
    copy_file(stage_root / "src" / "index.js", lib_dir / "index.js")
    validate_source_file(stage_root / "lib" / "index.js", "DSH distribution built entry")
    validate_distribution_manifest(stage_root)


def build_distribution(repository_root: Path, destination_root: Path) -> Path:
    validate_output_for_build(repository_root, destination_root)
    destination_root = lexical_absolute(destination_root)
    destination_root.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".dsh-charter-kit-stage-", dir=destination_root.parent) as temp_dir:
        stage_root = Path(temp_dir) / "dsh-charter-kit"
        stage_root.mkdir(parents=True, exist_ok=True)
        build_stage(repository_root, stage_root)
        canonical = lexical_absolute(repository_root) / DISTRIBUTION_RELATIVE
        if destination_root != canonical or not path_exists(destination_root):
            stage_root.replace(destination_root)
            return destination_root

        backup_parent = Path(tempfile.mkdtemp(prefix=".dsh-charter-kit-backup-", dir=destination_root.parent))
        backup = backup_parent / destination_root.name
        moved = False
        try:
            destination_root.rename(backup)
            moved = True
            stage_root.replace(destination_root)
        except Exception:
            if moved and not path_exists(destination_root) and path_exists(backup):
                backup.rename(destination_root)
            raise
        finally:
            if path_exists(backup_parent):
                shutil.rmtree(backup_parent, ignore_errors=True)
    return destination_root


def ensure_check_match(repository_root: Path, destination_root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix=".dsh-charter-kit-check-") as temp_dir:
        stage_root = Path(temp_dir) / "dsh-charter-kit"
        stage_root.mkdir(parents=True, exist_ok=True)
        build_stage(repository_root, stage_root)
        if not destination_root.exists():
            raise FileNotFoundError(f"missing distribution: {destination_root}")
        if tree_inventory(stage_root) != tree_inventory(destination_root):
            raise ValueError(f"{destination_root} differs from freshly generated bytes")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare the committed distribution against a fresh build")
    parser.add_argument("--output", default=None, help="distribution directory to build or compare")
    args = parser.parse_args(argv)

    repository_root = Path(__file__).resolve().parents[1]
    if args.output is None:
        output_root = repository_root / DISTRIBUTION_RELATIVE
    else:
        raw_output = Path(args.output).expanduser()
        validate_no_traversal(raw_output, "output")
        validate_no_links(raw_output, "output")
        output_root = lexical_absolute(raw_output)
    validate_no_links(output_root, "output")
    validate_output_boundary(repository_root, output_root)

    try:
        if args.check:
            ensure_check_match(repository_root, output_root)
        else:
            output_root = build_distribution(repository_root, output_root)
    except (FileNotFoundError, OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"Charter Kit DSH packager: FAIL: {exc}", file=sys.stderr)
        return 1

    if args.check:
        print(
            "Charter Kit DSH packager: PASS: "
            f"{output_root}"
        )
    else:
        print(
            "Charter Kit DSH packager: built "
            f"{output_root}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
