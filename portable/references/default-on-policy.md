# Default-on policy

Some rules in this workflow ship enabled with a conservative value and take a
recorded decision to turn down. The session execution ledger is one: enabled by
default, so an implementation session needs a reason not to, and `NOT_ENABLED` is a
recorded waiver rather than a silent omission. The Review B trigger table is
another: all five `RVB` rows ship `YES`, and narrowing one is a user decision in the
charter's change log.

The pattern exists because of what this workflow cannot do. There is no runtime.
Every gate is enforced by an agent reading the file that records whether the gate
passed. A rule that ships off is therefore not neutral — it is invisible, and the
next agent has no way to tell "considered and declined" from "never noticed". A rule
that ships on is visible in a file the agent already reads, and declining it leaves
a record behind.

## Shape

A default-on policy has four parts. One missing part makes it a suggestion instead.

1. **A shipped default that is the conservative choice** — not the common one and not
   the cheap one. If the default is wrong for a project, the cost is one recorded
   decision; if the default is absent, the cost is an unrecorded gap.
2. **A named narrowed value that states its exclusion.** `NO`, `NOT_ENABLED`, or a
   bounded `YES` has to say what it excludes. Narrowed with nothing excluded reads
   the same as never filled in.
3. **A recorded decision to narrow it,** with approver and date, in the file that
   owns the policy — not in a handoff block, which gets archived.
4. **Zero cost for the case that does not need it.** A low-risk leaf under a `YES`
   trigger row records `NOT_REQUIRED` and names the ids it considered; it does not
   run a review. If holding the default on is expensive for the ordinary case, it
   will be narrowed for the wrong reason.

## Why the cost lands where the knowledge is

A default-on policy defers nothing to setup time by accident. A new project cannot
answer "which reviewer, and what makes them fresh" during its first interview,
because nothing has been built yet; asking then produces a guess that is afterwards
cited as a decision. Shipping the conservative default and stopping at the first leaf
that actually hits the trigger asks the question exactly once, at the point where the
project can answer it.

The exception is a project that already has the answer. A migration into an existing
project fills the value from the evidence already on disk rather than shipping
`UNDECIDED` into a project whose own history has settled the matter. See
`contract-migrations.md`.
