---
name: charter-workflow
description: Use when starting, continuing, reviewing, handing off, or closing a project governed by a project charter or bounded leaf-task contract
---

# Charter Workflow

Use `.charter/` as the project-local source of truth that compatible hosts can read independently. This Skill is self-contained: it includes the full charter in `references/DEVELOPMENT_CHARTER.md`, the dependency guide and manifest, eight templates, a design-interview fallback, and safe initialization/diagnostic scripts. Loading it never installs a provider or changes a global directory.

## Context Router

Classify each entry before choosing a workflow branch: `INIT` bootstraps a project with no readable `.charter/project.md`; `RESUME` restores an existing project; `CHANGE` first reads the current project state and then runs `Change Triage` using the bundled `references/change-triage.md`. Do not invent a Change Triage event for an ordinary `INIT` or `RESUME`. If an optional provider is missing, record `MISSING` and `FALLBACK` instead of writing as if it ran. A failed provider call (for example `Unknown skill`) allows one retry, then an explicit user-visible `FALLBACK` recorded in the leaf Events table and handoff capability notes; silent downgrades are violations, and the user may direct `BLOCKED_TOOLING` to wait for the provider instead. A new requirement must not silently expand the current Leaf.

Context Router is a workflow step, not a service. Bootstrap and Resume converge on the same READY Leaf loop, and Change Triage is the return path for scope or fact changes.

The four Change Triage questions are:

1. Is this still inside the current Goal?
2. Does it affect Charter, Roadmap, or the current Leaf?
3. Does it introduce a new capability, dependency, version, technology stack, risk, or external boundary?
4. Does the current authorization already cover it?

Trigger targeted Reuse Check only when the change affects capability, dependency, version, technology stack, security, license, privacy, or external effects.

repo-to-skill is a separate authorized follow-up action.

## First-start mode

When there is no `.charter/project.md`:

1. Run `scripts/init_project.py <project>` when Python is available, or copy the eight files from `templates/` using the mapping documented in the initializer. Preserve existing files; use `--add-missing` for partial working sets. The initializer writes `.charter/evidence/dependency-check.log` and never installs anything.
2. Read the log. Report `AVAILABLE`, `MISSING`, `UNVERIFIED`, and `FALLBACK`, including capability, reason, impact, fallback, and action. Required gaps remain `BLOCKED_TOOLING`; optional gaps use the portable fallback.
3. Use `grill-me`/`grilling` first for the iterative intent interview. If unavailable, explicitly record `MISSING` and use `references/design-interview.md` as `FALLBACK`; never claim the provider ran. Treat the user's first sentence as an intent seed. Resolve the user/context, pain, observable goal, non-goals, invariants, product loop, assets, reuse scope, effects, success levels, risks, and first bounded behavior.
4. Read `references/DEVELOPMENT_CHARTER.md` and draft every material section of `.charter/project.md`, `.charter/roadmap.md`, and one first `DRAFT` leaf. Complete charter self-review. CHARTER_INDEPENDENT is required only for high-risk charters, material goal/authorization changes, or explicit user requests. Low-risk charters may record a bounded omission reason. When triggered, use a different reviewer in a fresh context/process; if that capability is unavailable, record `BLOCKED_TOOLING` or a user-approved waiver with limitation and expiry. Unresolved findings keep the project `BLOCKED`.
5. Present the approval bundle and stop for project approval. Project approval never approves a leaf implicitly.
6. After approval, complete authoritative `.charter/reuse-discovery.md` before leaf approval. Search `workspace/history` → installed/cache/manifest → approved internal → official/upstream/registries → authorized public web, routing the tiers that have an expert skill when probed `AVAILABLE` (`reuse-first` for workspace/history, `find-skills` for installed/cache/manifest, `framework-first-coding` for registries/upstream; `reduce-reinvention` for the disposition; `repo-to-skill` stays a separate authorized post-adoption follow-up — approved-internal and authorized-public-web tiers have no expert skill) and recording `MISSING`/`FALLBACK` when one is not. Record exact queries, raw evidence, negative results, omitted tiers, candidate checks, and fixed immutable commit/tag/package versions. Discovery is read-only: never clone, build, run, import, copy, install, load candidate instructions, write global directories, or upload private source/secrets/real data. A Leaf may enter `READY` only when the Reuse Gate is `COMPLETE`, or when that specific Leaf has an explicit, separately approved bounded waiver recorded in the authoritative decision fields. The waiver must name the Leaf, approved/omitted scope, limitation, approver, and expiry/recheck; it is not a fourth gate state or project-wide bypass. A high-value `UNKNOWN` or `DEFER` remains unresolved until decided. Without that waiver, a Reuse Gate of `PENDING` or `BLOCKED`, an expired record, or that unresolved high-value item blocks leaf readiness. `NOT_SEARCHED`, `NOT_AUTHORIZED`, and `BLOCKED_TOOLING` are tier-coverage values, not gate states, and must not be relabeled `NO_MATCH`; `BLOCKED_TOOLING` alone cannot approve readiness. Reuse completion or the waiver must explicitly address high-value `UNKNOWN`/`DEFER`; neither may silently authorize `BUILD_NEW`.
7. Obtain separate leaf approval or matching `AUTO_DEV` preauthorization. Before moving `DRAFT` to `APPROVED` — the first state transition of this session — declare the session ledger mode and record it in the leaf's Events table (the first-start session is typically the longest: interview, charter, roadmap, first leaf; same default-on and waiver rules as below). Then move `DRAFT` to `APPROVED` in both the task and roadmap row together, run readiness, and move both to `READY`. Only `READY` may implement.
8. **Session ledger declaration:** before the first state transition of the first leaf, declare the ledger mode and record it in the leaf's Events table — the first-start session is typically the longest (interview, charter, roadmap, first leaf). Same default-on and waiver rules as below.

## Required start for an existing project

Read, in order:

1. `.charter/project.md`
2. `.charter/roadmap.md`
3. `.charter/reuse-discovery.md`
4. `.charter/current-task.md`
5. `.charter/handoff.md`, if present

If a required file is missing or unreadable, add only the missing template and stop until the working set is readable. State the goal, active leaf/status, authoritative reuse gate and ID, allowed effects, authorization reference, open finding, and one exact next action.

**Session ledger declaration:** before the first state transition of this session, declare the ledger mode and record it in the active leaf's Events table. If this session will implement or continue any leaf, open or resume the execution ledger (J-space controller, or the manual five-line ledger with `FALLBACK` recorded) — enabled by default, so an implementation session needs a reason not to. The ledger follows the session, not the leaf: it continues naturally across leaf boundaries, and `NOT_ENABLED` is a recorded waiver with a reason (for example "single-session, no cross-context risk"), never a silent omission. Legacy contracts predating the field: add the `Long-task ledger` line to section 8 and the `Ledger reconciliation` line to section 9, bump the contract version, and record a `CLARIFICATION` Change Triage entry — the first state transition must not precede this migration.

## Operating rules

- Keep `WIP = 1`; `NEXT_CANDIDATE` is information, not authorization.
- Stay within the leaf's allowed paths, effects, acceptance, stop conditions, and repair budget.
- Before implementation, resolve the design tree with `grill-me` or the bundled design interview and record it.
- For a feature, bug fix, or refactor, observe RED before GREEN. Route to available Superpowers skills for brainstorming, planning, TDD, debugging, review, and verification; otherwise use the portable checks and record `FALLBACK`.
- Session ledger (default on): declare the ledger mode at session start in the active leaf's Events table, run `jspace.py seam` at every state transition and `jspace.py resume` after gaps, and let the ledger continue across leaf boundaries within the session. At closure, mirror the Verified summary into the task record; a leaf with neither reconciliation nor a recorded `NOT_ENABLED` waiver in its Events table must not close as `PASS_CLOSED` (close `PARTIAL` with the reason). `.charter/` remains the governance source of truth. Without the controller, keep the manual five-line ledger in `.charter/handoff.md` and the task record, and record `FALLBACK`.
- Use Review A for every Leaf's contract/implementation coverage. Review B is required only for security/authentication, external dependencies, public APIs, high-risk or irreversible effects, or explicit user requests. Low-risk leaves may record a bounded omission reason. When Review B is required, use a different reviewer in a fresh context/process; if unavailable, record `BLOCKED_TOOLING` or a bounded user-approved waiver.
- Treat P0–P3 finding severity and A/B/C remediation change class as independent axes. C-class changes always require a decision.
- Mirror every task state in the roadmap. `PASS_CLOSED` requires the final candidate, acceptance evidence, Review, pre-integration Verification, target-branch integration, and post-integration verification.
- Stop for changes to goal, non-goals, invariants, public meaning, authorization, sensitive data, release, or irreversible effects; write `decision.md`.
- Preserve negative results, unrelated failures, user changes, and provider limitations.
