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

- Use the bundled Change Triage reference to classify new requirements, defects, discovered constraints, and risks: `portable/references/change-triage.md` in the full kit or `references/change-triage.md` in the self-contained Skill.
- `CHARTER > ROADMAP > LEAF > IN_CONTRACT` is the precedence order when more than one route seems plausible.
- New requirement must not silently expand the current Leaf.

## 6. Current-state and asset audit

| Asset / capability | Evidence of current state | Classification (`KEEP / ADAPT / REPLACE / ARCHIVE / UNKNOWN`) | Why it serves the goal | Next action |
|---|---|---|---|---|
| `<asset>` | `<test, file, observation>` | `<classification>` | `<reason>` | `<action>` |
| | | | | |

Do not replace an asset merely because a new framework is attractive. Do not keep an asset merely because it exists.

### 6.1 Reuse discovery gate

After this charter's direction is approved, complete the single `.charter/reuse-discovery.md` record before approving or implementing the first leaf. A DRAFT leaf may be prepared during charter engineering, but it cannot move beyond DRAFT while the gate is `PENDING` or `BLOCKED` unless that specific Leaf has an explicit, separately approved bounded waiver recorded in the decision fields. The waiver must name the approved/omitted scope, limitation, approver, and expiry/recheck condition; it is not a fourth gate state or project-wide bypass. First record whether the requested capability is a material target; even `NO_MATERIAL_TARGET` receives a local sanity check. For a material target, choose `FAST`, `STANDARD`, or `DEEP` and search progressively: workspace/history → installed skills/plugins/cache/manifest and framework/SDK/dependencies → approved internal resources → official docs/upstream/registries and other explicitly authorized public sources. Scope meanings are fixed: `LOCAL_ONLY` = workspace/history; `LOCAL_ECOSYSTEM` = workspace/history + installed/cache + approved internal; `FULL_EXTERNAL` = LOCAL_ECOSYSTEM + official/upstream/registries + authorized public web. Record exact queries, coverage (`SEARCHED`, `NOT_SEARCHED`, `NOT_AUTHORIZED`, or `BLOCKED_TOOLING`), results (`MATCH`, `NO_MATCH`, or `UNKNOWN`), raw outputs under `.charter/evidence/`, fixed immutable candidate revisions, and the final route. Candidate disposition and final route are separate fields; `BUILD_NEW` is a capability-level final route justified in the hand-back, not a candidate-row decision.

- Discovery scope: `LOCAL_ONLY | LOCAL_ECOSYSTEM | FULL_EXTERNAL`
- External read authorization: `yes | no`
- Privacy restrictions: `<data that may not enter external queries>`
- Search timebox / query budget: `<bounded limit>`
- Stop condition: `<coverage and saturation rule>`
- Gate result and reviewed on: `<PENDING / COMPLETE / BLOCKED>` / `<date>`
- Latest coverage / result: `<SEARCHED | NOT_SEARCHED | NOT_AUTHORIZED | BLOCKED_TOOLING>` / `<MATCH | NO_MATCH | UNKNOWN>`
- Reuse discovery ID (mirrors the authoritative record): `<RD-...>`
- Limitation, waiver, approver, and recheck trigger: `<reference or none>`

The gate status in this file and in `.charter/roadmap.md` is a projection of the authoritative `.charter/reuse-discovery.md` record. Update all projections in the same change; any disagreement or expired recheck keeps the project/leaf `BLOCKED` until reconciled. A limited or waived search is recorded in the decision/waiver reference with its Leaf, omitted scope, accepted limitation, approver, and recheck condition. A valid leaf-specific waiver may authorize only that Leaf to reach `READY`; it does not create another gate state or change the project-wide projection.

`COMPLETE` requires every material capability to cover its approved scope with raw evidence, explicit out-of-scope coverage, fixed immutable selected revisions, and no unresolved high-value `UNKNOWN` or deferred candidate. `NO_MATCH` is valid only after an exact query ran in the declared scope; `NOT_SEARCHED`, `NOT_AUTHORIZED`, and `BLOCKED_TOOLING` are never `NO_MATCH`. An uncertain item must become a `REUSE_SPIKE`, an explicitly approved bounded waiver for the named Leaf, or a blocking decision; a waiver must explicitly address any high-value `UNKNOWN`/`DEFER` and may not silently turn it into `BUILD_NEW`. A candidate is not permission to install, execute, copy, or change the approved goal; each such action gets its own contract and authorization.

## 7. Capability map

| Capability | Input | Output | Depends on | Required host ability | Observable acceptance | Missing-ability fallback |
|---|---|---|---|---|---|---|
| `<capability>` | `<input>` | `<output>` | `<dependencies>` | `<git / test / network ...>` | `<check>` | `<offline / blocked>` |
| | | | | | | |

For each required or recommended ability, link the latest dependency-check log and state whether it is `AVAILABLE`, `MISSING`, `UNVERIFIED`, or `FALLBACK`.

### 7.1 Review B policy

Review B triggers are kit-owned and cited by ID. The set is append-only: a retired trigger keeps its number and a new one takes the next, so an archived leaf record still means what it meant when it was written. Fill the judgment column once here instead of re-arguing it in every leaf.

| ID | Trigger | This project | Reason or narrowing |
|---|---|---|---|
| RVB1 | Security or authentication | `YES` | `<why it applies, or what a narrowed value excludes>` |
| RVB2 | External dependency | `YES` | `<why it applies, or what a narrowed value excludes>` |
| RVB3 | Public API or public meaning | `YES` | `<why it applies, or what a narrowed value excludes>` |
| RVB4 | High-risk or irreversible effect | `YES` | `<why it applies, or what a narrowed value excludes>` |
| RVB5 | Explicit user request | `YES` | `<why it applies, or what a narrowed value excludes>` |

- Reviewer and freshness method: `<UNDECIDED, or the reviewer class per layer and what makes it fresh>`
- Decided on / by: `<date and approver, or UNDECIDED with the reason it can wait>`

A `YES` row ships enabled and says the trigger is in force, not that it has been hit. Narrowing a row to `NO`, or to a bounded `YES`, is a user decision recorded in `.charter/changelog.md`, and the narrowed value must state what it excludes; a narrowed row with no stated exclusion reads the same as an unfilled one. Leaving a row at `YES` costs a low-risk leaf nothing: that leaf records Review B `NOT_REQUIRED` and names the RVB ids it considered.

If `Reviewer and freshness method` is still `UNDECIDED` when a leaf first records Review B `REQUIRED`, stop and ask the user before implementing that leaf. The method is decided once, where the knowledge is, and then cited. A project that already holds independent-review evidence fills this line from that evidence instead of leaving it `UNDECIDED`.

Compare this table against the RVB list in the workflow Skill whenever either changes. An ID on either side that the other lacks is a recorded gap, not a silent pass: record it here and resolve it before the next leaf enters `READY`.

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

This table is the single authority for a question the project has not settled: it
is where a `NEEDS_DECISION` block is discharged. A decision that needed a full record
lives at `.charter/records/<Decision ID>.md` - the format is `decision.md`, and each
decision is its own file, never an appended ledger - and the roadmap's "Decisions affecting
the route" table is a projection of the rows that changed a route. Neither of
those two decides whether a question is still open - read it here.

| ID | Question / risk | What would settle it | Owner | State |
|---|---|---|---|---|
| D-01 | `<question>` | `<test, decision, or evidence>` | `<owner>` | `OPEN` |
| | | | | |

`State` takes one of these five values and no others:

| State | Means | The row must also carry |
|---|---|---|
| `OPEN` | unsettled | who can settle it, and what evidence would |
| `DECIDED` | settled and current | the decision reference, any limitation accepted, and its expiry or recheck trigger |
| `DEFERRED` | settled as "not now" | the recheck trigger that brings it back |
| `REJECTED` | considered and refused | the reason, so it is not proposed again |
| `EXPIRED` | no longer answerable as written | what superseded it |

A `DECIDED`, `REJECTED`, or `EXPIRED` row that carries its field is what discharges
a `NEEDS_DECISION` block; a state with no carrying field reads as `OPEN` whatever the
cell says. Two review outcomes land here by name: a finding recorded
`ACCEPTED_WITH_LIMITATION` becomes `DECIDED` carrying its limitation and expiry, and
a finding recorded `DECIDED_BACKLOG` becomes `DEFERRED` carrying its recheck trigger.

`OPEN`, `DEFERRED`, and `REJECTED` are live rows and stay: a refusal an agent cannot
see is a refusal it will propose again. A `DECIDED` row leaves only after a decision
record carries the decision in full, and it leaves as a move, never as a deletion -
keep one line with the id, the one-line outcome, and the reference to the record.

## 11. Approval record

- Charter self-review evidence:
- Independent charter review evidence / applicability: `<REQUIRED with trigger/evidence, NOT_REQUIRED with bounded omission reason, or waiver/limitation>`
- Approved goal and non-goals by:
- Approved on:
- Approved success level:
- Approved effects:
- Approval reference:
- Conditions or expiry:

Project-charter approval does not approve the first leaf task. Record leaf approval or matching `AUTO_DEV` preauthorization separately in `.charter/current-task.md` before moving it from `DRAFT` to `APPROVED`.
Before setting `Current status` to `APPROVED`, the self-review field must contain evidence and the independent-review field must record either required review evidence, a bounded `NOT_REQUIRED` reason, or an explicit waiver. If a waiver is used, name the unavailable capability, the approving person, the limitation accepted, and its expiry or re-review condition.

## 12. Change log

The charter's version history lives in `.charter/changelog.md` and is not repeated here.
Only the current version is readable in this file: `Charter version` in section 1. A
resume reads the charter's current state, never its earlier states, so a table
holding both is how a superseded value gets read as the current one. Keep this section
a pointer.

A row is required by these changes, and nothing else: any narrowing of `RVB1`-`RVB5`
or of another risk trigger; any new mandatory contract field or checklist item; any
charter-level or record-level migration; any change to the Goal, Non-goals,
`Invariants`, effect boundary, or release boundary. `.charter/changelog.md` carries the
full rule and the row format; the list above is the part that decides whether a row
exists, and it lives here because this file is read on resume and that one is not.
