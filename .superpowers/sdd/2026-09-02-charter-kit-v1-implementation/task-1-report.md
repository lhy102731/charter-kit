# Task 1 Implementation Report

Date: 2026-09-02

Status: DONE

Commit hash: `e193d0cc583b4f83552aa1be6749a05830cb11de`

## Files changed

- Added `portable/references/change-triage.md`
- Updated `portable/templates/project-charter.md`
- Updated `portable/templates/roadmap.md`
- Updated `portable/templates/leaf-task.md`
- Updated `portable/templates/handoff.md`
- Updated `portable/templates/decision.md`
- Updated `portable/templates/review.md`
- Updated `portable/templates/evidence-receipt.md`
- Added `tests/test_workflow_contract.py`
- Mirrored the same template changes into:
  - `skills/charter-workflow/templates/project-charter.md`
  - `skills/charter-workflow/templates/roadmap.md`
  - `skills/charter-workflow/templates/leaf-task.md`
  - `skills/charter-workflow/templates/handoff.md`
  - `skills/charter-workflow/templates/decision.md`
  - `skills/charter-workflow/templates/review.md`
  - `skills/charter-workflow/templates/evidence-receipt.md`
  - `targets/codex/skills/charter-workflow/templates/project-charter.md`
  - `targets/codex/skills/charter-workflow/templates/roadmap.md`
  - `targets/codex/skills/charter-workflow/templates/leaf-task.md`
  - `targets/codex/skills/charter-workflow/templates/handoff.md`
  - `targets/codex/skills/charter-workflow/templates/decision.md`
  - `targets/codex/skills/charter-workflow/templates/review.md`
  - `targets/codex/skills/charter-workflow/templates/evidence-receipt.md`
- Regenerated packaged mirrors in:
  - `plugins/charter-kit/portable/references/change-triage.md`
  - `plugins/charter-kit/portable/templates/project-charter.md`
  - `plugins/charter-kit/portable/templates/roadmap.md`
  - `plugins/charter-kit/portable/templates/leaf-task.md`
  - `plugins/charter-kit/portable/templates/handoff.md`
  - `plugins/charter-kit/portable/templates/decision.md`
  - `plugins/charter-kit/portable/templates/review.md`
  - `plugins/charter-kit/portable/templates/evidence-receipt.md`
  - `plugins/charter-kit/skills/charter-workflow/templates/project-charter.md`
  - `plugins/charter-kit/skills/charter-workflow/templates/roadmap.md`
  - `plugins/charter-kit/skills/charter-workflow/templates/leaf-task.md`
  - `plugins/charter-kit/skills/charter-workflow/templates/handoff.md`
  - `plugins/charter-kit/skills/charter-workflow/templates/decision.md`
  - `plugins/charter-kit/skills/charter-workflow/templates/review.md`
  - `plugins/charter-kit/skills/charter-workflow/templates/evidence-receipt.md`
  - `plugins/dsh-charter-kit/portable/references/change-triage.md`
  - `plugins/dsh-charter-kit/portable/templates/project-charter.md`
  - `plugins/dsh-charter-kit/portable/templates/roadmap.md`
  - `plugins/dsh-charter-kit/portable/templates/leaf-task.md`
  - `plugins/dsh-charter-kit/portable/templates/handoff.md`
  - `plugins/dsh-charter-kit/portable/templates/decision.md`
  - `plugins/dsh-charter-kit/portable/templates/review.md`
  - `plugins/dsh-charter-kit/portable/templates/evidence-receipt.md`
  - `plugins/dsh-charter-kit/skills/charter-workflow/templates/project-charter.md`
  - `plugins/dsh-charter-kit/skills/charter-workflow/templates/roadmap.md`
  - `plugins/dsh-charter-kit/skills/charter-workflow/templates/leaf-task.md`
  - `plugins/dsh-charter-kit/skills/charter-workflow/templates/handoff.md`
  - `plugins/dsh-charter-kit/skills/charter-workflow/templates/decision.md`
  - `plugins/dsh-charter-kit/skills/charter-workflow/templates/review.md`
  - `plugins/dsh-charter-kit/skills/charter-workflow/templates/evidence-receipt.md`

## RED

Command:

```text
pytest tests/test_workflow_contract.py -q
```

Output:

```text
FF                                                                       [100%]
================================== FAILURES ===================================
_ WorkflowContractTests.test_change_triage_reference_defines_one_route_contract _

self = <test_workflow_contract.WorkflowContractTests testMethod=test_change_triage_reference_defines_one_route_contract>

    def test_change_triage_reference_defines_one_route_contract(self) -> None:
        text = read("portable/references/change-triage.md")
>       self.assertIn("NEW_REQUIREMENT", text)
E       AssertionError: 'NEW_REQUIREMENT' not found in ''

tests\test_workflow_contract.py:18: AssertionError
__ WorkflowContractTests.test_runtime_working_set_has_single_state_authority ____

self = <test_workflow_contract.WorkflowContractTests testMethod=test_runtime_working_set_has_single_state_authority>

    def test_runtime_working_set_has_single_state_authority(self) -> None:
        current = read("portable/templates/leaf-task.md")
        roadmap = read("portable/templates/roadmap.md")
>       self.assertIn("current-task.md is the active Leaf state authority", roadmap)
E       AssertionError: 'current-task.md is the active Leaf state authority' not found in '# Project Roadmap\n\n> Copy this file to `.charter/roadmap.md`. It is the task projection, not a second product specification. Keep the approved goal in `project.md` and link to it here.\n\n## Goal reference\n\n- Project: `<name>`\n- Charter: `.charter/project.md`\n- Roadmap version: `0.1`\n- Last updated: `<YYYY-MM-DD>`\n\n## Delivery order\n\n| Order | ID | Level (`EPIC / CAPABILITY / SLICE / LEAF`) | One observable result | Depends on | Status | Evidence / task file |\n|---:|---|---|---|---|---|---|\n| 1 | R1 | `EPIC` | `<approved outcome>` | �� | `PLANNED` | `.charter/project.md` |\n| 2 | R1.1 | `CAPABILITY` | `<capability result>` | R1 | `PLANNED` | `<link>` |\n| 3 | R1.1-S1 | `SLICE` | `<small end-to-end behavior>` | R1.1 | `PLANNED` | `<link>` |\n| 4 | R1.1-S1-L1 | `LEAF` | `<one behavior>` | �� | `DRAFT` | `.charter/current-task.md` |\n\n## Active-work rule\n\n- Active leaf: `NONE` until one approved leaf passes the readiness check\n- WIP limit per parent: `1`\n- Current task contract: `.charter/current-task.md`\n- Reuse discovery record: `.charter/reuse-discovery.md`\n- Reuse discovery gate: `NOT_STARTED | IN_PROGRESS | COMPLETE | LIMITED | WAIVED | BLOCKED_TOOLING`\n- Gate source of truth: `.charter/reuse-discovery.md`; this status is a synchronized projection and must match `project.md`.\n- Reuse discovery ID: `<RD-...; must match .charter/reuse-discovery.md and project.md>`\n- Discovery freshness: `<current, or targeted recheck ID/date when a trigger applies>`\n- Dependency check evidence: `<.charter/evidence/dependency-check.log or manual record>`\n- Next candidate: `<informational ID; initially the first DRAFT leaf>`\n- Next authorization: `NOT_GRANTED`\n\n## Leaf readiness check\n\nBefore moving a leaf to `READY`, confirm:\n\n- [ ] the leaf contract is `APPROVED` and its approval or preauthorization reference is recorded;\n- [ ] predecessor is `��`, or every listed predecessor is actually `PASS_CLOSED`;\n- [ ] one observable result is written;\n- [ ] allowed paths/effects and forbidden effects are explicit;\n- [ ] positive and negative acceptance checks exist;\n- [ ] stop conditions and repair budget are written;\n- [ ] required host capabilities and approvals are available.\n- [ ] the dependency-check record is attached; every required capability is `AVAILABLE`, or an explicit `BLOCKED_TOOLING`/user waiver is recorded.\n- [ ] the reuse discovery gate is `COMPLETE`, or `LIMITED`/`WAIVED` has explicit user approval, limitations, and a recheck condition recorded in `.charter/reuse-discovery.md`;\n- [ ] the projected gate status matches `.charter/reuse-discovery.md` and `project.md`, and its recheck trigger/date is current; if a trigger applies, a targeted recheck is recorded before this leaf is approved;\n- [ ] when the gate is `COMPLETE`, every material capability has in-scope raw evidence, out-of-scope tiers are explicitly `NOT_SEARCHED`/`NOT_AUTHORIZED`, selected revisions are fixed immutable commit/tag/package versions, and no high-value `UNKNOWN`/`DEFER` remains unresolved;\n- [ ] every non-workspace/installed search tier used by this leaf is covered by the recorded discovery scope and `External read authorization`;\n- [ ] `BLOCKED_TOOLING` is treated as blocking: do not approve or move a leaf to `READY` until the capability is restored or the user approves a bounded `LIMITED`/`WAIVED` downgrade;\n\n`BLOCKED_TOOLING` blocks leaf readiness and is never equivalent to approval.\n\nProject approval does not bypass the reuse discovery gate. A pending or unsupported search keeps the leaf out of `APPROVED`/`READY`; `BLOCKED_TOOLING` requires restored capability or an explicit user-approved downgrade. For later leaves, do not repeat a full search unless a new capability, stack/boundary change, or expiry trigger applies; perform and link a targeted recheck instead. A selected candidate is still only a route decision until its own dependency, installation, and execution authorization exists.\n\nWhen the authoritative reuse record changes, update its status, this projection, and the project projection in the same change. Any mismatch is a blocking finding, not permission to choose the most optimistic copy.\n\nWhen moving a leaf from `DRAFT` to `APPROVED`, update the task file and roadmap row together; then move both to `READY` together after readiness. After the checklist passes, update the leaf status and roadmap row to `READY` together, and set `Active leaf` to that ID. Project-charter approval alone never moves a leaf out of `DRAFT`. Mirror every later leaf state transition (`IN_PROGRESS`, `REVIEW`, `INTEGRATION_PENDING`, `POST_MERGE_VERIFIED`, `PASS_CLOSED`) in the task file and roadmap row in the same change. When the leaf reaches `PASS_CLOSED`, record the closure evidence, clear `Active leaf` (or set it to the next explicitly authorized leaf), and update the row and `Next authorization` together; never leave `Active leaf: NONE` while a leaf is `READY` or `IN_PROGRESS`.\n\n## Closure rule\n\nOnly `PASS_CLOSED` leaves may unblock a dependent leaf. A branch commit, a focused green test, or a proposed next candidate is not closure by itself. Update the roadmap after the target branch and post-integration verification are recorded.\n\n## Decisions affecting the route\n\n| Decision ID | Affected IDs | What changed | Approval / evidence |\n|---|---|---|---|\n| `<DEC-ID>` | `<IDs>` | `<route or scope change>` | `<link>` |\n'
=========================== short test summary info ============================
FAILED tests\test_workflow_contract.py::WorkflowContractTests::test_change_triage_reference_defines_one_route_contract
FAILED tests\test_workflow_contract.py::WorkflowContractTests::test_runtime_working_set_has_single_state_authority
2 failed in 0.22s
```

## RED round 2

Command:

```text
pytest tests/test_generic_bootstrap.py tests/test_workflow_contract.py -q
```

Output:

```text
F.....F........F                                                         [100%]
================================== FAILURES ===================================
_ GenericBootstrapTests.test_bootstrap_docs_use_canonical_runtime_working_set_filenames _

self = <test_generic_bootstrap.GenericBootstrapTests testMethod=test_bootstrap_docs_use_canonical_runtime_working_set_filenames>

    def test_bootstrap_docs_use_canonical_runtime_working_set_filenames(self) -> None:
        for relative in (
            "portable/commands/charter-workflow.md",
            "portable/prompts/generic-bootstrap.md",
            "portable/prompts/codex-bootstrap.md",
            "portable/prompts/claude-bootstrap.md",
            "portable/prompts/gemini-bootstrap.md",
            "portable/prompts/deepseek-bootstrap.md",
        ):
            content = self.read(relative)
            self.assertIn("decision.md", content, relative)
>           self.assertIn("review.md", content, relative)
E           AssertionError: 'review.md' not found in "---\ndescription: Start or resume the host-neutral Charter Kit development workflow\nargument-hint: [one-sentence intent seed for a new project; leave empty to resume]\n---\n\n# Charter Workflow Entry\n\nRun the Charter Kit workflow. Choose the branch from project state; do not skip an approval or evidence gate. The command is usable from zero: an installed Skill is helpful but never a prerequisite.\n\n## Bootstrap mode �� no `.charter/project.md`\n\n1. Locate the nearest `portable/templates/` or Skill `templates/` and create the standard `.charter/` working set: `project.md`, `roadmap.md`, `current-task.md`, `reuse-discovery.md`, `handoff.md`, `decision-template.md`, `review-template.md`, `evidence-template.md`, plus `evidence/`. Preserve existing files and add only missing entries.\n2. Run `scripts/check_dependencies.py` when available (or perform equivalent local checks). Report `AVAILABLE`, `MISSING`, `UNVERIFIED`, and `FALLBACK` with capability, reason, impact, fallback, and action, and append the report to `.charter/evidence/dependency-check.log`. Required gaps remain `BLOCKED_TOOLING`; optional gaps use the portable fallback. Never install, and never record credentials, secrets, private source, or real data.\n3. Use `grill-me`/`grilling` first for a multi-round intent interview. If absent, report `MISSING` and use the portable fallback at `portable/references/design-interview.md` (or `skills/charter-workflow/references/design-interview.md` when running from the self-contained Skill) as `FALLBACK`; do not claim the provider ran. `$ARGUMENTS` is only a seed. Resolve user/context, pain, observable goal, non-goals, invariants, product loop, assets, reuse scope, effects, success levels, risks, and one first bounded behavior; record the answers.\n4. Load `DEVELOPMENT_CHARTER.md`, complete the full charter-engineering loop (requirements archaeology, goal correction, asset/capability audit, authorization boundaries, task tree, self-review), and obtain `CHARTER_INDEPENDENT` review from a different reviewer in a fresh context/process. If unavailable, record `BLOCKED_TOOLING` or a user-approved waiver with limitation and expiry. Unresolved findings keep the project `BLOCKED`; resolve each finding, record an explicit open decision or waiver with its limitation, and do not request or record project approval while one remains unhandled.\n5. Draft the project charter, roadmap, and one first `DRAFT` leaf. Present the approval bundle and stop for explicit project approval; project approval does not approve the leaf.\n6. After project approval, complete authoritative `.charter/reuse-discovery.md` in the approved scope before leaf approval. Search `workspace/history`, installed/cache/manifest, approved internal resources, official/upstream/registries, then authorized public web. Record exact queries, raw evidence under `.charter/evidence/`, negative results, omitted tiers, candidate checks, and fixed `immutable commit/tag/package version` values. Discovery is read-only: never clone, build, run, import, copy, install, load candidate instructions, write global directories, or upload private source/secrets/real data. `NOT_STARTED`, `IN_PROGRESS`, `BLOCKED_TOOLING`, or an expired record blocks leaf readiness unless a bounded `LIMITED`/`WAIVED` downgrade is explicitly approved; `COMPLETE` has no unresolved high-value `UNKNOWN`/`DEFER` remains unresolved.\n7. Reconcile the result, obtain separate leaf approval or matching `AUTO_DEV` preauthorization, update task and roadmap together `DRAFT �� APPROVED`, run readiness, then together to `READY`. `BLOCKED_TOOLING` cannot approve or move a leaf to `READY`. Implement only after `READY`.\n\n## Resume mode �� `.charter/project.md` exists\n\nRead `.charter/project.md`, `.charter/roadmap.md`, `.charter/reuse-discovery.md`, `.charter/current-task.md`, and `.charter/handoff.md` if present. If a required file is missing or unreadable, add only that template, record the repair/limitation, and do not plan or implement in that step. State the goal, active leaf/status, authoritative reuse gate and discovery ID, allowed effects, authorization reference, open finding, and one exact next action; then take only that action.\n\n## Shared rules\n\n- Keep `WIP = 1`; `NEXT_CANDIDATE` is informational and never authorization.\n- Follow the leaf's allowed paths, effects, acceptance, and stop conditions. Use RED �� GREEN and preserve negative checks.\n- Route work to optional Superpowers, J-space, and grill-me providers when present; when missing, emit `MISSING`/`UNVERIFIED`, explain the impact, and use the documented portable fallback. Never silently simulate a provider.\n- Review B requires a different reviewer and fresh context/process; otherwise record `BLOCKED_TOOLING`.\n- Mirror all task states in the roadmap. `PASS_CLOSED` requires final-candidate evidence, review, target-branch integration, and post-integration verification.\n- Stop and write `decision.md` for changes to goal, scope, public meaning, authorization, sensitive data, release behavior, or irreversible effects.\n- Loading this command never installs skills, plugins, packages, services, or global configuration; dependency setup is a separate explicit user action.\n" : portable/commands/charter-workflow.md

tests\test_generic_bootstrap.py:87: AssertionError
_ GenericBootstrapTests.test_initializer_creates_canonical_runtime_working_set_names _

3 failed, 13 passed in 1.24s
```

## GREEN round 2

Command:

```text
pytest tests/test_generic_bootstrap.py tests/test_workflow_contract.py -q
```

Output:

```text
................                                                         [100%]
16 passed in 1.05s
```

## Verification round 2

Command:

```text
pytest tests/test_charter_kit.py -q
```

Output:

```text
60 passed in 36.80s
```
## GREEN

Command:

```text
pytest tests/test_workflow_contract.py -q
```

Output:

```text
..                                                                       [100%]
2 passed in 0.01s
```

## Packaging regeneration

Commands:

```text
python scripts/build_codex_plugin.py
python scripts/build_dsh_plugin.py
```

Outputs:

```text
Charter Kit packager: built C:\Users\Administrator\Documents\Codex\2026-08-29\codex-threads-019ff5dc-4d04-73c2-a03a\outputs\charter-kit\charter-kit\plugins\charter-kit
Charter Kit DSH packager: built C:\Users\Administrator\Documents\Codex\2026-08-29\codex-threads-019ff5dc-4d04-73c2-a03a\outputs\charter-kit\charter-kit\plugins\dsh-charter-kit
```

## Verification

Command:

```text
pytest tests/test_workflow_contract.py tests/test_generic_bootstrap.py -q
```

Output:

```text
..............                                                           [100%]
16 passed in 1.05s
```

Command:

```text
pytest tests/test_charter_kit.py -q
```

Output:

```text
............................................................             [100%]
60 passed in 36.80s
```

## Self-review

- The canonical Change Triage contract is now defined in `portable/references/change-triage.md` and mirrored into the packaged distributions.
- The project, roadmap, leaf, decision, review, handoff, and evidence templates now all include a concise Change Triage section without introducing a second state machine.
- The leaf authority split is explicit: `current-task.md` owns the active leaf state, while `roadmap.md` remains a projection.
- The new contract test fails before implementation and passes after the minimal changes, and the existing bootstrap/charter-kit suite passes after regenerating the packaged mirrors.
- I preserved the unrelated working tree items (`$null` and the two draft docs) and did not touch them.
- Canonical runtime filenames are now emitted by the initializer and documented by the bootstrap prompts, while legacy `*-template.md` files remain untouched if they already exist.

## Concerns

- The pre-existing untracked items `$null`, `docs/superpowers/plans/2026-09-02-charter-kit-v1-implementation.md`, and `docs/superpowers/specs/2026-09-02-charter-kit-v1-architecture-design.md` were left untouched by design.

## Fix round 1

Date: 2026-09-02

Status: DONE

Commit hash: `566d7af2560ab8362d2004a99e2d05dbecdb6484`

### Files changed in this round

- Updated the generated plugin mirrors of the bootstrap entry points so they now create `decision.md`, `review.md`, and `evidence-receipt.md` instead of the legacy `*-template.md` names:
  - `plugins/charter-kit/portable/commands/charter-workflow.md`
  - `plugins/charter-kit/portable/prompts/claude-bootstrap.md`
  - `plugins/charter-kit/portable/prompts/codex-bootstrap.md`
  - `plugins/charter-kit/portable/prompts/deepseek-bootstrap.md`
  - `plugins/charter-kit/portable/prompts/gemini-bootstrap.md`
  - `plugins/charter-kit/portable/prompts/generic-bootstrap.md`
  - `plugins/charter-kit/scripts/init_project.py`
  - `plugins/charter-kit/skills/charter-workflow/scripts/init_project.py`
  - `plugins/dsh-charter-kit/portable/commands/charter-workflow.md`
  - `plugins/dsh-charter-kit/portable/prompts/claude-bootstrap.md`
  - `plugins/dsh-charter-kit/portable/prompts/codex-bootstrap.md`
  - `plugins/dsh-charter-kit/portable/prompts/deepseek-bootstrap.md`
  - `plugins/dsh-charter-kit/portable/prompts/gemini-bootstrap.md`
  - `plugins/dsh-charter-kit/portable/prompts/generic-bootstrap.md`
  - `plugins/dsh-charter-kit/scripts/init_project.py`
  - `plugins/dsh-charter-kit/skills/charter-workflow/scripts/init_project.py`

### Verification

- `pytest tests/test_workflow_contract.py tests/test_generic_bootstrap.py -q`
  - `18 passed, 16 subtests passed in 1.04s`
- `pytest tests/test_workflow_contract.py tests/test_generic_bootstrap.py tests/test_charter_kit.py -q`
  - `78 passed, 16 subtests passed in 37.81s`

### Notes

- The contract test now covers all Change Triage event kinds and routes, plus representative portable/skill template mirror checks.
- Legacy `*-template.md` names remain only as compatibility for already-existing files that predate the canonical bootstrap names.
