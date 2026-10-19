# Review Record

## Review identity

- Review ID: `REV-<TASK-ID>-<nn>`
- Task ID: `<TASK-ID>`
- Candidate revision: `<branch/commit/provider revision>`
- Reviewer: `<agent/person>`
- Host / process / session: `<reference>`
- Review type: `CHARTER_INDEPENDENT | A_SPEC_AND_CODE | B_FRESH_BEHAVIOR`
- Freshness (Review A): `fresh-subagent (no implementation context; fed leaf contract + spec + diff) | same-context (FALLBACK recorded, naming the lost independence)`
- Freshness (Review B): `fresh subagent, distinct from the Review A reviewer`
- Applicability: `REQUIRED | NOT_REQUIRED`
- Trigger or bounded omission reason: `<the RVB id(s) hit for `B_FRESH_BEHAVIOR`, or the RVB ids considered and why an independent review is not required>`
- Started: `<timestamp>`
- Finished: `<timestamp>`

The id is scoped by the task under review, so two leaves reviewed in the same session never mint the same id. Each review is its own file at `.charter/records/<Review ID>.md`: a second review of the same leaf is a new file, never an overwrite of the earlier one.

## Independence declaration

- Different from implementer: `yes | no`
- Fresh context: `yes | no | unavailable`
- Fresh process: `yes | no | unavailable`
- Read implementer report before testing: `yes | no`
- Limitation on independence:

Review A is required for every Leaf. `CHARTER_INDEPENDENT` and `B_FRESH_BEHAVIOR` are risk-triggered or explicitly user-requested; `B_FRESH_BEHAVIOR` applicability is decided by the `RVB1`-`RVB5` triggers recorded in `.charter/project.md` section 7.1 and is cited by id rather than re-argued here. When either is `REQUIRED`, the reviewer must be different from the implementer/author and use a fresh context or independent process; if that capability is unavailable, record `BLOCKED_TOOLING` or an explicit bounded waiver. When it is `NOT_REQUIRED`, record the bounded omission reason. Do not rename a self-review as an independent review.

## Checks performed

Checks are cited by their `CHK` id - never by position, never by restating the
text. The list is append-only: a new check appends at the end, existing text is
reworded only where the wording was wrong, and an id never moves to different
text and never disappears. Review records already written cite these ids, so a
renumbering would silently change what an archived record means. A check that
does not apply to this leaf is answered `N/A` with the reason; it is never
deleted.

This section is required in every review record: a record that omits it is not a record - mark the record `INVALID` rather than leaving the section out. Records written before a check existed keep the checks they were written against and are never retro-fitted; the id list below is what the reviewer of that version can be held to.

- [ ] `CHK1` Goal and task contract match.
- [ ] `CHK2` Design interview record exists and its branches are resolved or explicitly deferred.
- [ ] `CHK3` Allowed paths and effects respected.
- [ ] `CHK4` Positive acceptance checks pass.
- [ ] `CHK5` Negative and boundary checks pass.
- [ ] `CHK6` Tests assert behavior rather than implementation details.
- [ ] `CHK7` Candidate reference is the version actually reviewed.
- [ ] `CHK8` Applicable reuse discovery record is current, its candidates have explicit decisions, and selected revisions/licenses are pinned.
- [ ] `CHK9` Any `UNKNOWN` result, `DEFER` candidate, `NO_MATCH` claim, or missing search tier has a recorded limitation, `REUSE_SPIKE`, waiver, or blocking decision.
- [ ] `CHK10` Existing user changes and unrelated failures are separated.
- [ ] `CHK11` Integration and post-merge requirements are understood.
- [ ] `CHK12` Every default-on rule this leaf touched is visible in a file the next session reads; any narrowing names what it excludes, its approver, its date, and the file that owns the policy. This is hook `DOP3` of `portable/references/default-on-policy.md` (`references/default-on-policy.md` in the self-contained Skill).
- [ ] `CHK13` Every finding carries a `Disposition`, and every finding that is not `CLOSED` names its limitation, expiry or recheck trigger, and the section-10 or decision entry that carries it.
- [ ] `CHK14` Every measurement the read set states points to its single authority instead of copying the value; every changing state appears only in the projection that the charter declares for it, and that declaration names every place that carries the value; and every exception this review claims is written here as `item | clause | basis`, with `Exceptions claimed: none` when there is none.

## Change Triage

- Record the observed event kind and route from the bundled Change Triage reference: `portable/references/change-triage.md` in the full kit or `references/change-triage.md` in the self-contained Skill.
- Confirm whether the reviewed change stayed `IN_CONTRACT` or required `LEAF_CHANGE`, `ROADMAP_CHANGE`, or `CHARTER_CHANGE`.
- New requirement must not silently expand the current Leaf.

## Findings

| ID | Finding severity (`P0 / P1 / P2 / P3`) | Remediation change class (`A / B / C`) | Finding | Evidence reference | Required action | Disposition |
|---|---|---|---|---|---|---|
| F-01 | `<severity>` | `<change class>` | `<specific observed issue>` | `<raw ref>` | `<fix / decision / backlog>` | `<CLOSED / ACCEPTED_WITH_LIMITATION / DECIDED_BACKLOG / OPEN>` |

Every finding carries a `Disposition`; a blank cell is not one. `OPEN` is valid
only alongside a verdict of `REQUEST_CHANGES`, `BLOCKED_TOOLING`, or
`NEEDS_DECISION`. `ACCEPTED_WITH_LIMITATION` and `DECIDED_BACKLOG` each name the
limitation, its expiry or recheck trigger, and the entry that carries it, and in
the same commit the finding is written into `.charter/project.md` section 10 or a
decision record at `.charter/records/<Decision ID>.md` - so the next session meets it
without re-reading this review. Outside this record a finding is cited as the review id
plus its row id, `REV-<TASK-ID>-<nn>/F-NN`: the pair is unique because neither half
is ever reused, and it needs no central allocator to hand out.

No findings is a valid result only after every applicable check above has an observation.

Severity describes impact and urgency: `P0` blocks or risks immediate critical harm, `P1` is a major user or contract failure, `P2` is a bounded non-critical defect, and `P3` is a minor issue or polish. Change class describes the authorization needed for the proposed remedy. They are independent axes; any C-class remedy requires a decision regardless of severity, and a P0/P1 finding still receives urgent handling even when its remedy is A-class.

Findings are field-tested before disposition: a scope or attribution verdict is
recomputed with the implementer's own tool and against the baseline commit; an accepted
proposal is reproduced on real input before it is implemented; a refuted finding is
recorded with the refutation; and an evidence statement that describes code or sources
carries the line numbers it rests on, with counter-evidence sought, not summarized from
memory. Both directions fail in practice — the reviewer's verdict can be wrong, and so
can the implementer's reading of it.

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
