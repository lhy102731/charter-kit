# Lessons Self-Evolution Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give charter-kit a bounded, project-local lessons layer: pitfalls are distilled from existing leaf records at closure, read on resume, cited at decision points, reported at existing report moments, and promoted into the kit only by a user-confirmed hand edit.

**Architecture:** Two new portable files (a template and a rules reference) plus text edits to the entry documents (command, SKILL, prompts, charter, README, agentpack) and validator registration. No new scripts, no builder changes — the three builders copy `portable/` wholesale (`PACKAGE_ROOT_ITEMS`), so new files ship automatically once the mirror trees are refreshed. Every mechanism mirrors the existing `handoff.md` pattern: read-if-present, bounded size, archive with promotion sweep.

**Tech Stack:** Markdown templates and references, Python 3 standard library for the validator and tests (`unittest` style, run through `pytest`). No new dependencies, no Node toolchain.

**Spec:** `docs/superpowers/specs/2026-09-15-lessons-self-evolution-design.md`

## Global Constraints

- Pure standard library. Nothing in this plan may add a dependency to `dependencies.json`.
- Hand-edited sources only: `portable/`, `targets/codex/skills/charter-workflow/`, `targets/zcode/skills/charter-workflow/`, `targets/zcode/commands/charter-workflow.md`, root `DEVELOPMENT_CHARTER.md`, `agentpack.yaml`, `README.md`, `scripts/`, `tests/`, `docs/`. **Never hand-edit** root `skills/charter-workflow/` or `plugins/**` — the Codex builder's `--sync` deletes hand edits there (`shutil.rmtree` before copy).
- The ZCode command file is the portable command plus one extra frontmatter line `skills: charter-workflow`; body edits must be applied to both files.
- The five bootstrap prompts (`portable/prompts/{generic,claude,codex,gemini,deepseek}-bootstrap.md`) are byte-identical today and must stay byte-identical: apply the same edits to all five.
- `targets/codex/skills/charter-workflow/SKILL.md` and `targets/zcode/skills/charter-workflow/SKILL.md` are byte-identical today (pinned by `tests/test_zcode_target.py::test_target_skill_matches_codex_skill_bytes`); keep them identical.
- Builder order is fixed: `build_codex_plugin.py` first (it writes back root `skills/`), then `build_zcode_plugin.py`, then `build_dsh_plugin.py` (it reads root `skills/`). `--sync` refreshes; `--check` byte-compares every declared destination.
- Forbidden vocabulary: the word "Learning"/"learning" in any case is a validator error in shipped files (`FORBIDDEN_CORE_TERMS`, applied by `check_domain_neutrality`). Use "lesson"/"教训" only. Also never write the markers `[TODO:` or `[TBD:`.
- Per-task verification uses **targeted tests only** (the new file-content tests). The full suite is deferred to Task 6 because existing tests that invoke the validator or compare distributions go red while generated trees are stale; `python scripts/validate_kit.py .` also only goes green after Task 6's `--sync` runs.
- Version bumps in plugin manifests are out of scope: the maintainers' release process owns them, and the approved spec's change table does not include them.
- All shell commands run from the repository root (`charter-kit/`).

---

## File Structure

| Path | Responsibility |
|---|---|
| Create `portable/templates/lessons.md` | The entry shape: fields, the ID/status/hit semantics, the 8 KB bound, archive pointers. No tooling. |
| Create `portable/references/lessons.md` | The five rules (Distill / Cite / Report / Decay / Generalize) plus the "what this layer is not" limits. Single definition; entry documents cite it. |
| Modify `scripts/validate_kit.py` | Register both files; add `check_lessons_reference`; wire into `run()`. |
| Modify `scripts/init_project.py` | Add `lessons.md` to the template→working-set mapping. |
| Modify `portable/commands/charter-workflow.md` + `targets/zcode/commands/charter-workflow.md` | Bootstrap file list, resume read list + lessons status line, one shared-rules bullet. |
| Modify `targets/codex/skills/charter-workflow/SKILL.md` + `targets/zcode/skills/charter-workflow/SKILL.md` | "nine templates" counts, required-start item 6 + status sentence, one operating-rules bullet. |
| Modify `portable/prompts/*.md` (×5, identical edits) | Bootstrap create list, resume read sentence + status line, one rules bullet. |
| Modify `DEVELOPMENT_CHARTER.md` (root; mirrored by `--sync` into three skill trees) | Read-order chain gains `lessons.md`; one new paragraph defining the layer. |
| Modify `agentpack.yaml` | `working_set.optional` gains `.charter/lessons.md`. |
| Modify `tests/pressure-scenarios.md` | Read-order chain string. |
| Modify `README.md` | One bilingual addition to the core-resume-files paragraphs. |
| Modify `docs/MIRROR-TOPOLOGY.md` | One row in the hand-edited sources table for the two new portable files. |
| Modify `tests/test_documentation_contract.py`, `tests/test_workflow_contract.py`, `tests/test_charter_kit.py` | Contract and behavior assertions for the layer. |
| Refresh (generated, never hand-edited) root `skills/charter-workflow/`, `plugins/charter-kit/`, `plugins/zcode-charter-kit/`, `plugins/dsh-charter-kit/` | Task 6 `--sync` output. |

Copy targets for the two new files (byte-identical, done inside Tasks 1–2): `targets/codex/skills/charter-workflow/{templates,references}/lessons.md` and `targets/zcode/skills/charter-workflow/{templates,references}/lessons.md`.

---

## Task 1: Lessons template + validator registration

**Files:**
- Create: `portable/templates/lessons.md`
- Create (byte-identical copies): `targets/codex/skills/charter-workflow/templates/lessons.md`, `targets/zcode/skills/charter-workflow/templates/lessons.md`
- Modify: `scripts/validate_kit.py` (the `PORTABLE_TEMPLATES` dict, first entry block around line 34)
- Test: `tests/test_documentation_contract.py`

**Interfaces:**
- Consumes: nothing.
- Produces: the template file whose content Tasks 3 and 6 assert byte-equality against; the entry field spellings `Status:`, `Hits:`, `Pitfall:`, `Evidence:`, `Next defense:`, `Generalize candidate:` — the reference (Task 2), the init test (Task 3), and the doc tests use these spellings verbatim.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_documentation_contract.py` (inside the existing `DocumentationContractTests` class, after `test_portable_design_interview_reference_is_available` or any neighboring template test):

```python
    def test_lessons_template_defines_bounded_advisory_entries(self) -> None:
        text = read("portable/templates/lessons.md")
        for phrase in (
            "# Lessons",
            "## Entries",
            "## Archive pointers",
            "Status: ACTIVE",
            "Hits:",
            "Pitfall:",
            "Evidence:",
            "Next defense:",
            "Generalize candidate:",
            "8 KB",
            "lessons-archive.md",
            "not a gate",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m pytest tests/test_documentation_contract.py::DocumentationContractTests::test_lessons_template_defines_bounded_advisory_entries -v`
Expected: FAIL with `FileNotFoundError` for `portable/templates/lessons.md`.

- [ ] **Step 3: Create the template**

Create `portable/templates/lessons.md` with exactly this content:

```markdown
# Lessons

> Copy this file to `.charter/lessons.md` at initialization. It records the pitfalls this
> project actually hit and the defense for the next time. It is bounded project knowledge,
> not a gate: citing a lesson is advice, and no lesson changes a gate state or an
> authorization.

**Bounded size.** This file is in the required-start read set whenever it exists, so every
resume pays for it. Keep it at or under 8 KB. When it exceeds the bound, archive the weakest
entries (lowest hit count first, then oldest) to `.charter/lessons-archive.md` — outside the
required-start read set — and leave one pointer line per archived entry in the Archive
pointers section. Never archive an entry that a leaf cites as its defense basis or that
carries an open `GENERALIZE` candidacy; that promotion sweep mirrors the handoff archive
rule.

**One pitfall, one entry.** Before adding an entry, check whether the pitfall already has
one: a repeat hit updates that entry (hit count +1, evidence appended, defense revised)
instead of creating a duplicate. `LS-NNN` IDs are frozen, including after archival, so one
ID never names two different pitfalls.

## Entries

- LS-001 | Status: ACTIVE | Hits: 0 | Source: `<TASK-ID> Events / Review / Change Triage>` | Date: `<YYYY-MM-DD>`
  - Pitfall: `<what situation led to what cost, one scannable sentence>`
  - Evidence: `<path under .charter/evidence/ or commit>`
  - Next defense: `<at which decision point, check what, and do what>`
  - Generalize candidate: NO

## Archive pointers

- `<LS-NNN> : see .charter/lessons-archive.md` (kept only after the first archival)
```

- [ ] **Step 4: Register the template in the validator**

In `scripts/validate_kit.py`, add an entry to the `PORTABLE_TEMPLATES` dict (after the `"portable/templates/evidence-receipt.md"` entry, keeping dict style):

```python
    "portable/templates/lessons.md": (
        "# Lessons",
        "## Entries",
        "## Archive pointers",
    ),
```

This one registration automatically adds the file to `REQUIRED_FILES` (via `*PORTABLE_TEMPLATES`), to the `MIRRORS` generator that compares `portable/templates/lessons.md` against `skills/charter-workflow/templates/lessons.md`, and to the `check_domain_neutrality` forbidden-term scan. `check_templates` will now require the three headings and reject `[TODO:`/`[TBD:` markers.

- [ ] **Step 5: Copy the template into both target skill trees**

```bash
cp portable/templates/lessons.md targets/codex/skills/charter-workflow/templates/lessons.md
cp portable/templates/lessons.md targets/zcode/skills/charter-workflow/templates/lessons.md
```

- [ ] **Step 6: Run the test to verify it passes**

Run: `python -m pytest tests/test_documentation_contract.py::DocumentationContractTests::test_lessons_template_defines_bounded_advisory_entries -v`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add portable/templates/lessons.md targets/codex/skills/charter-workflow/templates/lessons.md targets/zcode/skills/charter-workflow/templates/lessons.md scripts/validate_kit.py tests/test_documentation_contract.py
git commit -m "feat: add the lessons template and register it in the validator"
```

---

## Task 2: Lessons rules reference + validator check

**Files:**
- Create: `portable/references/lessons.md`
- Create (byte-identical copies): `targets/codex/skills/charter-workflow/references/lessons.md`, `targets/zcode/skills/charter-workflow/references/lessons.md`
- Modify: `scripts/validate_kit.py` (constants near the other `*_REFERENCE` definitions around lines 139–207; `REQUIRED_FILES` around line 287; `MIRRORS` around line 353; the `check_domain_neutrality` file list around line 3018; a new `check_lessons_reference` method; the `run()` wiring around line 822)
- Test: `tests/test_documentation_contract.py`

**Interfaces:**
- Consumes: the template field spellings from Task 1 (`GENERALIZE`, `LS-NNN`, hit count).
- Produces: the reference whose required phrases `check_lessons_reference` and the Task 2 test assert; the five rule names (`Distill`, `Cite`, `Report`, `Decay`, `Generalize`) that Task 4's entry-document bullets cite; the constant names `LESSONS_REFERENCE`, `SKILL_LESSONS_REFERENCE`, `TARGET_LESSONS_REFERENCE`, `DISTRIBUTION_LESSONS_REFERENCE` used by the validator in this task and by nothing else.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_documentation_contract.py`:

```python
    def test_lessons_reference_keeps_the_five_rules_in_one_place(self) -> None:
        text = read("portable/references/lessons.md")
        for phrase in (
            "# Lessons rules",
            "## Distill",
            "## Cite",
            "## Report",
            "## Decay",
            "## Generalize",
            "8 KB",
            "Zero output is a legal result",
            "detectable failure",
            "not a gate",
            "unhooked ledger",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m pytest tests/test_documentation_contract.py::DocumentationContractTests::test_lessons_reference_keeps_the_five_rules_in_one_place -v`
Expected: FAIL with `FileNotFoundError`.

- [ ] **Step 3: Create the reference**

Create `portable/references/lessons.md` with exactly this content:

```markdown
# Lessons rules

This reference defines the lesson layer: how a pitfall becomes an entry, how entries are
cited, reported, archived, and promoted into the kit itself. The layer is project-local
knowledge with a bounded budget; it is advice, not a gate. This file (or
`references/lessons.md` in the self-contained Skill) is the single definition; entry
documents cite it instead of restating it.

## Distill — when an event becomes an entry

Run the distill sweep at three moments: when a leaf reaches `PASS_CLOSED`, during the
promotion sweep before archiving a handoff block, and on the defect route of Change Triage.
Sweep the leaf Events table (`FALLBACK`, rework, over-budget repair), Review A/B findings,
and expired waivers. A qualifying event names a pitfall, a cost, and evidence under
`.charter/evidence/` or a commit. One pitfall keeps one entry: a repeat hit updates the
existing entry — hit count +1, evidence appended, defense revised — and never creates a
duplicate. Zero output is a legal result: a leaf with no qualifying event adds nothing, and
an entry created to fill a quota is a defect, not a lesson.

## Cite — where an entry is used

At the Design step, the Reuse Check, and Change Triage, read `.charter/lessons.md` (when it
exists) and cite every relevant `LS-NNN` with one line saying why it applies. A citation
raises that entry's hit count whether it prevented the pitfall or not. Stepping on a
registered pitfall anyway is a defect signal for this layer, not an excuse: record the
event in the leaf Events table and let the next distill sweep revise the defense. A defense
that failed despite being cited must be re-distilled with the new evidence; the count still
rises.

## Report — how the user sees the layer

The layer reports at the moments the workflow already reports; the user never polls disk.
On resume, the status line names the active and archived entry counts, the newest entry,
and every open `GENERALIZE` candidacy: `lessons: 3 active / 1 archived | newest LS-012
(TASK-007, 09-14) | 1 GENERALIZE candidate awaiting your decision: LS-009`. At leaf
closure, the distill sweep result appears in the closure report: `distilled: 1 new
(LS-012), 2 updated (repeat LS-004), 3 cited this leaf`. A candidacy is decided, not
parked: the user promotes it, keeps it project-local, or drops it, and the decision is
recorded on the entry.

## Decay — how the file stays bounded

`.charter/lessons.md` is capped at 8 KB because every resume re-reads it. Over the cap,
archive the weakest entries — lowest hit count first, then oldest — to
`.charter/lessons-archive.md`, leaving one pointer line each. Before archiving any entry,
run the promotion sweep: an entry cited as a defense basis by any leaf, or carrying an open
`GENERALIZE` candidacy, is not archivable. Archiving without the sweep silently deletes a
live rule from every later reader — the same defect as archiving a handoff block by leaf ID
alone.

## Generalize — how the kit itself improves

A generalizable pitfall is promoted only by an explicit user action. The agent proposes by
marking the entry `GENERALIZE` and presenting the candidacy in the resume report. The user
confirms; the promotion is then a hand edit to `portable/` (or the equivalent Skill tree)
plus a rebuild — never an automatic write. A candidacy without a detectable failure mode
and the decision point that catches it is rejected, not escalated; a promotion that cannot
name a clause it replaces or strengthens is prompt bloat and is rejected too. After
promotion the entry is `GENERALIZED` and keeps one pointer line so the same pitfall is not
re-proposed.

## What this layer is not

It is not a gate: no lesson blocks `READY`, changes a gate state, or alters an
authorization. It is not cross-project: entries live in this project's `.charter/`, and
only a user-confirmed promotion reaches the kit. And it is not a transcript: evidence is a
pointer, never a copy. An unhooked ledger dies — records that no workflow step reads or
reports become an empty directory of `.gitkeep` files; the distill, cite, and report hooks
above are what keep this one alive.
```

- [ ] **Step 4: Copy the reference into both target skill trees**

```bash
cp portable/references/lessons.md targets/codex/skills/charter-workflow/references/lessons.md
cp portable/references/lessons.md targets/zcode/skills/charter-workflow/references/lessons.md
```

- [ ] **Step 5: Register the reference in the validator**

In `scripts/validate_kit.py`:

(a) Add constants next to the other reference constants (after the `TARGET_DEFAULT_ON_REFERENCE` / `DISTRIBUTION_DEFAULT_ON_REFERENCE` block):

```python
LESSONS_REFERENCE = "portable/references/lessons.md"
SKILL_LESSONS_REFERENCE = "skills/charter-workflow/references/lessons.md"
TARGET_LESSONS_REFERENCE = "targets/codex/skills/charter-workflow/references/lessons.md"
DISTRIBUTION_LESSONS_REFERENCE = (
    "plugins/charter-kit/skills/charter-workflow/references/lessons.md"
)
```

(b) Add all four to `REQUIRED_FILES` (the tuple starting `REQUIRED_FILES = (`), next to the existing `TARGET_CHANGE_TRIAGE_REFERENCE` / `DISTRIBUTION_CHANGE_TRIAGE_REFERENCE` entries:

```python
    LESSONS_REFERENCE,
    SKILL_LESSONS_REFERENCE,
    TARGET_LESSONS_REFERENCE,
    DISTRIBUTION_LESSONS_REFERENCE,
```

(c) Add a MIRRORS entry inside the `MIRRORS = (` tuple, next to the design-intelligence/design-interview entries:

```python
    (LESSONS_REFERENCE, SKILL_LESSONS_REFERENCE),
```

(d) Add both portable/skill paths to the `check_domain_neutrality` file list (the `files: list[str]` inside that method), next to `DEFAULT_ON_REFERENCE` / `SKILL_DEFAULT_ON_REFERENCE`:

```python
            LESSONS_REFERENCE,
            SKILL_LESSONS_REFERENCE,
```

(e) Add the check method (after `check_default_on_reference`):

```python
    def check_lessons_reference(self) -> None:
        """Keep the lesson-layer rules whole in one reference.

        The entry documents carry compact bullets; the distill/cite/report/
        decay/generalize definitions live here so two paraphrases cannot drift.
        """

        for relative in (LESSONS_REFERENCE, SKILL_LESSONS_REFERENCE):
            text = self.read(relative)
            for phrase in (
                "# Lessons rules",
                "## Distill",
                "## Cite",
                "## Report",
                "## Decay",
                "## Generalize",
                "8 KB",
                "Zero output is a legal result",
                "detectable failure",
                "not a gate",
                "unhooked ledger",
            ):
                self.require(text, phrase, relative)
```

(f) Wire it into `run()`, right after `self.check_default_on_reference()`:

```python
        self.check_lessons_reference()
```

- [ ] **Step 6: Run the test to verify it passes**

Run: `python -m pytest tests/test_documentation_contract.py::DocumentationContractTests::test_lessons_reference_keeps_the_five_rules_in_one_place -v`
Expected: PASS.

(Note: `python scripts/validate_kit.py .` stays red until Task 6 — `SKILL_LESSONS_REFERENCE` and `DISTRIBUTION_LESSONS_REFERENCE` do not exist until the builders refresh the generated trees. Do not run it yet.)

- [ ] **Step 7: Commit**

```bash
git add portable/references/lessons.md targets/codex/skills/charter-workflow/references/lessons.md targets/zcode/skills/charter-workflow/references/lessons.md scripts/validate_kit.py tests/test_documentation_contract.py
git commit -m "feat: add the lessons rules reference and its validator check"
```

---

## Task 3: Initialize lessons.md with the working set

**Files:**
- Modify: `scripts/init_project.py` (the `FILES` dict near the top)
- Test: `tests/test_charter_kit.py`

**Interfaces:**
- Consumes: `portable/templates/lessons.md` from Task 1 (via the existing `find_template_dir`, which already prefers `portable/templates` and falls back to `templates`).
- Produces: every newly initialized project gets `.charter/lessons.md` byte-identical to the template.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_charter_kit.py` (next to `test_init_creates_reuse_discovery_record`, reusing its `make_package_copy` / `run_script` helpers):

```python
    def test_init_creates_the_lessons_record(self) -> None:
        package = self.make_package_copy()
        project = package.parent / "project"
        init_script = package / "scripts" / "init_project.py"

        result = self.run_script(init_script, project)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        lessons = project / ".charter" / "lessons.md"
        self.assertTrue(lessons.is_file(), result.stdout + result.stderr)
        template = (package / "portable" / "templates" / "lessons.md").read_text(
            encoding="utf-8"
        )
        self.assertEqual(lessons.read_text(encoding="utf-8"), template)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m pytest tests/test_charter_kit.py::CharterKitBehaviorTests::test_init_creates_the_lessons_record -v`
Expected: FAIL — `lessons.is_file()` is False (the initializer does not create it yet).

- [ ] **Step 3: Add the mapping**

In `scripts/init_project.py`, add one entry to the `FILES` dict:

```python
    "evidence-receipt.md": "evidence-receipt.md",
    "lessons.md": "lessons.md",
```

No other change: `find_template_dir` already resolves both layouts, and the copy loop, `--add-missing`, and the backup path iterate the mapping.

- [ ] **Step 4: Run the test to verify it passes**

Run: `python -m pytest tests/test_charter_kit.py::CharterKitBehaviorTests::test_init_creates_the_lessons_record -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/init_project.py tests/test_charter_kit.py
git commit -m "feat: initialize lessons.md with the standard working set"
```

---

## Task 4: Wire the layer into the entry documents

**Files:**
- Modify: `portable/commands/charter-workflow.md` and `targets/zcode/commands/charter-workflow.md` (same body edits; the ZCode file keeps its extra frontmatter line)
- Modify: `targets/codex/skills/charter-workflow/SKILL.md` and `targets/zcode/skills/charter-workflow/SKILL.md` (identical edits in both)
- Modify: `portable/prompts/generic-bootstrap.md`, `portable/prompts/claude-bootstrap.md`, `portable/prompts/codex-bootstrap.md`, `portable/prompts/gemini-bootstrap.md`, `portable/prompts/deepseek-bootstrap.md` (identical edits in all five)
- Test: `tests/test_workflow_contract.py`

**Interfaces:**
- Consumes: the five rule names and the reference path from Task 2.
- Produces: entry-document text that Tasks 4 and 6 tests assert; the read-order chain `... → handoff.md → lessons.md` that Task 5 propagates to charter/pressure/README.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_workflow_contract.py`:

```python
    def test_entry_documents_wire_the_lessons_layer(self) -> None:
        for relative in (
            "portable/commands/charter-workflow.md",
            "targets/zcode/commands/charter-workflow.md",
            "targets/codex/skills/charter-workflow/SKILL.md",
            "targets/zcode/skills/charter-workflow/SKILL.md",
        ):
            with self.subTest(relative=relative):
                text = read(relative)
                self.assertIn(".charter/lessons.md", text)
                self.assertIn("references/lessons.md", text)
                self.assertIn("GENERALIZE", text)

        skill = read("targets/codex/skills/charter-workflow/SKILL.md")
        self.assertIn("nine templates", skill)
        self.assertIn("nine files", skill)

    def test_bootstrap_prompts_read_and_create_lessons(self) -> None:
        for relative in (
            "portable/prompts/generic-bootstrap.md",
            "portable/prompts/codex-bootstrap.md",
            "portable/prompts/claude-bootstrap.md",
            "portable/prompts/gemini-bootstrap.md",
            "portable/prompts/deepseek-bootstrap.md",
        ):
            with self.subTest(relative=relative):
                text = read(relative)
                self.assertIn("lessons.md", text)
                self.assertIn("GENERALIZE", text)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_workflow_contract.py -k lessons -v`
Expected: 2 FAILURES (`assertIn ".charter/lessons.md"` fails on all documents).

- [ ] **Step 3: Edit the command file (both copies)**

Apply these three edits to `portable/commands/charter-workflow.md`, then the same three to `targets/zcode/commands/charter-workflow.md`:

Edit 1 — Bootstrap step 1 file list. Replace:

```
create the standard `.charter/` working set: `project.md`, `roadmap.md`, `current-task.md`, `reuse-discovery.md`, `handoff.md`, `decision.md`, `review.md`, `evidence-receipt.md`, plus `evidence/`
```

with:

```
create the standard `.charter/` working set: `project.md`, `roadmap.md`, `current-task.md`, `reuse-discovery.md`, `handoff.md`, `decision.md`, `review.md`, `evidence-receipt.md`, `lessons.md`, plus `evidence/`
```

Edit 2 — Resume mode first sentence and status sentence. Replace:

```
Read `.charter/project.md`, `.charter/roadmap.md`, `.charter/reuse-discovery.md`, `.charter/current-task.md`, and `.charter/handoff.md` if present. If a required file is missing or unreadable, add only that template, record the repair/limitation, and do not plan or implement in that step. State the goal, active leaf/status, authoritative reuse gate and discovery ID, allowed effects, authorization reference, open finding, and one exact next action; then take only that action.
```

with:

```
Read `.charter/project.md`, `.charter/roadmap.md`, `.charter/reuse-discovery.md`, `.charter/current-task.md`, then `.charter/handoff.md` and `.charter/lessons.md` if present. If a required file is missing or unreadable, add only that template, record the repair/limitation, and do not plan or implement in that step. State the goal, active leaf/status, authoritative reuse gate and discovery ID, allowed effects, authorization reference, open finding, a lessons status line (active/archived counts, newest entry, open `GENERALIZE` candidacies), and one exact next action; then take only that action.
```

Edit 3 — Shared rules bullet. Insert this bullet immediately after the "Version control and read-set size:" bullet (before the "Probe before routing the Reuse Check stages" bullet):

```
- Lessons layer: `.charter/lessons.md` is bounded (≤ 8 KB), advisory project knowledge — never a gate. Read it on resume when present; cite relevant `LS-NNN` at Design, Reuse Check, and Change Triage; and at leaf `PASS_CLOSED`, at the handoff promotion sweep, and on the Change Triage defect route, distill qualifying events (`FALLBACK`, rework, over-budget repair, Review findings, expired waivers) into entries per `portable/references/lessons.md` (or `references/lessons.md` in the self-contained Skill). One pitfall keeps one entry; zero output is legal. Report the layer on resume and at leaf closure, surfacing every open `GENERALIZE` candidacy for a user decision. Promotion into the kit is a user-confirmed hand edit, never an automatic write.
```

- [ ] **Step 4: Edit SKILL.md (both target copies, identical edits)**

Apply to `targets/codex/skills/charter-workflow/SKILL.md`, then identically to `targets/zcode/skills/charter-workflow/SKILL.md`:

Edit 1 — intro count. Replace `eight templates` with `nine templates`.

Edit 2 — first-start step 1 count. Replace `copy the eight files from `templates/`` with `copy the nine files from `templates``.

Edit 3 — required-start list. Replace:

```
5. `.charter/handoff.md`, if present
```

with:

```
5. `.charter/handoff.md`, if present
6. `.charter/lessons.md`, if present
```

Edit 4 — the status sentence right below the list. Replace:

```
State the goal, active leaf/status, authoritative reuse gate and ID, allowed effects, authorization reference, open finding, and one exact next action.
```

with:

```
State the goal, active leaf/status, authoritative reuse gate and ID, allowed effects, authorization reference, open finding, a lessons status line (active/archived counts, newest entry, open `GENERALIZE` candidacies), and one exact next action.
```

Edit 5 — operating rules bullet. Insert immediately after the "Version control and read-set size:" bullet:

```
- Lessons layer: `.charter/lessons.md` is bounded (≤ 8 KB), advisory project knowledge — never a gate. Read it on resume when present; cite relevant `LS-NNN` at Design, Reuse Check, and Change Triage; and at leaf `PASS_CLOSED`, at the handoff promotion sweep, and on the Change Triage defect route, distill qualifying events (`FALLBACK`, rework, over-budget repair, Review findings, expired waivers) into entries per `references/lessons.md`. One pitfall keeps one entry; zero output is legal. Report the layer on resume and at leaf closure, surfacing every open `GENERALIZE` candidacy for a user decision. Promotion into the kit is a user-confirmed hand edit, never an automatic write.
```

- [ ] **Step 5: Edit the five bootstrap prompts (identical edits in all five)**

Apply to `portable/prompts/generic-bootstrap.md`, then identically to `claude-`, `codex-`, `gemini-`, `deepseek-bootstrap.md` (verify with `diff` afterwards that all five remain byte-identical):

Edit 1 — bootstrap step 1 create list. Replace:

```
Create `.charter/` with `project.md`, `roadmap.md`, `current-task.md`, `reuse-discovery.md`, `handoff.md`, `decision.md`, `review.md`, `evidence-receipt.md`, and an empty `evidence/` directory.
```

with:

```
Create `.charter/` with `project.md`, `roadmap.md`, `current-task.md`, `reuse-discovery.md`, `handoff.md`, `decision.md`, `review.md`, `evidence-receipt.md`, `lessons.md`, and an empty `evidence/` directory.
```

Edit 2 — resume paragraph. Replace:

```
Read, in order: `.charter/project.md`, `.charter/roadmap.md`, `.charter/reuse-discovery.md`, `.charter/current-task.md`, then `.charter/handoff.md` if present.
```

with:

```
Read, in order: `.charter/project.md`, `.charter/roadmap.md`, `.charter/reuse-discovery.md`, `.charter/current-task.md`, then `.charter/handoff.md` and `.charter/lessons.md` if present.
```

and in the same paragraph replace:

```
State the approved goal, active leaf/status, authoritative reuse gate and discovery ID, allowed effects, authorization reference, open finding, and one exact next action; then take only that action.
```

with:

```
State the approved goal, active leaf/status, authoritative reuse gate and discovery ID, allowed effects, authorization reference, open finding, a lessons status line (active/archived counts, newest entry, open `GENERALIZE` candidacies), and one exact next action; then take only that action.
```

Edit 3 — insert one bullet immediately after the "Version control and read-set size:" bullet:

```
- Lessons: read `.charter/lessons.md` if present, cite relevant entries at Design, Reuse Check, and Change Triage, distill at leaf closure per the bundled lessons reference, and report active/archived counts plus open GENERALIZE candidacies on resume. It is advisory, never a gate.
```

- [ ] **Step 6: Verify prompt identity and run the tests**

```bash
for f in claude codex deepseek gemini; do diff portable/prompts/generic-bootstrap.md portable/prompts/$f-bootstrap.md || exit 1; done
diff targets/codex/skills/charter-workflow/SKILL.md targets/zcode/skills/charter-workflow/SKILL.md
python -m pytest tests/test_workflow_contract.py -k lessons -v
```

Expected: both `diff` commands silent (identical), 2 PASS.

- [ ] **Step 7: Commit**

```bash
git add portable/commands/charter-workflow.md targets/zcode/commands/charter-workflow.md targets/codex/skills/charter-workflow/SKILL.md targets/zcode/skills/charter-workflow/SKILL.md portable/prompts
git commit -m "feat: wire the lessons layer into command, skill, and prompts"
```

---

## Task 5: Charter, agentpack, pressure scenarios, README, mirror doc

**Files:**
- Modify: `DEVELOPMENT_CHARTER.md` (root; the three skill-tree copies regenerate in Task 6 — do not hand-edit them)
- Modify: `agentpack.yaml`, `tests/pressure-scenarios.md`, `README.md`, `docs/MIRROR-TOPOLOGY.md`
- Test: `tests/test_documentation_contract.py`, `tests/test_workflow_contract.py`

**Interfaces:**
- Consumes: the read-order chain ending `handoff.md → lessons.md` established in Task 4.
- Produces: the documentation contract that Task 6's full suite verifies.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_documentation_contract.py`:

```python
    def test_charter_and_readme_carry_the_lessons_layer(self) -> None:
        charter = read("DEVELOPMENT_CHARTER.md")
        self.assertIn("handoff.md → lessons.md（如存在）", charter)
        self.assertIn("建议性知识而非门", charter)
        self.assertIn("用户显式确认", charter)

        readme = read("README.md")
        chinese, _, english = readme.partition("## English")
        self.assertIn("lessons.md", chinese)
        self.assertIn("lessons.md", english)
```

Add to `tests/test_workflow_contract.py` (inside `test_working_set_roles_stay_lightweight_and_consistent`, after the existing `self.assertIn("auxiliary:", required_block)` line):

```python
        self.assertIn(".charter/lessons.md", required_block)
```

Update the existing pressure assertion in `test_resume_pressure_scenario_reads_reuse_before_current_task`. Replace:

```python
        self.assertIn(
            "project.md → roadmap.md → reuse-discovery.md → current-task.md → handoff.md (if present)",
            pressure,
        )
```

with:

```python
        self.assertIn(
            "project.md → roadmap.md → reuse-discovery.md → current-task.md → handoff.md → lessons.md (if present)",
            pressure,
        )
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_documentation_contract.py -k lessons_layer -v && python -m pytest tests/test_workflow_contract.py -k "pressure or working_set_roles" -v`
Expected: FAILURES — charter/README/agentpack/pressure do not mention lessons yet.

- [ ] **Step 3: Edit the charter**

In `DEVELOPMENT_CHARTER.md`:

Edit 1 — the read-order chain (in the handoff/snapshot section). Replace:

```
恢复时重新按 `project.md → roadmap.md → reuse-discovery.md → current-task.md → handoff.md（如存在）` 检查；
```

with:

```
恢复时重新按 `project.md → roadmap.md → reuse-discovery.md → current-task.md → handoff.md → lessons.md（如存在）` 检查；
```

Edit 2 — insert a new paragraph immediately after that paragraph (same section):

```
`.charter/lessons.md` 是初始化即建、存在即读的项目本地经验层：记录实战中真实踩过的坑与下次防御。它有界（≤ 8 KB）、是建议性知识而非门——引用教训不改变任何门状态或授权。叶 `PASS_CLOSED`、handoff 归档提升扫掠与 Change Triage 缺陷路由时按 `portable/references/lessons.md` 的规则提炼条目；同一坑只保留一条，零提炼产出合法。教训要进套件本体，必须经用户显式确认后手工编辑，绝不由 agent 自动写入。
```

- [ ] **Step 4: Edit agentpack.yaml**

In the `working_set:` block, replace:

```yaml
  optional:
    - .charter/handoff.md
```

with:

```yaml
  optional:
    - .charter/handoff.md
    - .charter/lessons.md
```

- [ ] **Step 5: Edit tests/pressure-scenarios.md**

Replace the one occurrence of:

```
project.md → roadmap.md → reuse-discovery.md → current-task.md → handoff.md (if present)
```

with:

```
project.md → roadmap.md → reuse-discovery.md → current-task.md → handoff.md → lessons.md (if present)
```

- [ ] **Step 6: Edit README.md (both language sections)**

In the 中文 section, append to the end of the paragraph that starts `运行时的核心恢复文件（core Resume files）只有` (the paragraph ending `...只是投影。`):

```
`lessons.md` 是同族的第六项：存在即读，是记录实战教训的有界知识层（≤ 8 KB）——叶关闭时从 Events 表提炼、在 Design / Reuse Check / Change Triage 引用、随 Resume 与叶关闭汇报状态；它是建议性知识，不是门状态。教训要进套件本体必须经用户显式确认，规则见 `portable/references/lessons.md`。
```

In the English section, append to the end of the matching paragraph that starts `The four core Resume files are` (the paragraph ending `...while `roadmap.md` is a projection.`):

```
`lessons.md` is the sixth item of the same family: read whenever it exists, a bounded (≤ 8 KB) knowledge layer of pitfalls this project actually hit — distilled from the leaf Events table at closure, cited at Design / Reuse Check / Change Triage, and reported on resume and closure. It is advisory knowledge, not a gate state. A lesson reaches the kit itself only through an explicit user-confirmed promotion; the rules live in `portable/references/lessons.md`.
```

- [ ] **Step 7: Edit docs/MIRROR-TOPOLOGY.md**

Add one row at the end of the "Hand-edited sources" table:

```markdown
| `portable/templates/lessons.md`, `portable/references/lessons.md` | Lessons-layer sources; mirrored byte-identically into both target skill trees like the other portable files. |
```

- [ ] **Step 8: Run the tests to verify they pass**

Run: `python -m pytest tests/test_documentation_contract.py tests/test_workflow_contract.py -v`
Expected: ALL PASS in these two files (the full-suite run is Task 6).

- [ ] **Step 9: Commit**

```bash
git add DEVELOPMENT_CHARTER.md agentpack.yaml tests/pressure-scenarios.md README.md docs/MIRROR-TOPOLOGY.md tests/test_documentation_contract.py tests/test_workflow_contract.py
git commit -m "docs: carry the lessons layer in charter, agentpack, pressure scenarios, and readme"
```

---

## Task 6: Refresh generated trees and verify end to end

**Files:**
- Refresh (generated): root `skills/charter-workflow/`, `plugins/charter-kit/`, `plugins/zcode-charter-kit/`, `plugins/dsh-charter-kit/`
- Test: `tests/test_documentation_contract.py` (mirror equality test)

**Interfaces:**
- Consumes: every hand-edited change from Tasks 1–5.
- Produces: a repository where `validate_kit.py`, all three builder `--check` runs, and the full test suite are green.

- [ ] **Step 1: Write the failing mirror test**

Add to `tests/test_documentation_contract.py`:

```python
    def test_lessons_files_are_mirrored_into_skill_and_target_trees(self) -> None:
        template = read("portable/templates/lessons.md")
        for relative in (
            "skills/charter-workflow/templates/lessons.md",
            "targets/codex/skills/charter-workflow/templates/lessons.md",
            "targets/zcode/skills/charter-workflow/templates/lessons.md",
        ):
            with self.subTest(relative=relative):
                self.assertEqual(read(relative), template)

        reference = read("portable/references/lessons.md")
        for relative in (
            "skills/charter-workflow/references/lessons.md",
            "targets/codex/skills/charter-workflow/references/lessons.md",
            "targets/zcode/skills/charter-workflow/references/lessons.md",
        ):
            with self.subTest(relative=relative):
                self.assertEqual(read(relative), reference)
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest tests/test_documentation_contract.py::DocumentationContractTests::test_lessons_files_are_mirrored_into_skill_and_target_trees -v`
Expected: FAIL — root `skills/charter-workflow/templates/lessons.md` does not exist yet (the two target-tree copies from Tasks 1–2 pass; the root skills copy is still missing).

- [ ] **Step 3: Refresh the generated trees (fixed order)**

```bash
python scripts/build_codex_plugin.py --sync
python scripts/build_zcode_plugin.py --sync
python scripts/build_dsh_plugin.py --sync
```

Expected: each prints a successful sync. Codex first (it writes back root `skills/` and `.codex-plugin/plugin.json`), DSH last (it reads root `skills/`).

- [ ] **Step 4: Run the mirror test to verify it passes**

Run: `python -m pytest tests/test_documentation_contract.py::DocumentationContractTests::test_lessons_files_are_mirrored_into_skill_and_target_trees -v`
Expected: PASS.

- [ ] **Step 5: Run the full verification battery**

```bash
python scripts/validate_kit.py .
python scripts/build_codex_plugin.py --check
python scripts/build_zcode_plugin.py --check
python scripts/build_dsh_plugin.py --check
python -m pytest tests/ -v
```

Expected, in order: validator reports no errors; all three `--check` runs PASS (byte-identical destinations); the full test suite is green — including the pre-existing validator-invoking and distribution-freshness tests (`test_validator_covers_zcode_target`, `test_distribution_matches_fresh_build`, the `test_validator_*` family in `tests/test_charter_kit.py`) that could not pass before this task's `--sync`.

- [ ] **Step 6: Spot-check the read-set claim end to end**

```bash
grep -c "lessons.md" skills/charter-workflow/SKILL.md plugins/zcode-charter-kit/skills/charter-workflow/SKILL.md plugins/dsh-charter-kit/skills/charter-workflow/SKILL.md
git status --short
```

Expected: a positive count in each generated SKILL.md; `git status` shows only the intended new/modified paths (the two new portable files + their mirror copies + generated trees + the Task 1–5 edits).

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "chore: refresh generated trees and verify the lessons layer end to end"
```

---

## Plan self-review record

- **Spec coverage:** template (Task 1), reference with five rules + anti-patterns + promotion gate (Task 2), init creation (Task 3), read-if-present + status line + shared rules (Task 4), charter/agentpack/pressure/README (Task 5), mirror propagation + validator + builders + full suite (Task 6 = the spec's five acceptance criteria). Two additions beyond the spec's change table, discovered during plan-time verification and included here: `DEVELOPMENT_CHARTER.md` (line 365 enumerates the read order) and `tests/pressure-scenarios.md` (its order string is pinned by a test).
- **Deviations from spec, recorded:** `docs/MIRROR-TOPOLOGY.md` gets one table row rather than per-file rows (its tables are directory-level). `REQUIRED_FILES` registration follows the existing four-constant pattern (portable/skill/codex-target/codex-distribution), matching how `change-triage.md` is registered today.
- **Type consistency:** entry field spellings (`Status:`, `Hits:`, `Pitfall:`, `Evidence:`, `Next defense:`, `Generalize candidate:`), rule names (`Distill`, `Cite`, `Report`, `Decay`, `Generalize`), ID format `LS-NNN`, and constant names are used verbatim across template, reference, validator, tests, and entry documents.
