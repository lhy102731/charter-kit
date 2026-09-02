# Leaf Task Contract

> Copy this file to `.charter/current-task.md`. This contract is for one bounded behavior. If the result sentence contains “and” twice, split the task.

## 1. Identity

- Task ID: `<TASK-ID>`
- Parent task: `<parent-ID>`
- Project goal reference: `<project.md section or ID>`
- Title: `<short verb + observable result>`
- Owner / implementer: `<agent or person>`
- Mode: `MANUAL | AUTO_DEV`
- Status: `DRAFT`
- Leaf approval / preauthorization reference: `NOT_GRANTED`
- Contract version: `0.1`

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

-
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
- Design interview record: `<path or summary; design tree fully resolved before implementation>`
- Reuse discovery evidence reviewed: `<discovery ID, coverage/result, candidate revision, targeted recheck, NO_MATERIAL_TARGET sanity check, or BUILD_NEW rationale>`
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
