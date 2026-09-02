# Project Roadmap

> Copy this file to `.charter/roadmap.md`. It is the task projection, not a second product specification. Keep the approved goal in `project.md` and link to it here.

## Goal reference

- Project: `<name>`
- Charter: `.charter/project.md`
- Roadmap version: `0.1`
- Last updated: `<YYYY-MM-DD>`

## Delivery order

| Order | ID | Level (`EPIC / CAPABILITY / SLICE / LEAF`) | One observable result | Depends on | Status | Evidence / task file |
|---:|---|---|---|---|---|---|
| 1 | R1 | `EPIC` | `<approved outcome>` | — | `PLANNED` | `.charter/project.md` |
| 2 | R1.1 | `CAPABILITY` | `<capability result>` | R1 | `PLANNED` | `<link>` |
| 3 | R1.1-S1 | `SLICE` | `<small end-to-end behavior>` | R1.1 | `PLANNED` | `<link>` |
| 4 | R1.1-S1-L1 | `LEAF` | `<one behavior>` | — | `DRAFT` | `.charter/current-task.md` |

## Active-work rule

- Active leaf: `NONE` until one approved leaf passes the readiness check
- WIP limit per parent: `1`
- Current task contract: `.charter/current-task.md`
- Reuse discovery record: `.charter/reuse-discovery.md`
- Reuse discovery gate: `PENDING | COMPLETE | BLOCKED`
- Gate source of truth: `.charter/reuse-discovery.md`; this status is a synchronized projection and must match `project.md`.
- Reuse discovery ID: `<RD-...; must match .charter/reuse-discovery.md and project.md>`
- Discovery freshness: `<current, or targeted recheck ID/date when a trigger applies>`
- Dependency check evidence: `<.charter/evidence/dependency-check.log or manual record>`
- Next candidate: `<informational ID; initially the first DRAFT leaf>`
- Next authorization: `NOT_GRANTED`

### Change Triage

- current-task.md is the active Leaf state authority; roadmap.md is a projection.
- Use `portable/references/change-triage.md` when a new requirement, defect, discovered constraint, or risk arrives.
- New requirement must not silently expand the current Leaf.

### Reuse Check projection

- Material target: `YES | NO_MATERIAL_TARGET` (a `NO_MATERIAL_TARGET` leaf still records a local sanity check).
- Coverage / result: `<SEARCHED | NOT_SEARCHED | NOT_AUTHORIZED | BLOCKED_TOOLING>` / `<MATCH | NO_MATCH | UNKNOWN>`.
- Final route: `<ADOPT | ADAPT | REFERENCE_ONLY | BUILD_NEW | REUSE_SPIKE | NEEDS_DECISION>`.
- The authoritative record is one project-local `.charter/reuse-discovery.md`; do not create a registry, scoring board, or second memory database.

## Leaf readiness check

Before moving a leaf to `READY`, confirm:

- [ ] the leaf contract is `APPROVED` and its approval or preauthorization reference is recorded;
- [ ] predecessor is `—`, or every listed predecessor is actually `PASS_CLOSED`;
- [ ] one observable result is written;
- [ ] allowed paths/effects and forbidden effects are explicit;
- [ ] positive and negative acceptance checks exist;
- [ ] stop conditions and repair budget are written;
- [ ] required host capabilities and approvals are available.
- [ ] the dependency-check record is attached; every required capability is `AVAILABLE`, or an explicit `BLOCKED_TOOLING`/user waiver is recorded.
- [ ] the reuse discovery gate is `COMPLETE`; any approved limitation or waiver is recorded in `.charter/reuse-discovery.md` with its omitted scope, approver, and recheck condition;
- [ ] the projected gate status matches `.charter/reuse-discovery.md` and `project.md`, and its recheck trigger/date is current; if a trigger applies, a targeted recheck is recorded before this leaf is approved;
- [ ] when the gate is `COMPLETE`, every material capability has in-scope raw evidence, out-of-scope tiers are explicitly `NOT_SEARCHED`/`NOT_AUTHORIZED`, selected revisions are fixed immutable commit/tag/package versions, and no high-value `UNKNOWN`/`DEFER` remains unresolved;
- [ ] every non-workspace/installed search tier used by this leaf is covered by the recorded discovery scope and `External read authorization`;
- [ ] `BLOCKED` or `BLOCKED_TOOLING` is treated as blocking: do not approve or move a leaf to `READY` until the missing capability/evidence is restored or an explicit decision resolves the limitation;

`BLOCKED` and `BLOCKED_TOOLING` block leaf readiness and are never equivalent to approval. `PENDING` likewise cannot authorize a leaf.

Project approval does not bypass the reuse discovery gate. A `PENDING` or `BLOCKED` record keeps the leaf out of `APPROVED`/`READY`; an explicit limitation or waiver is decision evidence, not a new gate state. For later leaves, do not repeat a full search unless a new capability, stack/boundary change, or expiry trigger applies; perform and link a targeted recheck instead. A selected candidate is still only a route decision until its own dependency, installation, and execution authorization exists.

When the authoritative reuse record changes, update its status, this projection, and the project projection in the same change. Any mismatch is a blocking finding, not permission to choose the most optimistic copy.

When moving a leaf from `DRAFT` to `APPROVED`, update the task file and roadmap row together; then move both to `READY` together after readiness. After the checklist passes, update the leaf status and roadmap row to `READY` together, and set `Active leaf` to that ID. Project-charter approval alone never moves a leaf out of `DRAFT`. Mirror every later leaf state transition (`IN_PROGRESS`, `REVIEW`, `INTEGRATION_PENDING`, `POST_MERGE_VERIFIED`, `PASS_CLOSED`) in the task file and roadmap row in the same change. When the leaf reaches `PASS_CLOSED`, record the closure evidence, clear `Active leaf` (or set it to the next explicitly authorized leaf), and update the row and `Next authorization` together; never leave `Active leaf: NONE` while a leaf is `READY` or `IN_PROGRESS`.

## Closure rule

Only `PASS_CLOSED` leaves may unblock a dependent leaf. A branch commit, a focused green test, or a proposed next candidate is not closure by itself. Update the roadmap after the target branch and post-integration verification are recorded.

## Decisions affecting the route

| Decision ID | Affected IDs | What changed | Approval / evidence |
|---|---|---|---|
| `<DEC-ID>` | `<IDs>` | `<route or scope change>` | `<link>` |
