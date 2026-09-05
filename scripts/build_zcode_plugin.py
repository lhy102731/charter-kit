#!/usr/bin/env python3
"""Build the ZCode plugin distribution for Charter Kit.

The builder copies the portable core, the self-contained charter-workflow
skill, and the ZCode slash command into ``plugins/zcode-charter-kit/`` with
the ``.zcode-plugin/plugin.json`` manifest from ``targets/zcode/``. It is
read-only with respect to the source tree, rejects links/caches, and supports
``--check`` for deterministic byte comparison.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import sys
import tempfile
from pathlib import Path
from pathlib import PurePosixPath


PACKAGE_NAME = "zcode-charter-kit"
MANIFEST_RELATIVE = Path("targets") / "zcode" / ".zcode-plugin" / "plugin.json"
TARGET_SKILL_RELATIVE = Path("targets") / "zcode" / "skills" / "charter-workflow"
TARGET_COMMAND_RELATIVE = Path("targets") / "zcode" / "commands" / "charter-workflow.md"
DISTRIBUTION_RELATIVE = Path("plugins") / PACKAGE_NAME
PACKAGE_ROOT_ITEMS = (
    "LICENSE",
    "README.md",
    "DEVELOPMENT_CHARTER.md",
    "DEPENDENCIES.md",
    "dependencies.json",
    "dependencies.install.json",
    "agentpack.yaml",
    "portable",
)
PACKAGE_RUNTIME_SCRIPTS = (
    Path("scripts") / "check_dependencies.py",
    Path("scripts") / "init_project.py",
    Path("scripts") / "install_dependencies.py",
)
IGNORED_TREE_NAMES = {"__pycache__", ".git", ".hg", ".svn", "plugins", "tests"}


# Every tree this builder produces carries a marker naming the tree an edit
# survives in.  ``copy_tree`` replaces its destination wholesale, so a marker
# committed by hand would be deleted by the next build; writing it here means no
# produced tree can exist without one.  Markers are never copied between trees:
# the content is per-destination, so each builder writes its own.
GENERATED_MARKER_NAME = "GENERATED.md"
BUILD_COMMAND = "scripts/build_zcode_plugin.py"


def generated_marker_bytes(destination: str, source: str, note: str) -> bytes:
    """Render the marker body for one generated destination.

    Timestamp-free on purpose: ``--check`` compares committed bytes against a
    fresh build, and a marker that changed on every run would turn that
    comparison into noise instead of a signal.
    """

    lines = (
        "# Generated tree - do not hand-edit",
        "",
        f"`{destination}` is produced by `python {BUILD_COMMAND}`. Every build replaces",
        "this tree, so an edit made here is deleted rather than merged, and nothing",
        "reports the loss.",
        "",
        f"Edit `{source}` instead, then regenerate:",
        "",
        "```text",
        f"python {BUILD_COMMAND}",
        "```",
        "",
        note,
        "",
        "`docs/MIRROR-TOPOLOGY.md` maps every copy in this repository to the tree an",
        "edit survives in.",
    )
    return ("\n".join(lines) + "\n").encode("utf-8")


def write_generated_marker(root: Path, destination: str, source: str, note: str) -> None:
    """Write the marker after the copy step that would otherwise delete it."""

    (root / GENERATED_MARKER_NAME).write_bytes(
        generated_marker_bytes(destination, source, note)
    )


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
        if not stat.S_ISREG(child_mode):
            raise OSError(f"refusing special {label} entry: {child}")
        if is_hardlink(child):
            raise OSError(f"refusing hard-linked {label} entry: {child}")


def validate_source_tree(path: Path, label: str) -> None:
    validate_no_traversal(path, label)
    if not path_exists(path):
        raise FileNotFoundError(f"missing {label}: {path}")
    validate_no_links(path, label)
    if not path.is_dir():
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
    if not path_exists(path):
        raise FileNotFoundError(f"missing {label}: {path}")
    if is_link(path) or not is_regular_file(path):
        raise OSError(f"refusing non-regular {label}: {path}")
    if is_hardlink(path):
        raise OSError(f"refusing hard-linked {label}: {path}")


def copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with open(source, "rb") as reader, open(destination, "wb") as writer:
        shutil.copyfileobj(reader, writer)


def copy_tree(source: Path, destination: Path) -> None:
    for child in sorted(source.rglob("*"), key=lambda item: item.as_posix()):
        if child.is_dir():
            if child.name in IGNORED_TREE_NAMES or "__pycache__" in child.parts:
                continue
            (destination / child.relative_to(source)).mkdir(parents=True, exist_ok=True)
    for child in sorted(source.rglob("*"), key=lambda item: item.as_posix()):
        if (
            child.is_file()
            and "__pycache__" not in child.parts
            and child.name not in IGNORED_TREE_NAMES
            and child.name != GENERATED_MARKER_NAME
        ):
            copy_file(child, destination / child.relative_to(source))


def tree_inventory(root: Path) -> list[tuple[str, str, bytes | None]]:
    inventory: list[tuple[str, str, bytes | None]] = []
    for child in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        relative = PurePosixPath(child.relative_to(root)).as_posix()
        if child.is_dir():
            inventory.append(("dir", relative, None))
        elif child.is_file():
            inventory.append(("file", relative, child.read_bytes()))
    return inventory


def validate_manifest_source(path: Path) -> None:
    validate_source_file(path, "ZCode manifest source")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("ZCode manifest must be a JSON object")
    name = manifest.get("name")
    if name != "charter-kit":
        raise ValueError(f"ZCode manifest name must be charter-kit, got {name!r}")
    if manifest.get("skills") != "skills" or manifest.get("commands") != "commands":
        raise ValueError("ZCode manifest must declare component directories skills and commands")
    version = manifest.get("version")
    if not isinstance(version, str) or not version:
        raise ValueError("ZCode manifest version must be a non-empty string")


def validate_output_boundary(repository_root: Path, destination_root: Path) -> None:
    canonical = repository_root / DISTRIBUTION_RELATIVE
    if is_same_or_descendant(destination_root, canonical) or is_same_or_descendant(canonical, destination_root):
        return
    raise ValueError(f"refusing output outside {DISTRIBUTION_RELATIVE}: {destination_root}")


def validate_output_for_build(repository_root: Path, destination_root: Path) -> None:
    validate_no_links(destination_root, "distribution destination")
    validate_output_boundary(repository_root, destination_root)


def build_stage(source_root: Path, stage_root: Path) -> None:
    manifest_source = source_root / MANIFEST_RELATIVE
    skill_source = source_root / TARGET_SKILL_RELATIVE
    command_source = source_root / TARGET_COMMAND_RELATIVE
    validate_manifest_source(manifest_source)
    validate_source_tree(skill_source, "Charter skill source")
    validate_source_file(command_source, "ZCode command source")
    stage_root.mkdir(parents=True, exist_ok=True)
    for relative in PACKAGE_ROOT_ITEMS:
        source = source_root / relative
        if source.is_dir():
            copy_tree(source, stage_root / relative)
        else:
            validate_source_file(source, f"package source {relative}")
            copy_file(source, stage_root / relative)
    for relative in PACKAGE_RUNTIME_SCRIPTS:
        source = source_root / relative
        validate_source_file(source, f"package source {relative}")
        copy_file(source, stage_root / relative)
    copy_file(manifest_source, stage_root / ".zcode-plugin" / "plugin.json")
    copy_tree(skill_source, stage_root / "skills" / "charter-workflow")
    copy_file(command_source, stage_root / "commands" / "charter-workflow.md")
    write_generated_marker(
        stage_root,
        "plugins/zcode-charter-kit/",
        "targets/zcode/",
        "The Skill tree, the slash command, and the manifest are copied from that "
        "target; the portable core and the root-level files are copied from the "
        "repository root.",
    )


def build_distribution(repository_root: Path, destination_root: Path) -> Path:
    validate_output_for_build(repository_root, destination_root)
    destination_root = lexical_absolute(destination_root)
    destination_root.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f".{PACKAGE_NAME}-stage-", dir=destination_root.parent) as temp_dir:
        stage_root = Path(temp_dir) / PACKAGE_NAME
        build_stage(repository_root, stage_root)
        canonical = lexical_absolute(repository_root) / DISTRIBUTION_RELATIVE
        if destination_root != canonical or not path_exists(destination_root):
            stage_root.replace(destination_root)
            return destination_root

        backup_parent = Path(tempfile.mkdtemp(prefix=f".{PACKAGE_NAME}-backup-", dir=destination_root.parent))
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
    parser.add_argument("--check", action="store_true", help="compare the committed distribution against a fresh build")
    parser.add_argument("--output", default="", help="distribution directory to build or compare")
    args = parser.parse_args(argv)
    repository_root = Path(__file__).resolve().parents[1]
    destination_root = Path(args.output) if args.output else repository_root / DISTRIBUTION_RELATIVE
    try:
        if args.check:
            ensure_check_match(repository_root, destination_root)
            print(f"ZCode distribution check: {destination_root} matches a fresh build")
        else:
            built = build_distribution(repository_root, destination_root)
            print(f"ZCode distribution built: {built}")
    except (OSError, ValueError, FileNotFoundError) as exc:
        print(f"ZCode distribution build: FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
