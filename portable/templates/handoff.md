# Agent Handoff Packet

> Copy this file to `.charter/handoff.md` whenever another Agent or host may continue the work. Keep it short and factual; link to detailed evidence instead of copying a transcript.

Use this file as the resume packet for another actor. It records the current task state, evidence, and exact next action; it is not a second state machine or a transcript.

## Snapshot

- Protocol / kit version: `charter/v1 / 0.2.0`
- Project: `<name>`
- Goal reference: `<.charter/project.md>`
- Task ID: `<TASK-ID>`
- Current state: `<DRAFT / READY / IN_PROGRESS / REVIEW / ...>`
- Snapshot time: `<YYYY-MM-DDThh:mm:ssZ>`
- Handoff producer: `<agent + host>`

## Goal and boundary

- Approved result:
- Non-goals relevant to this task:
- Invariants that must remain true:
- Allowed effects:
- Forbidden effects:

### Change Triage

- Record the event kind and route from the bundled Change Triage reference whenever a new requirement or constraint appears: `portable/references/change-triage.md` in the full kit or `references/change-triage.md` in the self-contained Skill.
- New requirement must not silently expand the current Leaf.

## Current facts

- Last accepted event:
- Baseline revision/workspace:
- Current candidate revision:
- Predecessor receipts:
- Reuse discovery ID / gate status / selected revisions:
- Verified facts:
  -
  -
- Open findings:
  -
  -

## Evidence

| Reference | Kind | Candidate / scope | Producer | Result | Limitation |
|---|---|---|---|---|---|
| `<path or ID>` | `<test/review/verification/integration>` | `<scope>` | `<agent/host>` | `<result>` | `<limitation>` |

## Exact next action

`<One action that is allowed now, including the file, command, or decision to make.>`

## Do not do

- Do not start `<next candidate>` until the current task is `PASS_CLOSED` and authorization exists.
- Do not use sensitive or real data, reserved evaluation data, release systems, external network, or credentials unless an approval reference is listed above.
- Do not treat a report, old test run, or self-review as fresh evidence.

## Session ledger

- Ledger mode (this session): `jspace.py controller ENABLED | manual five-line ledger (FALLBACK) | NOT_ENABLED waiver: <reason>`
- Ledger location: `.jspace/` (workspace root, untracked) — on a fresh clone the ledger itself is gone; this section is its only carrier
- Last seam / state: `<what the ledger recorded last>`
- Five-line snapshot (if controller unavailable):

```text
Goal:      <current leaf result>
Core:      <the one binding constraint/interface>
Verified:  <appended verified facts; mirror into Events at closure>
Open:      <open questions and their resolution conditions>
Next:      <the single next action>
```

## Capability notes

- Dependency/independent-review gaps: `AVAILABLE | MISSING | UNVERIFIED | FALLBACK | BLOCKED_TOOLING` — `<record>`

- Git / isolated workspace:
- Subprocess / test runner:
- Fresh context or independent reviewer:
- Network / external service:
- Persistent state / resume:
- Missing capability and required fallback:

## Resume instructions

1. Read `.charter/project.md`.
2. Read `.charter/roadmap.md`.
3. Read `.charter/reuse-discovery.md` and confirm its gate status and recheck date.
4. Read `.charter/current-task.md`.
5. Check the current candidate and evidence references.
6. Perform only the exact next action above; update this packet after the next seam.
