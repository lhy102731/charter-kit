# Lesson Ledger Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give charter-kit a cross-project, model-tagged record of late-caught defects, and a threshold rule that turns a recurring pattern into a proposed process change — without ever letting a machine edit the rules by itself.

**Architecture:** One global append-only ledger of one-file-per-occidence records under a fixed home directory, parsed and summarised by a pure-stdlib Python script shipped with the skill. A `SKILL.md` closure step makes every leaf write to it, so the ledger is fed by the workflow rather than by intention. Promotion is a *report*, not a write: crossing a threshold prints a candidate for human review and names the detectable failure that justifies it.

**Tech Stack:** Markdown templates, Python 3 standard library only (`argparse`, `pathlib`, `re`, `datetime`), `unittest`. No Node toolchain, no third-party packages — the kit's existing discipline.

**Spec:** `docs/superpowers/specs/2026-09-15-lesson-ledger-design.md` (written in Task 1 from the decisions recorded below).

## Global Constraints

- Pure standard library. No dependency may be added to `dependencies.json` for this feature.
- `portable/` is shipped wholesale by every builder (`PACKAGE_ROOT_ITEMS` contains `"portable"`, `scripts/build_codex_plugin.py:31`, applied at `:413`), so new files under `portable/templates/` and `portable/references/` need **no builder change**.
- `SKILL.md` has three hand-edited copies (`skills/`, `targets/codex/skills/charter-workflow/`, `targets/zcode/skills/charter-workflow/`) that must stay byte-identical to the three regenerated copies; builders run codex → zcode → dsh, then `python scripts/validate_kit.py .`.
- `targets/dsh/` gains no `GENERATED.md`. `plugins/**` and root `skills/**` are never hand-edited.
- Every file added under `portable/` gains a `REQUIRED_FILES` entry in `scripts/validate_kit.py` in the same commit, following the existing per-template content-tuple pattern (`validate_kit.py:39,53,65,72,82,90`).
- Ledger path default: `{home}/.charter/lessons/`. Overridable by `--ledger` and by the `CHARTER_LESSONS_DIR` environment variable. A record is never rewritten after creation; promotion status changes are appended as a new `Promotion:` line, and the file's `Updated:` field moves.
- Record filename: `YYYY-MM-DD-<slug>.md`, `<slug>` matching `[a-z0-9][a-z0-9-]{1,60}`.
- Model identity is recorded **per observation**, never per session: this session changed model three times mid-task, so a session-level tag would mis-attribute.
- `pattern` is a closed enum. `unknown` is permitted only with a non-empty `Why-unknown:` field.
- A promotion candidate must name a **detectable failure** and the **gate** that catches it. Without both it is rejected, not escalated.

---

## File Structure

| Path | Responsibility |
|---|---|
| Create `portable/templates/lesson.md` | The record shape: fields, the enum, what each field is for. Contains no tooling. |
| Create `portable/references/lesson-ledger.md` | The rules: what qualifies as a record, the taxonomy, thresholds, the promotion gate, the anti-patterns (including why an unhooked ledger dies). |
| Create `scripts/lesson_ledger.py` **then relocate** to the shipped skill scripts directory resolved in Task 3 Step 1 | `new` scaffolds a record; `index` writes `INDEX.md`; `--promotions` prints threshold-crossing candidates. |
| Modify `skills/charter-workflow/SKILL.md` ×3 | Leaf-closure hook: write records for late-caught defects, run `--promotions`, surface candidates. |
| Modify `portable/templates/handoff.md` | Carry the session's new-lesson count and any unresolved promotion candidate across sessions. |
| Modify `scripts/validate_kit.py` | `REQUIRED_FILES` entries for the two new portable files. |
| Modify both `README.md` editions | One paragraph naming the ledger as a kit layer. |
| Create `tests/test_lesson_ledger.py` | Unit coverage for scaffolding, parsing, index, thresholds, and rejection cases. |
| Create `docs/superpowers/specs/2026-09-15-lesson-ledger-design.md` | Design basis, distilled from this conversation. |

---

## Task 1: Design basis and record template

**Files:**
- Create: `docs/superpowers/specs/2026-09-15-lesson-ledger-design.md`
- Create: `portable/templates/lesson.md`
- Test: `tests/test_lesson_ledger.py` (created here with one test; grown in Task 3)

**Interfaces:**
- Consumes: nothing.
- Produces: the field names `pattern`, `models`, `task-types`, `detection`, `prevention`, `gate`, `evidence`, `promoted-to`, `created`, `updated` — every later task and the parser use these spellings verbatim.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_lesson_ledger.py
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "portable" / "templates" / "lesson.md"

REQUIRED_FIELDS = (
    "Pattern:", "Models:", "Task-Types:", "Detection:",
    "Prevention:", "Gate:", "Evidence:", "Promoted-To:",
    "Created:", "Updated:",
)
PATTERNS = (
    "vacuous-verification", "stale-evidence", "assumed-not-verified",
    "silent-degradation", "scope-drift", "unknown",
)


class LessonTemplate(unittest.TestCase):
    def test_template_declares_every_field(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        for field in REQUIRED_FIELDS:
            self.assertIn(field, text, f"lesson template lacks {field}")

    def test_template_enumerates_the_closed_pattern_set(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        for pattern in PATTERNS:
            self.assertIn(pattern, text, f"lesson template omits {pattern}")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_lesson_ledger -q`
Expected: FAIL — `lesson template lacks Pattern:` (the template does not exist yet; `read_text` raises `FileNotFoundError`, which is also a failure).

- [ ] **Step 3: Write the spec**

`docs/superpowers/specs/2026-09-15-lesson-ledger-design.md` records, in this order: the goal (separate model-specific slips from process holes by recurrence across models); the five seed patterns with the real occurrence that named each; the thresholds; the human-only promotion rule; the "no detectable failure, no promotion" gate; and the two failure modes this design must not repeat — an unhooked ledger (evidence: `PA_Agent/experience/` is five empty channel directories of `.gitkeep`) and impression-fed records (evidence: only late-caught defects counted; a library fed by what a model happens to notice cannot see the class it exists to catch).

- [ ] **Step 4: Write the template**

```markdown
# Lesson Record

> Copy to `<ledger>/YYYY-MM-DD-<slug>.md`. One occurrence per file. Never rewrite a
> record's observed facts; append a `Correction:` line instead. A record is evidence
> that something was caught late, not that somebody was wrong.

## Identity

- Pattern: `vacuous-verification | stale-evidence | assumed-not-verified | silent-degradation | scope-drift | unknown`
- Slug: `<kebab-case-handle>`
- Created: `<YYYY-MM-DD>`
- Updated: `<YYYY-MM-DD>`
- Promoted-To: `none | <path to the rule, gate, or test that now prevents it>`

## Observation

- Models: `<provider/model>` — one entry per model actually running when the defect
  was made. A session may change model mid-task; never credit the session.
- Task-Types: `code-review | docs | build-verify | live-browser | planning | ops`
- Project: `<name or path>`
- Detection: how it was actually caught — `self-review | independent-review |
  live-run | user | downstream-failure`. `self-review` on a defect that survived
  self-review is a detection of the *late* catch, and still counts.
- Summary: `<one paragraph. What was believed, what was true, how the gap surfaced.>`

## Prevention

- Prevention: `<the rule or action that would have caught it earlier>`
- Gate: `<the concrete check that fails when it recurs: a test name, a validator rule,
  a probe that must go red. Empty is not allowed for a promotion candidate.>`
- Evidence: `<paths to the artifact that proves the occurrence: a diff, a JSON record,
  a log section>`

## Rules

- `unknown` requires a non-empty `Why-unknown:` line; without it the record is invalid.
- A pattern is a *class of failure*, not a file name. Two occurrences in different
  subsystems that share one mechanism are one pattern.
- Prose that describes a defect without naming a gate is a note, not a lesson.
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python -m unittest tests.test_lesson_ledger -q`
Expected: PASS (2 tests).

- [ ] **Step 6: Regenerate, validate, commit**

```bash
python scripts/build_codex_plugin.py && python scripts/build_zcode_plugin.py && python scripts/build_dsh_plugin.py
python scripts/validate_kit.py .
git add docs/superpowers/specs/2026-09-15-lesson-ledger-design.md portable/templates/lesson.md tests/test_lesson_ledger.py plugins/ skills/
git commit -m "feat: define the lesson record and its closed pattern taxonomy"
```

Expected: validator `PASS`; `git status --porcelain` empty after the commit.

---

## Task 2: The ledger rules reference

**Files:**
- Create: `portable/references/lesson-ledger.md`
- Modify: `scripts/validate_kit.py` (add two `REQUIRED_FILES` entries)

**Interfaces:**
- Consumes: the field spellings and enum from Task 1.
- Produces: the thresholds Task 3 implements verbatim — `OCCURRENCES_FOR_CANDIDATE = 2`, `OCCURRENCES_FOR_PROMOTION = 3`, `MIN_TASK_TYPES = 2`.

- [ ] **Step 1: Write the rules reference**

Content, in this order, each stated as an operation the workflow performs rather than advice:

1. **What qualifies.** Only a defect that was caught *later than it could have been* — an independent review finding, a live run contradicting a claim, a user discovering what a check should have shown. Not: a typo, a preference, a hypothetical risk.
2. **Why impression-fed ledgers are worthless.** The records must come from the review path, because the class this ledger exists to catch is precisely "the author believed it verified". Self-reporting cannot see that.
3. **Thresholds.** Occurrences counted per `pattern`. `>= 2` distinct models on one pattern → *candidate*. `>= 3` occurrences **and** `>= 2` task types **and** `>= 2` models → *promotion candidate*. Fewer than three occurrences never promotes regardless of how confident the pattern feels.
4. **The confounds that must be checked before escalating.** Task-difficulty skew (one model may have been given all the hard work) and sample size. A pattern whose records all come from one task type is not a process hole, it is a domain gap.
5. **The promotion gate.** A candidate may be written into a rule, template, test, or skill clause only when it names (a) a failure that is *detectable*, and (b) the gate that fails on it. If either is missing, the record stays open and says so.
6. **Human-only writes.** Promotion is a printed proposal. Nothing in this flow edits `SKILL.md`, a template, or a test automatically. Justification: in the session that produced this design, three controller-authored conclusions were overturned by review (a timeout bound computed against one attempt instead of two, a provider-priority attribution, and a "shipped but never used" claim) and one was overturned by the author's own later scan. A pipeline that auto-absorbs conclusions inherits that error rate.
7. **Rule-count ceiling.** Each accepted promotion must name a clause it replaces or the ledger becomes prompt bloat, which measurably degrades the thing it was meant to improve.
8. **Seeds.** The five patterns with their real origins, including `vacuous-verification` — "a check that cannot fail reports a pass that means nothing", from four occurrences in one session (an `assertNotIn` over a comprehension that filtered the tested value out; a mirror-hash command over 0 files; screenshots contradicting their own JSON; a promise surviving in a model-facing string after being retracted everywhere else).

- [ ] **Step 2: Add the validator entries**

Follow the existing tuple style at `validate_kit.py:39-95`. Require the reference to name its thresholds and its gate vocabulary:

```python
"portable/references/lesson-ledger.md": (
    "candidate",
    "promotion candidate",
    "detectable",
    "Human-only",
    "task type",
),
"portable/templates/lesson.md": (
    "Pattern:",
    "Gate:",
    "unknown",
    "not that somebody was wrong",
),
```

- [ ] **Step 3: Run the validator to verify it fails, then passes**

Run: `python scripts/validate_kit.py .`
Expected before writing the file: FAIL naming `portable/references/lesson-ledger.md` as missing. After writing it: `PASS`.

- [ ] **Step 4: Regenerate and commit**

```bash
python scripts/build_codex_plugin.py && python scripts/build_zcode_plugin.py && python scripts/build_dsh_plugin.py
python scripts/validate_kit.py . && git add -A && git commit -m "feat: state the ledger rules and their promotion gate"
```

---

## Task 3: The ledger script

**Files:**
- Create: the shipped skill scripts directory, resolved in Step 1 — record the answer in the report before writing code
- Test: `tests/test_lesson_ledger.py`

**Interfaces:**
- Consumes: field spellings from Task 1; thresholds from Task 2.
- Produces: `lesson_ledger.py new|index|promotions`, and `parse_record(path) -> dict`, `summarize(records) -> dict` used by Task 4 and the tests.

- [ ] **Step 1: Find where shipped scripts actually come from**

```bash
grep -rn "check_dependencies.py" scripts/build_codex_plugin.py scripts/validate_kit.py | head
```

Expected: the source path for the two scripts the built skill already ships. Write records and tests to that directory — **not** the repository's own `scripts/`, which is repo tooling and is not distributed. If `portable/` has no scripts tree and the builder copies skill scripts from somewhere else, follow that mechanism exactly and record it; do not add a new one.

- [ ] **Step 2: Write the failing tests**

```python
class LedgerScript(unittest.TestCase):
    def tmp_ledger(self, *bodies):
        # helper: build a ledger dir from record bodies, return Path
        ...

    def test_parses_fields_and_lists(self):
        body = ("# Lesson Record\n\n- Pattern: `vacuous-verification`\n"
                "- Models: `p/one`, `p/two`\n- Task-Types: `code-review`, `docs`\n"
                "- Detection: independent-review\n- Gate: `tests/test_x.py`\n"
                "- Promoted-To: `none`\n")
        path = self.tmp_ledger(body) / "2026-09-15-a.md"
        rec = lesson_ledger.parse_record(path)
        self.assertEqual(rec["pattern"], "vacuous-verification")
        self.assertEqual(rec["models"], ["p/one", "p/two"])
        self.assertEqual(rec["gate"], "tests/test_x.py")

    def test_two_distinct_models_makes_a_candidate(self):
        s = lesson_ledger.summarize([
            {"pattern": "p", "models": ["a/1"], "task_types": ["code-review"]},
            {"pattern": "p", "models": ["b/2"], "task_types": ["docs"]},
        ])
        self.assertEqual(s["candidates"]["p"]["models"], 2)

    def test_three_occurrences_two_types_two_models_makes_a_promotion(self):
        s = lesson_ledger.summarize([
            {"pattern": "p", "models": ["a/1"], "task_types": ["code-review"]},
            {"pattern": "p", "models": ["a/1"], "task_types": ["docs"]},
            {"pattern": "p", "models": ["b/2"], "task_types": ["docs"]},
        ])
        self.assertIn("p", s["promotions"])

    def test_promotion_needs_a_gate_on_every_record(self):
        s = lesson_ledger.summarize([
            {"pattern": "p", "models": ["a/1"], "task_types": ["code-review"], "gate": ""},
            {"pattern": "p", "models": ["a/1"], "task_types": ["docs"], "gate": ""},
            {"pattern": "p", "models": ["b/2"], "task_types": ["live-browser"], "gate": ""},
        ])
        self.assertNotIn("p", s["promotions"])
        self.assertIn("p", s["blocked"])

    def test_unknown_pattern_without_why_is_invalid(self):
        p = self.tmp_ledger("- Pattern: `unknown`\n") / "2026-09-15-b.md"
        self.assertFalse(lesson_ledger.parse_record(p).get("valid"))

    def test_index_is_regenerated_not_hand_maintained(self):
        out = lesson_ledger.render_index([
            {"pattern": "vacuous-verification", "models": ["a/1", "b/2"],
             "task_types": ["code-review"], "slug": "x", "valid": True, "gate": "g"}])
        self.assertIn("vacuous-verification", out)
        self.assertIn("models=2", out)
```

- [ ] **Step 3: Run to verify they fail**

Run: `python -m unittest tests.test_lesson_ledger -q`
Expected: FAIL — no module named `lesson_ledger`.

- [ ] **Step 4: Write the script**

```python
#!/usr/bin/env python3
"""Summarise the charter-kit lesson ledger and propose promotions.

Read-only except for `new` (scaffolds one file) and `index` (writes INDEX.md, which
is generated and never hand-edited). Promotion is a printed proposal: this tool does
not edit a rule, template, test, or skill clause.
"""
from __future__ import annotations
import argparse, os, re, sys
from collections import defaultdict
from datetime import date
from pathlib import Path

OCCURRENCES_FOR_CANDIDATE = 2
OCCURRENCES_FOR_PROMOTION = 3
MIN_TASK_TYPES = 2
DEFAULT_LEDGER = Path.home() / ".charter" / "lessons"
PATTERNS = {"vacuous-verification", "stale-evidence", "assumed-not-verified",
            "silent-degradation", "scope-drift", "unknown"}

LIST_FIELDS = {"Models": "models", "Task-Types": "task_types", "Evidence": "evidence"}
SCALAR_FIELDS = {"Pattern": "pattern", "Slug": "slug", "Detection": "detection",
                 "Gate": "gate", "Prevention": "prevention",
                 "Promoted-To": "promoted_to", "Created": "created", "Updated": "updated"}


def _values(raw: str) -> list[str]:
    return [v for v in (p.strip().strip("`").strip() for p in raw.split(",")) if v]


def parse_record(path: Path) -> dict:
    rec: dict = {"path": str(path), "valid": True, "gate": "", "models": [],
                 "task_types": [], "pattern": "", "slug": path.stem}
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^-\s+([A-Za-z-]+):\s*(.*)$", line.strip())
        if not m:
            continue
        key, raw = m.group(1), m.group(2).strip()
        if key in SCALAR_FIELDS:
            rec[SCALAR_FIELDS[key]] = raw.strip("`").strip() or rec.get(SCALAR_FIELDS[key], "")
        elif key in LIST_FIELDS:
            rec[LIST_FIELDS[key]] = _values(raw)
    if rec["pattern"] not in PATTERNS:
        rec["valid"] = False
        rec["invalid_reason"] = f"unknown pattern {rec['pattern']!r}"
    elif rec["pattern"] == "unknown" and "Why-unknown" not in path.read_text(encoding="utf-8"):
        rec["valid"] = False
        rec["invalid_reason"] = "pattern unknown without Why-unknown"
    return rec


def load(ledger: Path) -> list[dict]:
    if not ledger.is_dir():
        return []
    return [parse_record(p) for p in sorted(ledger.glob("*.md")) if p.name != "INDEX.md"]


def summarize(records: list[dict]) -> dict:
    by: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        if r.get("valid"):
            by[r["pattern"]].append(r)
    candidates, promotions, blocked, problems = {}, {}, {}, {}
    for pattern, group in by.items():
        models = {m for r in group for m in r["models"]}
        types_ = {t for r in group for t in r["task_types"]}
        stats = {"occurrences": len(group), "models": len(models), "task_types": len(types_)}
        if stats["occurrences"] >= OCCURRENCES_FOR_CANDIDATE and stats["models"] >= 2:
            candidates[pattern] = stats
        ready = (stats["occurrences"] >= OCCURRENCES_FOR_PROMOTION
                 and stats["task_types"] >= MIN_TASK_TYPES and stats["models"] >= 2)
        if not ready:
            continue
        ungated = [r["slug"] for r in group if not r["gate"]]
        if ungated:
            blocked[pattern] = {"need_gate": ungated}
            problems[pattern] = "promotion blocked: records without a named gate"
            continue
        promotions[pattern] = stats
    return {"candidates": candidates, "promotions": promotions,
            "blocked": blocked, "problems": problems, "patterns": dict(by)}


def render_index(records: list[dict]) -> str:
    s = summarize(records)
    lines = ["# Lesson Ledger Index", "",
             "<!-- Generated by lesson_ledger.py index. Do not edit by hand. -->", "",
             f"Records: {sum(len(g) for g in s['patterns'].values())}  "
             f"Patterns: {len(s['patterns'])}", ""]
    for pattern, group in sorted(s["patterns"].items()):
        models = {m for r in group for m in r["models"]}
        types_ = {t for r in group for t in r["task_types"]}
        lines.append(f"- `{pattern}` — occurrences={len(group)} models={len(models)} "
                     f"task-types={len(types_)}")
        for r in group:
            lines.append(f"  - [{r['slug']}]({Path(r['path']).name}) gate="
                         f"{'yes' if r['gate'] else 'MISSING'}")
    for pattern, note in s["problems"].items():
        lines.append(f"- **{pattern}**: {note}")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("command", choices=("new", "index", "promotions"))
    ap.add_argument("--ledger", type=Path, default=Path(
        os.environ.get("CHARTER_LESSONS_DIR", DEFAULT_LEDGER)))
    ap.add_argument("--pattern"); ap.add_argument("--slug"); ap.add_argument("--model")
    ap.add_argument("--task-type"); ap.add_argument("--gate", default="")
    ap.add_argument("--summary", default="")
    args = ap.parse_args(argv)
    records = load(args.ledger)
    if args.command == "index":
        args.ledger.mkdir(parents=True, exist_ok=True)
        (args.ledger / "INDEX.md").write_text(render_index(records), encoding="utf-8")
        print(f"wrote {args.ledger / 'INDEX.md'}")
        return 0
    if args.command == "new":
        missing = [f for f in ("pattern", "slug", "model", "task_type")
                   if not getattr(args, f)]
        if missing:
            print(f"new requires: {', '.join(missing)}", file=sys.stderr)
            return 2
        if args.pattern not in PATTERNS:
            print(f"pattern must be one of {sorted(PATTERNS)}", file=sys.stderr)
            return 2
        args.ledger.mkdir(parents=True, exist_ok=True)
        today = date.today().isoformat()
        path = args.ledger / f"{today}-{args.slug}.md"
        if path.exists():
            print(f"refusing to overwrite {path}", file=sys.stderr)
            return 2
        path.write_text(
            "# Lesson Record\n\n"
            f"- Pattern: `{args.pattern}`\n- Slug: `{args.slug}`\n"
            f"- Created: `{today}`\n- Updated: `{today}`\n- Promoted-To: `none`\n\n"
            f"- Models: `{args.model}`\n- Task-Types: `{args.task_type}`\n"
            "- Detection: ``\n"
            f"- Summary: {args.summary}\n\n"
            "- Prevention: ``\n"
            f"- Gate: {args.gate}\n- Evidence: ``\n", encoding="utf-8")
        print(path)
        return 0
    s = summarize(records)
    if not s["candidates"] and not s["blocked"]:
        print("no promotion candidate: every pattern is below "
              f"{OCCURRENCES_FOR_CANDIDATE} models")
    for pattern, stats in sorted(s["candidates"].items()):
        tier = "PROMOTION" if pattern in s["promotions"] else "candidate"
        print(f"{tier}: {pattern} occurrences={stats['occurrences']} "
              f"models={stats['models']} task-types={stats['task_types']}")
    for pattern, info in sorted(s["blocked"].items()):
        print(f"blocked: {pattern} records without a gate: {', '.join(info['need_gate'])}")
    print("Promotions are proposals. A human edits the rule, and each edit must "
          "name a clause it replaces.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Run the tests, then prove the script is not vacuous**

```bash
python -m unittest tests.test_lesson_ledger -q          # expect: PASS
```

Then the sabotage check the ledger itself demands of every check: run `index` against a fixture whose records all have an empty `Gate:` and confirm the output prints `MISSING` rather than a clean summary. A generator that reports success on an unusable record is the exact defect this feature records.

- [ ] **Step 6: Regenerate and commit**

```bash
python scripts/build_codex_plugin.py && python scripts/build_zcode_plugin.py && python scripts/build_dsh_plugin.py
python scripts/validate_kit.py . && git add -A && git commit -m "feat: add the lesson ledger script with human-only promotion"
```

---

## Task 4: Wire the hook into the workflow

**Files:**
- Modify: the three hand-edited `SKILL.md` copies
- Modify: `portable/templates/handoff.md`
- Test: `tests/test_workflow_contract.py`

**Interfaces:**
- Consumes: `lesson_ledger.py` commands from Task 3.
- Produces: the closure-time rule every future leaf executes — this is the load-bearing part; Tasks 1-3 without it reproduce the empty `experience/` directories.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_workflow_contract.py`, following the discovery pattern already established there (glob `portable/**`, `targets/**`, `skills/**` by content, with a floor assertion so a shrunken discovery fails — do not enumerate paths):

```python
def test_leaf_closure_opens_the_lesson_ledger(self):
    carriers = discover_carriers("lesson_ledger.py promotions")
    self.assertGreaterEqual(len(carriers), 3, "the ledger hook must be in every SKILL.md copy")
    for text in carriers:
        self.assertIn("caught later than it could have been", text)
        self.assertIn("Promotions are proposals", text)
        self.assertIn("per model actually running", text)
```

- [ ] **Step 2: Run to verify it fails**

Run: `python -m unittest tests.test_workflow_contract -q`
Expected: FAIL — no carrier contains `lesson_ledger.py promotions`.

- [ ] **Step 3: Write the closure clause**

Into all three hand-edited `SKILL.md` copies, as a step at leaf closure (the same place that already records `REVIEW_MODEL` and capability status), worded so it cannot be satisfied by intention:

> At leaf closure, before the leaf is marked complete: write one lesson record for each defect in this leaf that was **caught later than it could have been** — a review finding, a live run contradicting a claim, a check that passed while the thing it asserted was false. Do not record preferences, hypotheticals, or anything already prevented by an existing gate. Tag `Models:` with the **model actually running at the moment of each observation**, not the model that opened the session; a session may change model, and a session-level tag credits the wrong party. Then run `python <skill>/scripts/lesson_ledger.py promotions`. **Promotions are proposals**: report any candidate to the user with its occurrence, model, and task-type counts, and change no rule, template, test, or clause in this leaf. A pattern whose records lack a `Gate:` is blocked, and say so rather than promoting it.

- [ ] **Step 4: Write the handoff line**

In `portable/templates/handoff.md`, beside the existing capability-status line, add:

```markdown
- New lessons this session: `<count>` — patterns: `<list or none>`
- Open promotion candidate: `<pattern, counts, and the gate it still lacks, or none>`
```

so a candidate survives a session boundary instead of dying with the context that found it.

- [ ] **Step 5: Run to verify it passes**

Run: `python -m unittest tests.test_workflow_contract -q`
Expected: PASS. Then regenerate and confirm the six `SKILL.md` copies share one hash:

```bash
python scripts/build_codex_plugin.py && python scripts/build_zcode_plugin.py && python scripts/build_dsh_plugin.py
sha256sum skills/charter-workflow/SKILL.md targets/codex/skills/charter-workflow/SKILL.md \
          targets/zcode/skills/charter-workflow/SKILL.md plugins/*/skills/charter-workflow/SKILL.md
python scripts/validate_kit.py .
```
Expected: one digest, validator `PASS`.

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "feat: open the lesson ledger at leaf closure and carry candidates across sessions"
```

---

## Task 5: Seed the real records and document the layer

**Files:**
- Create: five records in the live ledger via `lesson_ledger.py new` (not committed to the repository — the ledger is a user-level store)
- Modify: both `README.md` editions

**Interfaces:**
- Consumes: everything above.
- Produces: the first real distribution, and the documentation that makes the layer discoverable.

- [ ] **Step 1: Scaffold the five occurrences through the tool, not by hand**

The five seeds are the defects from the review-model work, each with the artifact path that proves it: `vacuous-verification` ×4 (the `assertNotIn` whose comprehension filtered out the tested value; the mirror-hash command over 0 files; the screenshot pair contradicting its own JSON; the retracted promise surviving in the model-facing tool description) and `assumed-not-verified` ×1 (a handoff `Do-not-do` clause asserted from a report quote and then measured as zero occurrences in 35 scanned files — caught by the author's own later scan, which is itself the point: it survived self-review once).

Run `lesson_ledger.py new` once per occurrence, filling `Models:` with the model that was actually running — this session ran at least three. Then `lesson_ledger.py index` and `lesson_ledger.py promotions`.

- [ ] **Step 2: Read the output back and record what it says**

Expected on five records: `vacuous-verification` reaches *candidate* at minimum (≥2 models) and should reach *promotion* only if its records genuinely span ≥2 task types and every one names a gate. **If it promotes on the first run, be suspicious** — four records from one session, one task family, is precisely the difficulty-skew case the rules warn about. Report the actual numbers; do not tune thresholds to make a story come true.

- [ ] **Step 3: Write the README paragraph, both editions**

Name it as a kit layer, state the three properties that make it different from the empty directory precedent: append-only records with a closed taxonomy, thresholds that require cross-model recurrence, and promotion that a human performs. Say plainly that the ledger lives outside the project and that a record without a `Gate:` cannot promote.

- [ ] **Step 4: Full gate, then commit**

```bash
python -m unittest discover -s tests -q
python scripts/validate_kit.py .
python scripts/build_codex_plugin.py --check && python scripts/build_zcode_plugin.py --check && python scripts/build_dsh_plugin.py --check
git status --porcelain          # expect: empty
git add -A && git commit -m "docs: present the lesson ledger and seed it from the review-model work"
```

Note: the last `git add -A`/`commit` pair must be run **only after** the tree is clean from the `--check` builds, and the seed records in the user-level ledger are **not** repository content — `git status` will not see them, exactly as it could not see the undeleted screenshots in the last review round. Verify their existence by listing the ledger directory, not by trusting a clean tree.

---

## Out of scope (deliberately)

- Any dashboard, clustering, embedding, or "auto-detect similar lessons". The taxonomy is hand-curated; premature automation would launder the same false-confidence failure into a nicer UI.
- Automatic rule editing. Blocked by design at the tool level, not by convention.
- Cross-machine sync of the ledger.
- Feeding it from CI statistics. A review finding is a *human or independent-agent judgement about a claim*, which is the signal; a test failure is already handled by the test.
