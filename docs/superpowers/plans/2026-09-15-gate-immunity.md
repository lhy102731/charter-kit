# Gate Immunity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make charter-kit prove, on demand and without judgement, that every guard it relies on still fails when the defect it exists to catch is put back.

**Architecture:** A machine-readable registry pairs each guard with a concrete mutation that reproduces the historical defect. A pure-stdlib runner copies the repository to a scratch tree, applies the mutation there, runs only that guard, and demands it go red. A guard that passes on a re-injected defect is reported as `VACUOUS` — the harness is itself sabotage-tested, so it cannot quietly become the thing it detects. A small defect catalogue records what was caught late and still has no guard; that list is the only "learning" this plan promises.

**Tech Stack:** Python 3 standard library only (`json`, `argparse`, `pathlib`, `shutil`, `subprocess`, `unittest`), Markdown templates. No new dependencies. No Node toolchain.

**Spec:** `docs/superpowers/specs/2026-09-15-gate-immunity-design.md` (written in Task 1).

## Global Constraints

- Pure standard library. Nothing in this plan may add a dependency to `dependencies.json`.
- Scratch mutation never touches the working tree. The runner copies the repository to a temporary directory, ignoring `.git`, `node_modules`, `.superpowers`, and `.venv`, and mutates only the copy. Every path in the plan that could break this rule is called out in Task 2 Step 5.
- A registry entry with no `guard` command is invalid. A mutation that cannot fail any test is not a defect reproduction, it is decoration: the self-test in Task 2 Step 4 proves the runner reports it.
- `SKILL.md` has three hand-edited copies (`skills/`, `targets/codex/skills/charter-workflow/`, `targets/zcode/skills/charter-workflow/`) that stay byte-identical to the three regenerated copies. Builders run codex → zcode → dsh, then `python scripts/validate_kit.py .`.
- New files under `portable/` are shipped automatically (`PACKAGE_ROOT_ITEMS` contains `"portable"`, `scripts/build_codex_plugin.py:31`, applied at `:413`); each one still gains a `REQUIRED_FILES` content tuple in `scripts/validate_kit.py` in the same commit, following the pattern at `validate_kit.py:39-95`.
- `targets/dsh/` gains no `GENERATED.md`. `plugins/**` and root `skills/**` are never hand-edited.
- The runner is a maintenance command. It is **not** wired into leaf closure: a per-leaf tax was one of the costs this plan explicitly rejected.
- No rule, clause, or template text is written by this plan's tooling. Automatic inheritance was the piece whose oracle could not be defined, so it is deferred (Task 4), not implemented.

---

## File Structure

| Path | Responsibility |
|---|---|
| Create `portable/gates.json` | The registry. One entry per guard: the defect pattern it pins, the command that enforces it, and the mutation that reproduces the original defect. |
| Create `portable/references/gate-immunity.md` | What counts as a gate, how a mutation must be written, how to read the report, and the four limits this plan does not claim to solve. |
| Create `portable/templates/defect-record.md` | The catalogue record: caught late, by whom, and whether a guard exists yet. |
| Create `scripts/sabotage_check.py` (repository tooling — it is repo maintenance, so it lives with the builders, and is deliberately **not** distributed to hosts) | `verify` (registry is well-formed), `run` (execute every gate in scratch), `report` (defects with no guard), `--selftest` (the runner must be able to say VACUOUS). |
| Create `tests/test_sabotage_check.py` | Schema, scratch isolation, red/green discrimination, VACUOUS detection, report counting. |
| Modify `skills/charter-workflow/SKILL.md` ×3 | One closure clause: a late-caught defect with no guard becomes a record with `Guard: none-yet`. |
| Create `docs/superpowers/specs/2026-09-15-gate-immunity-design.md` | Design basis, including what this plan refuses to build and why. |
| Create `docs/superpowers/specs/2026-09-15-deferred-self-evolution.md` | The A/B-replay half, written as preconditions that must be met before it is attempted. |

---

## Task 1: Registry, schema, and design basis

**Files:**
- Create: `docs/superpowers/specs/2026-09-15-gate-immunity-design.md`
- Create: `portable/gates.json`
- Create: `portable/references/gate-immunity.md`
- Test: `tests/test_sabotage_check.py`

**Interfaces:**
- Consumes: nothing.
- Produces: the registry keys `schema`, `gates`, and per-entry `id`, `pattern`, `guard`, `mutation`, `origin` — used verbatim by Task 2's runner and tests.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_sabotage_check.py
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "portable" / "gates.json"

ENTRY_KEYS = {"id", "pattern", "guard", "mutation", "origin"}
PATTERNS = {
    "vacuous-verification", "stale-evidence", "assumed-not-verified",
    "silent-degradation", "scope-drift",
}


class RegistrySchema(unittest.TestCase):
    def load(self):
        return json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_registry_has_a_schema_version_and_entries(self):
        data = self.load()
        self.assertEqual(data["schema"], 1)
        self.assertGreaterEqual(len(data["gates"]), 3,
                               "seed at least the three gates this session already built")

    def test_every_entry_declares_every_field(self):
        for entry in self.load()["gates"]:
            self.assertEqual(set(entry) >= ENTRY_KEYS, True,
                             f"{entry.get('id')} is missing fields")
            self.assertTrue(entry["guard"].strip(), f"{entry['id']} has an empty guard command")
            self.assertTrue(entry["origin"].strip(), f"{entry['id']} has no origin")

    def test_pattern_is_a_closed_enum(self):
        for entry in self.load()["gates"]:
            self.assertIn(entry["pattern"], PATTERNS, f"{entry['id']} invents a pattern")

    def test_mutation_names_an_action_and_a_target(self):
        for entry in self.load()["gates"]:
            action = entry["mutation"]["action"]
            self.assertIn(action, ("replace", "create"), f"{entry['id']} uses action {action}")
            self.assertTrue(entry["mutation"]["file"].strip())
            if action == "replace":
                self.assertTrue(entry["mutation"]["old"].strip(),
                                f"{entry['id']} replaces nothing")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_sabotage_check -q`
Expected: FAIL — `FileNotFoundError` on `portable/gates.json` (then, once created, `assertGreaterEqual` on the entry count).

- [ ] **Step 3: Write the design basis**

`docs/superpowers/specs/2026-09-15-gate-immunity-design.md` must state, in this order, and must not soften any of it:

1. The evidence base. One session produced five defects that survived their author's own verification: an `assertNotIn` whose comprehension filtered out the tested value; a mirror-hash command that scanned 0 files and reported agreement; two screenshots contradicting the JSON written by the same run; a retracted promise that survived in the model-facing tool description; and a handoff `Do-not-do` clause asserted from a report quote that a 35-file scan showed did not exist. **All five were found by independent review. None was found by self-check.**
2. What survives automation. Only guards with an objective oracle: a command that exits non-zero. That is a test, a validator rule, or a scan with a pinned absence.
3. What is deferred, and the exact reason. Prose rules cannot be validated on the case that generated them — that is data leakage, and with all five seed cases already used to design the rules, a hold-out set is empty. A judge that is a model reproduces the failure class; a keyword oracle reproduces the vacuous check. State both as blockers, not as caveats.
4. The four limits this plan does not remove: a mutation proves the guard still bites on *that* defect, never that the guard covers others; the registry only grows by hand; a green run says nothing about whether the defect list is complete; and the harness state (phase, preset, unlocked tools) confounds any cross-model reading of a record, so no model attribution is inferred here.
5. Why no automatic inheritance: writing into `portable/` fans out to three host distributions and the filesystem skill copy the host actually serves, and that chain drifted three times in this session while it was being done by hand.

- [ ] **Step 4: Write the registry with the three gates that already exist**

```json
{
  "schema": 1,
  "gates": [
    {
      "id": "review-timeout-constants-are-arithmetic",
      "pattern": "vacuous-verification",
      "guard": "python -m unittest tests.test_dsh_review_tool -q",
      "mutation": {
        "action": "replace",
        "file": "targets/dsh/src/index.js",
        "old": "MAX_REVIEW_TIMEOUT_SECONDS = 270",
        "new": "MAX_REVIEW_TIMEOUT_SECONDS = 540"
      },
      "origin": "The controller dimensioned the timeout clamp against one attempt; the review rerun shares the budget, so 540 s x 2 exceeded the ~600 s host ceiling and the call would be killed before it could report. Found by review of commit d444a79's parent."
    },
    {
      "id": "guard-discovers-carriers-not-enumerated",
      "pattern": "vacuous-verification",
      "guard": "python -m unittest tests.test_workflow_contract -q",
      "mutation": {
        "action": "create",
        "file": "portable/templates/roadmap.md",
        "content": "\nRoute the reuse tier to its expert skill when probed `AVAILABLE` in `.charter/evidence/dependency-check.log`.\n"
      },
      "origin": "The first version of the probe-at-decision-point guard enumerated eleven hand-edited paths, so a log-bound branch reintroduced in a twelfth artifact passed. Review proved it with a fixture injected outside the list."
    },
    {
      "id": "no-retracted-empty-review-promise-anywhere",
      "pattern": "stale-evidence",
      "guard": "python -m unittest tests.test_dsh_review_tool -q",
      "mutation": {
        "action": "replace",
        "file": "targets/dsh/README.md",
        "old": "an empty review is never returned as a success shape",
        "new": "the call never returns an empty review"
      },
      "origin": "The retraction of 'never hands back an empty review' was applied to the README carriers while the model-facing tool description kept the false sentence, which is the carrier the model actually reads."
    }
  ]
}
```

- [ ] **Step 5: Write the rules reference**

`portable/references/gate-immunity.md`, each item written as something you do, not advice:

- A **gate** is a command that exits non-zero when its defect is present. Prose is not a gate. A TODO is not a gate.
- A **mutation** must name an edit that a human already observed, or would plausibly make. `replace` must target text that exists today, so a drifted guard command shows up as a broken mutation rather than a silent skip.
- `create` is for absence gates: the defect is that a banned phrasing reappears, so reproduce it in a file the guard is supposed to discover.
- Read the report as: `bit` = the guard still fails on its defect; **`VACUOUS` = the guard now passes while the defect is in the tree, which is an incident, not a pass**.
- Adding a gate requires running `sabotage_check.py run` in the same commit. A gate that has never been seen to bite is not a gate.
- Removing or renaming a guarded command requires updating the entry in the same commit; a stale `guard` command reports as `ERROR`, which is also an incident.
- What this file does not claim: that a biting guard covers neighbouring defects, that the defect list is complete, or anything at all about which model was at fault.

- [ ] **Step 6: Run tests to verify they pass, wire the validator, regenerate, commit**

```bash
python -m unittest tests.test_sabotage_check -q
```
Expected: PASS (4 tests).

Add to `scripts/validate_kit.py` `REQUIRED_FILES`, following the tuple style at `:39-95`:

```python
"portable/references/gate-immunity.md": (
    "VACUOUS", "not a gate", "incidents", "exits non-zero",
),
```

```bash
python scripts/build_codex_plugin.py && python scripts/build_zcode_plugin.py && python scripts/build_dsh_plugin.py
python scripts/validate_kit.py .
git add docs/superpowers/specs/2026-09-15-gate-immunity-design.md portable/gates.json \
        portable/references/gate-immunity.md tests/test_sabotage_check.py scripts/validate_kit.py plugins/ skills/
git commit -m "feat: register the guards this session built and the defects that produced them"
```
Expected: validator `PASS`; `git status --porcelain` empty after commit (note: `portable/gates.json` ships as part of `portable`, so the mirrors change here too).

---

## Task 2: The sabotage runner, and proving it can say VACUOUS

**Files:**
- Create: `scripts/sabotage_check.py`
- Test: `tests/test_sabotage_check.py`

**Interfaces:**
- Consumes: the registry keys from Task 1.
- Produces: `load_registry(path) -> list[dict]`, `apply_mutation(root: Path, mutation: dict) -> None`, `run_gate(root: Path, gate: dict) -> str` returning `bit | VACUOUS | ERROR`, and `main()` with `verify | run | report | --selftest`. Task 3's `report` command depends on `defect_records()`.

- [ ] **Step 1: Write the failing tests**

```python
class SabotageRunner(unittest.TestCase):
    def scratch(self, tmp: Path) -> Path:
        """A real repository copy is expensive; build the smallest tree the gate names."""
        (tmp / "targets/dsh/src").mkdir(parents=True)
        (tmp / "targets/dsh").mkdir(parents=True, exist_ok=True)
        (tmp / "targets/dsh/src/index.js").write_text(
            "const MAX_REVIEW_TIMEOUT_SECONDS = 270\n", encoding="utf-8")
        return tmp

    def test_replace_mutation_edits_only_the_copy(self, ):
        import shutil, tempfile
        with tempfile.TemporaryDirectory() as d:
            root = self.scratch(Path(d))
            before = (root / "targets/dsh/src/index.js").read_text(encoding="utf-8")
            sabotage_check.apply_mutation(root, {
                "action": "replace", "file": "targets/dsh/src/index.js",
                "old": "MAX_REVIEW_TIMEOUT_SECONDS = 270",
                "new": "MAX_REVIEW_TIMEOUT_SECONDS = 540"})
            after = (root / "targets/dsh/src/index.js").read_text(encoding="utf-8")
            self.assertIn("540", after)
            self.assertIn("270", before)          # the source tree is untouched

    def test_create_mutation_adds_a_file(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            root = self.scratch(Path(d))
            sabotage_check.apply_mutation(root, {
                "action": "create", "file": "portable/templates/roadmap.md",
                "content": "when probed `AVAILABLE`"})
            self.assertIn("AVAILABLE", (root / "portable/templates/roadmap.md").read_text(encoding="utf-8"))

    def test_missing_old_text_is_an_error_not_a_skip(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            root = self.scratch(Path(d))
            with self.assertRaises(sabotage_check.MutationError):
                sabotage_check.apply_mutation(root, {
                    "action": "replace", "file": "targets/dsh/src/index.js",
                    "old": "THIS TEXT IS NOT IN THE FILE", "new": "x"})

    def test_run_gate_reports_bit_when_the_command_fails(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            root = self.scratch(Path(d))
            gate = {"id": "x", "guard": "python -c \"import sys; sys.exit(1)\""}
            self.assertEqual(sabotage_check.run_gate(root, gate), "bit")

    def test_run_gate_reports_vacuous_when_the_command_succeeds(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            root = self.scratch(Path(d))
            gate = {"id": "x", "guard": "python -c \"import sys; sys.exit(0)\""}
            self.assertEqual(sabotage_check.run_gate(root, gate), "VACUOUS")

    def test_dead_guard_command_is_an_error(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            root = self.scratch(Path(d))
            gate = {"id": "x", "guard": "python -c \"raise SystemExit\" --no-such-thing"}
            self.assertEqual(sabotage_check.run_gate(root, gate), "ERROR")
```

- [ ] **Step 2: Run to verify they fail**

Run: `python -m unittest tests.test_sabotage_check -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'sabotage_check'` (Task 3's import line is added here too).

- [ ] **Step 3: Write the runner**

```python
#!/usr/bin/env python3
"""Prove that charter-kit's guards still fail on the defects they were built for.

Every registered gate is run against a scratch copy of the repository with its
historical defect put back. A guard that passes while the defect is present is
reported VACUOUS: that is the exact failure mode this tool exists to detect, and it
is why the tool sabotages itself first (--selftest).

Exit status: 0 when every gate bites, 1 when any gate is VACUOUS or ERROR.
"""
from __future__ import annotations
import argparse, json, shlex, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "portable" / "gates.json"
RECORDS_DIRNAME = "defect-records"
IGNORE = shutil.ignore_patterns(".git", "node_modules", ".superpowers", ".venv",
                                "__pycache__", "*.egg-info")


class MutationError(RuntimeError):
    """A mutation cannot be applied: wrong text, or wrong path."""


def load_registry(path: Path = REGISTRY) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    seen = set()
    for gate in data["gates"]:
        if gate["id"] in seen:
            raise MutationError(f"duplicate gate id {gate['id']}")
        seen.add(gate["id"])
        if not gate.get("guard", "").strip():
            raise MutationError(f"gate {gate['id']} declares no guard command")
    return data["gates"]


def copy_tree(dest: Path) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    target = dest / "repo"
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(ROOT, target, ignore=IGNORE)
    return target


def apply_mutation(root: Path, mutation: dict) -> None:
    action = mutation.get("action")
    path = root / mutation["file"]
    if action == "create":
        if path.exists() and mutation["content"].strip() not in path.read_text(encoding="utf-8"):
            path.write_text(
                path.read_text(encoding="utf-8") + mutation["content"], encoding="utf-8")
        elif not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(mutation["content"], encoding="utf-8")
        return
    if action != "replace":
        raise MutationError(f"unknown mutation action {action!r}")
    if not path.is_file():
        raise MutationError(f"{mutation['file']} does not exist")
    text = path.read_text(encoding="utf-8")
    if text.count(mutation["old"]) != 1:
        raise MutationError(
            f"{mutation['file']}: expected exactly one copy of {mutation['old'][:60]!r}, "
            f"found {text.count(mutation['old'])}")
    path.write_text(text.replace(mutation["old"], mutation["new"]), encoding="utf-8")


def run_gate(root: Path, gate: dict) -> str:
    """Run a guard in the scratch tree. shell=False so a dead command is detectable
    on every platform: a missing executable raises instead of printing a message
    whose wording is locale- and shell-dependent."""
    command = shlex.split(gate["guard"])
    try:
        proc = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        return "ERROR"
    except (FileNotFoundError, NotADirectoryError, OSError):
        return "ERROR"
    if proc.returncode == 0:
        return "VACUOUS"
    return "bit"


def defect_records(root: Path = ROOT) -> list[Path]:
    base = root / "docs" / "superpowers" / RECORDS_DIRNAME
    return sorted(base.glob("*.md")) if base.is_dir() else []


def selftest(root: Path) -> int:
    """Prove the runner can report VACUOUS. If it cannot, every green run is a lie."""
    fake = {"id": "selftest", "guard": "python -c \"raise SystemExit(0)\""}
    verdict = run_gate(root, fake)
    if verdict != "VACUOUS":
        print(f"SELFTEST FAILED: the runner reported {verdict!r} for a guard that "
              "cannot fail; its verdicts mean nothing", file=sys.stderr)
        return 1
    broken = {"id": "selftest", "guard": "python -m unittest no_such_module_at_all -q"}
    if run_gate(root, broken) != "ERROR":
        print("SELFTEST FAILED: a guard command that cannot start is not reported as ERROR",
              file=sys.stderr)
        return 1
    print("selftest ok: the runner distinguishes a bite from a vacuous pass and a dead command")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("command", choices=("verify", "run", "report"))
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--keep-scratch", action="store_true")
    args = ap.parse_args(argv)

    if args.command == "verify":
        try:
            gates = load_registry()
        except (MutationError, json.JSONDecodeError) as exc:
            print(f"registry invalid: {exc}", file=sys.stderr)
            return 1
        print(f"registry ok: {len(gates)} gates")
        return 0

    if args.command == "report":
        records = defect_records()
        unguarded = [p for p in records
                     if "Guard: `none-yet`" in p.read_text(encoding="utf-8")]
        print(f"defect records: {len(records)}, without a gate: {len(unguarded)}")
        for path in unguarded:
            print(f"  none-yet: {path.name}")
        return 0

    scratch = Path(tempfile.mkdtemp(prefix="charter-sabotage-"))
    rc = 0
    try:
        if args.selftest and selftest(copy_tree(scratch)) != 0:
            return 1
        root = copy_tree(scratch)
        for gate in load_registry():
            try:
                apply_mutation(root, gate["mutation"])
                verdict = run_gate(root, gate)
            except MutationError as exc:
                verdict, rc = "ERROR", max(rc, 1)
                print(f"{exc}")
            except Exception as exc:
                verdict, rc = "ERROR", max(rc, 1)
                print(f"{gate['id']}: {type(exc).__name__}: {exc}")
            finally:
                shutil.rmtree(root, ignore_errors=True)
                root = copy_tree(scratch)
            rc = max(rc, 1) if verdict != "bit" else rc
            print(f"{verdict:>8}: {gate['id']}")
        return rc
    finally:
        if args.keep_scratch:
            print(f"scratch kept at {scratch}")
        else:
            shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Prove the runner can fail, before trusting it to pass**

```bash
python -m unittest tests.test_sabotage_check -q
python scripts/sabotage_check.py --selftest run
```
Expected: unit tests PASS, and the self-test prints `selftest ok: ...`. **If the self-test passes on the first try, check that you did not write it backwards**: a runner whose every path reports "bit" would also print ok. Confirm by temporarily replacing one registry `guard` with `python -c "raise SystemExit(0)"`, re-running, and seeing `VACUOUS` plus exit 1 — then revert it without staging it.

- [ ] **Step 5: Run the real thing**

```bash
python scripts/sabotage_check.py run
```
Expected: `bit` three times, exit 0. If a gate reports `VACUOUS`, that is a genuine finding from Task 1's registry, not a bug in the runner: record it, do not relax the mutation.

- [ ] **Step 6: Isolation proof, then commit**

Run `git status --porcelain` immediately after Step 5. Expected: **empty** — every mutation must have happened inside the scratch copy. If any file is dirty, the copy is leaking; fix that before shipping, because a mutation that reaches the working tree is how a sabotage harness destroys a repository.

```bash
git add scripts/sabotage_check.py tests/test_sabotage_check.py
git commit -m "feat: sabotage the guards on demand, and sabotage the saboteur first"
```

---

## Task 3: The catalogue of defects that still have no guard

**Files:**
- Create: `portable/templates/defect-record.md`
- Create: `docs/superpowers/defect-records/` with five seeded records
- Modify: `skills/charter-workflow/SKILL.md` ×3, `portable/templates/handoff.md`
- Modify: `scripts/validate_kit.py`
- Test: `tests/test_workflow_contract.py`

**Interfaces:**
- Consumes: `defect_records()` from Task 2 and the `Guard: \`none-yet\`` spelling it searches for.
- Produces: the closure clause and the `report` output that Task 4 relies on.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_workflow_contract.py`, reusing that module's existing content-discovery helper (glob `portable/**`, `targets/**`, `skills/**`; do not enumerate paths):

```python
def test_leaf_closure_records_unguarded_defects(self):
    carriers = discover_carriers("Guard: `none-yet`")
    self.assertGreaterEqual(len(carriers), 3,
                            "the closure clause must live in every SKILL.md copy")
    for text in carriers:
        self.assertIn("caught later than it could have been", text)
        self.assertIn("no model attribution is inferred", text)
```

- [ ] **Step 2: Run to verify it fails**

Run: `python -m unittest tests.test_workflow_contract -q`
Expected: FAIL — zero carriers contain `Guard: \`none-yet\``.

- [ ] **Step 3: Write the record template**

```markdown
# Defect Record

> Copy to `docs/superpowers/defect-records/YYYY-MM-DD-<slug>.md`. One late-caught
> defect per file. A record is evidence that a check failed to fail, not that a
> person was careless.

- Pattern: `vacuous-verification | stale-evidence | assumed-not-verified | silent-degradation | scope-drift`
- Slug: `<kebab-case>`
- Detected-by: `self-review | independent-review | live-run | user | downstream-failure`
- Guard: `none-yet | <gate id from portable/gates.json>`
- Host-state: `<phase | preset | unlocked-tool note, or unknown>`

## What was believed, and what was true

<one paragraph. What was claimed, what was actually the case, and what surfaced it.>

## Why the existing checks could not see it

<the mechanism. "The assertion's comprehension had already filtered out the value it
 tested" is a mechanism. "Not careful enough" is not.>

## Gate

<for a new gate: the registry id once it is added. For none-yet: what an
 executable gate would have to observe, or why none is possible.>
```

- [ ] **Step 4: Seed the five records from this session**

Create the five files, each with a real mechanism and a `Guard:` value that is honest about status:

| slug | pattern | Guard |
|---|---|---|
| `2026-09-15-tautological-inject-assertion` | vacuous-verification | `review-timeout-constants-are-arithmetic` — no. Use `none-yet` unless a registry entry pins *this* defect |
| `2026-09-15-vacuous-mirror-hash` | vacuous-verification | `none-yet` |
| `2026-09-15-contradicting-screenshots` | stale-evidence | `none-yet` |
| `2026-09-15-retracted-promise-in-tool-description` | stale-evidence | `no-retracted-empty-review-promise-anywhere` |
| `2026-09-15-assumed-do-not-do-existed` | assumed-not-verified | `none-yet` |

Fill `Detected-by` truthfully: four are `independent-review`, one is `self-review` where the self-review was the *second* pass — say so in the body rather than flattering the record. Where the defect had a model attached, record it in `Host-state:` **with the confound named**, since this session changed model three times while its phase and unlocked tool set also changed.

Then:

```bash
python scripts/sabotage_check.py report
```
Expected: `defect records: 5, without a gate: 3` (or more). **That number is the deliverable.** A catalogue that reports zero unguarded defects on its first run is suspicious: it would mean every defect already has a gate, which is the claim that just failed four times.

- [ ] **Step 5: Write the closure clause**

Into all three hand-edited `SKILL.md` copies, beside the existing review-degradation and capability-status wording, and deliberately cheap enough that no leaf is ever tempted to skip it:

> At leaf closure: if anything in this leaf was **caught later than it could have been** — a review finding, a live run contradicting a claim, a check that passed while what it asserted was false — copy `defect-record.md` into `docs/superpowers/defect-records/` with one defect per file. Set `Guard:` to a `portable/gates.json` id only when that gate exists and `python scripts/sabotage_check.py run` reports it biting; otherwise leave the field written exactly as `- Guard: `none-yet`.` Report the count of none-yet records in the handoff. Do not attribute a defect to a model: the harness state changed alongside the model, so **no model attribution is inferred here**. Record nothing that an existing gate already catches.

In `portable/templates/handoff.md`, beside the capability-status line:

```markdown
- Defects caught late this session: `<count>` — without a guard yet: `<count>`
```

- [ ] **Step 6: Validator entry, regenerate, full gates, commit**

```python
"portable/templates/defect-record.md": (
    "none-yet", "Detected-by", "could not see it", "not that a person was careless",
),
```

```bash
python -m unittest discover -s tests -q
python scripts/validate_kit.py .
python scripts/build_codex_plugin.py && python scripts/build_zcode_plugin.py && python scripts/build_dsh_plugin.py
python scripts/build_codex_plugin.py --check && python scripts/build_zcode_plugin.py --check && python scripts/build_dsh_plugin.py --check
python scripts/sabotage_check.py run
sha256sum skills/charter-workflow/SKILL.md targets/*/skills/charter-workflow/SKILL.md plugins/*/skills/charter-workflow/SKILL.md
git add -A && git commit -m "feat: catalogue the defects still without a guard, and open the ledger at closure"
```
Expected: suite green; validator PASS; three `--check` PASS; every gate `bit`; one `SKILL.md` digest; clean tree.

---

## Task 4: Write down the half that is deferred, with its entry conditions

**Files:**
- Create: `docs/superpowers/specs/2026-09-15-deferred-self-evolution.md`
- Test: `tests/test_workflow_contract.py`

**Interfaces:**
- Consumes: nothing.
- Produces: a checklist that a future proposal must satisfy, so the deferral is a position with reasons rather than a wish.

- [ ] **Step 1: Write the failing test**

```python
def test_deferred_evolution_records_its_blockers(self):
    path = ROOT / "docs/superpowers/specs/2026-09-15-deferred-self-evolution.md"
    text = path.read_text(encoding="utf-8")
    for required in ("hold-out", "oracle", "blast radius", "budget", "NOT built"):
        self.assertIn(required, text, f"deferral spec omits {required}")
```

- [ ] **Step 2: Run to verify it fails**

Run: `python -m unittest tests.test_workflow_contract -q`
Expected: FAIL — the file does not exist.

- [ ] **Step 3: Write it**

State plainly that the A/B-replay promotion loop **is NOT built**, and give each blocker an entry condition a future attempt must satisfy:

1. **Hold-out.** A rule derived from a case cannot be validated on that case. Entry condition: a corpus of late-caught defects with at least half never used during rule design — the `defect-records/` catalogue is its feeder, which is why Task 3 ships and the replay does not.
2. **Oracle.** "Did the new agent catch it?" has no non-circular judge: a model judge reintroduces unverified judgement; a keyword check is a vacuous gate an agent can satisfy without understanding. Entry condition: a mechanical outcome the replay can observe, which today exists only for executable gates.
3. **Blast radius.** Automatic inheritance writes into `portable/`, which fans out to three host distributions plus the filesystem skill copy the host actually serves. That chain drifted three times in the session that motivated this plan, while a human was watching. Entry condition: the sync chain made self-verifying (a gate in `gates.json` that fails when the served copy and the build differ).
4. **Budget.** A single replay is 2 arms × repeated runs, because the same model on the same prompt does not reproduce; at this session's observed scale that is tens of full-size review calls per candidate rule, bounded by the timeout the review tool now enforces. Entry condition: a per-candidate call budget and a measured per-run cost, agreed before the first experiment.
5. **Attribution.** A model tag is confounded by phase, preset, and unlocked tools in the same session. Entry condition: records carry host state, and a pattern's records span at least two host states before they are called cross-model.
6. **Selection pressure on the catalogue itself.** If "recorded defects" is the visible metric, the cheap trivia gets written and the structural problems that no test can express — a route that hangs for 600 seconds — never do. Entry condition: the `none-yet` count is the metric, not the record count, so a catalogue full of trivia shows as failure.

- [ ] **Step 4: Run to verify it passes, regenerate, commit**

```bash
python -m unittest tests.test_workflow_contract -q
python scripts/validate_kit.py .
git add docs/superpowers/specs/2026-09-15-deferred-self-evolution.md tests/test_workflow_contract.py
git commit -m "docs: record the deferred evolution loop with the conditions to unblock it"
```

---

## Out of scope (deliberately)

- Any automatic editing of rules, clauses, templates, or skill text. Deferred with entry conditions, not dropped: its oracle was the part that had no honest answer.
- Cross-model or cross-person attribution. One author's task history cannot separate "process hole" from "this person's habits"; the field is recorded, nothing is inferred from it.
- A dashboard, embeddings, clustering, or similarity search. The taxonomy is hand-curated and small; automation here would launder the same false-confidence failure into a nicer interface.
- Running `sabotage_check.py` inside leaf closure. It is a maintenance command; making it a per-leaf tax was one of the costs this plan rejected.

## What this plan is actually for

One sentence, to keep every later edit honest: **it does not make charter-kit better by itself; it makes charter-kit unable to hide a guard that stopped working.** Every piece of value claimed in the earlier draft rested on an oracle that did not exist. This one's oracle is a non-zero exit code.
