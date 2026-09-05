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

Those two rows are one change and are applied together. The first declares the
ledger mode for the session; the second is what closure actually checks. A
contract carrying only the declaration can reach `PASS_CLOSED` with neither
reconciliation nor a recorded `NOT_ENABLED` waiver, which is the failure the pair
exists to prevent.

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
