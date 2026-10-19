# Project Roadmap

## Goal reference

- Project: `Charter Kit`
- Charter: `.charter/project.md`
- Roadmap version: `0.1`
- Last updated: `2026-10-19`

## Delivery order

| Order | ID | Level (`EPIC / CAPABILITY / SLICE / LEAF`) | One observable result | Depends on | Status | Evidence / task file |
|---:|---|---|---|---|---|---|
| 1 | R1 | `EPIC` | Charter Kit 本身受自己的治理，治理证据成为可复核的默认 | — | `IN_PROGRESS` | `.charter/project.md` |
| 2 | R1.1 | `CAPABILITY` | 从零建出可读工作集：章程、路线图、复用门、第一个叶 | R1 | `IN_PROGRESS` | `.charter/current-task.md` |
| 3 | R1.1-S1 | `SLICE` | 工作集填满、复用门 `COMPLETE`、第一个叶 `DRAFT` | R1.1 | `IN_PROGRESS` | `.charter/current-task.md` |
| 4 | R1.1-S1-L1 | `LEAF` | 用本仓自己的模板填出章程与第一个叶合同 | — | `APPROVED` | `.charter/current-task.md` |
| 5 | R1.2 | `CAPABILITY` | 本轮审阅 findings 的复验与提交（条数以 `.charter/records/` 为准）| R1.1 | `PLANNED` | `.charter/roadmap.md` |
| 6 | R1.2-S1 | `SLICE` | 第二次独立 Review A 非 BLOCK，树绿，提交落地 | R1.2 | `PLANNED` | `.charter/roadmap.md` |
| 7 | R1.2-S1-L1 | `LEAF` | 复验并提交本轮修复 | — | `PLANNED` | `.charter/roadmap.md` |
| 8 | R1.3 | `CAPABILITY` | 模板体积上限的决定（D-01） | R1 | `PLANNED` | `.charter/project.md` |
| 9 | R1.4 | `CAPABILITY` | 下游项目级校验（D-05） | R1 | `PLANNED` | `.charter/project.md` |

## Active-work rule

- Active leaf: `R1.1-S1-L1`（`APPROVED`；实现与关闭尚未开始）
- WIP limit per parent: `1`
- Current task contract: `.charter/current-task.md`
- Reuse discovery record: `.charter/reuse-discovery.md`
- Reuse discovery gate: `COMPLETE`（2026-10-20 随章程批准转）
- Gate source of truth: `.charter/reuse-discovery.md`；本行是同步投影，必须与 `project.md` 一致
- Reuse discovery ID: `RD-20261019-01`
- Discovery freshness: `current`（2026-10-19 首检；新能力、栈或边界变化时做定向复核）
- Dependency check evidence: `.charter/evidence/dependency-check.log`（两段：2026-10-19T12:43:28Z 全仓、12:54:05Z 复用阶段；后者另存 `.charter/evidence/reuse-probe-2026-10-19.txt`）
- Next candidate: `R1.2-S1-L1`（信息，不是授权）
- Next authorization: `GRANTED` for `R1.1-S1-L1` only —— 其余候选仍是信息，不是授权

### Change Triage

- current-task.md is the active Leaf state authority; roadmap.md is a projection.
- Use the bundled Change Triage reference when a new requirement, defect, discovered constraint, or risk arrives: `portable/references/change-triage.md` in the full kit or `references/change-triage.md` in the self-contained Skill.
- New requirement must not silently expand the current Leaf.

### Reuse Check projection

- Material target: 见权威记录 `.charter/reuse-discovery.md` 的 `Material target test` 行与其 rationale —— 本行不写取值、不复述理由。
- Coverage / result: 见权威记录第 3 节 Search log 的 `Coverage` / `Result` 两列 —— 本行不写取值。
- Final route / candidate disposition: 见权威记录第 3 节 Search log 的 `Final route` 与第 4 节候选表的 `Disposition` 列 —— 本行不写取值。
- The authoritative record is one project-local `.charter/reuse-discovery.md`; do not create a registry, scoring board, or second memory database.

## Leaf readiness check

Before moving a leaf to `READY`, confirm. Every checklist item carries a stable number (`RDY1`…); leaf contracts reference results by number plus a short label (e.g. `RDY10 recheck trigger current`), never by restating the item text. The numbering is append-only: retired items keep their number with a retirement date, new items take the next number — renumbering would silently change what archived leaf records mean.

- [ ] RDY1 — the leaf contract is `APPROVED` and its approval or preauthorization reference is recorded;
- [ ] RDY2 — predecessor is `—`, or every listed predecessor is actually `PASS_CLOSED`;
- [ ] RDY3 — one observable result is written;
- [ ] RDY4 — allowed paths/effects and forbidden effects are explicit;
- [ ] RDY5 — positive and negative acceptance checks exist;
- [ ] RDY6 — stop conditions and repair budget are written;
- [ ] RDY7 — required host capabilities and approvals are available.
- [ ] RDY8 — the dependency-check record is attached; every required capability is `AVAILABLE`, or an explicit `BLOCKED_TOOLING`/user waiver is recorded.
- [ ] RDY9 — the reuse discovery gate is `COMPLETE`, or this specific Leaf has an explicit, separately approved bounded waiver in `.charter/reuse-discovery.md`; if a bounded limitation or waiver is used, record its approved/omitted scope, limitation, approver, and expiry/recheck condition;
- [ ] RDY10 — the projected gate status matches `.charter/reuse-discovery.md` and `project.md`, and its recheck trigger/date is current; if a trigger applies, a targeted recheck is recorded before this leaf is approved;
- [ ] RDY11 — when the gate is `COMPLETE`, every material capability has in-scope raw evidence, out-of-scope tiers are explicitly `NOT_SEARCHED`/`NOT_AUTHORIZED`, selected revisions are fixed immutable commit/tag/package versions, and no high-value `UNKNOWN`/`DEFER` remains unresolved;
- [ ] RDY12 — every non-workspace/installed search tier used by this leaf is covered by the recorded discovery scope and `External read authorization`;
- [ ] RDY13 — without that leaf-specific waiver, `PENDING`, `BLOCKED`, or `BLOCKED_TOOLING` is treated as blocking; a waiver is not a new gate state or project-wide bypass;

`BLOCKED` and `BLOCKED_TOOLING` block leaf readiness and are never equivalent to approval unless the current Leaf has the explicit bounded waiver above. `PENDING` likewise cannot authorize a leaf without that waiver.

Project approval does not bypass the reuse discovery gate. A `PENDING` or `BLOCKED` record keeps a leaf out of `APPROVED`/`READY` unless that specific Leaf has the recorded, separately approved bounded waiver; the waiver is decision evidence, not a new gate state or project-wide bypass. For later leaves, do not repeat a full search unless a new capability, stack/boundary change, or expiry trigger applies; perform and link a targeted recheck instead. A selected candidate is still only a route decision until its own dependency, installation, and execution authorization exists.

When the authoritative reuse record changes, update its status, this projection, and the project projection in the same change. Any mismatch is a blocking finding, not permission to choose the most optimistic copy.

When moving a leaf from `DRAFT` to `APPROVED`, update the task file and roadmap row together; then move both to `READY` together after readiness. After the checklist passes, update the leaf status and roadmap row to `READY` together, and set `Active leaf` to that ID. Project-charter approval alone never moves a leaf out of `DRAFT`. Mirror the full normal sequence `DRAFT → APPROVED → READY → IN_PROGRESS → REVIEW → VERIFIED → PASS_CLOSED` in the task file and roadmap row. Git integration and post-integration verification are required closure evidence between `VERIFIED` and `PASS_CLOSED`, not additional Leaf states. When the leaf reaches `PASS_CLOSED`, record the closure evidence, clear `Active leaf` (or set it to the next explicitly authorized leaf), and update the row and `Next authorization` together; never leave `Active leaf: NONE` while a leaf is `READY` or `IN_PROGRESS`.

## Closure rule

Only `PASS_CLOSED` leaves may unblock a dependent leaf. A branch commit, a focused green test, or a proposed next candidate is not closure by itself. Update the roadmap after the target branch and post-integration verification are recorded.

## Decisions affecting the route

| Decision ID | Affected IDs | What changed | Approval / evidence |
|---|---|---|---|
| — | — | 尚无影响路线的决定 | — |
