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
- Contract version: `0.1` — a contract predating a field this workflow now requires is migrated, and its version bumped, before the next state transition: `portable/references/contract-migrations.md` in the full kit or `references/contract-migrations.md` in the self-contained Skill

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

### Evidence to attach

- Command or operation:
- Expected observation:
- Actual observation:
- Raw output reference:
- Coverage limitation:

## 6. Stop conditions and repair budget

Stop and write a decision record when:

- the goal, scope, authority, or public meaning would change;
- a required capability is unavailable;
- a predecessor is not actually closed;
- the same class of failure repeats after `<number>` repair attempts;
- the next fix would touch a forbidden path or effect;
- existing user changes could be overwritten.

- Maximum repair iterations: `<number>`
- WIP limit: `1`
- Escalation owner: `<person>`

## 7. Integration policy

- Candidate revision reference: `<branch/commit/provider revision>`
- Target branch or destination: `<main or other>`
- Merge allowed: `yes | no`
- Push / PR / deployment allowed: `yes | no` (default `no`)
- Required post-integration verification:

## 8. Execution record

### Design and plan

- Design note: `<path or short description>`
- Design interview record: `<path or summary; the design tree lives in section 10 and must be fully resolved before implementation>`
- Reuse discovery evidence reviewed: `<discovery ID, coverage/result, candidate revision, targeted recheck, NO_MATERIAL_TARGET sanity check, or BUILD_NEW rationale>`
- Long-task ledger: `<session ledger mode: jspace.py controller (seam/resume at state transitions, continuing across leaf boundaries), or manual five-line ledger with FALLBACK, or NOT_ENABLED waiver with reason recorded in Events>; .charter/ stays the governance source of truth>`
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

- Review A: `<path, reviewer, candidate, verdict>`
- Review B / fresh behavior check: `<REQUIRED with trigger/path/reviewer/freshness/verdict, or NOT_REQUIRED with bounded omission reason>`
- Ledger reconciliation: `<execution-ledger Verified summary mirrored into Events/Evidence>` — a leaf with neither reconciliation nor a recorded `NOT_ENABLED` waiver in its Events table must not close as `PASS_CLOSED` (close `PARTIAL` with the reason instead)
- Pre-integration verification receipt: `<path, command, candidate, result>`
- Final candidate: `<revision>`
- Target-branch integration receipt: `<path or not yet>`
- Post-merge verification: `<path, command, result>`
- Unrelated failures and limitations:

Required order: `Review → Verification → target-branch integration → post-integration verification`. Do not integrate directly from Review, and do not treat pre-integration Verification as post-integration proof.

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
