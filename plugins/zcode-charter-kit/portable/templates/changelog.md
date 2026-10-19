# Charter Change Log

> Copy this file to `.charter/changelog.md`. It is the charter's own version history, and it sits
> deliberately outside the resume read set: a resume reads the charter's current
> state, never its earlier states. Nothing here may be restated in `project.md`,
> and `project.md` must not restate anything here.

| Version | Date | Change | Reason | Approved by |
|---|---|---|---|---|
| 0.1 | `<date>` | Initial charter | `<reason>` | `<person>` |

## Rules

- One row per version, one version per approval. A row with no approval reference
  records a change nobody authorized.
- New rows append at the bottom. A row is never edited after the version it records
  has been used by a session; a correction is a new row naming the row it corrects.
  The number identifies a charter approval, not a document revision.
- `Change` says what moved; `Reason` says why it had to. A row that says only
  "updated" is a row the next session will re-litigate.
- A row that supersedes a decision records that decision's id, so the change and
  the decision can be read together.

## When a row is required

A row is required by these changes, and nothing else:

- any narrowing of `RVB1`-`RVB5` or of another risk trigger, because the next session
  reads the narrow trigger as the whole rule;
- any new mandatory contract field or checklist item, because an archived leaf that
  lacks it can no longer be read as compliant;
- any charter-level migration recorded in `references/contract-migrations.md`;
- any change to `Invariants` or to the effect boundary, because both decide what a
  later session may do without asking.

`Reason` names what the row excludes or replaces. A row whose `Reason` only says the
change was needed cannot be told apart from a row nobody reasoned about.
`Approved by` is never blank: a change made before approval is recorded as
`UNDECIDED - <why the change could not wait for approval>`, which a later session can
read and act on, where a blank cell is a state it has to guess.

## Growth

This is the one file in `.charter/` expected to grow without bound: it grows by
history, not by live state, which is why nothing reads it by default. When it
becomes hard to scan, split it by charter major version into `changelog-v<N>.md`
files with one index row per file. The split is a move, never a deletion, and the
row order is preserved.

## Migration from section 12

A charter whose history still sits in its own section 12 moves the table here
unchanged: same rows, same order, same version numbers. Then that section becomes
the pointer sentence. Nothing is renumbered - a version number is what an
archived approval cites.
