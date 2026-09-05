#!/usr/bin/env python3
"""Validate the portable, host-neutral Charter Kit package.

The checker is deliberately read-only and uses only the Python standard
library. It validates the protocol documents, the zero-start entry points,
the dependency declaration/diagnostic scripts, and the byte-for-byte mirrors
that make the bundled Skill self-contained. It does not install, execute, or
load a provider and it never changes the package being inspected.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import sys
from pathlib import Path
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any, Iterable


SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)"
    r"(?:-(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)(?:\."
    r"(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)


PORTABLE_TEMPLATES: dict[str, tuple[str, ...]] = {
    "portable/templates/project-charter.md": (
        "## 1. Identity",
        "## 2. Desired outcome",
        "## 3. Product loop",
        "## 4. Success levels and proof",
        "## 5. Scope and effects",
        "## 6. Current-state and asset audit",
        "## 7. Capability map",
        "## 8. Task tree and route",
        "## 9. Automatic development authorization",
        "## 10. Risks and open decisions",
        "## 11. Approval record",
        "## 12. Change log",
    ),
    "portable/templates/leaf-task.md": (
        "## 1. Identity",
        "## 2. Result contract",
        "## 3. Preconditions",
        "## 4. Scope",
        "## 5. Acceptance",
        "## 6. Stop conditions and repair budget",
        "## 7. Integration policy",
        "## 8. Execution record",
        "## 9. Review and closure",
        "## 10. Design tree",
    ),
    "portable/templates/reuse-discovery.md": (
        "## 1. Discovery identity",
        "## 2. Search contract",
        "## 3. Search log",
        "## 4. Candidate evaluation",
        "## 5. Final decision and hand-back",
    ),
    "portable/templates/handoff.md": (
        "## Snapshot",
        "## Goal and boundary",
        "## Current facts",
        "## Evidence",
        "## Exact next action",
        "## Do not do",
        "## Capability notes",
        "## Resume instructions",
    ),
    "portable/templates/review.md": (
        "## Review identity",
        "## Independence declaration",
        "## Checks performed",
        "## Findings",
        "## Verdict",
        "## Re-review trigger",
    ),
    "portable/templates/decision.md": (
        "## Decision identity",
        "## Question that cannot be solved inside the current contract",
        "## Why it matters",
        "## Options",
        "## Recommendation",
        "## Approval",
        "## After the decision",
    ),
    "portable/templates/roadmap.md": (
        "## Goal reference",
        "## Delivery order",
        "## Active-work rule",
        "## Leaf readiness check",
        "## Closure rule",
        "## Decisions affecting the route",
    ),
    "portable/templates/evidence-receipt.md": (
        "## Identity",
        "## Subject and version",
        "## Operation",
        "## Coverage and limitations",
        "## Interpretation",
    ),
}

HOST_PROMPTS = (
    "portable/prompts/generic-bootstrap.md",
    "portable/prompts/codex-bootstrap.md",
    "portable/prompts/claude-bootstrap.md",
    "portable/prompts/gemini-bootstrap.md",
    "portable/prompts/deepseek-bootstrap.md",
)

SKILL_TEMPLATE_ROOT = "skills/charter-workflow/templates"

# Distribution boundaries.  ``portable/`` and the root charter documents are
# canonical; target and distribution trees are checked copies/adapters.
MARKETPLACE_RELATIVE = ".agents/plugins/marketplace.json"
TARGET_ROOT_RELATIVE = "targets/codex"
TARGET_MANIFEST_RELATIVE = "targets/codex/.codex-plugin/plugin.json"
TARGET_README_RELATIVE = "targets/codex/README.md"
TARGET_SKILL_RELATIVE = "targets/codex/skills/charter-workflow"
DISTRIBUTION_ROOT_RELATIVE = "plugins/charter-kit"
DISTRIBUTION_MANIFEST_RELATIVE = "plugins/charter-kit/.codex-plugin/plugin.json"
DISTRIBUTION_SKILL_RELATIVE = "plugins/charter-kit/skills/charter-workflow"
LEGACY_MANIFEST_RELATIVE = ".codex-plugin/plugin.json"
LEGACY_SKILL_RELATIVE = "skills/charter-workflow"
CHANGE_TRIAGE_REFERENCE = "portable/references/change-triage.md"
SKILL_CHANGE_TRIAGE_REFERENCE = "skills/charter-workflow/references/change-triage.md"
TARGET_CHANGE_TRIAGE_REFERENCE = "targets/codex/skills/charter-workflow/references/change-triage.md"
DISTRIBUTION_CHANGE_TRIAGE_REFERENCE = "plugins/charter-kit/skills/charter-workflow/references/change-triage.md"

# DSH target/distribution boundaries.
DSH_TARGET_ROOT_RELATIVE = "targets/dsh"
DSH_TARGET_PACKAGE_JSON_RELATIVE = "targets/dsh/package.json"
DSH_TARGET_SRC_RELATIVE = "targets/dsh/src/index.js"
DSH_TARGET_BUILD_SCRIPT_RELATIVE = "targets/dsh/scripts/build.sh"
DSH_TARGET_README_RELATIVE = "targets/dsh/README.md"
DSH_DISTRIBUTION_ROOT_RELATIVE = "plugins/dsh-charter-kit"
DSH_DISTRIBUTION_PACKAGE_JSON_RELATIVE = "plugins/dsh-charter-kit/package.json"
DSH_DISTRIBUTION_SRC_RELATIVE = "plugins/dsh-charter-kit/src/index.js"
DSH_DISTRIBUTION_BUILD_SCRIPT_RELATIVE = "plugins/dsh-charter-kit/scripts/build.sh"
DSH_DISTRIBUTION_LIB_RELATIVE = "plugins/dsh-charter-kit/lib/index.js"
DSH_DISTRIBUTION_SKILL_RELATIVE = "plugins/dsh-charter-kit/skills/charter-workflow"

ZCODE_TARGET_ROOT_RELATIVE = "targets/zcode"
ZCODE_TARGET_MANIFEST_RELATIVE = "targets/zcode/.zcode-plugin/plugin.json"
ZCODE_TARGET_COMMAND_RELATIVE = "targets/zcode/commands/charter-workflow.md"
ZCODE_DISTRIBUTION_ROOT_RELATIVE = "plugins/zcode-charter-kit"
ZCODE_DISTRIBUTION_MANIFEST_RELATIVE = "plugins/zcode-charter-kit/.zcode-plugin/plugin.json"
ZCODE_DISTRIBUTION_COMMAND_RELATIVE = "plugins/zcode-charter-kit/commands/charter-workflow.md"
ZCODE_DISTRIBUTION_SKILL_RELATIVE = "plugins/zcode-charter-kit/skills/charter-workflow"

# These are the root files copied into the self-contained distribution by the
# deterministic packager.  Keeping the list explicit makes an accidental
# omission visible and avoids treating arbitrary repository files as package
# input.
DISTRIBUTION_ROOT_ITEMS = (
    "LICENSE",
    "README.md",
    "DEVELOPMENT_CHARTER.md",
    "DEPENDENCIES.md",
    "dependencies.json",
    "dependencies.install.json",
    "agentpack.yaml",
    "portable",
    "scripts/check_dependencies.py",
    "scripts/init_project.py",
    "scripts/install_dependencies.py",
)

MARKETPLACE_INSTALLATION_POLICIES = ("NOT_AVAILABLE", "AVAILABLE", "INSTALLED_BY_DEFAULT")
MARKETPLACE_AUTHENTICATION_POLICIES = ("ON_INSTALL", "ON_USE")

REQUIRED_FILES = (
    "LICENSE",
    "DEVELOPMENT_CHARTER.md",
    "README.md",
    "DEPENDENCIES.md",
    "dependencies.json",
    "agentpack.yaml",
    ".codex-plugin/plugin.json",
    TARGET_MANIFEST_RELATIVE,
    TARGET_README_RELATIVE,
    f"{TARGET_SKILL_RELATIVE}/SKILL.md",
    DISTRIBUTION_MANIFEST_RELATIVE,
    f"{DISTRIBUTION_SKILL_RELATIVE}/SKILL.md",
    MARKETPLACE_RELATIVE,
    "scripts/build_codex_plugin.py",
    "scripts/build_dsh_plugin.py",
    "scripts/build_zcode_plugin.py",
    DSH_TARGET_PACKAGE_JSON_RELATIVE,
    DSH_TARGET_SRC_RELATIVE,
    DSH_TARGET_BUILD_SCRIPT_RELATIVE,
    DSH_TARGET_README_RELATIVE,
    DSH_DISTRIBUTION_PACKAGE_JSON_RELATIVE,
    DSH_DISTRIBUTION_SRC_RELATIVE,
    DSH_DISTRIBUTION_BUILD_SCRIPT_RELATIVE,
    DSH_DISTRIBUTION_LIB_RELATIVE,
    f"{DSH_DISTRIBUTION_SKILL_RELATIVE}/SKILL.md",
    *PORTABLE_TEMPLATES,
    *HOST_PROMPTS,
    "portable/commands/charter-workflow.md",
    CHANGE_TRIAGE_REFERENCE,
    "portable/references/design-interview.md",
    "skills/charter-workflow/SKILL.md",
    SKILL_CHANGE_TRIAGE_REFERENCE,
    "skills/charter-workflow/references/DEVELOPMENT_CHARTER.md",
    "skills/charter-workflow/references/DEPENDENCIES.md",
    "skills/charter-workflow/references/design-interview.md",
    "skills/charter-workflow/references/tool-routing.md",
    "skills/charter-workflow/dependencies.json",
    "skills/charter-workflow/scripts/check_dependencies.py",
    "skills/charter-workflow/scripts/init_project.py",
    *(f"{SKILL_TEMPLATE_ROOT}/{Path(path).name}" for path in PORTABLE_TEMPLATES),
    "scripts/validate_kit.py",
    "scripts/check_dependencies.py",
    "scripts/init_project.py",
    "scripts/install_dependencies.py",
    "dependencies.install.json",
    TARGET_CHANGE_TRIAGE_REFERENCE,
    DISTRIBUTION_CHANGE_TRIAGE_REFERENCE,
    "tests/test_charter_kit.py",
    "tests/test_dependencies.py",
    "tests/test_generic_bootstrap.py",
    "tests/pressure-scenarios.md",
    "tests/structure-checklist.md",
)

MIRRORS = (
    ("DEVELOPMENT_CHARTER.md", "skills/charter-workflow/references/DEVELOPMENT_CHARTER.md"),
    ("DEPENDENCIES.md", "skills/charter-workflow/references/DEPENDENCIES.md"),
    ("dependencies.json", "skills/charter-workflow/dependencies.json"),
    ("scripts/check_dependencies.py", "skills/charter-workflow/scripts/check_dependencies.py"),
    ("scripts/init_project.py", "skills/charter-workflow/scripts/init_project.py"),
    ("portable/references/design-interview.md", "skills/charter-workflow/references/design-interview.md"),
    (CHANGE_TRIAGE_REFERENCE, SKILL_CHANGE_TRIAGE_REFERENCE),
    *((path, f"{SKILL_TEMPLATE_ROOT}/{Path(path).name}") for path in PORTABLE_TEMPLATES),
    (
        "portable/references/design-interview.md",
        "skills/charter-workflow/references/design-interview.md",
    ),
)

FORBIDDEN_CORE_TERMS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("KBase", re.compile(r"\bkbase\b", re.IGNORECASE)),
    ("AG2", re.compile(r"\bag2\b", re.IGNORECASE)),
    ("ExperimentSpec", re.compile(r"\bexperimentspec\b", re.IGNORECASE)),
    ("NextQuestion", re.compile(r"\bnextquestion\b", re.IGNORECASE)),
    ("daily_run.py", re.compile(r"\bdaily_run\.py\b", re.IGNORECASE)),
    ("daily_select.py", re.compile(r"\bdaily_select\.py\b", re.IGNORECASE)),
    ("a-share-quant-selector", re.compile(r"\ba-share-quant-selector\b", re.IGNORECASE)),
    ("个人版", re.compile("个人版")),
    ("研究闭环", re.compile("研究闭环")),
    ("量化研究", re.compile("量化研究")),
    ("BUSINESS", re.compile(r"\bBUSINESS\b")),
    ("PRODUCTION_AUTHORIZED", re.compile(r"\bPRODUCTION_AUTHORIZED\b")),
    ("Holdout", re.compile(r"\bHoldout\b", re.IGNORECASE)),
    ("V3.4.2", re.compile(r"\bV3\.4\.2\b", re.IGNORECASE)),
    ("R1.13", re.compile(r"\bR1\.13\b", re.IGNORECASE)),
    ("R2.0", re.compile(r"\bR2\.0\b", re.IGNORECASE)),
    ("Claude CLI", re.compile(r"\bClaude\s+CLI\b", re.IGNORECASE)),
    ("DeepSeek Harness", re.compile(r"\bDeepSeek\s+Harness\b", re.IGNORECASE)),
    ("Evaluator", re.compile(r"\bEvaluator\b")),
    ("Learning", re.compile(r"\bLearning\b")),
    ("Experiment", re.compile(r"\bExperiment\b")),
)

FORBIDDEN_MARKERS = ("[TODO:", "[TBD:")
NO_SKILL_PREREQUISITE = re.compile(
    r"(?:required\s+prerequisite|must\s+(?:first\s+)?install|install\s+the)"
    r"[^\n]{0,120}(?:charter-workflow|charter\s+workflow)[^\n]{0,40}skill",
    re.IGNORECASE,
)

PLUGIN_INTERFACE_STRING_FIELDS = (
    "displayName",
    "shortDescription",
    "longDescription",
    "developerName",
    "category",
)

PROMPT_REQUIREMENTS = (
    ".charter/project.md",
    ".charter/roadmap.md",
    ".charter/reuse-discovery.md",
    ".charter/current-task.md",
)

HOST_LEAF_APPROVAL_RULE = (
    "Project approval does not approve any leaf; in `MANUAL` obtain separate leaf approval, "
    "or in `AUTO_DEV` cite matching preauthorization, before moving the leaf beyond `DRAFT`."
)

DEPENDENCY_STATUSES = ("AVAILABLE", "MISSING", "UNVERIFIED", "FALLBACK")

# Reuse Check deliberately has one small gate state vocabulary.  Coverage,
# result, and final route are recorded independently in the discovery record;
# keeping the sets here prevents validators from accidentally reviving the
# older all-in-one status field.
REUSE_GATE_STATES = ("PENDING", "COMPLETE", "BLOCKED")
REUSE_COVERAGE_VALUES = (
    "SEARCHED",
    "NOT_SEARCHED",
    "NOT_AUTHORIZED",
    "BLOCKED_TOOLING",
)
REUSE_RESULT_VALUES = ("MATCH", "NO_MATCH", "UNKNOWN")
REUSE_FINAL_ROUTES = (
    "ADOPT",
    "ADAPT",
    "REFERENCE_ONLY",
    "BUILD_NEW",
    "REUSE_SPIKE",
    "NEEDS_DECISION",
)

# A high-value uncertainty must be visibly blocking until it is resolved.
# Permit either Markdown code ticks or plain words, and allow ``or DEFER``
# between UNKNOWN and the resolution phrase.  The order is intentional: it
# makes the rule easy to audit in every host entry point.
HIGH_VALUE_UNKNOWN_RULE = re.compile(
    r"(?i)high-value\s+`?UNKNOWN`?"
    r"[^\n]{0,140}(?:remains?\s+unresolved|unresolved)"
)

# A bounded waiver is a leaf-scoped readiness exception, not another gate
# state.  Entry points repeat this compact rule because a host may load one
# prompt without loading the full Skill.  Allow line wrapping between words,
# but require the explicit COMPLETE-or-waiver relationship and the Leaf scope.
REUSE_READY_WAIVER_RULE = re.compile(
    r"(?is)A\s+Leaf\s+may\s+enter\s+`READY`\s+only\s+when"
    r".{0,260}?`COMPLETE`.{0,260}?specific\s+Leaf"
    r".{0,180}?bounded\s+waiver"
)

# The legacy aggregate vocabulary must never be presented as the Reuse Gate
# state.  This catches stale mirrors even when all three new words happen to
# be present elsewhere in the same document.
LEGACY_REUSE_GATE_CONTRACTS = (
    "NOT_STARTED | IN_PROGRESS | COMPLETE | LIMITED | WAIVED | BLOCKED_TOOLING",
    "NOT_STARTED`, `IN_PROGRESS`, `BLOCKED_TOOLING",
)

# The session ledger must be declared before the first state transition, so
# the first-start section may carry exactly one declaration and it has to sit
# in the step that performs `DRAFT` -> `APPROVED`.  A second copy elsewhere in
# that section is what re-creates the contradiction this rule exists to close:
# a leftover "before the first state transition of the first leaf" wording lets
# an executor defer the declaration past the transition it guards.  Presence
# checks cannot see duplication, so match whole lines and count them.
LEDGER_DECLARATION_LINE_RE = re.compile(r"(?i)(?:session )?ledger (?:mode|declaration)")
LEDGER_BEFORE_TRANSITION_RE = re.compile(
    r"Before moving `DRAFT` to `APPROVED`[^.]*?declare the session ledger mode"
)

# DSH is retained as an experimental adapter shell.  Its presence is useful
# for structural checks, but it is not a verified installation target.  Keep
# the claim detector narrow enough to allow ordinary words such as "build"
# and the root README's Codex installation instructions while rejecting an
# explicit DSH install command or a statement that DSH itself is supported.
DSH_INSTALL_COMMAND_RE = re.compile(r"(?i)\bdev_(?:inject_plugin|install_package)\b")
DSH_SUPPORTED_CLAIM_RE = re.compile(
    r"(?i)\b(?:supported|official(?:ly)?|verified|production(?:[- ]ready)?)\b|"
    r"正式(?:支持|安装)|官方(?:支持|安装)|已验证(?:支持|安装)|可安装"
)


def _contains_dsh_supported_claim(text: str) -> bool:
    """Return whether a line positively claims verified DSH support.

    The repository's shared README deliberately says that DSH is
    experimental/unverified and makes *no* supported-install claim.  A broad
    regex would flag that disclaimer itself, so inspect each DSH-containing
    line and ignore explicit negative/disclaimer wording.
    """

    # Inspect short clauses rather than whole paragraphs.  A README commonly
    # says that Codex is verified and then mentions DSH as experimental on the
    # same line; treating that whole line as one claim would be a false
    # positive.  Conversely, "experimental but supported" must still be
    # rejected because the positive claim is in the DSH clause itself.
    for line in text.splitlines():
        for clause in re.split(r"[.!?;；。！？]+", line):
            low = clause.lower().strip()
            if "dsh" not in low and "@dsh-external" not in low:
                continue
            match = DSH_SUPPORTED_CLAIM_RE.search(clause)
            if match is None:
                continue
            before = clause[: match.start()].lower()
            after = clause[match.end() :].lower()
            negative = re.search(
                r"(?:not|no|never|cannot|can't|does\s+not|do\s+not|"
                r"without|unverified|unsupported)\b[^\n]{0,50}$",
                before,
            )
            negative = negative or re.search(
                r"^\s*(?:installation\s+is\s+)?(?:not|never|unsupported|"
                r"unverified)\b|\b(?:not|never|unsupported|unverified)\b",
                after,
            )
            if negative is None:
                return True
    return False


def _is_junction(path: Path) -> bool:
    """Return whether *path* is a directory junction/reparse point.

    ``Path.is_symlink`` does not identify Windows junctions on every Python
    version.  Validation must treat both forms as links because either can
    make a supposedly self-contained package read outside its root.
    """

    checker = getattr(path, "is_junction", None)
    if callable(checker):
        try:
            return bool(checker())
        except OSError:
            return False
    if os.name == "nt":
        try:
            attributes = os.lstat(path).st_file_attributes
        except (AttributeError, FileNotFoundError, OSError):
            return False
        return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x0400))
    return False


def _is_link(path: Path) -> bool:
    return path.is_symlink() or _is_junction(path)


def _is_regular_file(path: Path) -> bool:
    try:
        return stat.S_ISREG(os.lstat(path).st_mode)
    except (FileNotFoundError, OSError):
        return False


def _is_hardlink(path: Path) -> bool:
    try:
        return _is_regular_file(path) and os.lstat(path).st_nlink > 1
    except OSError:
        return False


class Checker:
    """Collect actionable validation failures without mutating the package."""

    def __init__(self, root: Path) -> None:
        self.root = root.expanduser().resolve()
        self.errors: list[str] = []
        self.checked = 0
        self._missing: set[str] = set()
        self._missing_dirs: set[str] = set()

    def _path(self, relative: str) -> Path:
        return self.root / relative

    def _missing_file(self, relative: str) -> None:
        if relative not in self._missing:
            self._missing.add(relative)
            self.errors.append(f"missing file: {relative}")

    def _missing_dir(self, relative: str) -> None:
        if relative not in self._missing_dirs:
            self._missing_dirs.add(relative)
            self.errors.append(f"missing directory: {relative}")

    def read(self, relative: str) -> str:
        path = self._path(relative)
        if not path.is_file():
            self._missing_file(relative)
            return ""
        self.checked += 1
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            self.errors.append(f"not UTF-8: {relative} ({exc})")
        except OSError as exc:
            self.errors.append(f"cannot read: {relative} ({exc})")
        return ""

    def read_bytes(self, relative: str) -> bytes | None:
        path = self._path(relative)
        if not path.is_file():
            self._missing_file(relative)
            return None
        self.checked += 1
        try:
            return path.read_bytes()
        except OSError as exc:
            self.errors.append(f"cannot read: {relative} ({exc})")
            return None

    def require(self, text: str, needle: str, where: str) -> None:
        if needle not in text:
            self.errors.append(f"{where}: missing {needle!r}")

    def require_regex(
        self,
        text: str,
        pattern: str | re.Pattern[str],
        where: str,
        message: str,
        flags: int = re.IGNORECASE | re.MULTILINE,
    ) -> None:
        compiled = re.compile(pattern, flags) if isinstance(pattern, str) else pattern
        if compiled.search(text) is None:
            self.errors.append(f"{where}: {message}")

    def _safe_relative_path(
        self,
        value: Any,
        where: str,
        *,
        expected: str | None = None,
        require_directory: bool = False,
    ) -> Path | None:
        """Validate a marketplace/plugin path and resolve it inside ``root``.

        Marketplace paths are deliberately stricter than ordinary Markdown
        links: they must be relative POSIX paths beginning with ``./`` and
        cannot contain traversal, drive letters, or links escaping the
        repository.  Returning the resolved path lets callers check existence
        without duplicating the boundary logic.
        """

        if not isinstance(value, str) or not value.strip():
            self.errors.append(f"{where} must be a non-empty relative path")
            return None
        if "\\" in value:
            self.errors.append(f"{where} must use POSIX / separators")
        normalized = value.replace("\\", "/")
        if expected is not None and normalized != expected:
            self.errors.append(f"{where} must be {expected}")
        if not normalized.startswith("./"):
            self.errors.append(f"{where} must start with ./")
        # ``PurePosixPath`` discards a leading ``.`` component, so strip the
        # required prefix explicitly before resolving rather than indexing
        # ``parts[1:]`` (which would accidentally drop ``plugins``).
        relative_text = normalized[2:] if normalized.startswith("./") else normalized
        pure_posix = PurePosixPath(relative_text)
        pure_windows = PureWindowsPath(value)
        if pure_posix.is_absolute() or pure_windows.is_absolute() or pure_windows.drive:
            self.errors.append(f"{where} must be relative")
            return None
        if not pure_posix.parts or any(part in {"", ".", ".."} for part in pure_posix.parts):
            # ``.`` is harmless but rejecting it keeps identity checks
            # deterministic and prevents alternate spellings of a source.
            self.errors.append(f"{where} contains an unsafe relative path")
            return None
        candidate = (self.root / Path(*pure_posix.parts)).resolve(strict=False)
        try:
            inside = candidate.is_relative_to(self.root)
        except AttributeError:  # pragma: no cover - Python < 3.9 fallback
            inside = str(candidate).startswith(str(self.root) + os.sep)
        if not inside:
            self.errors.append(f"{where} resolves outside the package root")
            return None
        # Check every existing component, including the source root itself.
        current = candidate
        components = [current, *current.parents]
        for component in components:
            if component == self.root.parent:
                break
            if component.exists() and _is_link(component):
                self.errors.append(f"{where} contains a symlink or junction: {component}")
                return None
            if component == self.root:
                break
        if require_directory and candidate.exists() and not candidate.is_dir():
            self.errors.append(f"{where} must point to a directory")
            return None
        return candidate

    def _check_tree_safety(
        self,
        relative: str,
        *,
        required: bool = True,
        reject_caches: bool = True,
    ) -> Path | None:
        """Check a package subtree for links and unsafe generated artifacts."""

        path = self._path(relative)
        if _is_link(path):
            self.errors.append(f"{relative}: symlink or junction is not allowed")
            return None
        if not path.exists():
            if required:
                self._missing_dir(relative)
            return None
        try:
            root_mode = os.lstat(path).st_mode
        except OSError as exc:
            self.errors.append(f"cannot inspect directory: {relative} ({exc})")
            return None
        if not stat.S_ISDIR(root_mode):
            self.errors.append(f"expected directory: {relative}")
            return None
        for child in sorted(path.rglob("*"), key=lambda item: item.as_posix()):
            if _is_link(child):
                self.errors.append(f"{relative}: symlink or junction is not allowed: {child.relative_to(self.root)}")
                continue
            try:
                child_mode = os.lstat(child).st_mode
            except OSError as exc:
                self.errors.append(f"{relative}: cannot inspect entry {child.relative_to(self.root)} ({exc})")
                continue
            if stat.S_ISDIR(child_mode):
                continue
            if not stat.S_ISREG(child_mode):
                self.errors.append(f"{relative}: special file is not allowed: {child.relative_to(self.root)}")
                continue
            if _is_hardlink(child):
                self.errors.append(f"{relative}: hard-linked file is not allowed: {child.relative_to(self.root)}")
                continue
            rel_parts = child.relative_to(path).parts
            if any(part == ".." for part in rel_parts):
                self.errors.append(f"{relative}: unsafe traversal entry {child}")
            if reject_caches and (
                child.suffix.lower() == ".pyc" or "__pycache__" in rel_parts
            ):
                self.errors.append(f"{relative}: generated cache is not allowed: {child.relative_to(self.root)}")
        return path

    def _tree_bytes(self, relative: str, *, reject_caches: bool) -> dict[str, bytes] | None:
        path = self._check_tree_safety(relative, reject_caches=reject_caches)
        if path is None:
            return None
        result: dict[str, bytes] = {}
        for child in sorted(path.rglob("*"), key=lambda item: item.relative_to(path).as_posix()):
            if _is_regular_file(child) and not _is_link(child):
                if not reject_caches and (
                    child.suffix.lower() == ".pyc" or "__pycache__" in child.relative_to(path).parts
                ):
                    continue
                result[child.relative_to(path).as_posix()] = child.read_bytes()
        return result

    def _compare_trees(self, left: str, right: str, *, label: str) -> None:
        # Canonical source trees may contain interpreter caches left by local
        # test runs; those are ignored on the source side.  Generated target
        # and distribution trees must remain cache-free.
        left_tree = self._tree_bytes(left, reject_caches=False)
        right_tree = self._tree_bytes(right, reject_caches=True)
        if left_tree is None or right_tree is None:
            return
        left_names = set(left_tree)
        right_names = set(right_tree)
        for missing in sorted(left_names - right_names):
            self.errors.append(f"{right}: missing {missing} required by {left}")
        for extra in sorted(right_names - left_names):
            self.errors.append(f"{right}: unexpected {extra} ({label} tree drift)")
        for name in sorted(left_names & right_names):
            if left_tree[name] != right_tree[name]:
                self.errors.append(
                    f"{right}/{name}: differs from {left}/{name} ({label}; byte mismatch)"
                )

    def run(self) -> int:
        # Touch every expected path up front so omissions are reported even if
        # a later semantic check has no text to inspect.
        for relative in REQUIRED_FILES:
            if not self._path(relative).is_file():
                self._missing_file(relative)

        self.check_manifest()
        self.check_license()
        self.check_charter()
        self.check_templates()
        self.check_prompts()
        self.check_command()
        self.check_skill()
        self.check_dependencies_manifest()
        self.check_dependency_script("scripts/check_dependencies.py")
        self.check_initializer("scripts/init_project.py")
        self.check_tool_references()
        self.check_agentpack()
        self.check_marketplace()
        self.check_target_and_distribution()
        self.check_dsh_target_and_distribution()
        self.check_zcode_target_and_distribution()
        self.check_readme()
        self.check_tests_and_docs()
        self.check_mirrors()
        self.check_host_prompt_identity()
        self.check_domain_neutrality()

        if self.errors:
            print("Charter Kit validation: FAIL")
            for error in self.errors:
                print(f"- {error}")
            return 1

        print(f"Charter Kit validation: PASS ({self.checked} files checked)")
        print("- portable core present")
        print("- zero-start and resume entry points present")
        print("- dependency manifest and diagnostics present")
        print("- self-contained Skill mirrors are byte-identical")
        print("- host prompts share the generic canonical entry")
        print("- plugin manifest and LICENSE valid")
        print("- marketplace, Codex target, and generated distribution valid")
        print("- DSH target and generated distribution valid")
        print("- ZCode target and generated distribution valid")
        print("- target/distribution and legacy mirrors are byte-identical")
        print("- no install side effect is declared")
        return 0

    # ------------------------------------------------------------------
    # Package and manifest checks
    # ------------------------------------------------------------------
    def check_manifest(self) -> None:
        relative = ".codex-plugin/plugin.json"
        text = self.read(relative)
        if not text:
            return
        try:
            manifest = json.loads(text)
        except json.JSONDecodeError as exc:
            self.errors.append(f"{relative}: invalid JSON ({exc})")
            return
        if not isinstance(manifest, dict):
            self.errors.append(f"{relative}: top-level value must be an object")
            return

        allowed_top = {
            "id",
            "name",
            "version",
            "description",
            "skills",
            "apps",
            "mcpServers",
            "interface",
            "author",
            "homepage",
            "repository",
            "license",
            "keywords",
        }
        for key in sorted(set(manifest) - allowed_top):
            self.errors.append(f"plugin manifest field `{key}` is not accepted")

        if manifest.get("name") != "charter-kit":
            self.errors.append("plugin manifest name must be charter-kit")
        version = manifest.get("version")
        if not isinstance(version, str) or SEMVER_RE.fullmatch(version) is None:
            self.errors.append("plugin manifest version must be strict semver")
        description = manifest.get("description")
        if not isinstance(description, str) or not description.strip():
            self.errors.append("plugin manifest description must be a non-empty string")
        if manifest.get("license") != "MIT":
            self.errors.append("plugin manifest license must be MIT")

        skills = manifest.get("skills")
        if skills != "./skills/":
            self.errors.append("plugin manifest must expose ./skills/")
        elif not self._path("skills").is_dir():
            self.errors.append("plugin manifest skills path must exist")

        author = manifest.get("author")
        if not isinstance(author, dict):
            self.errors.append("plugin manifest author must be an object")
        elif not isinstance(author.get("name"), str) or not author["name"].strip():
            self.errors.append("plugin manifest author.name must be a non-empty string")

        keywords = manifest.get("keywords")
        if keywords is not None and (
            not isinstance(keywords, list)
            or not all(isinstance(value, str) and value.strip() for value in keywords)
        ):
            self.errors.append("plugin manifest keywords must be an array of non-empty strings")

        interface = manifest.get("interface")
        if not isinstance(interface, dict):
            self.errors.append("plugin manifest interface must be an object")
            return
        allowed_interface = {
            "displayName",
            "shortDescription",
            "longDescription",
            "developerName",
            "category",
            "capabilities",
            "websiteURL",
            "privacyPolicyURL",
            "termsOfServiceURL",
            "brandColor",
            "composerIcon",
            "logo",
            "logoDark",
            "screenshots",
            "defaultPrompt",
            "default_prompt",
        }
        for key in sorted(set(interface) - allowed_interface):
            self.errors.append(f"plugin manifest interface field `{key}` is not accepted")
        for field in PLUGIN_INTERFACE_STRING_FIELDS:
            value = interface.get(field)
            if not isinstance(value, str) or not value.strip():
                self.errors.append(
                    f"plugin manifest interface.{field} must be a non-empty string"
                )
        capabilities = interface.get("capabilities")
        if not isinstance(capabilities, list) or not capabilities or not all(
            isinstance(value, str) and value.strip() for value in capabilities
        ):
            # Keep this wording stable for callers and behavior tests.
            self.errors.append(
                "plugin manifest interface.capabilities must be an array of non-empty strings"
            )
        prompt_key = "defaultPrompt" if "defaultPrompt" in interface else "default_prompt"
        if prompt_key not in interface:
            # Keep the historical field name in the diagnostic even though
            # the ingestion schema also accepts snake_case.
            self.errors.append("plugin manifest interface.defaultPrompt is required")
        else:
            prompts = interface[prompt_key]
            if not isinstance(prompts, list) or not 1 <= len(prompts) <= 3:
                self.errors.append(
                    "plugin manifest interface.defaultPrompt must contain 1 to 3 strings"
                )
            elif not all(
                isinstance(value, str) and value.strip() and len(value) <= 128
                for value in prompts
            ):
                self.errors.append(
                    "plugin manifest interface.defaultPrompt entries must be non-empty strings of at most 128 characters"
                )

    def _load_json_object(self, relative: str, label: str) -> dict[str, Any] | None:
        """Read a JSON object and emit a stable, path-qualified diagnostic."""

        text = self.read(relative)
        if not text:
            return None
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            self.errors.append(f"{relative}: invalid JSON ({exc})")
            return None
        if not isinstance(data, dict):
            self.errors.append(f"{relative}: {label} top-level value must be an object")
            return None
        return data

    def _check_secondary_plugin_manifest(
        self,
        relative: str,
        base_relative: str,
        label: str,
    ) -> dict[str, Any] | None:
        """Validate a target/distribution plugin manifest.

        The root manifest has the historical, detailed checks above.  Target
        and generated manifests use this smaller shared contract so target
        prose may vary while identity, version, license, and self-contained
        Skill paths remain fixed.
        """

        data = self._load_json_object(relative, f"{label} manifest")
        if data is None:
            return None
        if data.get("name") != "charter-kit":
            self.errors.append(f"{relative}: {label} manifest name must be charter-kit")
        version = data.get("version")
        if not isinstance(version, str) or SEMVER_RE.fullmatch(version) is None:
            self.errors.append(f"{relative}: {label} manifest version must be strict semver")
        if data.get("license") != "MIT":
            self.errors.append(f"{relative}: {label} manifest license must be MIT")
        description = data.get("description")
        if not isinstance(description, str) or not description.strip():
            self.errors.append(f"{relative}: {label} manifest description must be non-empty")
        author = data.get("author")
        if not isinstance(author, dict) or not isinstance(author.get("name"), str) or not author["name"].strip():
            self.errors.append(f"{relative}: {label} manifest author.name must be non-empty")
        skills = data.get("skills")
        if skills != "./skills/":
            self.errors.append(f"{relative}: {label} manifest must expose ./skills/")
        base = self._path(base_relative)
        skill_root = base / "skills"
        if not skill_root.is_dir():
            self.errors.append(f"{relative}: {label} manifest skills directory is missing: {base_relative}/skills")
        elif _is_link(skill_root):
            self.errors.append(f"{relative}: {label} manifest skills directory must not be a symlink or junction")
        interface = data.get("interface")
        if not isinstance(interface, dict):
            self.errors.append(f"{relative}: {label} manifest interface must be an object")
        else:
            for field in ("displayName", "shortDescription", "longDescription", "developerName", "category"):
                value = interface.get(field)
                if not isinstance(value, str) or not value.strip():
                    self.errors.append(f"{relative}: {label} manifest interface.{field} must be non-empty")
            if interface.get("category") != "Developer Tools":
                self.errors.append(f"{relative}: {label} manifest interface.category must be Developer Tools")
        return data

    def check_marketplace(self) -> None:
        """Validate the repository marketplace registration and source safety."""

        relative = MARKETPLACE_RELATIVE
        data = self._load_json_object(relative, "marketplace")
        if data is None:
            return

        allowed_top = {"name", "interface", "plugins"}
        for key in sorted(set(data) - allowed_top):
            self.errors.append(f"{relative}: unsupported top-level field `{key}`")
        if data.get("name") != "charter-kit":
            self.errors.append(f"{relative}: marketplace name must be charter-kit")

        interface = data.get("interface")
        if not isinstance(interface, dict):
            self.errors.append(f"{relative}: marketplace interface must be an object")
        elif not isinstance(interface.get("displayName"), str) or not interface["displayName"].strip():
            self.errors.append(f"{relative}: marketplace interface.displayName must be non-empty")

        entries = data.get("plugins")
        if not isinstance(entries, list) or not entries:
            self.errors.append(f"{relative}: marketplace plugins must be a non-empty array")
            # Keep the canonical contract visible even when a caller supplies
            # the obsolete single-entry shape; this makes repair diagnostics
            # actionable and preserves compatibility with early layout tests.
            self.errors.append(f"{relative}: missing marketplace plugin entry charter-kit")
            self.errors.append(f"{relative}: expected source path ./plugins/charter-kit")
            return

        seen: set[str] = set()
        charter_entries = 0
        for index, entry in enumerate(entries):
            prefix = f"{relative}: plugins[{index}]"
            if not isinstance(entry, dict):
                self.errors.append(f"{prefix} must be an object")
                continue
            name = entry.get("name")
            if not isinstance(name, str) or not name.strip():
                self.errors.append(f"{prefix}.name must be a non-empty string")
                name = ""
            elif name in seen:
                self.errors.append(f"{relative}: duplicate plugin name {name!r}")
            else:
                seen.add(name)
            if name == "charter-kit":
                charter_entries += 1

            source = entry.get("source")
            source_path: Any = None
            if not isinstance(source, dict):
                self.errors.append(f"{prefix}.source must be an object with source.path")
            else:
                if source.get("source") != "local":
                    self.errors.append(f"{prefix}.source.source must be local")
                source_path = source.get("path")
                if source_path is None:
                    self.errors.append(f"{prefix}.source.path is required")
                else:
                    expected = "./plugins/charter-kit" if name == "charter-kit" else None
                    resolved = self._safe_relative_path(
                        source_path,
                        f"{prefix}.source.path",
                        expected=expected,
                        require_directory=True,
                    )
                    if resolved is not None and not resolved.is_dir():
                        self.errors.append(f"{prefix}.source.path does not exist: {source_path}")
            if name == "charter-kit" and source_path != "./plugins/charter-kit":
                self.errors.append(f"{prefix}.source.path must be ./plugins/charter-kit")

            policy = entry.get("policy")
            if not isinstance(policy, dict):
                self.errors.append(f"{prefix}.policy must be an object")
                self.errors.append(f"{prefix}.policy.installation is required")
                self.errors.append(f"{prefix}.policy.authentication is required")
            else:
                installation = policy.get("installation")
                if installation not in MARKETPLACE_INSTALLATION_POLICIES:
                    self.errors.append(
                        f"{prefix}.policy.installation must be one of {', '.join(MARKETPLACE_INSTALLATION_POLICIES)}"
                    )
                authentication = policy.get("authentication")
                if authentication not in MARKETPLACE_AUTHENTICATION_POLICIES:
                    self.errors.append(
                        f"{prefix}.policy.authentication must be one of {', '.join(MARKETPLACE_AUTHENTICATION_POLICIES)}"
                    )
                products = policy.get("products")
                if products is not None and (
                    not isinstance(products, list)
                    or not all(isinstance(value, str) and value.strip() for value in products)
                ):
                    self.errors.append(f"{prefix}.policy.products must be an array of non-empty strings")

            category = entry.get("category")
            if not isinstance(category, str) or not category.strip():
                self.errors.append(f"{prefix}.category must be a non-empty string")
            elif name == "charter-kit" and category != "Developer Tools":
                self.errors.append(f"{prefix}.category must be Developer Tools")

        if charter_entries == 0:
            self.errors.append(f"{relative}: missing marketplace plugin entry charter-kit")
        elif charter_entries > 1:
            # The duplicate-name diagnostic above is useful for callers, while
            # this explicit cardinality message explains the package contract.
            self.errors.append(f"{relative}: marketplace must contain exactly one charter-kit entry")

    def _compare_file_bytes(self, left: str, right: str, *, label: str) -> None:
        left_path = self._path(left)
        right_path = self._path(right)
        left_bytes = self.read_bytes(left)
        right_bytes = self.read_bytes(right)
        if left_bytes is not None and right_bytes is not None and left_bytes != right_bytes:
            self.errors.append(f"{right}: differs from {left} ({label}; byte mismatch)")

    def _compare_distribution_root_item(self, relative: str) -> None:
        source = self._path(relative)
        destination = self._path(f"{DISTRIBUTION_ROOT_RELATIVE}/{relative}")
        if source.is_dir():
            self._compare_trees(relative, f"{DISTRIBUTION_ROOT_RELATIVE}/{relative}", label="distribution mirror")
        elif source.is_file():
            if not destination.is_file():
                self._missing_file(f"{DISTRIBUTION_ROOT_RELATIVE}/{relative}")
            else:
                self._compare_file_bytes(relative, f"{DISTRIBUTION_ROOT_RELATIVE}/{relative}", label="distribution mirror")

    def _check_target_readme(self) -> None:
        relative = TARGET_README_RELATIVE
        text = self.read(relative)
        if not text:
            return
        # Target-specific prose is allowed, but the adapter must continue to
        # state the shared packaging/security boundary in at least one language.
        for alternatives, message in (
            (("portable/",), "must identify the portable core"),
            (("plugins/charter-kit",), "must identify the generated distribution"),
            (("external harness", "外部 harness"), "must say that it does not install an external harness"),
            (("not the installable", "不是可安装"), "must distinguish the target source from the installable package"),
            (("do not", "不要"), "must include target safety restrictions"),
        ):
            if not any(phrase.lower() in text.lower() for phrase in alternatives):
                self.errors.append(f"{relative}: {message}")

    def check_target_and_distribution(self) -> None:
        """Check target source, self-contained distribution, and migration mirrors."""

        target_root = self._check_tree_safety(TARGET_ROOT_RELATIVE)
        distribution_root = self._check_tree_safety(DISTRIBUTION_ROOT_RELATIVE)
        self._check_target_readme()

        target_manifest = self._check_secondary_plugin_manifest(
            TARGET_MANIFEST_RELATIVE,
            TARGET_ROOT_RELATIVE,
            "Codex target",
        )
        distribution_manifest = self._check_secondary_plugin_manifest(
            DISTRIBUTION_MANIFEST_RELATIVE,
            DISTRIBUTION_ROOT_RELATIVE,
            "generated distribution",
        )

        # A target adapter and its generated package must carry exactly the
        # same manifest bytes; this catches formatting and newline drift too.
        self._compare_file_bytes(
            TARGET_MANIFEST_RELATIVE,
            DISTRIBUTION_MANIFEST_RELATIVE,
            label="target/distribution manifest",
        )
        if target_manifest is not None and distribution_manifest is not None:
            for key in ("name", "version", "license"):
                if target_manifest.get(key) != distribution_manifest.get(key):
                    self.errors.append(
                        f"{DISTRIBUTION_MANIFEST_RELATIVE}: {key} differs from {TARGET_MANIFEST_RELATIVE}"
                    )

        # The target Skill is a controlled mirror of the canonical Skill, and
        # the generated package is a byte-identical copy of that target tree.
        self._compare_trees(
            LEGACY_SKILL_RELATIVE,
            TARGET_SKILL_RELATIVE,
            label="target/core mirror",
        )
        self._compare_trees(
            TARGET_SKILL_RELATIVE,
            DISTRIBUTION_SKILL_RELATIVE,
            label="generated distribution mirror",
        )

        # Root-level core files copied by the packager are also checked.  This
        # prevents a stale package from silently carrying an older protocol.
        if distribution_root is not None:
            for item in DISTRIBUTION_ROOT_ITEMS:
                self._compare_distribution_root_item(item)

            expected_top_level = {
                Path(item).parts[0] for item in DISTRIBUTION_ROOT_ITEMS
            } | {".codex-plugin", "skills"}
            for child in distribution_root.iterdir():
                if child.name not in expected_top_level:
                    self.errors.append(
                        f"{DISTRIBUTION_ROOT_RELATIVE}: unexpected top-level entry {child.name!r}"
                    )

            # A generated package must not recursively contain another target
            # or distribution root (a common mistake when output is nested).
            for child in distribution_root.rglob("*"):
                if not child.exists():
                    continue
                relative_parts = child.relative_to(distribution_root).parts
                if relative_parts and relative_parts[0] in {"plugins", "targets"}:
                    self.errors.append(
                        f"{DISTRIBUTION_ROOT_RELATIVE}: nested {relative_parts[0]}/ tree is not allowed"
                    )

        # During migration the old root snapshot remains valid only as a
        # generated copy.  If either side exists, compare the available pair.
        if self._path(LEGACY_MANIFEST_RELATIVE).is_file():
            self._compare_file_bytes(
                LEGACY_MANIFEST_RELATIVE,
                DISTRIBUTION_MANIFEST_RELATIVE,
                label="legacy manifest mirror",
            )
        if self._path(LEGACY_SKILL_RELATIVE).is_dir():
            self._compare_trees(
                LEGACY_SKILL_RELATIVE,
                DISTRIBUTION_SKILL_RELATIVE,
                label="legacy distribution mirror",
            )

    def check_dsh_target_and_distribution(self) -> None:
        """Check the DSH adapter source and its generated plugin distribution."""

        self._check_tree_safety(DSH_TARGET_ROOT_RELATIVE, required=True)
        distribution_root = self._check_tree_safety(DSH_DISTRIBUTION_ROOT_RELATIVE, required=True)

        target_pkg = self._load_json_object(
            DSH_TARGET_PACKAGE_JSON_RELATIVE,
            "DSH target package",
        )
        dist_pkg = self._load_json_object(
            DSH_DISTRIBUTION_PACKAGE_JSON_RELATIVE,
            "DSH distribution package",
        )
        for relative, data in (
            (DSH_TARGET_PACKAGE_JSON_RELATIVE, target_pkg),
            (DSH_DISTRIBUTION_PACKAGE_JSON_RELATIVE, dist_pkg),
        ):
            if data is None:
                continue
            if data.get("name") != "@dsh-external/dsh-charter-kit":
                self.errors.append(f"{relative}: DSH package name must be @dsh-external/dsh-charter-kit")
            version = data.get("version")
            if not isinstance(version, str) or SEMVER_RE.fullmatch(version) is None:
                self.errors.append(f"{relative}: version must be strict semver")
            if data.get("license") != "MIT":
                self.errors.append(f"{relative}: license must be MIT")
            if data.get("main") != "./lib/index.js":
                self.errors.append(f"{relative}: main must be ./lib/index.js")
            if data.get("type") != "module":
                self.errors.append(f"{relative}: type must be module")

        self._compare_file_bytes(
            DSH_TARGET_PACKAGE_JSON_RELATIVE,
            DSH_DISTRIBUTION_PACKAGE_JSON_RELATIVE,
            label="DSH target/distribution package.json",
        )
        self._compare_file_bytes(
            DSH_TARGET_SRC_RELATIVE,
            DSH_DISTRIBUTION_SRC_RELATIVE,
            label="DSH target/distribution src",
        )
        self._compare_file_bytes(
            DSH_TARGET_BUILD_SCRIPT_RELATIVE,
            DSH_DISTRIBUTION_BUILD_SCRIPT_RELATIVE,
            label="DSH target/distribution build.sh",
        )
        if distribution_root is not None:
            lib_text = self.read(DSH_DISTRIBUTION_LIB_RELATIVE)
            if "export const name = 'dsh-charter-kit'" not in lib_text:
                self.errors.append(f"{DSH_DISTRIBUTION_LIB_RELATIVE}: missing plugin name marker")

            expected_top_level = {
                Path(item).parts[0] for item in DISTRIBUTION_ROOT_ITEMS
            } | {"package.json", "lib", "src", "scripts", "skills"}
            for child in distribution_root.iterdir():
                if child.name not in expected_top_level:
                    self.errors.append(
                        f"{DSH_DISTRIBUTION_ROOT_RELATIVE}: unexpected top-level entry {child.name!r}"
                    )

            for child in distribution_root.rglob("*"):
                if not child.exists():
                    continue
                relative_parts = child.relative_to(distribution_root).parts
                if relative_parts and relative_parts[0] in {"plugins", "targets"}:
                    self.errors.append(
                        f"{DSH_DISTRIBUTION_ROOT_RELATIVE}: nested {relative_parts[0]}/ tree is not allowed"
                    )

    def check_zcode_target_and_distribution(self) -> None:
        """Check the ZCode adapter target and its generated plugin distribution."""

        self._check_tree_safety(ZCODE_TARGET_ROOT_RELATIVE, required=True)
        distribution_root = self._check_tree_safety(ZCODE_DISTRIBUTION_ROOT_RELATIVE, required=True)
        if distribution_root is None:
            return

        target_manifest = self._load_json_object(
            ZCODE_TARGET_MANIFEST_RELATIVE,
            "ZCode target manifest",
        )
        dist_manifest = self._load_json_object(
            ZCODE_DISTRIBUTION_MANIFEST_RELATIVE,
            "ZCode distribution manifest",
        )
        for relative, data in (
            (ZCODE_TARGET_MANIFEST_RELATIVE, target_manifest),
            (ZCODE_DISTRIBUTION_MANIFEST_RELATIVE, dist_manifest),
        ):
            if data is None:
                continue
            if data.get("name") != "charter-kit":
                self.errors.append(f"{relative}: ZCode manifest name must be charter-kit")
            version = data.get("version")
            if not isinstance(version, str) or SEMVER_RE.fullmatch(version) is None:
                self.errors.append(f"{relative}: version must be strict semver")
            if data.get("license") != "MIT":
                self.errors.append(f"{relative}: license must be MIT")
            if data.get("skills") != "skills" or data.get("commands") != "commands":
                self.errors.append(f"{relative}: manifest must declare component directories skills and commands")

        self._compare_file_bytes(
            ZCODE_TARGET_MANIFEST_RELATIVE,
            ZCODE_DISTRIBUTION_MANIFEST_RELATIVE,
            label="ZCode target/distribution manifest",
        )
        self._compare_file_bytes(
            ZCODE_TARGET_COMMAND_RELATIVE,
            ZCODE_DISTRIBUTION_COMMAND_RELATIVE,
            label="ZCode target/distribution command",
        )

        dist_command = self.read(ZCODE_DISTRIBUTION_COMMAND_RELATIVE)
        if dist_command and "skills: charter-workflow" not in dist_command:
            self.errors.append(
                f"{ZCODE_DISTRIBUTION_COMMAND_RELATIVE}: command must mount the charter-workflow skill"
            )
        self._check_zcode_command_derivation()

        dist_skill_skill = f"{ZCODE_DISTRIBUTION_SKILL_RELATIVE}/SKILL.md"
        self._compare_file_bytes(
            "skills/charter-workflow/SKILL.md",
            dist_skill_skill,
            label="ZCode distribution skill mirror",
        )
        root_charter = "DEVELOPMENT_CHARTER.md"
        dist_charter = f"{ZCODE_DISTRIBUTION_SKILL_RELATIVE}/references/DEVELOPMENT_CHARTER.md"
        self._compare_file_bytes(root_charter, dist_charter, label="ZCode distribution charter mirror")

        if distribution_root.is_dir():
            expected_top_level = {
                Path(item).parts[0] for item in DISTRIBUTION_ROOT_ITEMS
            } | {".zcode-plugin", "commands", "skills"}
            for child in distribution_root.iterdir():
                if child.name not in expected_top_level:
                    self.errors.append(
                        f"{ZCODE_DISTRIBUTION_ROOT_RELATIVE}: unexpected top-level entry {child.name!r}"
                    )
            for child in distribution_root.rglob("*"):
                if not child.exists():
                    continue
                relative_parts = child.relative_to(distribution_root).parts
                if relative_parts and relative_parts[0] in {"plugins", "targets"}:
                    self.errors.append(
                        f"{ZCODE_DISTRIBUTION_ROOT_RELATIVE}: nested {relative_parts[0]}/ tree is not allowed"
                    )

    def _check_zcode_command_derivation(self) -> None:
        """Require the ZCode command to be the portable command plus its mount line.

        The adapter command is hand-maintained and shipped, but nothing else
        compares it to its source, so it can fall silently behind the portable
        command while every other gate still passes — which is exactly what
        happened: it lost the provider-protocol and session-ledger rules while
        remaining byte-identical to its own generated copy. The only sanctioned
        difference is the ZCode frontmatter line that mounts the Skill.
        """

        portable = self.read("portable/commands/charter-workflow.md")
        adapter = self.read(ZCODE_TARGET_COMMAND_RELATIVE)
        if not portable or not adapter:
            return
        mount_line = "skills: charter-workflow"
        kept = [line for line in adapter.split("\n") if line.strip() != mount_line]
        if "\n".join(kept) != portable:
            self.errors.append(
                f"{ZCODE_TARGET_COMMAND_RELATIVE}: must equal "
                "portable/commands/charter-workflow.md apart from the "
                f"{mount_line!r} frontmatter line; regenerate it from the portable command"
            )

    def check_license(self) -> None:
        text = self.read("LICENSE")
        if text and (
            "MIT License" not in text
            or "Permission is hereby granted" not in text
            or "THE SOFTWARE IS PROVIDED" not in text
        ):
            self.errors.append("LICENSE: expected the declared MIT license text")

    # ------------------------------------------------------------------
    # Canonical charter and templates
    # ------------------------------------------------------------------
    def check_charter(self) -> None:
        relative = "DEVELOPMENT_CHARTER.md"
        text = self.read(relative)
        if not text:
            return
        self.require(text, "# AI 项目开发章程", relative)
        for number in range(13):
            self.require_regex(
                text,
                rf"^##\s+{number}\.\s+",
                relative,
                f"missing section heading {number}",
            )
        for phrase in (
            "循环 A：章程工程",
            "循环 B：章程驱动开发",
            "需求考古",
            "目标纠偏",
            "资产审计",
            "Goal",
            "Non-goals",
            "Invariants",
            "WIP = 1",
            "NEXT_CANDIDATE",
            "AUTO_DEV",
            "DRAFT",
            "APPROVED",
            "READY",
            "PASS_CLOSED",
            "BLOCKED_TOOLING",
            "CHARTER_INDEPENDENT",
            "Review A",
            "Review B",
            "P0",
            "P1",
            "P2",
            "P3",
            "A/B/C",
            "grill-me",
            "design-interview",
            "Superpowers",
            "J-space",
            "AVAILABLE",
            "MISSING",
            "UNVERIFIED",
            "FALLBACK",
            "dependency-check.log",
            ".charter/reuse-discovery.md",
            "immutable commit/tag/package version",
        ):
            self.require(text, phrase, relative)
        self.require_regex(
            text,
            r"(?i)independent\s+(?:axes|review)|独立轴|两轴不自动映射",
            relative,
            "independent review/severity axes rule is missing",
        )
        self.require_regex(
            text,
            r"(?i)(?:does not|never)\s+approve.*first leaf|项目批准.*不批准",
            relative,
            "project approval must not implicitly approve the first leaf",
        )
        self.require_regex(
            text,
            r"(?i)never\s+install|不会自动安装",
            relative,
            "automatic dependency installation must be prohibited",
        )
        for marker in FORBIDDEN_MARKERS:
            if marker in text:
                self.errors.append(f"{relative}: unfinished marker {marker}")

    def check_templates(self) -> None:
        for relative, headings in PORTABLE_TEMPLATES.items():
            text = self.read(relative)
            for heading in headings:
                self.require(text, heading, relative)
            for marker in FORBIDDEN_MARKERS:
                if marker in text:
                    self.errors.append(f"{relative}: unfinished marker {marker}")

        project = self.read("portable/templates/project-charter.md")
        self.require(
            project,
            "Current status: `DRAFT | APPROVED | BLOCKED | BLOCKED_TOOLING | NEEDS_DECISION | PARTIAL | PAUSED | SUPERSEDED | CLOSED`",
            "project-charter.md",
        )
        for phrase in (
            "Current status:",
            "Define project-specific success levels",
            "### Goal",
            "### Non-goals",
            "### Invariants",
            "## 3. Product loop",
            "### Allowed effects",
            "### Forbidden effects",
            "Current-state and asset audit",
            "## 7. Capability map",
            "## 8. Task tree and route",
            "Charter self-review evidence",
            "Independent charter review evidence",
            "waiver",
            "does not approve the first leaf",
            "Reuse discovery record: `.charter/reuse-discovery.md`",
            "Intent interview evidence:",
            "Intent interview mode:",
            "BLOCKED_TOOLING",
        ):
            self.require(project, phrase, "project-charter.md")
        self.require_regex(
            project,
            r"(?i)before\s+approv(?:ing|ed).*first leaf|before approving or implementing the\s+first leaf",
            "project-charter.md",
            "reuse discovery must precede first-leaf approval",
        )

        leaf = self.read("portable/templates/leaf-task.md")
        self.require(leaf, "Status: `DRAFT`", "leaf-task.md")
        self.require(leaf, "- `BLOCKED_TOOLING` —", "leaf-task.md")
        self.require(
            leaf,
            "Reuse assessment: `YES | NO_MATERIAL_TARGET`",
            "leaf-task.md",
        )
        if "Reuse assessment: `MATERIAL_TARGET | NO_MATERIAL_TARGET`" in leaf:
            self.errors.append(
                "leaf-task.md: material-target values must be YES | NO_MATERIAL_TARGET"
            )
        for phrase in (
            "Reuse discovery record: `.charter/reuse-discovery.md`",
            "Reuse final route / candidate IDs:",
            "Long-task ledger:",
            "Ledger reconciliation:",
            "## 10. Design tree",
            "Recommended:",
            "### Positive behavior",
            "### Negative behavior / boundaries",
            "### Evidence to attach",
            "repair budget",
            "Review A",
            "Review B",
            "PASS_CLOSED",
            # Delta-writing keeps the per-leaf contract from restating the
            # charter, but only while its limit travels with it: a reference may
            # stand in for a baseline already in the read set, never for a
            # leaf-specific field or a deviation from that baseline.
            "**Write the delta, not the project.**",
        ):
            self.require(leaf, phrase, "leaf-task.md")
        for phrase in (
            "Anything that narrows, widens, or contradicts that baseline is written out here in full.",
            "Never replace a leaf-specific field with a reference",
        ):
            self.require(leaf, phrase, "leaf-task.md")

        handoff = self.read("portable/templates/handoff.md")
        for phrase in (
            "## Session ledger",
            "Ledger mode (this session):",
            "NOT_ENABLED waiver:",
            "Five-line snapshot",
            # The packet is re-read on every resume, so its size bound and the
            # archive that absorbs superseded blocks are part of the contract:
            # without them the required read set grows for the life of the
            # project and every future actor pays for closed leaves.
            "**Bounded size.**",
            ".charter/handoff-archive.md",
            "Governance tracked / ledger ignored:",
            ".gitignore",
        ):
            self.require(handoff, phrase, "portable/templates/handoff.md")

        roadmap = self.read("portable/templates/roadmap.md")
        first_leaf_rows = [
            line
            for line in roadmap.splitlines()
            if re.search(r"`LEAF`|\bLEAF\b", line)
            and ".charter/current-task.md" in line
        ]
        if not first_leaf_rows or any(
            re.search(r"`?DRAFT`?", line) is None for line in first_leaf_rows
        ):
            # Stable phrase used by the behavior tests and by downstream CI.
            self.errors.append("portable/templates/roadmap.md: first leaf must start DRAFT")
        for phrase in (
            "Active leaf",
            ".charter/reuse-discovery.md",
            "Reuse discovery gate:",
            "COMPLETE",
            "limitation or waiver",
            "BLOCKED_TOOLING",
            "Dependency check evidence:",
            "PASS_CLOSED",
            "Mirror the full normal sequence",
            "recheck trigger/date",
            "readiness",
        ):
            self.require(roadmap, phrase, "portable/templates/roadmap.md")
        if (
            "When moving a leaf from `DRAFT` to `APPROVED`, update the task file and roadmap row together; then move both to `READY` together after readiness."
            not in roadmap
        ):
            # Preserve the concise diagnostic consumed by existing behavior
            # tests and downstream checks.
            self.errors.append("roadmap.md: APPROVED state must be mirrored")

        reuse = self.read("portable/templates/reuse-discovery.md")
        for phrase in (
            "Gate status: `PENDING | COMPLETE | BLOCKED`",
            "NO_MATCH",
            "ADOPT / ADAPT / REFERENCE_ONLY / REJECT / DEFER",
            "do not clone, build, run, import, copy, install",
            "Fixed revision/version",
            "Decision / waiver reference",
            "`BUILD_NEW` is a capability-level route",
            "UNKNOWN` means the available evidence is insufficient",
            "Gate freshness for this leaf",
            "LOCAL_ONLY = workspace/history",
            "LOCAL_ECOSYSTEM = workspace/history + installed/cache + approved internal",
            "FULL_EXTERNAL = LOCAL_ECOSYSTEM + official/upstream/registries + authorized public web",
            "Coverage: `SEARCHED | NOT_SEARCHED | NOT_AUTHORIZED | BLOCKED_TOOLING`",
            "Result: `MATCH | NO_MATCH | UNKNOWN`",
            "`NO_MATCH` requires an evidence reference",
            "no unresolved high-value `UNKNOWN` or `DEFER`",
            "immutable Git commit/tag or package version",
        ):
            self.require(reuse, phrase, "portable/templates/reuse-discovery.md")
        self._check_reuse_record_contract(
            "portable/templates/reuse-discovery.md",
            reuse,
        )

        review = self.read("portable/templates/review.md")
        for phrase in (
            "CHARTER_INDEPENDENT",
            "P0 / P1 / P2 / P3",
            "Remediation change class",
            "independent axes",
            "fresh context",
        ):
            self.require(review, phrase, "review.md")

        evidence = self.read("portable/templates/evidence-receipt.md")
        for phrase in (
            "Discovery coverage (when `DISCOVERY`): `SEARCHED | NOT_SEARCHED | NOT_AUTHORIZED | BLOCKED_TOOLING`",
            "Discovery result (when `DISCOVERY`): `MATCH | NO_MATCH | UNKNOWN`",
            "immutable Git commit/tag or package version",
            "NO_MATCH` is valid only",
        ):
            self.require(evidence, phrase, "evidence-receipt.md")

        handoff = self.read("portable/templates/handoff.md")
        for phrase in ("Goal reference", "Evidence", "Exact next action", "Do not do", "Capability notes"):
            self.require(handoff, phrase, "handoff.md")
        decision = self.read("portable/templates/decision.md")
        for phrase in ("Question that cannot be solved inside the current contract", "Recommendation", "Approval"):
            self.require(decision, phrase, "decision.md")

    # ------------------------------------------------------------------
    # Entry points and bootstrap semantics
    # ------------------------------------------------------------------
    def _has_missing_working_set_rule(self, text: str) -> bool:
        low = text.lower()
        # Require a deliberate stop/blocked statement tied to the missing
        # working set. A later resume note saying only "add the template" is
        # not enough; otherwise removing the bootstrap gate would go unseen.
        if "required working-set" in low and "remain `blocked`" in low:
            return True
        if "required working-set" in low and "repair or restore" in low:
            return True
        if (
            "required file" in low
            and "missing" in low
            and re.search(r"missing[^\n]{0,500}(?:do not plan|do not implement)[^\n]{0,500}stop until", low)
        ):
            return True
        return bool(
            "required file" in low
            and "missing" in low
            and re.search(r"missing[^\n]{0,180}(?:stop until|do not plan|do not implement)", low)
        )

    def _has_separate_leaf_approval_rule(self, text: str) -> bool:
        low = text.lower()
        project_boundary = (
            "project approval" in low
            and ("does not approve" in low or "never approves" in low or "never approve" in low)
        )
        separate = "separate leaf approval" in low or (
            "separate" in low and "leaf" in low and "approval" in low
        )
        return project_boundary and separate

    def _has_unresolved_finding_rule(self, text: str) -> bool:
        """Return whether unresolved charter findings explicitly block approval.

        Do not merely look for the three words anywhere in a document.  That
        allows an unrelated ``unresolved`` reuse item, a resume field named
        ``open finding``, and a separate ``BLOCKED`` state to accidentally
        satisfy the gate.  Keep the evidence local to one sentence/line and
        require a blocking verb so removing the actual rule is detectable.
        """

        low = text.lower()
        # Markdown prose is normally one rule per line; splitting on sentence
        # terminators also handles wrapped paragraphs without allowing distant
        # sections to be combined.
        segments = re.split(r"[\r\n.!?。！？]+", low)
        for segment in segments:
            if not ("unresolved" in segment and "finding" in segment):
                continue
            if re.search(r"\b(?:block\w*|keep\w*|remain\w*)\b[^;]{0,100}\bblocked\b", segment):
                return True
            if re.search(r"\bblocked\b[^;]{0,100}\b(?:block\w*|keep\w*|remain\w*)\b", segment):
                return True
        # A compact Chinese host entry may express the same invariant without
        # the English keywords used by the canonical prompts.
        return bool(
            re.search(
                r"未解决[^\n。！？]{0,80}(?:发现|问题)[^\n。！？]{0,80}"
                r"(?:阻塞|保持|不得|不能)[^\n。！？]{0,40}(?:审批|批准|就绪|READY)",
                text,
            )
        )

    def _has_reuse_gate_rule(self, text: str) -> bool:
        low = text.lower()
        return (
            ".charter/reuse-discovery.md" in low
            and "reuse" in low
            and ("after project approval" in low or "after approval" in low)
            and ("before" in low and ("leaf" in low or "approv" in low))
        )

    def _check_reuse_entry_contract(self, relative: str, text: str) -> None:
        """Validate the small Reuse Gate contract in an entry point.

        Entry points repeat the safety boundary because a host may load one
        prompt or command without loading the full Skill.  Keep this check
        semantic rather than requiring a particular paragraph layout: the
        canonical wording may be translated or wrapped, while the gate must
        still expose the same three states and stop conditions.
        """

        for state in REUSE_GATE_STATES:
            self.require(text, state, relative)
        for obsolete in LEGACY_REUSE_GATE_CONTRACTS:
            if obsolete in text:
                self.errors.append(
                    f"{relative}: obsolete aggregate Reuse Gate state list {obsolete!r}"
                )

        if HIGH_VALUE_UNKNOWN_RULE.search(text) is None:
            self.errors.append(
                f"{relative}: high-value UNKNOWN remains unresolved rule is missing"
            )
        if REUSE_READY_WAIVER_RULE.search(text) is None:
            self.errors.append(
                f"{relative}: READY must require COMPLETE or a leaf-specific bounded waiver"
            )

        # Coverage is metadata about what was searched, not a fourth gate
        # state.  Requiring the distinction here prevents a host entry from
        # silently turning an unavailable tier into NO_MATCH.
        coverage_pattern = re.compile(
            r"(?i)(?:NOT_SEARCHED|NOT_AUTHORIZED|BLOCKED_TOOLING)"
            r"[^\n]{0,320}(?:(?:not|never)\s+(?:a\s+)?|"
            r"(?:visibly\s+)?(?:distinct|separate|different)\s+from\s+)"
            r"(?:gate\s+state(?:s)?|gate|`?NO_MATCH`?)"
        )
        if coverage_pattern.search(text) is None:
            self.errors.append(
                f"{relative}: coverage values must remain distinct from gate state/result"
            )

        # A tooling block is a hard stop unless an explicit, bounded decision
        # is recorded.  This is intentionally checked separately from the
        # generic BLOCKED state so a stale prompt cannot pass by mentioning
        # BLOCKED_TOOLING in an inventory only.
        blocked_pattern = re.compile(
            r"(?i)BLOCKED_TOOLING[^\n]{0,260}"
            r"(?:(?:cannot|must\s+not|do\s+not)[^\n]{0,120}"
            r"(?:READY|readiness)|blocks?\s+(?:leaf\s+)?readiness)"
        )
        if blocked_pattern.search(text) is None:
            self.errors.append(
                f"{relative}: BLOCKED_TOOLING cannot approve or move a leaf to READY"
            )

    def _check_reuse_record_contract(self, relative: str, text: str) -> None:
        """Validate the canonical discovery-record field separation.

        The record is the authoritative Reuse Check template.  It therefore
        gets a slightly stricter check than host prose: gate state, tier
        coverage, search result, candidate disposition, and capability-level
        route must each remain separate fields.
        """

        self.require(
            text,
            "Gate status: `PENDING | COMPLETE | BLOCKED`",
            relative,
        )
        for obsolete in LEGACY_REUSE_GATE_CONTRACTS:
            if obsolete in text:
                self.errors.append(
                    f"{relative}: obsolete aggregate Reuse Gate state list {obsolete!r}"
                )
        for label, values in (
            ("Coverage", " | ".join(REUSE_COVERAGE_VALUES)),
            ("Result", " | ".join(REUSE_RESULT_VALUES)),
        ):
            self.require(text, f"{label}: `{values}`", relative)
        self.require(text, "Final route:", relative)
        for route in REUSE_FINAL_ROUTES:
            self.require(text, route, relative)

        # ``NO_MATCH`` is evidence-backed only; unavailable or out-of-scope
        # tiers must not be collapsed into it.
        self.require_regex(
            text,
            r"(?i)`?NO_MATCH`?[^\n]{0,180}(?:requires|only after)[^\n]{0,120}"
            r"(?:evidence|query|ran)",
            relative,
            "NO_MATCH must follow an executed query and evidence",
        )
        self.require_regex(
            text,
            r"(?i)(?:NOT_SEARCHED|NOT_AUTHORIZED|BLOCKED_TOOLING)[^\n]{0,320}"
            r"(?:(?:not|never)\s+(?:a\s+)?|(?:visibly\s+)?"
            r"(?:distinct|separate|different)\s+from\s+)"
            r"(?:gate\s+state(?:s)?|gate|`?NO_MATCH`?)",
            relative,
            "coverage values must stay distinct from NO_MATCH and gate state",
        )
        self.require_regex(
            text,
            r"(?i)(?:high-value\s+`?UNKNOWN`?[^\n]{0,180}(?:unresolved|remains)|"
            r"(?:unresolved|remains)[^\n]{0,80}high-value\s+`?UNKNOWN`?)",
            relative,
            "high-value UNKNOWN/DEFER must be resolved before completion",
        )
        self.require_regex(
            text,
            r"(?i)UNKNOWN[^\n]{0,180}(?:not|never)\s+(?:permission|authorization|permission to build)",
            relative,
            "UNKNOWN must not authorize BUILD_NEW",
        )
        if REUSE_READY_WAIVER_RULE.search(text) is None:
            self.errors.append(
                f"{relative}: READY must require COMPLETE or a leaf-specific bounded waiver"
            )

    def _ordered_bootstrap_section(self, text: str) -> str:
        """Return the actionable zero-start section, excluding inventories.

        A Skill often names its bundled fallback in the introductory
        self-contained description before it reaches the ordered first-start
        steps.  Ordering provider names in that inventory is not the workflow
        order, so compare them only inside the bootstrap section.
        """
        match = re.search(
            r"(?im)^##\s+(?:bootstrap mode|first-start mode|first start mode)\b",
            text,
        )
        if match is None:
            return text
        body = text[match.end() :]
        next_heading = re.search(r"(?im)^##\s+", body)
        return body[: next_heading.start()] if next_heading else body

    def _check_bootstrap_semantics(self, relative: str, text: str) -> None:
        low = text.lower()
        for requirement in PROMPT_REQUIREMENTS:
            self.require(text, requirement, relative)
        self.require(text, ".charter/handoff.md", relative)
        if not any(marker in low for marker in ("if present", "optional", "如存在", "可选")):
            self.errors.append(f"{relative}: handoff reference must be explicitly optional")

        # The no-project branch must be discoverable and precede the normal
        # resume/read sequence. This is what makes the kit usable from zero.
        self.require_regex(
            text,
            r"no\s+[`']?\.charter/project\.md|没有.*\.charter/project\.md",
            relative,
            "zero-start branch (no `.charter/project.md`) is missing",
        )
        for status in (*DEPENDENCY_STATUSES, "BLOCKED_TOOLING"):
            self.require(text, status, relative)
        self.require(text, ".charter/evidence/dependency-check.log", relative)
        for field in ("capability", "reason", "impact", "fallback", "action"):
            self.require(text, field, relative)
        # Provider protocol: j-space operational guidance and the one-retry,
        # user-visible fallback rule must survive in every shared entry file.
        for phrase in (
            "jspace.py seam",
            "jspace.py resume",
            "allows one retry",
            "silent downgrades are violations",
            "reduce-reinvention",
            "repo-to-skill",
            "Session ledger",
            "NOT_ENABLED",
            "must not close as `PASS_CLOSED`",
            # Two rules that only hold if every entry document carries them: the
            # governance record must be committed to be citable as history, and
            # the mandatory read set must stay bounded or every later resume pays
            # for work that is already closed.
            "Version control and read-set size",
            "cannot be cited as authoritative",
            "`.gitignore` entry",
            ".charter/handoff-archive.md",
        ):
            self.require(text, phrase, relative)
        self.require(text, "grill-me", relative)
        self.require(text, "design-interview", relative)
        # A provider may be named in an introductory inventory before the
        # actual ordered instruction. Compare names within that section.
        ordered = self._ordered_bootstrap_section(text)
        ordered_low = ordered.lower()
        grill_position = ordered_low.find("grill-me")
        fallback_position = ordered_low.find("design-interview")
        if (
            grill_position < 0
            or fallback_position < 0
            or grill_position >= fallback_position
            or not re.search(r"\bfirst\b|\bpriorit|\bprefer|优先", ordered, re.IGNORECASE)
        ):
            self.errors.append(f"{relative}: grill-me must be preferred before design-interview fallback")
        if "fallback" not in low:
            self.errors.append(f"{relative}: design-interview fallback is missing")
        # The ledger declaration is an ordering rule, so check position and
        # uniqueness, not presence: two declarations in one first-start section
        # mean one of them can still point past the transition it guards.
        declarations = [
            line for line in ordered.splitlines() if LEDGER_DECLARATION_LINE_RE.search(line)
        ]
        if len(declarations) != 1:
            self.errors.append(
                f"{relative}: first-start section must declare the session ledger exactly once "
                f"(found {len(declarations)})"
            )
        elif LEDGER_BEFORE_TRANSITION_RE.search(declarations[0]) is None:
            self.errors.append(
                f"{relative}: session ledger declaration must precede DRAFT to APPROVED in the same step"
            )
        if not self._has_missing_working_set_rule(text):
            self.errors.append(f"{relative}: missing required-file BLOCKED rule")
        # Accept either the compact host wording or the fuller MANUAL/AUTO_DEV
        # wording. The invariant is semantic: project approval must not grant
        # leaf authorization, and a separate leaf approval/preauthorization
        # must be named.
        separate_ok = self._has_separate_leaf_approval_rule(text)
        if not separate_ok:
            self.errors.append(f"{relative}: project and leaf approval must be separate")
        if not self._has_unresolved_finding_rule(text):
            self.errors.append(f"{relative}: unresolved charter findings must block approval")
        if not self._has_reuse_gate_rule(text):
            self.errors.append(f"{relative}: reuse discovery gate must be explicit")
        self._check_reuse_entry_contract(relative, text)
        for phrase in ("workspace/history", ".charter/evidence/", "authoritative"):
            self.require(text, phrase, relative)
        self.require(text, "PASS_CLOSED", relative)
        # Loading an entry may mention an explicit later install action, but
        # it must never make Skill installation a prerequisite for zero-start.
        if NO_SKILL_PREREQUISITE.search(text):
            self.errors.append(f"{relative}: Skill installation must not be a prerequisite")

    def check_prompts(self) -> None:
        for relative in HOST_PROMPTS:
            text = self.read(relative)
            self._check_bootstrap_semantics(relative, text)

    def check_command(self) -> None:
        relative = "portable/commands/charter-workflow.md"
        text = self.read(relative)
        if not text:
            return
        for phrase in (
            "$ARGUMENTS",
            ".charter/project.md",
            ".charter/roadmap.md",
            ".charter/reuse-discovery.md",
            ".charter/current-task.md",
            "grill-me",
            "design-interview",
            "BLOCKED_TOOLING",
            "PASS_CLOSED",
        ):
            self.require(text, phrase, relative)
        lower = text.lower()
        for mode in ("bootstrap mode", "resume mode"):
            if mode not in lower:
                self.errors.append(f"{relative}: missing {mode}")
        if "--add-missing" not in text and "add only missing" not in lower:
            self.errors.append(f"{relative}: command must document --add-missing behavior")
        self._check_bootstrap_semantics(relative, text)
        for phrase in (
            "immutable commit/tag/package version",
            "never clone, build, run, import, copy",
            "private source",
            "high-value",
        ):
            self.require(text, phrase, relative)
        self.require_regex(
            text,
            r"(?i)high-value[^\n]{0,100}(?:UNKNOWN|DEFER)[^\n]{0,100}(?:unresolved|remains)",
            relative,
            "reuse completion must resolve high-value UNKNOWN/DEFER",
        )
        if NO_SKILL_PREREQUISITE.search(text):
            self.errors.append(f"{relative}: Skill installation must not be a prerequisite")

    def check_skill(self) -> None:
        relative = "skills/charter-workflow/SKILL.md"
        text = self.read(relative)
        if not text:
            return
        if not text.startswith("---"):
            self.errors.append(f"{relative}: missing YAML frontmatter")
        else:
            frontmatter = text.split("---", 2)
            if len(frontmatter) < 3:
                self.errors.append(f"{relative}: missing YAML frontmatter")
            else:
                self.require(frontmatter[1], "name: charter-workflow", "skill frontmatter")
                self.require(frontmatter[1], "description:", "skill frontmatter")
        for phrase in (
            "self-contained",
            "no `.charter/project.md`",
            "grill-me",
            "design-interview",
            "fallback",
            "dependency",
            "CHARTER_INDEPENDENT",
            "PASS_CLOSED",
            "BLOCKED_TOOLING",
            "DRAFT",
            "APPROVED",
            "READY",
                "reuse",
            ".charter/reuse-discovery.md",
            "DRAFT` to `APPROVED",
        ):
            self.require(text, phrase, relative)
        self._check_bootstrap_semantics(relative, text)
        if NO_SKILL_PREREQUISITE.search(text):
            self.errors.append(f"{relative}: Skill installation must not be a prerequisite")

    # ------------------------------------------------------------------
    # Dependency declarations and scripts
    # ------------------------------------------------------------------
    def check_dependencies_manifest(self) -> None:
        relative = "dependencies.json"
        text = self.read(relative)
        if not text:
            return
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            self.errors.append(f"{relative}: invalid JSON ({exc})")
            return
        if not isinstance(data, dict):
            self.errors.append(f"{relative}: top-level value must be an object")
            return
        schema = data.get("schema")
        if not isinstance(schema, str) or "charter-kit/dependencies/v1" not in schema:
            self.errors.append(f"{relative}: missing or invalid schema")
        capabilities = data.get("capabilities")
        if not isinstance(capabilities, list) or not capabilities:
            self.errors.append(f"{relative}: capabilities must be a non-empty array")
            return
        seen: set[str] = set()
        for index, item in enumerate(capabilities):
            prefix = f"{relative}: capabilities[{index}]"
            if not isinstance(item, dict):
                self.errors.append(f"{prefix} must be an object")
                continue
            identifier = item.get("id")
            if not isinstance(identifier, str) or not identifier.strip():
                self.errors.append(f"{prefix}.id must be a non-empty string")
            elif identifier in seen:
                self.errors.append(f"{relative}: duplicate capability id {identifier!r}")
            else:
                seen.add(identifier)
            if item.get("kind") not in {"command", "provider", "capability", "path", "directory", "skill"}:
                self.errors.append(f"{prefix}.kind is invalid")
            if not isinstance(item.get("required"), bool):
                self.errors.append(f"{prefix}.required must be boolean")
            for field in ("impact", "fallback"):
                if not isinstance(item.get(field), str) or not item[field].strip():
                    self.errors.append(f"{prefix}.{field} must be a non-empty string")
        expected = {
            "readable-markdown",
            "project-directory-access",
            "python",
            "git",
            "superpowers",
            "j-space",
            "grill-me",
            "design-interview",
            "independent-review",
        }
        missing = sorted(expected - seen)
        if missing:
            self.errors.append(f"{relative}: missing capability declarations: {', '.join(missing)}")
        for required in (
            "readable-markdown",
            "project-directory-access",
            "python",
            "design-interview",
        ):
            entries = [item for item in capabilities if isinstance(item, dict) and item.get("id") == required]
            if entries and entries[0].get("required") is not True:
                self.errors.append(f"{relative}: {required} must be declared required")
        for optional in ("git", "superpowers", "j-space", "grill-me", "independent-review"):
            entries = [item for item in capabilities if isinstance(item, dict) and item.get("id") == optional]
            if entries and entries[0].get("required") is not False:
                self.errors.append(f"{relative}: {optional} must remain optional")
        if re.search(r"(?i)(pip\s+install|npm\s+install|curl\s*\||invoke-webrequest)", text):
            self.errors.append(f"{relative}: dependency declaration contains an installer command")

    def _check_python_source(self, relative: str, text: str) -> None:
        try:
            compile(text, relative, "exec")
        except SyntaxError as exc:
            self.errors.append(f"{relative}: invalid Python ({exc})")
        for forbidden in ("subprocess", "requests", "urllib.request", "pip install", "npm install"):
            if forbidden.lower() in text.lower():
                self.errors.append(f"{relative}: unexpected install/network dependency {forbidden!r}")

    def check_dependency_script(self, relative: str) -> None:
        text = self.read(relative)
        if not text:
            return
        self._check_python_source(relative, text)
        for phrase in (
            "STATUS_AVAILABLE",
            "STATUS_MISSING",
            "STATUS_UNVERIFIED",
            "STATUS_FALLBACK",
            "argparse",
            "--project",
            "--config",
            "--log-file",
            "--require",
            "--optional",
            "--provider-dir",
            "--require-provider",
            "--require-git",
            "--json",
            "impact",
            "fallback",
            "action",
            "MISSING",
            "UNVERIFIED",
            "FALLBACK",
        ):
            self.require(text, phrase, relative)
        self.require_regex(
            text,
            r"(?i)(?:does not|never)\s+(?:install|execute)|never\s+invokes|not\s+executed",
            relative,
            "checker must be metadata-only",
        )
        self.require_regex(text, r"(?i)redact|redaction", relative, "checker must redact log output")

    def check_initializer(self, relative: str) -> None:
        text = self.read(relative)
        if not text:
            return
        self._check_python_source(relative, text)
        for phrase in (
            "FILES =",
            "portable",
            "templates",
            "--force",
            "--add-missing",
            "backup",
            "atomic_copy",
            "symlink",
            "dependency-check.log",
            "run_dependency_check",
            "never installs",
            "evidence",
            # The ledger-ignore rule is the initializer's one write outside
            # `.charter/`. It has to stay append-only and idempotent, so the gate
            # names the helper and the negation branch rather than the effect
            # alone: a rewritten user `.gitignore` would be a worse defect than
            # the discipline it replaces.
            "ensure_ledger_ignored",
            ".gitignore",
            ".jspace",
            "covers_ledger",
        ):
            self.require(text, phrase, relative)
        for template in (
            "project-charter.md",
            "leaf-task.md",
            "reuse-discovery.md",
            "handoff.md",
            "decision.md",
            "review.md",
            "evidence-receipt.md",
            "roadmap.md",
        ):
            self.require(text, template, relative)

    # ------------------------------------------------------------------
    # Supporting docs and declarations
    # ------------------------------------------------------------------
    def check_tool_references(self) -> None:
        portable_interview = self.read("portable/references/design-interview.md")
        for phrase in ("# Design Interview", "Negative paths and boundaries", "Stop line", "Record"):
            self.require(portable_interview, phrase, "portable/references/design-interview.md")
        routing = self.read("skills/charter-workflow/references/tool-routing.md")
        for phrase in (
            "superpowers:",
            "superpowers:requesting-code-review",
            "j-space",
            "Portable fallback",
            "grill-me",
            "design-interview",
            "PENDING",
            "COMPLETE",
            "BLOCKED",
            "Coverage",
            "Result",
            "Final route",
        ):
            self.require(routing, phrase, "tool-routing reference")
        self._check_reuse_entry_contract(
            "skills/charter-workflow/references/tool-routing.md",
            routing,
        )
        interview = self.read("skills/charter-workflow/references/design-interview.md")
        for phrase in ("grilling", "Negative paths and boundaries", "Stop line", "Record"):
            self.require(interview, phrase, "design-interview reference")

        dependencies = self.read("DEPENDENCIES.md")
        for phrase in (
            "## 1. 分级要求",
            "## 2. 机器可读声明",
            "## 3. 运行依赖检查器",
            "## 4. 首次启动时机",
            "## 5. 复用发现工具的边界",
            "## 6. 安装与授权原则",
            "Superpowers",
            "J-space",
            "grill-me",
            "check_dependencies.py",
            "MISSING",
            "UNVERIFIED",
            "FALLBACK",
            "不会自动安装",
            "capability",
            "reason",
            "impact",
            "fallback",
            "action",
            ".charter/evidence/dependency-check.log",
        ):
            self.require(dependencies, phrase, "DEPENDENCIES.md")

    def check_agentpack(self) -> None:
        relative = "agentpack.yaml"
        text = self.read(relative)
        if not text:
            return
        for phrase in (
            "name: charter-kit",
            "version: 0.2.0",
            "protocol: charter/v1",
            "purpose: project-local-development-governance",
            "source_of_truth:",
            "working_set:",
            ".charter/project.md",
            ".charter/roadmap.md",
            ".charter/reuse-discovery.md",
            ".charter/current-task.md",
            "dependencies:",
            "manifest: dependencies.json",
            "checker: scripts/check_dependencies.py",
            "log: .charter/evidence/dependency-check.log",
            "explicit-user-action",
            "optional_providers:",
            "superpowers",
            "j-space",
            "grill-me",
            "host_neutral_entry: portable/prompts/generic-bootstrap.md",
            "reuse_gate:",
            "candidate_decisions:",
            "evidence_required: true",
            "reuse_discovery_policy:",
            "prohibited_actions:",
            "clone",
            "build",
            "import",
            "copy",
            "private_source",
            "blocked_tooling:",
            "instruction_files:",
            "AGENTS.md:",
            "CLAUDE.md:",
            "user_commands:",
            "targets:",
            "distributions:",
            "marketplace:",
            "mirror_policy:",
            "byte_identity: true",
            "newline_sensitive: true",
            "legacy_snapshot: generated",
        ):
            self.require(text, phrase, relative)
        for key, value in {
            "generic": "portable/prompts/generic-bootstrap.md",
            "codex": "portable/prompts/generic-bootstrap.md",
            "claude": "portable/prompts/claude-bootstrap.md",
            "gemini": "portable/prompts/gemini-bootstrap.md",
            "deepseek": "portable/prompts/deepseek-bootstrap.md",
        }.items():
            self.require_regex(
                text,
                rf"^\s+{re.escape(key)}:\s*{re.escape(value)}\s*$",
                relative,
                f"host entry {key} must map to {value}",
            )
        def top_level_block(name: str) -> str:
            lines = text.splitlines()
            start = None
            for index, line in enumerate(lines):
                if line.strip() == f"{name}:" and not line.startswith((" ", "\t")):
                    start = index + 1
                    break
            if start is None:
                return ""
            collected: list[str] = []
            for line in lines[start:]:
                if line and not line.startswith((" ", "\t")) and line.rstrip().endswith(":"):
                    break
                collected.append(line)
            return "\n".join(collected)

        def require_yaml_value(block: str, pattern: str, message: str) -> None:
            if re.search(pattern, block, re.MULTILINE) is None:
                self.errors.append(f"{relative}: {message}")

        targets_block = top_level_block("targets")
        if not targets_block:
            self.errors.append(f"{relative}: targets declaration is missing")
        require_yaml_value(targets_block, r"^\s{2}codex:\s*$", "targets.codex declaration is missing")
        require_yaml_value(
            targets_block,
            r"^\s{4}source:\s*targets/codex\s*$",
            "targets.codex.source must be targets/codex",
        )
        require_yaml_value(
            targets_block,
            r"^\s{4}manifest:\s*targets/codex/\.codex-plugin/plugin\.json\s*$",
            "targets.codex.manifest declaration is missing",
        )
        require_yaml_value(
            targets_block,
            r"^\s{4}skill:\s*targets/codex/skills/charter-workflow\s*$",
            "targets.codex.skill declaration is missing",
        )

        distributions_block = top_level_block("distributions")
        if not distributions_block:
            self.errors.append(f"{relative}: distributions declaration is missing")
        require_yaml_value(
            distributions_block,
            r"^\s{2}codex:\s*$",
            "distributions.codex declaration is missing",
        )
        require_yaml_value(
            distributions_block,
            r"^\s{4}path:\s*plugins/charter-kit\s*$",
            "distributions.codex.path must be plugins/charter-kit",
        )
        require_yaml_value(
            distributions_block,
            r"^\s{4}generated_from:\s*targets/codex\s*$",
            "distributions.codex.generated_from declaration is missing",
        )

        marketplace_block = top_level_block("marketplace")
        if not marketplace_block:
            self.errors.append(f"{relative}: marketplace declaration is missing")
        require_yaml_value(
            marketplace_block,
            r"^\s{2}path:\s*\.agents/plugins/marketplace\.json\s*$",
            "marketplace.path must be .agents/plugins/marketplace.json",
        )
        require_yaml_value(
            marketplace_block,
            r"^\s{2}source_path:\s*\./plugins/charter-kit\s*$",
            "marketplace.source_path must be ./plugins/charter-kit",
        )

        mirror_block = top_level_block("mirror_policy")
        if not mirror_block:
            self.errors.append(f"{relative}: mirror_policy declaration is missing")
        require_yaml_value(
            mirror_block,
            r"^\s{2}canonical_core:\s*portable\s*$",
            "mirror_policy.canonical_core must be portable",
        )
        require_yaml_value(
            mirror_block,
            r"^\s{2}byte_identity:\s*true\s*$",
            "mirror_policy.byte_identity must be true",
        )
        require_yaml_value(
            mirror_block,
            r"^\s{2}newline_sensitive:\s*true\s*$",
            "mirror_policy.newline_sensitive must be true",
        )
        require_yaml_value(
            mirror_block,
            r"^\s{2}legacy_snapshot:\s*generated\s*$",
            "mirror_policy.legacy_snapshot must be generated",
        )
        if "\t" in text:
            self.errors.append(f"{relative}: tabs are not valid indentation in this YAML declaration")
        if re.search(r"(?i)(pip\s+install|npm\s+install|curl\s*\|)", text):
            self.errors.append(f"{relative}: hidden installer command")

    def check_readme(self) -> None:
        relative = "README.md"
        text = self.read(relative)
        if not text:
            return
        for phrase in (
            "host-neutral",
            "empty directory",
            "grill-me",
            "design-interview",
            "dependencies",
            "MISSING",
            "UNVERIFIED",
            "FALLBACK",
            "dependency-check.log",
            "DRAFT",
            "APPROVED",
            "READY",
            "PASS_CLOSED",
            "high-value",
            "immutable commit/tag/package version",
            "never clones, builds, runs, imports, copies, installs",
            "AGENTS.md",
            "CLAUDE.md",
        ):
            self.require(text, phrase, relative)
        self.require_regex(
            text,
            r"(?i)high-value[^\n]{0,100}(?:UNKNOWN|DEFER)[^\n]{0,100}(?:unresolved|remains)",
            relative,
            "reuse completion must resolve high-value UNKNOWN/DEFER",
        )
        if NO_SKILL_PREREQUISITE.search(text):
            self.errors.append(f"{relative}: Skill installation must not be a prerequisite")
        self._check_no_hidden_installers()

    def _check_no_hidden_installers(self) -> None:
        files = (
            "README.md",
            "DEVELOPMENT_CHARTER.md",
            "DEPENDENCIES.md",
            "agentpack.yaml",
            "skills/charter-workflow/SKILL.md",
            "portable/commands/charter-workflow.md",
            *HOST_PROMPTS,
        )
        pattern = re.compile(r"(?i)(?:pip\s+install|npm\s+install|invoke-webrequest|curl\s*\|)")
        for relative in files:
            text = self.read(relative)
            if pattern.search(text):
                self.errors.append(f"{relative}: hidden installer command")

    def check_tests_and_docs(self) -> None:
        pressure = self.read("tests/pressure-scenarios.md")
        for phrase in ("DRAFT", "APPROVED", "READY", "roadmap.md", "P0–P3", "A/B/C", "reuse"):
            self.require(pressure, phrase, "tests/pressure-scenarios.md")
        structure = self.read("tests/structure-checklist.md")
        for phrase in ("LICENSE", "byte identity", "behavior tests"):
            self.require(structure, phrase, "tests/structure-checklist.md")

    # ------------------------------------------------------------------
    # Byte identity and genericity
    # ------------------------------------------------------------------
    def check_mirrors(self) -> None:
        for canonical, bundled in MIRRORS:
            left = self.read_bytes(canonical)
            right = self.read_bytes(bundled)
            if left is not None and right is not None and left != right:
                self.errors.append(f"{bundled}: differs from {canonical}")

    def check_host_prompt_identity(self) -> None:
        generic = self.read_bytes(HOST_PROMPTS[0])
        if generic is None:
            return
        for relative in HOST_PROMPTS[1:]:
            candidate = self.read_bytes(relative)
            if candidate is not None and candidate != generic:
                self.errors.append(
                    f"{relative}: differs from {HOST_PROMPTS[0]} (generic canonical prompt)"
                )

    def check_domain_neutrality(self) -> None:
        # Keep the validator itself out of this scan: its explicit forbidden
        # vocabulary is test data, not content shipped into an agent prompt.
        files: list[str] = [
            "DEVELOPMENT_CHARTER.md",
            "README.md",
            "DEPENDENCIES.md",
            "agentpack.yaml",
            "dependencies.json",
            "portable/commands/charter-workflow.md",
            "portable/references/design-interview.md",
            *PORTABLE_TEMPLATES,
            *HOST_PROMPTS,
            "skills/charter-workflow/SKILL.md",
            "skills/charter-workflow/references/DEVELOPMENT_CHARTER.md",
            "skills/charter-workflow/references/DEPENDENCIES.md",
            "skills/charter-workflow/references/design-interview.md",
            "skills/charter-workflow/references/tool-routing.md",
            *(f"{SKILL_TEMPLATE_ROOT}/{Path(path).name}" for path in PORTABLE_TEMPLATES),
            "scripts/check_dependencies.py",
            "scripts/init_project.py",
        ]
        seen: set[str] = set()
        for relative in files:
            if relative in seen:
                continue
            seen.add(relative)
            text = self.read(relative)
            for label, pattern in FORBIDDEN_CORE_TERMS:
                if pattern.search(text):
                    self.errors.append(
                        f"{relative}: forbidden project-specific term {label!r}"
                    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="package directory")
    args = parser.parse_args(argv)
    return Checker(Path(args.root)).run()


if __name__ == "__main__":
    sys.exit(main())
