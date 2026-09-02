# Evidence Receipt

> Use one receipt per meaningful test, inspection, review, or integration check. Record what was observed, not only what the Agent concluded.

## Identity

- Evidence ID: `<E-ID>`
- Project / task: `<project> / <TASK-ID>`
- Kind: `TEST | REVIEW | VERIFICATION | INTEGRATION | DECISION | AUDIT | DISCOVERY`
- Producer: `<agent/person>`
- Host / run: `<host and run reference>`
- Recorded at: `<YYYY-MM-DDThh:mm:ssZ>`

## Subject and version

- Candidate / revision: `<branch, commit, or provider revision>`
- Scope inspected: `<paths, inputs, dataset scope, or behavior>`
- Predecessor evidence: `<IDs>`
- Discovery query / source tier (when `DISCOVERY`): `<exact query or path; workspace / installed / internal / official / web>`
- Discovery result status (when `DISCOVERY`): `MATCHES | NO_MATCH | NOT_SEARCHED | NOT_AUTHORIZED | BLOCKED_TOOLING`
- Candidate revision / license (when `DISCOVERY`): `<fixed immutable commit/tag/package version or NO_MATCH; SPDX and attribution status>`

## Change Triage

- Record the event kind and route from `portable/references/change-triage.md` when this receipt supports a scope or authority decision.
- Keep the precedence choice explicit: `CHARTER > ROADMAP > LEAF > IN_CONTRACT`.
- New requirement must not silently expand the current Leaf.

## Operation

- Command, test, or manual operation:

```text
<exact operation or a precise manual observation>
```

- Expected result:
- Actual result:
- Exit class: `PASS | FAIL | ERROR | SKIPPED | NOT_RUN`
- Raw output reference: `<path, log, screenshot, or other artifact>`

For `DISCOVERY`, `NO_MATCH` is valid only when the exact operation actually ran and this raw output reference is present; an omitted or unauthorized tier must use `NOT_SEARCHED`/`NOT_AUTHORIZED` instead.

## Coverage and limitations

- Covered:
- Not covered:
- Fresh context/process: `yes | no | unavailable | not applicable`
- Independent from implementer: `yes | no | not applicable`
- Capability limitation:
- Search limitation / recheck trigger (when `DISCOVERY`): `<uncovered scope, tool gap, or expiry condition>`

## Interpretation

`<What this receipt proves, and what it does not prove.>`

An evidence receipt does not by itself change task state. The task contract and state transition record decide whether it is sufficient.
