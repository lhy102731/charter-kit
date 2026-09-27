# Leaf Task Contract

> Copy this file to `.charter/current-task.md`. This contract is for one bounded behavior. If the result sentence contains “and” twice, split the task.

> **Write the delta, not the project.** A clause whose authoritative source is already in the required-start read set may be carried by an explicit reference plus this leaf's delta — for example `project.md section 5 baseline, plus: <leaf-specific item>` for forbidden effects, or `roadmap.md verification commands` for the standard checks. Anything that narrows, widens, or contradicts that baseline is written out here in full. Never replace a leaf-specific field with a reference: the result sentence, allowed paths, acceptance checks, repair budget, and any stop condition that differs from the standard list are always inline. A reference names its source file and section so the archived contract stays resolvable at the commit that recorded it.

> **Bounded size.** Every resume re-reads this contract, so its length is paid by every later actor. Keep it under 36 KB. This template is about 10 KB and a long real project's contract lands near 35 KB while it stays a contract, so the ceiling is where absorbed material starts to show rather than a style preference. Past that, the growth is almost always material that belongs to a file already in the read set: move goal or scope prose to `project.md`, sequencing to `roadmap.md`, candidate evidence and pinned versions to `reuse-discovery.md`, and command output to `.charter/evidence/`, leaving the reference behind. Never buy the reduction by deleting acceptance checks, stop conditions, allowed paths, or effects: a contract that no longer states what the gate needs is a worse defect than a long one.

## 1. Identity

- Task ID: `<TASK-ID>`
- Parent task: `<parent-ID>`
- Project goal reference: `<project.md section or ID>`
- Title: `<short verb + observable result>`
- Owner / implementer: `<agent or person>`
- Mode: `MANUAL | AUTO_DEV`
- Status: `DRAFT`
- Leaf approval / preauthorization reference: `NOT_GRANTED`
- Contract version: `0.2` — a contract predating a field this workflow now requires is migrated, and its version bumped, before the next state transition: `portable/references/contract-migrations.md` in the full kit or `references/contract-migrations.md` in the self-contained Skill

## 2. Result contract

### One result sentence

> `<Given input/context, the system produces observable result>`

### Why this leaf matters

`<Which part of the approved product loop does this unlock?>`

### Change Triage

- Record the Change Triage event kind and route from the bundled reference: `portable/references/change-triage.md` in the full kit or `references/change-triage.md` in the self-contained Skill.
- New requirement must not silently expand the current Leaf.

### Explicit non-results

- This task does not:
- This task does not:

## 3. Preconditions

- [ ] Project charter is approved.
- [ ] Reuse discovery record: `.charter/reuse-discovery.md` has been read; its gate is `COMPLETE`, or this specific Leaf has an explicit, separately approved bounded waiver recording the approved/omitted scope, limitation, approver, and expiry/recheck condition, before this leaf becomes `READY`. The waiver is not a fourth gate state or project-wide bypass.
- Reuse assessment: `YES | NO_MATERIAL_TARGET` — `<rationale and local sanity-check evidence>`
- Reuse coverage / result: `<SEARCHED | NOT_SEARCHED | NOT_AUTHORIZED | BLOCKED_TOOLING>` / `<MATCH | NO_MATCH | UNKNOWN>`
- Reuse final route / candidate IDs: `<ADOPT / ADAPT / REFERENCE_ONLY / BUILD_NEW / REUSE_SPIKE / NEEDS_DECISION>` / `<IDs or justification>`
- [ ] The reuse record is current for this leaf; if its recheck trigger/date applies, a targeted recheck is linked. Without the leaf-specific waiver above, `PENDING`, `BLOCKED`, and `BLOCKED_TOOLING` are not approval; resolve the evidence or authorization gap before continuing. Any limitation or waiver is recorded in the decision field with approver, omitted scope, and recheck condition.
- [ ] This leaf is approved under its selected mode and the authorization reference is recorded.
- [ ] Predecessor tasks: `<IDs at PASS_CLOSED, or — for the first leaf>`
- [ ] Baseline revision/workspace: `<branch, commit, or provider revision>`
- [ ] User's existing changes recorded and protected.
- [ ] Required host abilities available: `<list>`
- [ ] Dependency check evidence: `<path; AVAILABLE/MISSING/UNVERIFIED/FALLBACK records>`
- [ ] Required authorization references: `<list or none>`

## 4. Scope

### Allowed paths / artifacts

- `<workspace-relative path or artifact>`
-

### Allowed effects

- [ ] `read_only`
- [ ] `sample_run`
- [ ] `code_write`
- [ ] `local_merge`
- [ ] `external_service`
- [ ] `sensitive_data`
- [ ] `release`
- [ ] `irreversible`

### Forbidden effects

- `<project.md section 5 forbidden-effects baseline>` — cite the baseline, then write out every addition or narrowing below
-

## 5. Acceptance

### Positive behavior

- [ ] `<observable check 1>`
- [ ] `<observable check 2>`

### Negative behavior / boundaries

- [ ] `<invalid input or forbidden effect is rejected or remains unchanged>`
- [ ] `<failure path is recorded>`

### Suite verification

- [ ] Whole-suite verification: `<the project's own test command, run in full — a green run of this leaf's files alone is not a green suite>` — unrelated failures that run shows are reported by name in the Evidence index; a red test watched and not reported falsifies the record by omission.

### Review focus

The spec implies inputs and failure modes that no acceptance check above exercises. Name the ones most likely to bite a user of this leaf, most likely first, each with the check that pins it — add that check to Positive or Negative behavior, or record here why it cannot run:

- `<input or condition — expected behavior — pinning check, or why none can run>`

If none are identified, state `none identified` in one line; the declared absence is the field's value, not an omission.

### Evidence to attach

- Command or operation:
- Expected observation:
- Actual observation:
- Raw output reference:
- Coverage limitation:

A receipt asserts checkable facts: the recorded command is re-run before the receipt is
committed; a statement of fact is checkable in the same commit, or marked aspirational;
the receipt names the commit a proof describes (a guard added after the write describes
the re-run, not the write); a result boolean is named after the assertion it makes; and a
self-verification recomputes each asserted value from the originals — a check that
re-reads the field it certifies proves at most that the file was not edited, and a
tampered copy must fail it. When the measuring criteria change, the before/after
comparison runs under one ruler, with a per-item delta.

### Check discipline

A check this leaf delivers — acceptance script, gate, self-verification — answers three
questions before its result is trusted: **it reads the object under test** (a check whose
inputs come from the artifact it certifies can pass a mutated copy); **every instance is
covered** (an existence-shaped assertion is survived by the second occurrence — uncovered
instances fail the check, they are not printed); **it moves the exit code** (a printed
violation that cannot fail the run is a log line, not a gate, and a crash-caused non-zero
exit is not a verdict — the liveness test asserts the failure reason).

Delivery includes a liveness test: an injected violation goes red, and a real input shows
a non-zero match count. A check over a set of inputs also validates the set against its
baseline (a shrunken input list is indistinguishable from a real decline); "not scanned"
is registered with the reason; a claim about an external source is worded as "not found
this pass", never as "does not exist". Failures are classified: present and wrong is a
failure; not-yet-downloaded, pre-listing, or out-of-scope is pending — the exit code
reflects only failures. After changing behavior, search for what still asserts the old
one: reproduction scripts, docstrings, and summary prints.

## 6. Stop conditions and repair budget

Stop and write a decision record when:

- the goal, scope, authority, or public meaning would change;
- a required capability is unavailable;
- a predecessor is not actually closed;
- the same class of failure repeats after `<number>` repair attempts;
- the next fix would touch a forbidden path or effect;
- existing user changes could be overwritten.

### Rulings protocol

Everything the stop list above does not name is decided, not stalled. When the contract, the spec, and what the work actually found disagree on a point no stop condition covers, record one line in the Events table —

- `Ruling: <what was decided> — <why> — <what it costs if wrong>` —

and keep going. Deviating without a recorded Ruling is a decision made in secret; a Ruling the closure review disagrees with is one line to overturn, not a hidden fork.

- Maximum repair iterations: `<number>`
- WIP limit: `1`
- Escalation owner: `<person>`

## 7. Integration policy

- Candidate revision reference: `<branch/commit/provider revision>`
- Target branch or destination: `<main or other>`
- Merge allowed: `yes | no`
- Push / PR / deployment allowed: `yes | no` (default `no`)
- Required post-integration verification:
- Governance-record discipline: in the main worktree, stage explicit paths only — never a
  directory, `-A`, or `.`; read `git diff --cached --name-only` before every commit and
  confirm each path is one this leaf owns; a dirty or untracked count that moved without
  this task touching it is an alarm. Governance records are committed before they are at
  risk: the outgoing contract is archived to
  `.charter/evidence/<date>-<leaf>-contract-archive.md` and committed in the same session
  as its closure, before `current-task.md` is overwritten — with an incremental edit,
  never a whole-file rewrite — and a record left uncommitted in a leaf worktree dies with
  the worktree.

## 8. Execution record

### Design and plan

- Design note: `<path or short description>`
- Design interview record: `<path or summary; the design tree lives in section 10 and must be fully resolved before implementation>`
- Reuse discovery evidence reviewed: `<discovery ID, coverage/result, candidate revision, targeted recheck, NO_MATERIAL_TARGET sanity check, or BUILD_NEW rationale>`
- Long-task ledger: `<session ledger mode: control.py controller (j-space SV1 — init at session start, pulse at tool boundaries, check at state transitions, route/failure/handoff/resume/compact at their events; state lives in .jspace/control.json), or jspace.py controller (legacy ledger: seam/resume at state transitions, continuing across leaf boundaries), or manual five-line ledger with FALLBACK, or NOT_ENABLED waiver with reason recorded in Events>; .charter/ stays the governance source of truth>`
- First failing check (RED): `<test or inspection>`
- Minimal implementation plan:
  1.
  2.
  3.

### Events

| Time | State / event | Actor | Evidence reference | Note |
|---|---|---|---|---|
| `<time>` | `DRAFT` | `<actor>` | `<ref>` | Initial contract; project approval does not authorize this leaf. |

### Evidence index

| ID | Kind (`test / review / verification / integration`) | Candidate | Producer | Result | Raw reference |
|---|---|---|---|---|---|
| E-01 | `<kind>` | `<revision>` | `<agent/host>` | `<PASS/FAIL/ERROR/SKIPPED>` | `<path>` |

## 9. Review and closure

- Review A: `<path, reviewer, candidate, verdict, freshness: fresh-subagent | same-context (FALLBACK recorded, naming the lost independence)>` — executed by a reviewer holding no implementation context; see project.md section 7.1 and the kit's default-on policy
- Review B / fresh behavior check: `<REQUIRED with the RVB id(s) hit plus path/reviewer/freshness/verdict, or NOT_REQUIRED naming the RVB ids considered plus the bounded omission reason, or WAIVED only for a triggered review whose reviewer was unavailable and whose bounded waiver the user approved>` — the judgments come from `.charter/project.md` section 7.1; cite ids, do not re-argue them here, and do not cite a sibling leaf in place of the ids
- Readiness record: `<RDY1-RDY13 PASS with the evidence source, then one | RDY# | result | evidence | row for every item that is not a plain PASS — UNVERIFIED, a bounded waiver, or its own evidence path; cite items by number plus a short label, never by restating the checklist text>`
- Ledger reconciliation: `<execution-ledger Verified summary mirrored into Events/Evidence>` — a leaf with neither reconciliation nor a recorded `NOT_ENABLED` waiver in its Events table must not close as `PASS_CLOSED` (close `PARTIAL` with the reason instead)
- Pre-integration verification receipt: `<path, command, candidate, result>`
- Final candidate: `<revision>`
- Target-branch integration receipt: `<path or not yet>`
- Post-merge verification: `<path, command, result>`
- Unrelated failures and limitations:

Required order: `Review → Verification → target-branch integration → post-integration verification`. Do not integrate directly from Review, and do not treat pre-integration Verification as post-integration proof.

Closure status is written only after the last review or verification has returned, into
every carrier at once — contract §9, the roadmap status column, the handoff active-leaf
block — never one file ahead of the review; a claim corrected in one holder is corrected
in all of them in the same commit (search the claim's wording for the remaining copies,
and mark superseded lines that carry priority flags). Before a CAPABILITY/SLICE container
row closes, the spec's planned leaves are reconciled against the roadmap's implemented
rows; a leaf ID is checked against the full roadmap table when it is assigned — IDs are
single-use, and "planned but never opened" is adjudicated explicitly, never left silent.

### Closure decision

Choose exactly one:

- `PASS_CLOSED` — acceptance, Review, pre-integration Verification, target-branch integration, and post-integration verification are all evidenced.
- `PARTIAL` — useful result exists but a stated requirement remains open.
- `BLOCKED` — an invariant, predecessor, or safety boundary prevents continuation.
- `BLOCKED_TOOLING` — a required host capability or independent context is unavailable.
- `NEEDS_DECISION` — a human choice or new authorization is required.

- Closure date:
- Closed by:
- Next candidate (informational only): `<TASK-ID or none>`
- Next authorization: `<reference or NOT_GRANTED>`

## 10. Design tree

Resolve before implementation; this tree is drafted during the section 8 design phase and each adjudication is mirrored into the Events table. The current **frontier** lists questions whose prerequisites are already settled — ask only what is answerable now, with the agent's recommended answer attached.

Format per question:

1. **Q1 — `<question title>`**
   - Recommended: `<answer with a concrete example — type signature, field list, or code sketch>`
   - Reason: `<why this answer; the facts already verified that support it>`
   - Alternative: `<the rejected option and its cost>`
   - Disclosed cost: `<side effects the user should see, e.g. workspace baseline changes>`

A round closes when every question is settled or explicitly carried forward (named owner and leaf), and an empty frontier is stated in one line. **Provider line:** record which interview method ran (`grill-me` / `grilling` / the bundled design-interview) and whether it was verified `AVAILABLE`.
