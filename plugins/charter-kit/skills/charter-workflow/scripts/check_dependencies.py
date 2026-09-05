#!/usr/bin/env python3
"""Check Charter Kit host capabilities without installing or executing anything.

The checker deliberately performs local, read-only probes only.  It does not install or execute anything; it checks
executable names with :func:`shutil.which` and provider/skill locations with
filesystem metadata.  It never invokes a discovered executable, imports a
provider, contacts the network, or changes a global directory.

Usage examples::

    python scripts/check_dependencies.py
    python scripts/check_dependencies.py path/to/project --log-file .charter/evidence/dependencies.log
    python scripts/check_dependencies.py path/to/project --config .charter/dependencies.json
    python scripts/check_dependencies.py --provider-dir grill-me=~/.agents/skills/grilling

The optional JSON configuration is intentionally small and uses only the
standard library.  ``commands`` and ``providers`` are arrays of objects.  A
command object has ``id``, ``command``, ``required``, ``impact`` and
``fallback`` fields.  A provider object has ``id``, ``paths`` (an array),
``required``, ``impact`` and ``fallback`` fields.  Paths may contain
``{project}``, ``{package}``, ``{home}``, or ``{env:VARIABLE}``.  An unset
environment variable is reported as ``UNVERIFIED`` rather than guessed.

When a requirement is missing or unverifiable and has a fallback, a separate
``FALLBACK`` record is emitted.  Required ``MISSING``/``UNVERIFIED`` checks
produce exit status 1; optional provider gaps remain usable through the
portable workflow and produce exit status 0.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import stat
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


STATUS_AVAILABLE = "AVAILABLE"
STATUS_MISSING = "MISSING"
STATUS_UNVERIFIED = "UNVERIFIED"
STATUS_FALLBACK = "FALLBACK"
STATUSES = frozenset(
    {STATUS_AVAILABLE, STATUS_MISSING, STATUS_UNVERIFIED, STATUS_FALLBACK}
)

# A provider directory must identify itself before the checker calls it
# AVAILABLE.  Merely being a readable directory is not evidence that the
# requested skill/plugin is installed; an empty or unrelated directory would
# otherwise silently satisfy a required capability.  The markers are
# intentionally conservative and host-neutral.  A manifest may replace them
# with its own relative marker list (``markers`` or ``required_files``).
DEFAULT_PROVIDER_MARKERS = (
    "SKILL.md",
    ".codex-plugin/plugin.json",
    "plugin.json",
)

_IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
_ENV_TOKEN_RE = re.compile(r"\{env:([A-Za-z_][A-Za-z0-9_]*)\}")
_SECRET_ASSIGNMENT_RE = re.compile(
    r"(?i)(\b(?:password|passwd|token|secret|api[_-]?key|authorization|bearer)\b\s*[:=]\s*)([^\s,;]+)"
)
_BEARER_RE = re.compile(
    r"(?i)(\b(?:authorization\s*[:=]\s*)?bearer\s+)([^\s,;]+)"
)
_QUERY_SECRET_RE = re.compile(
    r"(?i)([?&](?:password|passwd|token|secret|api[_-]?key|authorization|bearer)=)([^&\s]+)"
)
_URL_USERINFO_RE = re.compile(r"(?i)(\bhttps?://[^/\s:@]+:)([^@\s/]+)(@)")
_CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")


@dataclass(frozen=True)
class Requirement:
    """A local capability declaration."""

    id: str
    kind: str
    required: bool
    impact: str
    fallback: str
    command: str | None = None
    paths: tuple[str, ...] = ()
    markers: tuple[str, ...] = ()
    min_version: str | None = None
    # ``auto`` probes the declared command/path, ``missing`` is used for an
    # explicit CLI request with no discoverable target, and ``unverified`` is
    # used for a capability that needs host or human confirmation.
    probe: str = "auto"
    action: str = ""


@dataclass(frozen=True)
class CheckResult:
    """A single human- and machine-readable diagnostic record."""

    id: str
    status: str
    kind: str
    required: bool
    message: str
    impact: str = ""
    fallback: str = ""
    location: str = ""
    action: str = ""
    # ``reason`` is the stable semantic name used by the dependency-log
    # contract.  Keep ``message`` as a compatibility alias for older hosts.
    reason: str = ""

    def __post_init__(self) -> None:
        if not self.reason:
            object.__setattr__(self, "reason", self.message)
        if not self.message:
            object.__setattr__(self, "message", self.reason)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class ConfigurationError(ValueError):
    """Raised when a supplied JSON dependency declaration is malformed."""


def redact_text(value: object) -> str:
    """Return safe diagnostic text without credentials or control characters.

    Configuration is user-editable, so all values are sanitized before they
    reach stdout or a log.  The checker does not dump environment variables or
    command output; this redaction is an additional guard for values such as
    ``token=...`` and URL user-info accidentally placed in a declaration.
    """

    text = _CONTROL_RE.sub("?", str(value))
    text = _URL_USERINFO_RE.sub(r"\1[REDACTED]\3", text)
    text = _BEARER_RE.sub(r"\1[REDACTED]", text)
    text = _QUERY_SECRET_RE.sub(r"\1[REDACTED]", text)
    text = _SECRET_ASSIGNMENT_RE.sub(r"\1[REDACTED]", text)
    return text


def _default_provider_paths(provider_id: str, project_dir: Path) -> tuple[str, ...]:
    """Build conservative local-only search paths for known providers."""

    aliases: dict[str, tuple[str, ...]] = {
        "superpowers": ("superpowers",),
        "j-space": ("j-space",),
        # grilling is the primitive behind the grill-me experience on some
        # hosts, so either directory satisfies the capability.
        "grill-me": ("grill-me", "grilling"),
    }
    names = aliases.get(provider_id, (provider_id,))
    roots: list[Path] = [
        project_dir / ".agents" / "skills",
        project_dir / ".codex" / "skills",
        Path.home() / ".agents" / "skills",
        Path.home() / ".codex" / "skills",
    ]
    if provider_id == "superpowers":
        # Some hosts distribute Superpowers as a plugin bundle rather than a
        # single skills directory.  Probe only the bundle metadata path; do
        # not recurse into or execute its instructions.
        roots.extend(
            [
                Path.home() / ".codex" / "plugins" / "cache" / "openai-api-curated",
                Path.home() / ".codex" / "plugins" / "cache" / "openai-bundled",
            ]
        )
    for variable in ("CODEX_HOME", "AGENTS_HOME"):
        configured = os.environ.get(variable)
        if configured:
            roots.append(Path(configured).expanduser() / "skills")

    # De-duplicate without resolving paths (resolve may touch a broken link).
    seen: set[str] = set()
    paths: list[str] = []
    for root in roots:
        for name in names:
            raw = str(root / name)
            key = os.path.normcase(os.path.normpath(raw))
            if key not in seen:
                seen.add(key)
                paths.append(raw)
    return tuple(paths)


def default_requirements(project_dir: Path, package_root: Path) -> list[Requirement]:
    """Return the host-neutral baseline declarations.

    Python is optional: it powers this checker and the kit's safe initializer,
    but the governance core is Markdown and the documented manual path creates
    the same working set without it.  A missing or too-old interpreter therefore
    routes to that fallback instead of blocking the project.  Git is recommended
    for code projects, but is optional for document-only projects.  Provider
    capabilities are always optional and have explicit portable fallbacks.
    """

    requirements = [
        Requirement(
            id="python",
            kind="command",
            command=sys.executable,
            required=False,
            impact="the bundled diagnostics and safe initializer cannot run; the Markdown governance core is unaffected",
            fallback="create the working set manually, add the .jspace/ entry to .gitignore by hand, and record a host-native check",
            min_version="3.9",
        ),
        Requirement(
            id="git",
            kind="command",
            command="git",
            required=False,
            impact="branch, commit, and post-integration provenance cannot be checked automatically",
            fallback="record the host's version-control or manual provenance in the charter",
        ),
        Requirement(
            id="superpowers",
            kind="provider",
            required=False,
            paths=_default_provider_paths("superpowers", project_dir),
            impact="native brainstorming, planning, TDD, debugging, review, and verification routines are unavailable",
            fallback="portable checklists in the Charter Kit skill",
        ),
        Requirement(
            id="j-space",
            kind="provider",
            required=False,
            paths=_default_provider_paths("j-space", project_dir),
            impact="native long-task ledger, seam refresh, and resume support are unavailable",
            fallback=".charter/handoff.md and the task ledger sections",
        ),
        Requirement(
            id="grill-me",
            kind="provider",
            required=False,
            paths=_default_provider_paths("grill-me", project_dir),
            impact="interactive design-interview questioning is unavailable",
            fallback="the bundled references/design-interview.md interview",
        ),
    ]
    # A provider bundled directly beside the kit is also a valid local
    # installation. Keep this path explicit; do not recursively scan or load
    # arbitrary instructions from the package.
    for index, requirement in enumerate(requirements):
        if requirement.kind == "provider":
            requirements[index] = Requirement(
                id=requirement.id,
                kind=requirement.kind,
                required=requirement.required,
                impact=requirement.impact,
                fallback=requirement.fallback,
                command=requirement.command,
                paths=requirement.paths + (str(package_root / "skills" / requirement.id),),
                markers=requirement.markers,
                min_version=requirement.min_version,
                probe=requirement.probe,
                action=requirement.action,
            )
    return requirements


def _require_identifier(value: object, field: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER_RE.fullmatch(value):
        raise ConfigurationError(
            f"{field} must be a short identifier matching {_IDENTIFIER_RE.pattern}"
        )
    return value


def _require_text(value: object, field: str, default: str = "") -> str:
    if value is None:
        value = default
    if not isinstance(value, str) or not value.strip():
        raise ConfigurationError(f"{field} must be a non-empty string")
    if _CONTROL_RE.search(value):
        raise ConfigurationError(f"{field} must not contain control characters")
    return value.strip()


def _optional_text(value: object, field: str) -> str:
    """Validate an optional human-facing declaration without requiring it."""

    if value is None:
        return ""
    return _require_text(value, field)


def _parse_bool(value: object, field: str, default: bool = False) -> bool:
    if value is None:
        return default
    if not isinstance(value, bool):
        raise ConfigurationError(f"{field} must be true or false")
    return value


def _parse_min_version(value: object, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not re.fullmatch(r"\d+(?:\.\d+){1,2}", value.strip()):
        raise ConfigurationError(f"{field} must look like '3.9' or '3.10.1'")
    return value.strip()


def _parse_paths(value: object, field: str, *, allow_empty: bool = False) -> tuple[str, ...]:
    if value is None and allow_empty:
        return ()
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list) or (not value and not allow_empty):
        raise ConfigurationError(f"{field} must be a non-empty array of paths")
    paths: list[str] = []
    for index, item in enumerate(value):
        paths.append(_require_text(item, f"{field}[{index}]"))
    return tuple(paths)


def _parse_markers(value: object, field: str) -> tuple[str, ...]:
    """Validate provider metadata marker paths.

    Markers are shallow, relative paths inside a provider location.  They are
    used only as metadata evidence; accepting absolute paths or ``..`` would
    let a declaration certify an unrelated directory.  An omitted (or empty)
    value selects the conservative built-in marker set.
    """

    if value is None:
        return ()
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        raise ConfigurationError(f"{field} must be an array of relative marker paths")
    if not value:
        return ()
    markers: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        marker = _require_text(item, f"{field}[{index}]")
        # Treat both slash styles as separators so declarations authored on a
        # different host remain portable.  Marker paths are never expanded as
        # project/package/environment tokens.
        normalized = marker.replace("\\", "/")
        if (
            normalized.startswith("/")
            or re.match(r"^[A-Za-z]:/", normalized)
            or "://" in normalized
        ):
            raise ConfigurationError(f"{field}[{index}] must be relative")
        parts = tuple(part for part in normalized.split("/") if part)
        if not parts or any(part in {".", ".."} for part in parts):
            raise ConfigurationError(f"{field}[{index}] must not contain '.' or '..'")
        if any(ch in normalized for ch in "*?[]"):
            raise ConfigurationError(f"{field}[{index}] must be an exact path, not a pattern")
        # Preserve the first spelling while de-duplicating case-insensitively;
        # Windows hosts treat these names case-insensitively and duplicate
        # markers add no evidence.
        key = normalized.casefold()
        if key not in seen:
            seen.add(key)
            markers.append(normalized)
    return tuple(markers)


def _parse_command(item: object, index: int) -> Requirement:
    if not isinstance(item, Mapping):
        raise ConfigurationError(f"commands[{index}] must be an object")
    prefix = f"commands[{index}]"
    identifier = _require_identifier(item.get("id"), f"{prefix}.id")
    command_value = item.get("command")
    # A capability manifest may use ``probe: unverified`` for a command that
    # is intentionally host-specific.  Keep the declaration valid without
    # inventing a command to probe.
    probe = item.get("probe", "auto")
    if probe not in {"auto", "missing", "unverified"}:
        raise ConfigurationError(f"{prefix}.probe must be auto, missing, or unverified")
    command = None
    if command_value is not None:
        command = _require_text(command_value, f"{prefix}.command")
    if command is None and probe == "auto":
        probe = "unverified"
    impact = _require_text(
        item.get("impact"), f"{prefix}.impact", "command capability is unavailable"
    )
    fallback = _require_text(
        item.get("fallback"), f"{prefix}.fallback", "record a portable/manual fallback"
    )
    action = _optional_text(item.get("action"), f"{prefix}.action")
    return Requirement(
        id=identifier,
        kind="command",
        command=command,
        required=_parse_bool(item.get("required"), f"{prefix}.required"),
        impact=impact,
        fallback=fallback,
        min_version=_parse_min_version(item.get("min_version"), f"{prefix}.min_version"),
        probe=probe,
        action=action,
    )


def _parse_provider(item: object, index: int) -> Requirement:
    if not isinstance(item, Mapping):
        raise ConfigurationError(f"providers[{index}] must be an object")
    prefix = f"providers[{index}]"
    identifier = _require_identifier(item.get("id"), f"{prefix}.id")
    impact = _require_text(
        item.get("impact"), f"{prefix}.impact", "provider capability is unavailable"
    )
    fallback = _require_text(
        item.get("fallback"), f"{prefix}.fallback", "use the portable workflow fallback"
    )
    action = _optional_text(item.get("action"), f"{prefix}.action")
    paths_value = item.get("paths", item.get("path"))
    paths = _parse_paths(paths_value, f"{prefix}.paths", allow_empty=True)
    marker_value = item.get("markers")
    if marker_value is None:
        marker_value = item.get("required_files")
    markers = _parse_markers(marker_value, f"{prefix}.markers")
    probe = item.get("probe", "auto")
    if probe not in {"auto", "missing", "unverified"}:
        raise ConfigurationError(f"{prefix}.probe must be auto, missing, or unverified")
    if not paths and probe == "auto":
        probe = "unverified"
    return Requirement(
        id=identifier,
        kind="provider",
        paths=paths,
        required=_parse_bool(item.get("required"), f"{prefix}.required"),
        impact=impact,
        fallback=fallback,
        markers=markers,
        probe=probe,
        action=action,
    )


def _parse_capability(item: object, index: int) -> Requirement:
    """Parse a manually declared capability that cannot be probed locally."""

    if not isinstance(item, Mapping):
        raise ConfigurationError(f"capabilities[{index}] must be an object")
    prefix = f"capabilities[{index}]"
    identifier = _require_identifier(item.get("id"), f"{prefix}.id")
    impact = _require_text(
        item.get("impact"), f"{prefix}.impact", "capability cannot be verified by local probes"
    )
    fallback = _require_text(
        item.get("fallback"), f"{prefix}.fallback", "record a portable/manual fallback"
    )
    action = _optional_text(item.get("action"), f"{prefix}.action")
    paths_value = item.get("paths", item.get("path"))
    paths = _parse_paths(paths_value, f"{prefix}.paths", allow_empty=True) if paths_value is not None else ()
    marker_value = item.get("markers")
    if marker_value is None:
        marker_value = item.get("required_files")
    markers = _parse_markers(marker_value, f"{prefix}.markers")
    command_value = item.get("command")
    command = None
    if command_value is not None:
        command = _require_text(command_value, f"{prefix}.command")
    probe = item.get("probe", "auto")
    if probe not in {"auto", "missing", "unverified"}:
        raise ConfigurationError(f"{prefix}.probe must be auto, missing, or unverified")
    declared_kind = item.get("kind", "capability")
    if not isinstance(declared_kind, str) or not declared_kind.strip():
        raise ConfigurationError(f"{prefix}.kind must be a non-empty string")
    normalized_kind = declared_kind.strip().lower()
    if normalized_kind in {"command", "executable", "runtime", "tool"} or command is not None:
        kind = "command"
    elif normalized_kind in {"path", "directory"}:
        # A path capability (for example a readable bundled Markdown file or
        # the project directory) needs only a filesystem probe; it is not a
        # provider and therefore must not require a provider marker.
        kind = normalized_kind
    elif normalized_kind in {"provider", "skill"} or paths:
        kind = "provider"
    else:
        kind = "capability"
    return Requirement(
        id=identifier,
        kind=kind,
        required=_parse_bool(item.get("required"), f"{prefix}.required"),
        impact=impact,
        fallback=fallback,
        paths=paths,
        markers=markers,
        command=command,
        probe=probe,
        action=action,
    )


def _merge_requirements(
    baseline: Sequence[Requirement], additions: Iterable[Requirement]
) -> list[Requirement]:
    result = list(baseline)
    positions = {item.id: index for index, item in enumerate(result)}
    for item in additions:
        if item.id in positions:
            result[positions[item.id]] = item
        else:
            positions[item.id] = len(result)
            result.append(item)
    return result


def load_requirements(
    config_path: Path | None,
    project_dir: Path,
    package_root: Path,
) -> list[Requirement]:
    """Load defaults and layered JSON declarations.

    The package manifest supplies the portable baseline.  When no explicit
    ``--config`` is given, a project-local ``.charter/dependencies.json`` is
    discovered and merged on top of that baseline.  An explicit config is a
    deliberate override and therefore suppresses automatic project discovery
    while still inheriting the package manifest.  This keeps a project
    declaration useful to the initializer without making an invocation with a
    typo silently fall back to unrelated defaults.
    """

    requirements = default_requirements(project_dir, package_root)
    bundled_config = package_root / "dependencies.json"
    config_paths: list[Path] = []
    if bundled_config.is_file():
        config_paths.append(bundled_config)
    if config_path is not None:
        config_paths.append(Path(config_path).expanduser())
    else:
        project_config = project_dir / ".charter" / "dependencies.json"
        if project_config.is_file():
            config_paths.append(project_config)

    # The caller commonly passes the package manifest explicitly (older
    # initializer versions did so).  Avoid parsing the same file twice while
    # retaining the explicit-config precedence above.
    unique_paths: list[Path] = []
    seen_paths: set[str] = set()
    for candidate in config_paths:
        key = os.path.normcase(os.path.abspath(str(candidate)))
        if key not in seen_paths:
            seen_paths.add(key)
            unique_paths.append(candidate)

    def parse_file(path: Path) -> list[Requirement]:
        try:
            raw = path.read_text(encoding="utf-8")
            payload = json.loads(raw)
        except OSError as exc:
            raise ConfigurationError(f"cannot read config {path}: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise ConfigurationError(f"invalid JSON in {path}: {exc}") from exc
        if not isinstance(payload, Mapping):
            raise ConfigurationError(f"dependency config top level must be an object: {path}")

        parsed: list[Requirement] = []
        commands = payload.get("commands", [])
        providers = payload.get("providers", [])
        capabilities = payload.get("capabilities", [])
        for field, values in (
            ("commands", commands),
            ("providers", providers),
            ("capabilities", capabilities),
        ):
            if not isinstance(values, list):
                raise ConfigurationError(f"{field} must be an array in {path}")
        parsed.extend(_parse_command(item, index) for index, item in enumerate(commands))
        parsed.extend(_parse_provider(item, index) for index, item in enumerate(providers))
        parsed.extend(_parse_capability(item, index) for index, item in enumerate(capabilities))
        return parsed

    for path in unique_paths:
        requirements = _merge_requirements(requirements, parse_file(path))
    return requirements


def _expand_path(raw: str, project_dir: Path, package_root: Path) -> tuple[Path | None, str | None]:
    """Expand only documented local tokens; return ``None`` for unknown state."""

    value = raw.strip()
    if "://" in value:
        return None, "remote URL is outside the local read-only probe"
    env_error: str | None = None

    def replace_env(match: re.Match[str]) -> str:
        nonlocal env_error
        variable = match.group(1)
        configured = os.environ.get(variable)
        if not configured:
            env_error = f"environment variable {variable} is unset"
            return match.group(0)
        return configured

    value = _ENV_TOKEN_RE.sub(replace_env, value)
    if env_error is not None:
        return None, env_error
    replacements = {
        "{project}": str(project_dir),
        "{package}": str(package_root),
        "{home}": str(Path.home()),
    }
    for token, replacement in replacements.items():
        value = value.replace(token, replacement)
    if "{" in value or "}" in value:
        return None, "path contains an unsupported expansion token"
    try:
        path = Path(value).expanduser()
        if not path.is_absolute():
            path = project_dir / path
        # Do not let a local-only diagnostic unexpectedly contact a network
        # share.  ``Path.anchor`` identifies UNC paths on Windows without
        # resolving or touching the share.
        if os.name == "nt" and path.anchor.startswith("\\\\"):
            return None, "UNC/network path is outside the local probe"
        return path, None
    except (OSError, ValueError) as exc:
        return None, f"invalid local path ({exc})"


def _is_link(path: Path) -> bool:
    """Check links without following them where the platform exposes metadata."""

    if path.is_symlink():
        return True
    try:
        attributes = os.lstat(path).st_file_attributes
    except (AttributeError, FileNotFoundError, OSError):
        return False
    reparse_point = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x0400)
    return bool(attributes & reparse_point)


def _linked_parent(path: Path) -> Path | None:
    """Return a linked ancestor, if any, without resolving the path."""

    current = path
    while True:
        if _is_link(current):
            return current
        parent = current.parent
        if parent == current:
            return None
        current = parent


def _marker_file_exists(base: Path, marker: str) -> bool:
    """Check one marker without following links in any path component."""

    current = base
    try:
        for component in marker.replace("\\", "/").split("/"):
            if not component or component == ".":
                continue
            current = current / component
            if _is_link(current) or not current.exists():
                return False
        return current.is_file() and os.access(current, os.R_OK)
    except (OSError, PermissionError):
        return False


def _has_provider_marker(path: Path, markers: Sequence[str] = ()) -> bool:
    """Return whether a provider location has recognizable local metadata.

    A readable directory alone is not evidence that a provider is installed:
    an empty directory (or an unrelated cache directory) must not make the
    workflow invoke a missing tool.  Inspect only shallow metadata and never
    load or execute provider instructions.
    """

    marker_list = tuple(markers) or DEFAULT_PROVIDER_MARKERS

    def direct(candidate: Path) -> bool:
        try:
            if _is_link(candidate):
                return False
            if candidate.is_file():
                # A declaration may point directly at a marker file.  Compare
                # only the basename so ``plugin.json`` and
                # ``.codex-plugin/plugin.json`` both work in that form.
                return any(
                    candidate.name.casefold() == Path(marker).name.casefold()
                    for marker in marker_list
                ) and os.access(candidate, os.R_OK)
            if not candidate.is_dir():
                return False
            return any(_marker_file_exists(candidate, marker) for marker in marker_list)
        except OSError:
            return False

    if direct(path):
        return True
    # Plugin caches commonly contain one immutable version directory.  A
    # single-level metadata check recognizes that layout without recursively
    # traversing arbitrary provider content.
    if path.is_dir():
        try:
            for child in path.iterdir():
                # Do not let a cache-level probe follow a linked child or a
                # linked marker subtree into an unrelated location.
                if not _is_link(child) and child.is_dir() and direct(child):
                    return True
        except OSError:
            return False
    return False


def _probe_path(
    path: Path, *, provider: bool = False, markers: Sequence[str] = ()
) -> tuple[str, str]:
    """Return ``(status, message)`` for a local path capability."""

    try:
        if _is_link(path):
            # A provider may legitimately be installed through a symlink, but
            # following links would make a diagnostic probe less predictable.
            return STATUS_UNVERIFIED, "location is a symlink or junction"
        if not path.exists():
            return STATUS_MISSING, "location does not exist"
        if not (path.is_dir() or path.is_file()):
            return STATUS_UNVERIFIED, "location is neither a file nor directory"
        if not os.access(path, os.R_OK):
            return STATUS_UNVERIFIED, "location is not readable"
        if provider and not _has_provider_marker(path, markers):
            marker_list = ", ".join(markers or DEFAULT_PROVIDER_MARKERS)
            return STATUS_UNVERIFIED, f"location has no provider metadata marker ({marker_list})"
        if path.is_dir():
            # Metadata-only read check.  Do not import or execute provider
            # instructions; listing is enough to catch inaccessible folders.
            next(path.iterdir(), None)
        return STATUS_AVAILABLE, "local provider location is readable"
    except (OSError, PermissionError) as exc:
        return STATUS_UNVERIFIED, f"location could not be inspected ({exc.__class__.__name__})"


def _version_tuple(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in value.split("."))


def _probe_command(requirement: Requirement) -> tuple[str, str, str]:
    """Return ``(status, message, location)`` for a command requirement."""

    assert requirement.command is not None
    command = requirement.command
    try:
        located = shutil.which(command)
    except (OSError, ValueError):
        return STATUS_UNVERIFIED, "command lookup failed", ""
    # This process is already running under Python.  A Windows host may not
    # expose the conventional ``python`` alias on PATH (for example when the
    # launcher is disabled), so do not report the interpreter used to invoke
    # this checker as missing merely because the manifest alias is absent.
    alias_fallback = False
    if not located and requirement.id == "python" and sys.executable:
        located = sys.executable
        alias_fallback = True
    if not located:
        return STATUS_MISSING, "executable was not found on PATH", ""
    if requirement.id == "python" and requirement.min_version:
        try:
            if _version_tuple(".".join(str(part) for part in sys.version_info[:3])) < _version_tuple(
                requirement.min_version
            ):
                return (
                    STATUS_MISSING,
                    f"running interpreter is below required version {requirement.min_version}",
                    located,
                )
        except (TypeError, ValueError):
            return STATUS_UNVERIFIED, "interpreter version could not be compared", located
    message = (
        "current interpreter is available (alias not on PATH)"
        if alias_fallback
        else "executable is discoverable (not executed)"
    )
    return STATUS_AVAILABLE, message, located


def check_requirement(
    requirement: Requirement, project_dir: Path, package_root: Path
) -> list[CheckResult]:
    """Probe one declaration and add a fallback record when needed."""

    def action_for(status: str, fallback_record: bool = False) -> str:
        noun = "provider" if requirement.kind == "provider" else "capability"
        if requirement.action:
            return requirement.action
        if fallback_record:
            return f"use the stated fallback now; install or restore the {noun} only as a separate user action"
        if status == STATUS_AVAILABLE:
            return "continue and retain this probe as evidence"
        if requirement.required:
            return "restore the capability or obtain an explicit user waiver before proceeding"
        return f"continue with the stated fallback; install or restore the {noun} later if needed"

    if requirement.probe == "missing":
        status, message, location = STATUS_MISSING, "no local capability was found", ""
    elif requirement.probe == "unverified":
        status, message, location = (
            STATUS_UNVERIFIED,
            "capability requires host or human confirmation",
            "",
        )
    elif requirement.kind == "command" and requirement.command:
        status, message, location = _probe_command(requirement)
    elif requirement.kind in {"provider", "path", "directory"}:
        if not requirement.paths:
            status, message, location = (
                STATUS_UNVERIFIED,
                "no local provider location was declared",
                "",
            )
        else:
            statuses: list[tuple[str, str, str]] = []
            for raw_path in requirement.paths:
                path, expansion_error = _expand_path(raw_path, project_dir, package_root)
                if expansion_error:
                    statuses.append((STATUS_UNVERIFIED, expansion_error, raw_path))
                    continue
                assert path is not None
                path_status, path_message = _probe_path(
                    path,
                    provider=requirement.kind == "provider",
                    markers=requirement.markers,
                )
                statuses.append((path_status, path_message, str(path)))
            # An available location wins.  If none is available, an unknown
            # location takes precedence over a definite miss.
            available = next((item for item in statuses if item[0] == STATUS_AVAILABLE), None)
            unverified = next((item for item in statuses if item[0] == STATUS_UNVERIFIED), None)
            chosen = available or unverified or statuses[0]
            status, message, location = chosen
            if not available and unverified is not None:
                message = f"{message}; other candidate locations were not available"
    else:
        status, message, location = (
            STATUS_UNVERIFIED,
            "capability requires host or human confirmation",
            "",
        )

    primary = CheckResult(
        id=requirement.id,
        status=status,
        kind=requirement.kind,
        required=requirement.required,
        message=redact_text(message),
        reason=redact_text(message),
        impact=redact_text(requirement.impact),
        fallback=redact_text(requirement.fallback),
        location=redact_text(location),
        action=redact_text(action_for(status)),
    )
    records = [primary]
    if status in {STATUS_MISSING, STATUS_UNVERIFIED} and requirement.fallback:
        records.append(
            CheckResult(
                id=requirement.id,
                status=STATUS_FALLBACK,
                kind=requirement.kind,
                required=requirement.required,
                message=f"portable fallback is available: {redact_text(requirement.fallback)}",
                reason=f"portable fallback is available: {redact_text(requirement.fallback)}",
                impact=redact_text(requirement.impact),
                fallback=redact_text(requirement.fallback),
                location=redact_text(location),
                action=redact_text(action_for(status, fallback_record=True)),
            )
        )
    return records


def check_requirements(
    requirements: Sequence[Requirement], project_dir: Path, package_root: Path
) -> list[CheckResult]:
    """Probe all declarations in stable order."""

    records: list[CheckResult] = []
    for requirement in requirements:
        records.extend(check_requirement(requirement, project_dir, package_root))
    return records


def _parse_provider_override(value: str) -> tuple[str, str]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("expected PROVIDER=PATH")
    identifier, path = value.split("=", 1)
    try:
        identifier = _require_identifier(identifier.strip(), "provider id")
        path = _require_text(path, "provider path")
    except ConfigurationError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc
    return identifier, path


def _parse_identifier_argument(value: str) -> str:
    try:
        return _require_identifier(value.strip(), "provider id")
    except ConfigurationError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def _resolve_config_path(value: Path, project_dir: Path) -> Path:
    """Resolve a relative config beside the selected project when present.

    Keeping this deterministic lets a host invoke the checker from the package
    directory while storing project-specific declarations under
    ``<project>/.charter/``.
    """

    candidate = value.expanduser()
    if candidate.is_absolute() or candidate.exists():
        return candidate
    project_candidate = project_dir / candidate
    if project_candidate.exists():
        return project_candidate
    # Preserve the original path for a useful error message if neither exists.
    return candidate


def apply_cli_overrides(
    requirements: Sequence[Requirement],
    provider_overrides: Sequence[tuple[str, str]],
    required_providers: Sequence[str],
    require_git: bool,
    project_dir: Path | None = None,
    required_ids: Sequence[str] = (),
    optional_ids: Sequence[str] = (),
) -> list[Requirement]:
    """Apply explicit command-line declarations without mutating defaults."""

    result = list(requirements)
    search_project = project_dir or Path.cwd()
    positions = {item.id: index for index, item in enumerate(result)}

    def add_or_mark(identifier: str, required: bool) -> None:
        """Mark a known id or add an explicit, conservatively missing one."""

        if identifier in positions:
            previous = result[positions[identifier]]
            result[positions[identifier]] = Requirement(
                id=previous.id,
                kind=previous.kind,
                required=required,
                impact=previous.impact,
                fallback=previous.fallback,
                command=previous.command,
                paths=previous.paths,
                markers=previous.markers,
                min_version=previous.min_version,
                probe=previous.probe,
                action=previous.action,
            )
            return
        # A bare CLI capability has no safe target to inspect.  Report a
        # definite local miss so the caller can distinguish it from a host
        # capability that exists but could not be verified.
        result.append(
            Requirement(
                id=identifier,
                kind="capability",
                required=required,
                impact="the requested capability is not declared or discoverable",
                fallback="use the portable workflow fallback or declare a local probe",
                probe="missing",
            )
        )
        positions[identifier] = len(result) - 1

    for identifier in required_ids:
        add_or_mark(identifier, True)
    for identifier in optional_ids:
        # An explicitly required declaration wins if both switches mention it,
        # and a manifest-required capability can never be downgraded by a
        # convenience ``--optional`` flag.  Otherwise callers could bypass a
        # project safety gate merely by changing the diagnostic invocation.
        if identifier not in set(required_ids):
            if identifier in positions and result[positions[identifier]].required:
                continue
            add_or_mark(identifier, False)

    for identifier, path in provider_overrides:
        if identifier in positions:
            previous = result[positions[identifier]]
            result[positions[identifier]] = Requirement(
                id=previous.id,
                kind="provider",
                required=previous.required,
                impact=previous.impact,
                fallback=previous.fallback,
                paths=(path,),
                markers=previous.markers,
                probe="auto",
                action=previous.action,
            )
        else:
            result.append(
                Requirement(
                    id=identifier,
                    kind="provider",
                    required=False,
                    impact="the requested provider capability is unavailable",
                    fallback="use the portable workflow fallback",
                    paths=(path,),
                    probe="auto",
                )
            )
            positions[identifier] = len(result) - 1
    for identifier in required_providers:
        if identifier not in positions:
            result.append(
                Requirement(
                    id=identifier,
                    kind="provider",
                    required=True,
                    impact="a required provider capability is unavailable",
                    fallback="stop and request the provider or an explicit waiver",
                    paths=_default_provider_paths(identifier, search_project),
                    probe="auto",
                )
            )
            positions[identifier] = len(result) - 1
        else:
            previous = result[positions[identifier]]
            result[positions[identifier]] = Requirement(
                id=previous.id,
                kind=previous.kind,
                required=True,
                impact=previous.impact,
                fallback=previous.fallback,
                command=previous.command,
                paths=previous.paths,
                markers=previous.markers,
                min_version=previous.min_version,
                probe=previous.probe,
                action=previous.action,
            )
    if require_git and "git" in positions:
        previous = result[positions["git"]]
        result[positions["git"]] = Requirement(
            id=previous.id,
            kind=previous.kind,
            required=True,
            impact=previous.impact,
            fallback=previous.fallback,
            command=previous.command,
            paths=previous.paths,
            markers=previous.markers,
            min_version=previous.min_version,
            probe=previous.probe,
            action=previous.action,
        )
    return result


def format_record(record: CheckResult) -> str:
    """Format one record without untrusted multiline content."""

    required = "required" if record.required else "optional"
    # Keep records ASCII-friendly so logs survive hosts with a non-UTF-8
    # console code page (the package itself remains UTF-8).
    details = f"[{record.status}] {record.id} ({required}, {record.kind}) - {record.message}"
    if record.location:
        details += f"; location: {record.location}"
    if record.impact:
        impact_label = "impact-if-missing" if record.status == STATUS_AVAILABLE else "impact"
        details += f"; {impact_label}: {record.impact}"
    if record.fallback:
        fallback_label = "fallback-if-missing" if record.status == STATUS_AVAILABLE else "fallback"
        details += f"; {fallback_label}: {record.fallback}"
    # ``action`` is part of the public diagnostic contract.  Keep the field in
    # every human-readable record, even when a malformed/legacy declaration
    # left it empty, so a user can always tell what to do next.
    details += f"; action: {record.action or 'review the capability state and choose the stated fallback or an explicit user action'}"
    return redact_text(details)


def write_log(path: Path, records: Sequence[CheckResult]) -> None:
    """Append a safe diagnostic snapshot to an explicit log path."""

    path = path.expanduser()
    if path.exists() and _is_link(path):
        raise OSError(f"refusing to write through linked log path: {path}")
    linked_parent = _linked_parent(path.parent)
    if linked_parent is not None:
        raise OSError(f"refusing to write through linked log directory: {linked_parent}")
    path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(f"# Charter Kit dependency check {timestamp}\n")
        for record in records:
            handle.write(format_record(record) + "\n")


def _required_failures(records: Sequence[CheckResult]) -> list[CheckResult]:
    return [
        record
        for record in records
        if record.required and record.status in {STATUS_MISSING, STATUS_UNVERIFIED}
    ]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "project_dir",
        nargs="?",
        default=".",
        help="project directory used to expand {project} and locate local skills (default: current directory)",
    )
    parser.add_argument(
        "--project",
        dest="project_option",
        type=Path,
        help="project directory (alternative to the positional argument)",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="explicit JSON dependency declaration; package defaults remain enabled and automatic project discovery is suppressed",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        help="append a redacted human-readable diagnostic log at this path",
    )
    parser.add_argument(
        "--provider-dir",
        "--skill-dir",
        dest="provider_dirs",
        action="append",
        type=_parse_provider_override,
        metavar="PROVIDER=PATH",
        help="override/add a provider or skill location (repeatable; no install is performed)",
    )
    parser.add_argument(
        "--require-provider",
        dest="required_providers",
        action="append",
        default=[],
        type=_parse_identifier_argument,
        metavar="PROVIDER",
        help="treat a provider as required for this run (repeatable)",
    )
    parser.add_argument(
        "--require",
        dest="required_ids",
        action="append",
        default=[],
        type=_parse_identifier_argument,
        metavar="CAPABILITY",
        help="require a capability id from the manifest (repeatable)",
    )
    parser.add_argument(
        "--optional",
        dest="optional_ids",
        action="append",
        default=[],
        type=_parse_identifier_argument,
        metavar="CAPABILITY",
        help="check an optional capability id from the manifest (repeatable)",
    )
    parser.add_argument(
        "--require-git",
        action="store_true",
        help="treat Git as required for this run",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit a JSON array to stdout instead of human-readable records",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    selected_project = args.project_option if args.project_option is not None else args.project_dir
    project_dir = Path(selected_project).expanduser().resolve()
    package_root = Path(__file__).resolve().parents[1]
    config_path = (
        _resolve_config_path(args.config, project_dir) if args.config is not None else None
    )
    try:
        requirements = load_requirements(config_path, project_dir, package_root)
        # Keep a required declaration required even when a caller supplies a
        # convenience ``--optional`` switch.  Emit a warning so the decision
        # is visible in logs/CI instead of being a silent no-op.  JSON output
        # remains machine-readable because the warning goes to stderr.
        required_before_optional = {
            item.id for item in requirements if item.required
        }
        downgraded = sorted(
            required_before_optional.difference(args.required_ids or [])
            .intersection(args.optional_ids or [])
        )
        if downgraded:
            print(
                "Dependency warning: --optional cannot downgrade required capability(s): "
                + ", ".join(downgraded),
                file=sys.stderr,
            )
        requirements = apply_cli_overrides(
            requirements,
            args.provider_dirs or [],
            args.required_providers,
            args.require_git,
            project_dir,
            args.required_ids,
            args.optional_ids,
        )
        records = check_requirements(requirements, project_dir, package_root)
    except (ConfigurationError, OSError, ValueError) as exc:
        message = (
            f"[UNVERIFIED] dependency configuration - {redact_text(exc)}"
            "; impact: declared dependency capabilities could not be evaluated"
            "; fallback: use the built-in defaults or a portable manual check"
            "; action: repair the declaration and rerun before relying on capability status"
        )
        print(message)
        if args.log_file is not None:
            try:
                safe_log = args.log_file.expanduser()
                if safe_log.exists() and _is_link(safe_log):
                    raise OSError("refusing to write through linked log path")
                linked_parent = _linked_parent(safe_log.parent)
                if linked_parent is not None:
                    raise OSError("refusing to write through linked log directory")
                safe_log.parent.mkdir(parents=True, exist_ok=True)
                with safe_log.open("a", encoding="utf-8", newline="\n") as handle:
                    handle.write(message + "\n")
            except OSError as log_exc:
                print(f"Dependency log: unable to write log ({log_exc.__class__.__name__})", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps([record.as_dict() for record in records], ensure_ascii=False, indent=2))
    else:
        for record in records:
            print(format_record(record))

    log_error = False
    if args.log_file is not None:
        try:
            write_log(args.log_file, records)
        except OSError as exc:
            log_error = True
            print(f"Dependency log: unable to write log ({exc.__class__.__name__})", file=sys.stderr)

    failures = _required_failures(records)
    if failures:
        return 1
    return 1 if log_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
