---
name: charter-workflow
description: Use when starting, continuing, reviewing, handing off, or closing a project governed by a project charter or bounded leaf-task contract
---

# Charter Workflow

Use `.charter/` as the shared source of truth across agents and hosts. This Skill is self-contained: it includes the full charter in `references/DEVELOPMENT_CHARTER.md`, the dependency guide and manifest, eight templates, a design-interview fallback, and safe initialization/diagnostic scripts. Loading it never installs a provider or changes a global directory.

## First-start mode

When there is no `.charter/project.md`:

1. Run `scripts/init_project.py <project>` when Python is available, or copy the eight files from `templates/` using the mapping documented in the initializer. Preserve existing files; use `--add-missing` for partial working sets. The initializer writes `.charter/evidence/dependency-check.log` and never installs anything.
2. Read the log. Report `AVAILABLE`, `MISSING`, `UNVERIFIED`, and `FALLBACK`, including capability, reason, impact, fallback, and action. Required gaps remain `BLOCKED_TOOLING`; optional gaps use the portable fallback.
3. Use `grill-me`/`grilling` first for the iterative intent interview. If unavailable, explicitly record `MISSING` and use `references/design-interview.md` as `FALLBACK`; never claim the provider ran. Treat the user's first sentence as an intent seed. Resolve the user/context, pain, observable goal, non-goals, invariants, product loop, assets, reuse scope, effects, success levels, risks, and first bounded behavior.
4. Read `references/DEVELOPMENT_CHARTER.md` and draft every material section of `.charter/project.md`, `.charter/roadmap.md`, and one first `DRAFT` leaf. Complete charter self-review and request `CHARTER_INDEPENDENT` review from a different reviewer in a fresh context/process. Unresolved findings keep the project `BLOCKED`; if fresh review is unavailable, record `BLOCKED_TOOLING` or a user-approved waiver with limitation and expiry.
5. Present the approval bundle and stop for project approval. Project approval never approves a leaf implicitly.
6. After approval, complete authoritative `.charter/reuse-discovery.md` before leaf approval. Search `workspace/history` → installed/cache/manifest → approved internal → official/upstream/registries → authorized public web. Record exact queries, raw evidence, negative results, omitted tiers, candidate checks, and fixed immutable commit/tag/package versions. Discovery is read-only: never clone, build, run, import, copy, install, load candidate instructions, write global directories, or upload private source/secrets/real data. `COMPLETE` requires raw evidence and no unresolved high-value `UNKNOWN`/`DEFER` remains unresolved; `BLOCKED_TOOLING` cannot approve or move a leaf to `READY` unless a bounded `LIMITED`/`WAIVED` downgrade is approved.
7. Obtain separate leaf approval or matching `AUTO_DEV` preauthorization. Move `DRAFT` to `APPROVED` in both the task and roadmap row together, run readiness, then move both to `READY`. Only `READY` may implement.

## Required start for an existing project

Read, in order:

1. `.charter/project.md`
2. `.charter/roadmap.md`
3. `.charter/reuse-discovery.md`
4. `.charter/current-task.md`
5. `.charter/handoff.md`, if present

If a required file is missing or unreadable, add only the missing template and stop until the working set is readable. State the goal, active leaf/status, authoritative reuse gate and ID, allowed effects, authorization reference, open finding, and one exact next action.

## Operating rules

- Keep `WIP = 1`; `NEXT_CANDIDATE` is information, not authorization.
- Stay within the leaf's allowed paths, effects, acceptance, stop conditions, and repair budget.
- Before implementation, resolve the design tree with `grill-me` or the bundled design interview and record it.
- For a feature, bug fix, or refactor, observe RED before GREEN. Route to available Superpowers skills for brainstorming, planning, TDD, debugging, review, and verification; otherwise use the portable checks and record `FALLBACK`.
- Use J-space for long-task ledger/seam/resume support when present; otherwise keep the ledger in `.charter/handoff.md` and the task record.
- Use Review A for contract/implementation coverage. Review B requires a different reviewer and fresh context/process; otherwise record `BLOCKED_TOOLING`.
- Treat P0–P3 finding severity and A/B/C remediation change class as independent axes. C-class changes always require a decision.
- Mirror every task state in the roadmap. `PASS_CLOSED` requires the final candidate, acceptance evidence, review, target-branch integration, and post-integration verification.
- Stop for changes to goal, non-goals, invariants, public meaning, authorization, sensitive data, release, or irreversible effects; write `decision.md`.
- Preserve negative results, unrelated failures, user changes, and provider limitations.
