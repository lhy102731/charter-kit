# Decision Record

## Decision identity

- Decision ID: `DEC-<YYYYMMDD>-<slug>`
- Project / task: `<project> / <TASK-ID>`
- Requested by: `<agent/person>`
- Requested at: `<timestamp>`
- Required authority: `OWNER | PRODUCT | SECURITY | PRODUCTION_OPERATOR`
- Status: `OPEN | DECIDED | REJECTED | EXPIRED`
  A `DEFERRED` question lives in `project.md` section 10 and has not become a decision
  record yet. `DECIDED` is the same word section 10 uses for a settled row; a record written
  before this wording may say `APPROVED` - read it as `DECIDED` and do not write it again.

A decision is project-scoped, not leaf-scoped: two leaves can open decisions in the same session, so a per-leaf sequence would mint one id twice. A date plus a slug needs no central allocator to stay unique, and each decision is its own file at `.charter/records/<Decision ID>.md` - a later decision is a new file, not an edit.

## Question that cannot be solved inside the current contract

`<State the exact choice. Do not hide a scope change inside an implementation note.>`

## Why it matters

- Current contract says:
- Evidence so far:
- If we continue without a decision:
- Goal or invariant at risk:

## Change Triage

- Record the event kind and route from the bundled Change Triage reference: `portable/references/change-triage.md` in the full kit or `references/change-triage.md` in the self-contained Skill.
- `CHARTER > ROADMAP > LEAF > IN_CONTRACT` decides whether the request stays local or needs a broader change.
- New requirement must not silently expand the current Leaf.

## Options

| Option | Effect on goal | Cost / risk | Reversibility | Evidence needed |
|---|---|---|---|---|
| A: `<option>` | `<impact>` | `<impact>` | `<high/low>` | `<evidence>` |
| B: `<option>` | `<impact>` | `<impact>` | `<high/low>` | `<evidence>` |

## Recommendation

`<recommended option and why>`

## Approval

- Decision: `<A / B / hold / stop / reopen>`
- Approved by:
- Approval reference:
- Approved scope/effects:
- Expiry or conditions:
- Follow-up task or charter version:

## After the decision

- Update the project charter if Goal, Non-goals, Invariants, success level, or authorization changed.
- Create a new task candidate if the current contract changed materially.
- Preserve the original evidence and record which candidate it applies to.
