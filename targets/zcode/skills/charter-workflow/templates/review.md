# Review Record

## Review identity

- Review ID: `<REV-ID>`
- Task ID: `<TASK-ID>`
- Candidate revision: `<branch/commit/provider revision>`
- Reviewer: `<agent/person>`
- Host / process / session: `<reference>`
- Review type: `CHARTER_INDEPENDENT | A_SPEC_AND_CODE | B_FRESH_BEHAVIOR`
- Applicability: `REQUIRED | NOT_REQUIRED`
- Trigger or bounded omission reason: `<risk/user trigger, or why an independent review is not required>`
- Started: `<timestamp>`
- Finished: `<timestamp>`

## Independence declaration

- Different from implementer: `yes | no`
- Fresh context: `yes | no | unavailable`
- Fresh process: `yes | no | unavailable`
- Read implementer report before testing: `yes | no`
- Limitation on independence:

Review A is required for every Leaf. `CHARTER_INDEPENDENT` and `B_FRESH_BEHAVIOR` are risk-triggered or explicitly user-requested. When either is `REQUIRED`, the reviewer must be different from the implementer/author and use a fresh context or independent process; if that capability is unavailable, record `BLOCKED_TOOLING` or an explicit bounded waiver. When it is `NOT_REQUIRED`, record the bounded omission reason. Do not rename a self-review as an independent review.

## Checks performed

- [ ] Goal and task contract match.
- [ ] Design interview record exists and its branches are resolved or explicitly deferred.
- [ ] Allowed paths and effects respected.
- [ ] Positive acceptance checks pass.
- [ ] Negative and boundary checks pass.
- [ ] Tests assert behavior rather than implementation details.
- [ ] Candidate reference is the version actually reviewed.
- [ ] Applicable reuse discovery record is current, its candidates have explicit decisions, and selected revisions/licenses are pinned.
- [ ] Any `UNKNOWN` result, `DEFER` candidate, `NO_MATCH` claim, or missing search tier has a recorded limitation, `REUSE_SPIKE`, waiver, or blocking decision.
- [ ] Existing user changes and unrelated failures are separated.
- [ ] Integration and post-merge requirements are understood.

## Change Triage

- Record the observed event kind and route from the bundled Change Triage reference: `portable/references/change-triage.md` in the full kit or `references/change-triage.md` in the self-contained Skill.
- Confirm whether the reviewed change stayed `IN_CONTRACT` or required `LEAF_CHANGE`, `ROADMAP_CHANGE`, or `CHARTER_CHANGE`.
- New requirement must not silently expand the current Leaf.

## Findings

| ID | Finding severity (`P0 / P1 / P2 / P3`) | Remediation change class (`A / B / C`) | Finding | Evidence reference | Required action |
|---|---|---|---|---|---|
| F-01 | `<severity>` | `<change class>` | `<specific observed issue>` | `<raw ref>` | `<fix / decision / backlog>` |

No findings is a valid result only after every applicable check above has an observation.

Severity describes impact and urgency: `P0` blocks or risks immediate critical harm, `P1` is a major user or contract failure, `P2` is a bounded non-critical defect, and `P3` is a minor issue or polish. Change class describes the authorization needed for the proposed remedy. They are independent axes; any C-class remedy requires a decision regardless of severity, and a P0/P1 finding still receives urgent handling even when its remedy is A-class.

## Verdict

Choose one:

- `APPROVE`
- `APPROVE_WITH_LIMITATIONS`
- `REQUEST_CHANGES`
- `BLOCKED_TOOLING`
- `NEEDS_DECISION`

Reason:

`<one paragraph tied to the candidate and evidence>`

## Re-review trigger

Any change to the reviewed behavior, candidate revision, scope, or public meaning requires a new review. Unchanged evidence may be referenced only when the reviewed candidate relation is clear.
