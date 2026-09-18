# Review budget calibration

> Purpose: replace the **provisional** constants in `targets/dsh/src/index.js`
> (`MIN_REVIEW_TIMEOUT_SECONDS = 30`, `DEFAULT_REVIEW_TIMEOUT_SECONDS = 600`,
> `MAX_REVIEW_TIMEOUT_SECONDS = 1800`) with values measured from real reviews.
> Until this file has numbers in it, those constants are hypotheses and the source
> says so.

## Why the current numbers are provisional

`270` was measured and found too small: a real project lost a Review B to two
attempts that both died on **this** clock at 270 s (540 021 ms together), with no
host mechanism intervening — one seat needed 130 s for a compact brief, the other
spent 85 s and 5 702 reasoning tokens on a single completion. `600`/`1800` are a
deliberate over-correction because erring low is the defect being fixed. They are
not measurements.

## What bounds what (do not conflate these)

- **Our budget** bounds *our own patience*: it is the per-attempt wall clock, and a
  review makes up to two attempts (the configured route, then the session model).
- **The host's per-stream idle watchdog** bounds *silence*: `DEFAULT_STREAM_IDLE_TIMEOUT_MS
  = 300_000` in `packages/llm/llm-pi-ai/src/config.ts`, whose `TIMEOUT` is retryable
  per `packages/llm/llm/src/retry-policy.ts`. A review that keeps streaming is **not**
  bounded by it.
- A **hung tool call** inside the child (no stream outstanding) is bounded by
  neither in a useful way — that is what the deferred progress probe is for.

## How to measure

1. **Sizes.** Classify the review's input by the candidate diff: small (< 100 changed
   lines), medium (100–400), large (> 400). Record files touched alongside lines,
   because turn count tracks both.
2. **Runs.** **N ≥ 5 per size per seat.** One run is not a measurement; a single
   fast or slow sample says nothing about the distribution.
3. **Record per run**, from the tool's own result rather than from memory:
   - the result JSON as returned (`outcome`, `model`, `effort`);
   - `elapsedMs` — and, when the task-2 instrumentation lands, the per-attempt
     breakdown, attempts taken, remaining budget, and `killedWhileProgressing`;
   - diff size (files / lines) and whether the **brief contained the diff** or the
     child had to discover it (that distinction is what the guidance in item C exists
     to change, and it moves the numbers more than any constant).
4. **Reduce with p95, not the median.** A median budget fails the slow tail, and the
   slow tail is exactly the case that produced this work.
5. **Set the constants** from the largest per-size p95 plus margin for `DEFAULT`, and
   from the worst observed run for `MAX`. Update them in one commit; the guard in
   `tests/test_dsh_review_tool.py` re-derives `REVIEW_TOOL_TIMEOUT_MS` from them, so a
   constant edit that forgets the derivation fails rather than ships.

## Honesty rules for this file

- **Do not tune the constants to make a preferred story true.** Record the raw runs
  in the table below, including the ones that argue against the value you picked.
- **An unobserved measurement is not a zero and not a guess.** If throughput or turn
  counts cannot be read from the host half, calibrate from wall-clock p95 alone and
  say so; never substitute an assumed tokens/second figure.
- Record which measurements were actually available, so the next reader knows the
  basis of the number rather than assuming the full set.

## Runs

| date | project | seat | size | diff files/lines | brief had diff? | outcome | model | effort | elapsed | notes |
|---|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | | |

## Open questions this file must close

- Is `600` enough for a medium diff on the slowest seat actually in use, or does the
  p95 exceed it?
- Does a two-attempt worst case ever get reached in practice, and if so does the
  second attempt succeed (which would argue for the sequential-consumption design) or
  fail identically (which would argue for skipping a doomed rerun)?
- When a review dies on our clock, was it **still producing output**? That single
  datum decides whether raising the budget helps at all, and it is why
  `killedWhileProgressing` exists.
