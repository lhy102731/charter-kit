# Project Charter

> Copy this file to `.charter/project.md`. Replace every angle-bracket field before approving the project. Keep it short enough to reread, but do not remove a section because the project feels small.

## 1. Identity

- Project: `<name>`
- Charter version: `0.1`
- Owner / approver: `<person or role>`
- Date: `<YYYY-MM-DD>`
- Current status: `DRAFT | APPROVED | BLOCKED | BLOCKED_TOOLING | NEEDS_DECISION | PARTIAL | PAUSED | SUPERSEDED | CLOSED`
- Current success level: `<project-defined level; name, entry condition, and evidence below>`
- Reuse discovery gate: `PENDING | COMPLETE | BLOCKED`
- Reuse discovery record: `.charter/reuse-discovery.md`
- Reuse material-target / final-route projection: `<YES | NO_MATERIAL_TARGET>` / `<ADOPT | ADAPT | REFERENCE_ONLY | BUILD_NEW | REUSE_SPIKE | NEEDS_DECISION>`
- Intent interview evidence: `<path/ID; provider, rounds, unresolved branches, and user confirmation>`
- Intent interview mode: `GRILL_ME | PORTABLE_FALLBACK | NOT_STARTED`

## 2. Desired outcome

### Goal

Write one sentence describing the observable result a user or operator should receive:

> `<When ... happens, ... can ... with ...>`

### User and context

- Primary user:
- Trigger or situation:
- Existing pain:
- Evidence that the pain is real:

### Non-goals for this charter version

-
-
-

### Invariants

These remain true even when the implementation changes:

-
-
-

## 3. Product loop

Describe the shortest chain from input to outcome. Use the project's own domain terms; a useful neutral shape is `input → processing → verification → observable outcome → next action`.

```text
Input → <step> → <step> → Observable outcome
```

The chain is the product. Gates, logs, branch names, and agent count are supporting controls, not the outcome.

## 4. Success levels and proof

Define project-specific success levels. Each level needs an entry condition, an observable result, required evidence, and an explicit unverified boundary. The following are optional neutral examples; rename or replace them as needed:

| Level | What must be true | Evidence required | Current result |
|---|---|---|---|
| COMPONENT | One component can be called under its contract | focused check or test | `<not started / result>` |
| SYNTHETIC | A controlled sample or offline end-to-end path works | reproducible run record | `<not started / result>` |
| INTEGRATED | The relevant project parts cooperate within the declared boundary | integration evidence | `<not started / result>` |
| USER_VALIDATED | A target user confirms the result in the stated context | user validation record | `<not started / result>` |
| RELEASE_AUTHORIZED | A responsible person approves release and post-release checks pass | authorization and release evidence | `<not started / result>` |

State explicitly which level this charter is allowed to reach. Never describe a lower level as a higher one.

## 5. Scope and effects

### Included

-
-

### Allowed effects

Mark only what this charter authorizes; add project-specific effects when needed:

- [ ] `read_only`
- [ ] `sample_run`
- [ ] `code_write`
- [ ] `local_merge`
- [ ] `external_service`
- [ ] `sensitive_data`
- [ ] `release`
- [ ] `irreversible`

### Forbidden effects

-
-

Sensitive data, release changes, credential changes, and irreversible external actions require a separate decision record even if the project later needs them.

### Change Triage

- Use `portable/references/change-triage.md` to classify new requirements, defects, discovered constraints, and risks.
- `CHARTER > ROADMAP > LEAF > IN_CONTRACT` is the precedence order when more than one route seems plausible.
- New requirement must not silently expand the current Leaf.

## 6. Current-state and asset audit

| Asset / capability | Evidence of current state | Classification (`KEEP / ADAPT / REPLACE / ARCHIVE / UNKNOWN`) | Why it serves the goal | Next action |
|---|---|---|---|---|
| `<asset>` | `<test, file, observation>` | `<classification>` | `<reason>` | `<action>` |
| | | | | |

Do not replace an asset merely because a new framework is attractive. Do not keep an asset merely because it exists.

### 6.1 Reuse discovery gate

After this charter's direction is approved, complete the single `.charter/reuse-discovery.md` record before approving or implementing the first leaf. A DRAFT leaf may be prepared during charter engineering, but it cannot move beyond DRAFT while the gate is `PENDING` or `BLOCKED`. First record whether the requested capability is a material target; even `NO_MATERIAL_TARGET` receives a local sanity check. For a material target, choose `FAST`, `STANDARD`, or `DEEP` and search progressively: workspace/history → installed skills/plugins/cache/manifest and framework/SDK/dependencies → approved internal resources → official docs/upstream/registries and other explicitly authorized public sources. Scope meanings are fixed: `LOCAL_ONLY` = workspace/history; `LOCAL_ECOSYSTEM` = workspace/history + installed/cache + approved internal; `FULL_EXTERNAL` = LOCAL_ECOSYSTEM + official/upstream/registries + authorized public web. Record exact queries, coverage (`SEARCHED`, `NOT_SEARCHED`, `NOT_AUTHORIZED`, or `BLOCKED_TOOLING`), results (`MATCH`, `NO_MATCH`, or `UNKNOWN`), raw outputs under `.charter/evidence/`, fixed immutable candidate revisions, and the final route. Candidate disposition and final route are separate fields; `BUILD_NEW` is a capability-level final route justified in the hand-back, not a candidate-row decision.

- Discovery scope: `LOCAL_ONLY | LOCAL_ECOSYSTEM | FULL_EXTERNAL`
- External read authorization: `yes | no`
- Privacy restrictions: `<data that may not enter external queries>`
- Search timebox / query budget: `<bounded limit>`
- Stop condition: `<coverage and saturation rule>`
- Gate result and reviewed on: `<PENDING / COMPLETE / BLOCKED>` / `<date>`
- Latest coverage / result: `<SEARCHED | NOT_SEARCHED | NOT_AUTHORIZED | BLOCKED_TOOLING>` / `<MATCH | NO_MATCH | UNKNOWN>`
- Reuse discovery ID (mirrors the authoritative record): `<RD-...>`
- Limitation, waiver, approver, and recheck trigger: `<reference or none>`

The gate status in this file and in `.charter/roadmap.md` is a projection of the authoritative `.charter/reuse-discovery.md` record. Update all projections in the same change; any disagreement or expired recheck keeps the project/leaf `BLOCKED` until reconciled. A limited or waived search is recorded in the decision/waiver reference with its omitted scope, accepted limitation, approver, and recheck condition; it does not create another gate state.

`COMPLETE` requires every material capability to cover its approved scope with raw evidence, explicit out-of-scope coverage, fixed immutable selected revisions, and no unresolved high-value `UNKNOWN` or deferred candidate. `NO_MATCH` is valid only after an exact query ran in the declared scope; `NOT_SEARCHED`, `NOT_AUTHORIZED`, and `BLOCKED_TOOLING` are never `NO_MATCH`. An uncertain item must become a `REUSE_SPIKE`, an approved waiver recorded in the decision field, or a blocking decision. A candidate is not permission to install, execute, copy, or change the approved goal; each such action gets its own contract and authorization.

## 7. Capability map

| Capability | Input | Output | Depends on | Required host ability | Observable acceptance | Missing-ability fallback |
|---|---|---|---|---|---|---|
| `<capability>` | `<input>` | `<output>` | `<dependencies>` | `<git / test / network ...>` | `<check>` | `<offline / blocked>` |
| | | | | | | |

For each required or recommended ability, link the latest dependency-check log and state whether it is `AVAILABLE`, `MISSING`, `UNVERIFIED`, or `FALLBACK`.

## 8. Task tree and route

```text
Epic: <outcome>
  └─ Capability: <capability>
      └─ Vertical slice: <small end-to-end behavior>
          └─ Leaf: <single observable behavior>
          └─ Leaf: <single observable behavior>
```

Rules for leaves:

- one observable behavior per leaf;
- explicit predecessor and allowed scope;
- a test or inspection that can prove the result;
- a stop line and a repair budget;
- default `WIP = 1` for each parent.

## 9. Automatic development authorization

- Mode: `MANUAL | AUTO_DEV`
- Authorized task IDs or range:
- Allowed effects for automatic continuation:
- Maximum repair iterations per leaf:
- Allowed B-class changes:
- Mandatory stop conditions:
- Expiry or review date:

Automatic continuation never includes a change to the Goal, Non-goals, Invariants, release boundary, sensitive-data policy, public semantic contract, or irreversible external effect.

## 10. Risks and open decisions

| ID | Question / risk | What would settle it | Owner | State |
|---|---|---|---|---|
| D-01 | `<question>` | `<test, decision, or evidence>` | `<owner>` | `OPEN` |
| | | | | |

## 11. Approval record

- Charter self-review evidence:
- Independent charter review evidence, or explicit waiver / limitation:
- Approved goal and non-goals by:
- Approved on:
- Approved success level:
- Approved effects:
- Approval reference:
- Conditions or expiry:

Project-charter approval does not approve the first leaf task. Record leaf approval or matching `AUTO_DEV` preauthorization separately in `.charter/current-task.md` before moving it from `DRAFT` to `APPROVED`.
Before setting `Current status` to `APPROVED`, the self-review field and the independent-review field must contain non-empty evidence references. If a waiver is used, name the unavailable capability, the approving person, the limitation accepted, and its expiry or re-review condition.

## 12. Change log

| Version | Date | Change | Reason | Approved by |
|---|---|---|---|---|
| 0.1 | `<date>` | Initial charter | `<reason>` | `<person>` |
