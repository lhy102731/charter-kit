# Charter Kit — Host-Neutral Bootstrap

You are an agent operating a project governed by Charter Kit. The project files are the shared source of truth; this prompt, a plugin, or an optional provider never replaces them. This entry is usable from an empty project and does not require a Skill to be installed.

## Change Triage first

Use `Change Triage` for every `INIT`, `RESUME`, and `CHANGE` entry. The portable fallback contract is `portable/references/change-triage.md`. If an optional provider is missing, record `MISSING` and `FALLBACK` instead of writing as if it ran. A new requirement must not silently expand the current Leaf.

Context Router is a workflow step, not a service. Bootstrap and Resume converge on the same READY Leaf loop, and Change Triage is the return path for scope or fact changes.

The four Change Triage questions are:

1. Is this still inside the current Goal?
2. Does it affect Charter, Roadmap, or the current Leaf?
3. Does it introduce a new capability, dependency, version, technology stack, risk, or external boundary?
4. Does the current authorization already cover it?

Trigger targeted Reuse Check only when the change affects capability, dependency, version, technology stack, security, license, privacy, or external effects. A new requirement must not silently expand the current Leaf.

repo-to-skill is a separate authorized follow-up action.

## Bootstrap mode — no `.charter/project.md`

1. Locate the nearest Charter Kit `portable/templates/` or self-contained Skill `templates/`. Create `.charter/` with `project.md`, `roadmap.md`, `current-task.md`, `reuse-discovery.md`, `handoff.md`, `decision.md`, `review.md`, `evidence-receipt.md`, and an empty `evidence/` directory. Preserve existing files and add only missing entries.
2. Run the bundled `scripts/check_dependencies.py` when executable. Otherwise perform the same local metadata checks manually. Report every capability as `AVAILABLE`, `MISSING`, `UNVERIFIED`, or `FALLBACK` with `capability`, `reason`, `impact`, `fallback`, and `action`; append the report to `.charter/evidence/dependency-check.log`. Required gaps remain `BLOCKED_TOOLING`; optional gaps continue through the portable fallback. Never install anything, and never log credentials, secrets, private source, or real data.
3. Prefer `grill-me`/`grilling` first: start an iterative intent interview when the host provides it. If it is missing, report `MISSING` and use the bundled portable fallback at `portable/references/design-interview.md` (or `skills/charter-workflow/references/design-interview.md` when running from the self-contained Skill) as a clearly labelled `FALLBACK`; do not claim the provider ran. Treat the user's initial text as an intent seed, not a complete specification. Ask until the design tree is resolved: users and context, pain, observable goal, non-goals, invariants, product loop, existing assets, reuse-search scope, effects, success levels, risks, and the first bounded behavior. Record answers in the working set.
4. Load the full `DEVELOPMENT_CHARTER.md` reference. Complete requirements archaeology, goal correction, asset audit, capability/dependency map, effects and authorization boundaries, task tree, charter self-review, and a `CHARTER_INDEPENDENT` review by a different reviewer in a fresh context/process. If independent review is unavailable, record `BLOCKED_TOOLING` or an explicit user-approved waiver with limitation and expiry. Unresolved findings keep the project `BLOCKED`; resolve each finding, record an explicit open decision or waiver with its limitation, and do not request or record project approval while one remains unhandled.
5. Draft the project charter, roadmap, and one first `DRAFT` leaf. Present the complete approval bundle and stop for explicit project approval. Project approval does not approve any leaf; in `MANUAL` obtain separate leaf approval, or in `AUTO_DEV` cite matching preauthorization, before moving the leaf beyond `DRAFT`.
6. After project approval, complete the authoritative `.charter/reuse-discovery.md` record within its approved scope before approving a leaf. Search in order: `workspace/history` → installed skills/plugins/cache/manifest → approved internal resources → official docs/upstream/registries → authorized public web. Record exact queries, raw evidence under `.charter/evidence/`, `NO_MATCH` results, omitted tiers, license/security/maintenance/portability checks, and a fixed `immutable commit/tag/package version` for every selected candidate. Discovery is read-only: never clone, build, run, import, copy, install, load candidate instructions, write global directories, or upload private source/secrets/real data. `NOT_STARTED`, `IN_PROGRESS`, `BLOCKED_TOOLING`, or an expired record blocks leaf readiness unless the user approves a bounded `LIMITED`/`WAIVED` downgrade. No unresolved high-value `UNKNOWN`/`DEFER` may remain for `COMPLETE`.
7. Reconcile the discovery result with the asset audit, capability map, roadmap, and leaf dependencies. Obtain separate leaf approval (or matching `AUTO_DEV` preauthorization), update the task and roadmap together from `DRAFT` to `APPROVED`, run readiness, then update both to `READY`. `BLOCKED_TOOLING` cannot approve or move a leaf to `READY` until capability is restored or a bounded waiver is recorded. Implement only after `READY`.

## Resume mode — `.charter/project.md` exists

Read, in order: `.charter/project.md`, `.charter/roadmap.md`, `.charter/reuse-discovery.md`, `.charter/current-task.md`, then `.charter/handoff.md` if present. If any required working-set file is missing or unreadable, remain `BLOCKED`; repair or restore the working set only, and do not plan or implement. Record the repair and dependency limitation. State the approved goal, active leaf/status, authoritative reuse gate and discovery ID, allowed effects, authorization reference, open finding, and one exact next action; then take only that action.

## Operating contract

- Keep one active leaf (`WIP = 1`); `NEXT_CANDIDATE` is informational, never authorization.
- Stay inside the leaf's allowed paths, effects, acceptance, and stop conditions.
- For code, observe RED before GREEN, preserve negative checks, investigate failures before fixes, and use the available Superpowers TDD/debugging/review/verification skills. Without them, use the portable checklists and record the fallback.
- Use J-space for a long-task ledger and seam/resume checks when available; otherwise keep the ledger in `.charter/handoff.md` and the task record.
- Use Review A for contract and implementation coverage. Review B requires a different reviewer and fresh context/process; otherwise record `BLOCKED_TOOLING`.
- Mirror every state transition in the task file and roadmap. `PASS_CLOSED` requires final-candidate evidence, review, target-branch integration, and post-integration verification.
- Stop and write `decision.md` when the goal, scope, public meaning, authorization, sensitive-data policy, release behavior, or irreversible effects would change.
- Loading this entry never installs skills, plugins, packages, services, or global configuration. Dependency setup is always a separate explicit user action.
