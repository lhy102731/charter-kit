# Decision Record

## Decision identity

- Decision ID: `<DEC-ID>`
- Project / task: `<project> / <TASK-ID>`
- Requested by: `<agent/person>`
- Requested at: `<timestamp>`
- Required authority: `OWNER | PRODUCT | SECURITY | PRODUCTION_OPERATOR`
- Status: `OPEN | APPROVED | REJECTED | EXPIRED`

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
