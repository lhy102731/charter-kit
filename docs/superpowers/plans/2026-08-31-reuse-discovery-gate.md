# Reuse Discovery Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a bounded, auditable reuse/prior-art discovery gate between project-charter approval and first-leaf authorization so agents check existing code, skills, projects, packages, and references before building new work.

**Architecture:** Keep the existing leaf state machine unchanged. Add one project-level `.charter/reuse-discovery.md` record with an explicit status and evidence fields; require `COMPLETE`, user-approved `LIMITED`, or user-approved `WAIVED` before a leaf can become `READY`. Discovery is read-only and time-boxed; adoption, installation, execution, and scope changes remain separate authorized actions.

**Tech Stack:** Markdown templates, Python standard-library initializer/validator, existing host prompt and Skill routing files, unittest behavior tests, ZIP packaging.

**Spec:** The approved design in the preceding conversation and the canonical `DEVELOPMENT_CHARTER.md` in this package.

## Global Constraints

- The portable package remains the single semantic source of truth; bundled Skill copies must remain byte-identical.
- The discovery record is a summary ledger; raw logs belong under `.charter/evidence/`.
- Discovery never installs, clones, executes, imports, or silently adopts a candidate.
- External search is read-only and only allowed when the charter/effects authorize it; private data and secrets must not enter queries.
- Missing search capability is reported as `LIMITED` or `BLOCKED_TOOLING`, never as an unsupported claim that no reusable resource exists.
- A candidate that changes Goal, Non-goals, Invariants, public semantics, or effect boundaries requires `NEEDS_DECISION` and re-approval.
- Existing `.charter/` data is preserved; initialization and packaging remain side-effect free outside their declared targets.

---

### Task 1: Add RED behavior checks for the reuse gate

**Files:**
- Modify: `tests/test_charter_kit.py`
- Modify: `tests/structure-checklist.md`
- Modify: `tests/pressure-scenarios.md`

- [ ] Add tests that fail when the initializer does not create `reuse-discovery.md`, when the validator accepts a missing reuse gate, and when a prompt/roadmap omits the gate before leaf readiness.
- [ ] Run `python -B -m unittest -v tests.test_charter_kit` and confirm the new assertions fail for the expected missing-content reasons.

### Task 2: Add the canonical reuse-discovery artifact and initializer mapping

**Files:**
- Create: `portable/templates/reuse-discovery.md`
- Create: `skills/charter-workflow/templates/reuse-discovery.md`
- Modify: `scripts/init_project.py`

- [ ] Define statuses, search tiers, query log, candidate evaluation, negative-result evidence, decision classes, timebox, limitations, expiry/recheck trigger, and approval/waiver references.
- [ ] Map `reuse-discovery.md` to `.charter/reuse-discovery.md`; preserve the refusal/backup/link-safety behavior for existing projects.
- [ ] Run the focused initializer tests and confirm the new file is generated without overwriting user data.

### Task 3: Wire the gate into canonical charter and workflow instructions

**Files:**
- Modify: `DEVELOPMENT_CHARTER.md`
- Modify: `portable/templates/project-charter.md`
- Modify: `portable/templates/roadmap.md`
- Modify: `portable/templates/leaf-task.md`
- Modify: `portable/templates/review.md`
- Modify: `portable/templates/handoff.md`
- Modify: `skills/charter-workflow/SKILL.md`
- Modify: `portable/commands/charter-workflow.md`
- Modify: `portable/prompts/claude-bootstrap.md`
- Modify: `portable/prompts/codex-bootstrap.md`
- Modify: `portable/prompts/deepseek-bootstrap.md`
- Modify: `portable/prompts/gemini-bootstrap.md`
- Modify: `portable/prompts/generic-bootstrap.md`
- Modify: `skills/charter-workflow/references/tool-routing.md`

- [ ] State the sequence `project approved → reuse discovery → leaf authorization`, distinguish local asset audit from prior-art discovery, and define targeted re-check triggers for later leaves.
- [ ] Require gate completion or an explicit, bounded user waiver before `READY`; route missing tooling to `LIMITED`/`BLOCKED_TOOLING`.
- [ ] State candidate safety, licensing, version pinning, privacy, and no-install/no-execute boundaries.
- [ ] Add the reuse record to required start/read and handoff references without making optional providers mandatory.

### Task 4: Extend the validator and keep portable copies synchronized

**Files:**
- Modify: `scripts/validate_kit.py`
- Modify: `tests/test_charter_kit.py`

- [ ] Validate the new template in both locations, required status/decision vocabulary, gate wording in roadmap/prompts/Skill, and byte identity for the new bundled copy.
- [ ] Add negative tests for missing gate, incomplete status, missing waiver evidence, and unsafe “no result” claims.
- [ ] Run the full unittest suite and package validator.

### Task 5: Verify and rebuild the distributable package

**Files:**
- Modify: `README.md`
- Modify: `agentpack.yaml`
- Modify: `DEPENDENCIES.md`
- Modify: `docs/superpowers/plans/2026-08-31-reuse-discovery-gate.md`
- Rebuild: `../charter-kit.zip`

- [ ] Document the new artifact, search tools, optional provider routing, and explicit installation boundary.
- [ ] Run initializer positive/refusal/force-backup smoke checks, official plugin and Skill validators, YAML parsing, and ZIP extraction regression.
- [ ] Confirm no `__pycache__`/`.pyc` files or runtime snapshot writes remain, then report the final ZIP hash and evidence.
