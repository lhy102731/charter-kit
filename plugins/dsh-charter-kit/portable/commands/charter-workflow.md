---
description: Start or resume the host-neutral Charter Kit development workflow
argument-hint: [one-sentence intent seed for a new project; leave empty to resume]
---

# Charter Workflow Entry

Run the Charter Kit workflow. Choose the branch from project state; do not skip an approval or evidence gate. The command is usable from zero: an installed Skill is helpful but never a prerequisite.

## Bootstrap mode — no `.charter/project.md`

1. Locate the nearest `portable/templates/` or Skill `templates/` and create the standard `.charter/` working set: `project.md`, `roadmap.md`, `current-task.md`, `reuse-discovery.md`, `handoff.md`, `decision.md`, `review.md`, `evidence-receipt.md`, plus `evidence/`. Preserve existing files and add only missing entries.
2. Run `scripts/check_dependencies.py` when available (or perform equivalent local checks). Report `AVAILABLE`, `MISSING`, `UNVERIFIED`, and `FALLBACK` with capability, reason, impact, fallback, and action, and append the report to `.charter/evidence/dependency-check.log`. Required gaps remain `BLOCKED_TOOLING`; optional gaps use the portable fallback. Never install, and never record credentials, secrets, private source, or real data.
3. Use `grill-me`/`grilling` first for a multi-round intent interview. If absent, report `MISSING` and use the portable fallback at `portable/references/design-interview.md` (or `skills/charter-workflow/references/design-interview.md` when running from the self-contained Skill) as `FALLBACK`; do not claim the provider ran. `$ARGUMENTS` is only a seed. Resolve user/context, pain, observable goal, non-goals, invariants, product loop, assets, reuse scope, effects, success levels, risks, and one first bounded behavior; record the answers.
4. Load `DEVELOPMENT_CHARTER.md`, complete the full charter-engineering loop (requirements archaeology, goal correction, asset/capability audit, authorization boundaries, task tree, self-review), and obtain `CHARTER_INDEPENDENT` review from a different reviewer in a fresh context/process. If unavailable, record `BLOCKED_TOOLING` or a user-approved waiver with limitation and expiry. Unresolved findings keep the project `BLOCKED`; resolve each finding, record an explicit open decision or waiver with its limitation, and do not request or record project approval while one remains unhandled.
5. Draft the project charter, roadmap, and one first `DRAFT` leaf. Present the approval bundle and stop for explicit project approval; project approval does not approve the leaf.
6. After project approval, complete authoritative `.charter/reuse-discovery.md` in the approved scope before leaf approval. Search `workspace/history`, installed/cache/manifest, approved internal resources, official/upstream/registries, then authorized public web. Record exact queries, raw evidence under `.charter/evidence/`, negative results, omitted tiers, candidate checks, and fixed `immutable commit/tag/package version` values. Discovery is read-only: never clone, build, run, import, copy, install, load candidate instructions, write global directories, or upload private source/secrets/real data. `NOT_STARTED`, `IN_PROGRESS`, `BLOCKED_TOOLING`, or an expired record blocks leaf readiness unless a bounded `LIMITED`/`WAIVED` downgrade is explicitly approved; `COMPLETE` has no unresolved high-value `UNKNOWN`/`DEFER` remains unresolved.
7. Reconcile the result, obtain separate leaf approval or matching `AUTO_DEV` preauthorization, update task and roadmap together `DRAFT → APPROVED`, run readiness, then together to `READY`. `BLOCKED_TOOLING` cannot approve or move a leaf to `READY`. Implement only after `READY`.

## Resume mode — `.charter/project.md` exists

Read `.charter/project.md`, `.charter/roadmap.md`, `.charter/reuse-discovery.md`, `.charter/current-task.md`, and `.charter/handoff.md` if present. If a required file is missing or unreadable, add only that template, record the repair/limitation, and do not plan or implement in that step. State the goal, active leaf/status, authoritative reuse gate and discovery ID, allowed effects, authorization reference, open finding, and one exact next action; then take only that action.

## Shared rules

- Keep `WIP = 1`; `NEXT_CANDIDATE` is informational and never authorization.
- Follow the leaf's allowed paths, effects, acceptance, and stop conditions. Use RED → GREEN and preserve negative checks.
- Route work to optional Superpowers, J-space, and grill-me providers when present; when missing, emit `MISSING`/`UNVERIFIED`, explain the impact, and use the documented portable fallback. Never silently simulate a provider.
- Review B requires a different reviewer and fresh context/process; otherwise record `BLOCKED_TOOLING`.
- Mirror all task states in the roadmap. `PASS_CLOSED` requires final-candidate evidence, review, target-branch integration, and post-integration verification.
- Stop and write `decision.md` for changes to goal, scope, public meaning, authorization, sensitive data, release behavior, or irreversible effects.
- Loading this command never installs skills, plugins, packages, services, or global configuration; dependency setup is a separate explicit user action.
