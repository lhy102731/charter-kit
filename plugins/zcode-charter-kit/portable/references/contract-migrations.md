# Contract migrations

A leaf-task contract is written once and then used for the life of the leaf. This
workflow occasionally adds a field that every contract is required to carry. A
project that started before that change has contracts predating the field, and
nothing about reading such a contract announces the gap: the field is simply
absent, which looks the same as a field that was considered and left empty.

Migration therefore has a fixed position — **before the first state transition of
the session that noticed the gap.** A transition recorded against a contract
missing a required field produces a record that cannot be audited against the
rule it was meant to follow, and afterwards the omission is indistinguishable
from a decision not to apply the rule at all.

## Steps

For each field below that the active contract does not carry:

1. Add the listed line to the listed section of `.charter/current-task.md`, using
   the wording from `templates/leaf-task.md` so the field reads exactly as it
   does in a contract created today.
2. Bump `Contract version` in section 1.
3. Record a `CLARIFICATION` Change Triage entry naming the field added and the
   version before and after. Use the bundled Change Triage reference:
   `portable/references/change-triage.md` in the full kit or
   `references/change-triage.md` in the self-contained Skill.
4. Only then make the state transition.

A migration adds a required field and its declared value. It never changes the
result sentence, allowed paths, acceptance checks, effects, or authorization of a
contract that is already approved — those are scope changes, and each takes its
own Change Triage route and its own decision.

## Fields added after `0.1`

| Field | Contract section | Line to add |
| --- | --- | --- |
| Session execution ledger mode | `## 8. Execution record` | `Long-task ledger` |
| Ledger reconciliation at closure | `## 9. Review and closure` | `Ledger reconciliation` |
| Readiness record | `## 9. Review and closure` | `Readiness record` |
| Review B id citation | `## 9. Review and closure` | `Review B / fresh behavior check` — add the `RVB` ids to the existing line |

The two ledger rows are one change and are applied together. The first declares the
ledger mode for the session; the second is what closure actually checks. A
contract carrying only the declaration can reach `PASS_CLOSED` with neither
reconciliation nor a recorded `NOT_ENABLED` waiver, which is the failure the pair
exists to prevent.

The readiness row records a check that already happened. On a contract still
`DRAFT` or `APPROVED`, fill it while running the checklist. On a contract already
`READY` or later, reconstruct it from the evidence that existed at that
transition — the roadmap row, the handoff block, the receipts under
`.charter/evidence/` — and say in the field that it was reconstructed. An item
whose evidence cannot be found is recorded `UNVERIFIED` with what was looked for;
it is never recorded `PASS` on the strength of the transition having happened.
Reference items by their roadmap `RDY` number plus a short label, so the record
stays a delta against the checklist instead of a second copy of it.

## Charter-level migrations

Some required fields belong to `.charter/project.md` rather than to a leaf. The
position rule is the same — before the first state transition of the session that
noticed the gap — but the mechanics differ: a charter has no `Contract version` to
bump, so the version lands in its section 12 change log, while the `CLARIFICATION`
entry still goes in the active leaf's Events table so one place holds the session's
audit trail. A charter-level migration is records-only. A change to Goal,
Non-goals, Invariants, authorization, or public meaning is a scope change with its
own Change Triage route and its own decision.

| Field | Charter section | Line or block to add |
| --- | --- | --- |
| Review B policy (`RVB1`-`RVB5`, reviewer and freshness method) | `## 7. Capability map` | `### 7.1 Review B policy` |

Add the block as `### 7.1`, never as a new numbered section. Charter sections are
cited by number from the roadmap and from leaf contracts, so inserting one
mid-numbering silently redirects every citation that already exists.

Ship the trigger rows at their default `YES` and leave narrowing to a recorded user
decision. Two things are decided at migration time rather than deferred:

- **Reviewer and freshness method.** If the project already holds independent-review
  evidence — a fresh-context review under `.charter/evidence/`, an external reviewer
  bound to a candidate revision, anything showing the practice has actually run —
  fill this line from that evidence instead of leaving it `UNDECIDED`. A project
  that can answer today should not be scheduled to stop and ask later. A probe
  recorded `UNVERIFIED` in the dependency-check log means the capability could not be
  machine-confirmed, not that it is absent, and it is not grounds for
  `BLOCKED_TOOLING` on its own.
- **How existing records read.** Closed leaves are not migrated, so their Review B
  lines keep the label they were written with. Where that label no longer matches the
  current vocabulary — most commonly `WAIVED` on a leaf that hit no trigger and
  should have read `NOT_REQUIRED` — record the reading once in `### 7.1` instead of
  editing the closed records. One boundary note that says how to read them preserves
  the history and still stops the next leaf from copying the wrong label forward.

## When the migration is not applied

Leaving a required field out silently is not one of the options, and
`BLOCKED_TOOLING` does not apply: migration is an edit to a project file, not a
provider call.

- **Closed and archived contracts** are not migrated. They record what was
  required when they closed. Migrate the active contract only.
- **A user who declines the migration** has granted a bounded waiver. Record it
  in the active leaf's Events table with the reason, the limitation, the
  approver, and an expiry or recheck point, exactly as for any other waiver, then
  proceed within that limitation.
