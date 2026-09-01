# Design Interview (Portable Fallback)

Use this checklist for the first project-intent interview and for every leaf design when `grill-me`/`grilling` is unavailable. When the host provides that provider, use it first and retain the same evidence fields. Resolve the design as a tree of decisions, work in rounds, ask every currently answerable question in one numbered batch with a recommended answer, investigate environmental facts yourself, reserve decisions for the user, and stop only when no unresolved branch remains — never let an assumption pass silently.

## Interview rounds

For each round, cover the clusters below that still have open branches. Close every round by restating the tree: what is settled, what newly unblocked questions exist, and what still waits on a decision.

### 1. Intent and contract

- Who is the user, what situation triggers the work, and what pain is being addressed?
- What is the one observable project Goal, and what are explicit Non-goals and Invariants?
- What is the shortest product loop from input to outcome and next action?
- Exact inputs and outputs: types, ranges, units, error values?
- Who calls this, and what public surface must stay compatible?
- What is the one observable result sentence for this leaf?

### 2. Normal path

- What happens step by step on the happy path?
- What will be observed or tested to prove it (the future RED check)?

### 3. Negative paths and boundaries

- Invalid, missing, duplicated, extreme, or out-of-order input: rejected how?
- Which forbidden paths or effects must stay untouched?

### 4. State, concurrency, and failure

- What state is read or written; who else touches it; what happens on overlapping access?
- How does each piece fail; what is reversible; what residue is left behind?

### 5. Reuse, effects, and authorization

- Which existing assets, skills, plugins, libraries, or services might be reused? What search scope and privacy limits apply?
- Which effect classes (`read_only`, `sample_run`, `code_write`, `local_merge`, `external_service`, `sensitive_data`, `release`, `irreversible`) does the design touch?
- Does every touched class have an authorization reference?

### 6. Stop line

- What outcome means stop-and-decide rather than repair?
- What is the repair budget, and which findings would exhaust it?

## Record

For a new project, write the resolved tree into the project charter's `Intent interview evidence` field and retain the provider/mode, round summaries, user confirmations, recommendations accepted or overridden, facts discovered, and branches explicitly closed. For a leaf, also link the same decision tree from that leaf's design note. An unresolved branch at implementation start is a stop condition, not a footnote.
