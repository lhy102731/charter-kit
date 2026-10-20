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

Two things are decided before the numbered steps, because both change what the
steps have to cover:

- **What kind of member the change added.** A field usually arrives with either a
  review check that now has to be answered or an enumeration member that did not
  exist before. `## Check-level and enum-level additions` covers that
  granularity; a migration that stops at the field leaves it half applied.
- **Whether the migration is landing a default value.** A default-on rule that
  arrives with the field is filled from the evidence already on disk rather than
  shipped `UNDECIDED` into a project whose history has settled it. See
  `default-on-policy.md`, which also names the hook that reads each default back.

For each field below that the active contract does not carry:

1. Add the listed line to the listed section of `.charter/current-task.md`, using
   the wording from `templates/leaf-task.md` so the field reads exactly as it
   does in a contract created today.
2. Bump `Contract version` in section 1 to the template's current version (`0.5`).
   The number records the approval that carried the migration, not the number of steps
   taken: a `0.1` contract lands on `0.4` in one pass.
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
| Suite verification | `## 5. Acceptance` | `Whole-suite verification` |
| Review focus | `## 5. Acceptance` | `Review focus` — `none identified` is a declared value, not an omission |
| Rulings protocol | `## 6. Stop conditions and repair budget` | `Rulings protocol` |
| Closure checklist (`CLS1`-`CLS11`) | `## 9. Review and closure` | `Closure checklist` - the whole table, every row answered, `N/A` plus reason where a row does not apply |
| Acceptance items (`AC1`-`ACn`) | `## 5. Acceptance` | `### Acceptance items` - number the existing items, add the `check:` slot to each; ids are never renumbered |
| Scratch root | `## 4. Scope` | `### Scratch root` - the whole subsection, plus `CLS11` in the closure checklist; keep both the order it states (evidence written, root emptied, closure signed) and the three lifetimes, since a scratch root that only forbids paths drops the part that keeps proof alive |

Which template ships which row: the seven rows above `Closure checklist` are present in
the `0.2` template; `Closure checklist` and `Acceptance items` arrive with the `0.4`
template; `Scratch root` arrives with the current `0.5` template. No `0.3`
template was ever released - the version number records an approval, and the two `0.4`
additions were approved together - so a `0.2` contract adds both of those rows and
bumps straight to `0.4`, and a `0.4` contract adds `Scratch root` and bumps to `0.5`. A
`0.1` contract carries none of the ten rows and numbers no items, so it migrates
every row in one pass. The `Long-task ledger` declaration also gained an allowed value — `control.py controller` (j-space SV1) — when `0.2` shipped. That is an enum extension, not a migration: a contract already declaring `jspace.py controller` keeps it, and the legacy mode stays valid for as long as the session's installed j-space is what provides the ledger.

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

## Check-level and enum-level additions

A field holds a value; something else decides what that value is compared
against. When a change adds a field it usually also adds a review check that now
has to be answered, or a member of an enumeration that did not exist before.

Neither is a contract migration in the field sense - a contract that lacks
`CHK12` is not missing a field, and a contract declaring the older ledger member
is not out of date. Both still need a recorded row, at member granularity,
because the failure mode is identical to the field-level one: an unanswered check
and a check nobody added read the same in a checklist, and an extended
enumeration reads the same as a renamed one.

Member granularity means one row per member. "The template was upgraded" is not a
migration record; it does not tell a later reader which member arrived, in which
order, or what the older members now mean.

### Checks

| Check id | Section | Applies from |
| --- | --- | --- |
| `CHK12` | `## Checks performed` | Reviews started after this template version. Review records written before it keep the checks they were written against. |
| `CHK13` | `## Findings` | Reviews started after this template version. A review record written before it keeps the findings table it was written against. |
| `CHK14` | `## Checks performed` | Reviews started after this template version. A review record written before it keeps the checks it was written against. |

`CHK14` was reworded once, inside the same round that introduced it, because its third clause named no artifact that had to produce the answer. The id did not move and no archived record cites it; the rewording is recorded here rather than appended as a second check.

A review record is a record of a review that happened, so it is never migrated
forward: a check that did not exist when the review ran was not skipped, it did
not apply. What carries the addition is the append-only rule in the template plus
this row - the template says ids do not move, and the table says which id is new.

### Enumeration members

| Enumeration | Member added | Standing of the older members |
| --- | --- | --- |
| `Long-task ledger` (`## 8. Execution record`) | `control.py controller` | `jspace.py controller` stays valid for as long as the installed j-space is what provides the ledger |

An extension is not a rewrite: a contract already declaring an older member keeps
it, and the row exists so a later reader can tell an extended enumeration from a
renamed one. Renaming or retiring a member is a different act - it changes what an
archived record means - so a retired name stays in the table with its meaning and
is never reused for something new.

### Renamed members

| Enumeration | Old name | New name | Standing of the old name |
|---|---|---|---|
| `decision.md` `Status` | `APPROVED` | `DECIDED` | an archived decision keeps meaning `DECIDED`; the old name is never reused for something new |

A rename is recorded in both directions so an archived record stays readable: read
the old name in an older record as the new one, and never write the old name on a
new record. This rename exists because `project.md` section 10 already calls the
settled state `DECIDED`; one state with two words is a drift an agent resolves
silently, and section 10 is the authority for whether a question is still open.

## Record-level migrations

The three event records - evidence receipt, review, decision - carry an id that now states
its scope, and each record is one file under `.charter/records/` instead of a shared file
that is appended to or overwritten. Renaming an id an archived leaf already cites breaks
the citation, so this migration has exactly two legal finishes: rename and update every
citation in the same commit, or leave the historical record untouched and write the new
shape from now on. What is not legal is a shared file that new records keep appending to:
the next write destroys the previous record, and nothing in the repository then says it
was ever there.

| Record | Field | New shape |
| --- | --- | --- |
| `evidence-receipt.md` | `Evidence ID` | `E-<TASK-ID>-<nn>`, one file at `.charter/records/<Evidence ID>.md` |
| `review.md` | `Review ID` | `REV-<TASK-ID>-<nn>`, one file at `.charter/records/<Review ID>.md` |
| `decision.md` | `Decision ID` | `DEC-<YYYYMMDD>-<slug>`, one file at `.charter/records/<Decision ID>.md` |

Evidence and review ids are scoped by the task that produced them, so a bare `E-01` from
two leaves no longer collides. Decisions are project-scoped and dated instead: two leaves
can open decisions in the same session, so a per-leaf sequence would mint one id twice.
None of the three needs a central allocator, which is the point - no runtime exists to hand
out numbers.

### Steps

1. Create `.charter/records/` if it does not exist. It holds record files and nothing
   else: no index, no notes, no scratch.
2. Split every record already written into a shared file into one file per record. Keep
   the original text and the original date; name the file after the new id and take
   `<nn>` from `01` in the order the records were written, oldest first.
3. A record whose id cannot be reconstructed from the shared file takes the migration
   date with a slug from its title, and says so in one line. An invented date is worse
   than a declared one, but a record left behind in the shared file is worse than both.
4. Leave the shared file as a format rather than a ledger: keep its field schema, remove
   the migrated bodies, and add one line per migrated record naming its id and its file.
   Delete the file only when its format is reachable another way.
5. In the same commit, update every live citation of a migrated record - an archived
   leaf, a review, the roadmap's route table, a `project.md` section 10 pointer - to the
   new id and path. A renamed id with live citations reads as a missing record.
6. Then record the migration itself in `.charter/changelog.md`: an id shape that
   archived leaves cite is a change to what a later session reads.

## Charter-level migrations

Some required fields belong to `.charter/project.md` rather than to a leaf. The
position rule is the same — before the first state transition of the session that
noticed the gap — but the mechanics differ: a charter has no `Contract version` to
bump, so the version lands in `.charter/changelog.md`, while the `CLARIFICATION`
entry still goes in the active leaf's Events table so one place holds the session's
audit trail. A charter-level migration is records-only. A change to Goal,
Non-goals, Invariants, authorization, or public meaning is a scope change with its
own Change Triage route and its own decision.

| Field | Charter section | Line or block to add |
| --- | --- | --- |
| Review B policy (`RVB1`-`RVB5`, reviewer and freshness method) | `## 7. Capability map` | `### 7.1 Review B policy` |
| Charter change log | `## 12. Change log` | move the table unchanged to `.charter/changelog.md`, then leave the pointer sentence |

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
