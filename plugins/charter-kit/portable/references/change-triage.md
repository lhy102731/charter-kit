# Change Triage

Use this contract whenever a new requirement, clarification, defect, discovered constraint, or risk appears during a chartered task.

## Event kinds

- `NEW_REQUIREMENT` — the request adds observable behavior or acceptance.
- `CLARIFICATION` — the request makes an existing requirement precise without changing scope.
- `DEFECT` — the current implementation or contract no longer matches the approved result.
- `DISCOVERED_CONSTRAINT` — a new limit, dependency, or boundary changes what is safely possible.
- `RISK` — a concern that does not yet justify a scope change but may influence the route.

## Routes

- `IN_CONTRACT` — the current Leaf can absorb the change without changing the approved goal, non-goals, or invariants.
- `LEAF_CHANGE` — the Leaf contract needs an adjustment, but the roadmap and charter still stand.
- `ROADMAP_CHANGE` — the sequence, dependencies, or slice boundary must change, but the charter goal still stands.
- `CHARTER_CHANGE` — the approved goal, non-goals, invariants, scope, or public meaning must change.
- `OUT_OF_SCOPE` — the request is outside the approved charter or needs new authorization before it can be accepted.

## Precedence

Choose the first route that applies in this order:

`CHARTER > ROADMAP > LEAF > IN_CONTRACT`

If a route would change the approved goal, non-goals, invariants, or public meaning, treat it as `CHARTER_CHANGE` even if a smaller leaf edit also seems possible.

## Rules

- New requirement must not silently expand the current Leaf.
- Record the triggering event kind before selecting a route.
- Keep the current task contract as the active Leaf state authority; use the roadmap only as a projection.
- If a request can be satisfied by clarification alone, do not widen scope.
- If the route is `OUT_OF_SCOPE`, stop and ask for the new authorization instead of folding the request into the current task.
