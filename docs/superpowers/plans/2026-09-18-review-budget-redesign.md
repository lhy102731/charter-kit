# Review Budget Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. **This plan is written for review first — do not start Task 1 until the user approves it.**

**Goal:** Replace `charter_review`'s per-attempt wall-clock budget with a single total-call budget consumed sequentially, so a slow-but-working review is never killed while a genuinely stalled one still is — and make the numbers measurable instead of asserted.

**Architecture:** The tool anchors one deadline at `execute()` and lets each attempt take `min(perAttemptCeiling, remaining)`. A fast route failure therefore leaves almost the whole budget for the session-model rerun, while a slow route failure leaves too little for a rerun that was doomed anyway — the rerun is then skipped with a reason rather than burning a second full budget. The provider's per-stream idle watchdog (default 300 s, `TIMEOUT` retryable) keeps owning true hangs; our total budget drops to a wide backstop against non-convergence and hung tool calls. The result carries the measurements that let the next budget be computed rather than guessed.

**Tech Stack:** Existing only — plain-JS DSH plugin (`targets/dsh/src/index.js`, `targets/dsh/client/client.js`), Python 3 stdlib tests, the repo's three builders and validator, headless Chromium for card evidence.

**Spec:** `docs/superpowers/specs/2026-09-18-review-budget-redesign-design.md` (written in Task 1, Step 1).

## Global Constraints

- **Do not restart DSH, do not reload the plugin, do not sync either install copy** (`D:\workspace\dsh-plugin-src\charter-kit-release\pkg`, `%USERPROFILE%\.agents\skills\charter-workflow`). Other work runs in this instance. Everything here is verified offline against the repo; activation is a separate, deliberate, user-approved step listed under *Out of scope*.
- Any live claim that would need the running instance is reported as **pending activation**, never simulated and never assumed.
- `portable/`, `skills/`, `targets/**` are hand-edited sources; `plugins/**` and root mirrors are generated and byte-checked. Builders run **codex → zcode → dsh**, then `python scripts/validate_kit.py .`. `SKILL.md` has three hand-edited copies that must end byte-identical to the three regenerated ones. `targets/dsh/` gains no `GENERATED.md`. Never hand-edit `plugins/**` or root `skills/**`.
- The tool's declared `timeoutMs` is **derived from the constants** and guard-enforced; a constant edit without re-deriving the deadline must fail a test.
- **The retracted premise stays retracted.** The rejected wording claimed a ~600 s host ceiling on total call duration. The measured mechanism is a **per-stream idle** watchdog (`DEFAULT_STREAM_IDLE_TIMEOUT_MS = 300_000`, `packages/llm/llm-pi-ai/src/config.ts:46`) whose `TIMEOUT` is retryable (`packages/llm/llm/src/retry-policy.ts:18`), which bounds *silence*, not *duration*. No task may reintroduce a total-duration claim derived from it.
- Card copy is Chinese and consistent with the existing card. Any behaviour the card claims must be true of the shipped tool.
- Real-DOM card behaviour is invisible to the committed harness (its `type()` passes a synthetic `target.value`), so card states require **real headless-browser evidence captured per state from the same run that writes the JSON**, and the report must state what that evidence proves and what it does not.
- **The idle-watchdog handover is an assumption, not a finding.** This plan raises the total budget on the premise that a genuinely silent provider stream is still cut by the adapter's own idle watchdog. That premise has **not been measured**. Until the activation check passes, the new defaults must not be trusted in production; if it fails, the correct response is to build the deferred progress probe **before** raising the budget — not to lower the budget back.
- **The shipped numbers are provisional hypotheses and are labelled as such.** `1800` and `7200` have no measurement behind them; Task 5 replaces them. No task, comment, README line, or spec sentence may present them as decided. Shipping them before calibration is a concession to the activation constraint (Task 5 Step 1), not a judgement that they are right.
- **No new arbitrary constant replaces an old one.** The previous `[30, 270]` clamp was rejected for being arithmetic on an unmeasured premise. Every threshold this plan introduces must state its justification in a comment, and any that cannot be justified from a mechanism or a measurement is marked `provisional` in the source and listed in the spec's open-questions section.

---

## File Structure

| Path | Responsibility |
|---|---|
| Modify `targets/dsh/src/index.js` | Budget semantics (one total deadline, sequential consumption, rerun floor), instrumentation fields, constants, optional per-call override. |
| Modify `targets/dsh/client/client.js` | Card: budget range/default/copy, and the override affordance if the design lands one. |
| Modify `tests/test_dsh_review_tool.py` | Behavioural coverage of budget consumption via a stubbed subagent registry; the rewritten arithmetic guard. |
| Modify `tests/dsh_client_card_harness.cjs` + `tests/test_dsh_client_card_behaviour.py` | Pinned card behaviours and the corrected range. |
| Modify `targets/dsh/README.md`, `README.md` (zh + en) | Contract text: what the budget bounds, what bounds hangs. |
| Modify `skills/charter-workflow/SKILL.md` ×3 (+ any hand-edited artifact stating the review contract) | Brief guidance: pass a self-contained brief containing the candidate diff; slow-model seats are for narrow scope. |
| Create `docs/superpowers/specs/2026-09-18-review-budget-redesign-design.md` | Design basis, including the retraction and its evidence. |
| Create `docs/superpowers/calibration/2026-09-18-review-budget.md` | The measurement recipe to run in the real project, with the numbers to fill in. |

---

## Task 1: One total budget, consumed sequentially

**Files:**
- Create: `docs/superpowers/specs/2026-09-18-review-budget-redesign-design.md`
- Modify: `targets/dsh/src/index.js`
- Test: `tests/test_dsh_review_tool.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `MIN_RERUN_BUDGET_SECONDS`, `totalBudgetMs()`, `remainingBudgetMs()`, `attemptBudgetMs()`, and the result fields `budgetSeconds`, `elapsedMs`, `attempts`, `rerunSkippedReason` — every later task uses these spellings.

- [ ] **Step 1: Write the design basis**

`docs/superpowers/specs/2026-09-18-review-budget-redesign-design.md` records, in this order and without softening:

1. **The observed failure.** A real project's Review B reported `cmd/z-ai/glm-5.3-flash timed out after 270.0s (budget 270s); the session-model rerun also failed: the session model timed out after 270.0s (budget 270s)`, total 540 021 ms. Both attempts died on our own clock; no host mechanism intervened. Measured shape: a compact-brief review took 130 s on one seat; the other seat's **single completion** took 85 s and 5 702 reasoning tokens (against 28 s / 1 331 tokens). A multi-turn review therefore cannot fit in 270 s.
2. **Why the old number existed and why it was wrong.** The clamp `[30, 270]` was derived from an assumed ~600 s host ceiling on total duration. That ceiling does not exist as described: the measured mechanism is a per-stream **idle** watchdog (`DEFAULT_STREAM_IDLE_TIMEOUT_MS = 300_000`) whose `TIMEOUT` is retryable, which produced the observed ~600 s on *hung* routes and does not bound a route that keeps streaming. `270 < 300` therefore protected nothing; it only guaranteed we killed working reviews before the stall detector could ever act.
3. **The corrected control model.** Silence is the host's business; non-convergence and hung tool calls are ours. Our budget must be wide enough for the slowest legitimate review and must never be the thing that fails a working one.
4. **The slow-model arithmetic.** At 20 tok/s, 5 000 tokens is 250 s and 10 000 is 500 s; a four-turn review is ~20 minutes. Raising the ceiling is necessary but is not the fix — the judgement must become progress-based (Task 6 lists that as deferred with entry conditions).
5. **What this plan does not claim.** It does not measure throughput, does not implement a progress probe, and does not activate anything in the running instance.

- [ ] **Step 2: Write the failing tests**

Add to `tests/test_dsh_review_tool.py` a small in-process stub registry so budget consumption is observable without waiting minutes. The stub drives `execute()` with a fake `ctx.subagents.start` whose run settles only when the test says so, and a clock the test advances.

**Naming convention, used by every test in this plan:** the helper `run_review(...)` returns an object whose attributes are spelled **exactly as the tool's JSON result spells them** (`outcome`, `attempts`, `elapsedMs`, `budgetSeconds`, `rerunSkippedReason`). Test arguments may use short names (`total_budget_s`, `route_fails_after_s`), but assertions must use the shipped spellings, so a rename in the tool breaks the test rather than silently passing.

```python
class BudgetConsumption(unittest.TestCase):
    """The stub's clock is the tool's `Date.now` source, so budgets are exercised in microseconds."""

    def test_a_fast_route_failure_leaves_the_rest_of_the_budget_for_the_rerun(self):
        # total 600s; the configured route fails at ~1s; the rerun must get ~599s, not 300s.
        calls = run_review(total_budget_s=600, route_fails_after_s=1, rerun_needs_s=200)
        self.assertEqual(calls.outcome, "fallback")
        self.assertGreaterEqual(calls.attempts[1].budget_s, 590)

    def test_a_slow_route_failure_skips_a_doomed_rerun_and_says_so(self):
        # total 600s; the route consumes 580s, leaving 20s — below 25% of the total.
        calls = run_review(total_budget_s=600, route_fails_after_s=580, rerun_needs_s=10)
        self.assertEqual(calls.outcome, "unavailable")
        self.assertEqual(len(calls.attempts), 1)
        self.assertIn("rerun skipped", calls.rerunSkippedReason)
        # which term bound the decision must be readable, so calibration can tell
        # whether the ratio or the absolute floor is doing the work
        self.assertIn("threshold", calls.rerunSkippedReason)

    def test_a_short_total_does_not_authorise_a_rerun_it_cannot_finish(self):
        # total 120s; 90s spent leaves 30s, under the 60s absolute floor even though
        # 30s is above 25% of 120s — the floor must bind here.
        calls = run_review(total_budget_s=120, route_fails_after_s=90, rerun_needs_s=1)
        self.assertIn("absolute floor", calls.rerunSkippedReason)

    def test_total_elapsed_never_exceeds_the_total_budget_plus_the_teardown_grace(self):
        calls = run_review(total_budget_s=600, route_fails_after_s=595, rerun_needs_s=999)
        self.assertLessEqual(calls.elapsedMs, (600 + TEARDOWN_GRACE_S) * 1000 + 2_000)

    def test_an_unset_seat_still_reproduces_todays_behaviour(self):
        calls = run_review(total_budget_s=600, route=None, rerun_needs_s=0)
        self.assertEqual(len(calls.attempts), 1)
        self.assertFalse(hasattr(calls, "rerunSkippedReason"))
        self.assertNotIn("agentOptions", calls.start_requests[0])
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `python -m unittest tests.test_dsh_review_tool -q`
Expected: FAIL — `run_review` does not exist.

- [ ] **Step 4: Implement the budget semantics**

In `targets/dsh/src/index.js`, replace the per-attempt fixed budget with one anchored deadline. The existing call-deadline helper used for dispatch/teardown races is the same mechanism; promote it to own the whole call.

```js
/**
 * A rerun repeats the same work, so it is worth starting only when enough of the
 * call budget remains for it to plausibly finish.
 *
 * PROVISIONAL. Both numbers are hypotheses pending the calibration in
 * docs/superpowers/calibration/2026-09-18-review-budget.md — erring low is the
 * defect this change exists to fix, so they start generous. The ratio is the
 * primary rule; the absolute floor exists only so that a tiny configured total
 * cannot authorise a rerun that cannot possibly complete.
 */
const MIN_RERUN_BUDGET_RATIO = 0.25          // provisional
const MIN_RERUN_BUDGET_SECONDS = 60          // provisional; floor only

const startedAt = Date.now()
const totalBudgetMs = () => budgetSeconds * 1000
const remainingBudgetMs = () => totalBudgetMs() - (Date.now() - startedAt)

const rerunThresholdMs = () =>
  Math.max(MIN_RERUN_BUDGET_SECONDS * 1000, totalBudgetMs() * MIN_RERUN_BUDGET_RATIO)

const rerunWorthAttempting = () => remainingBudgetMs() >= rerunThresholdMs()

/**
 * One attempt may take everything left. This is load-bearing and is an
 * ASSUMPTION, not a measurement: starving the rerun is right only when a slow
 * attempt means the work outgrew the budget, rather than the configured route
 * being slower than the session model. When the two seats differ sharply in
 * speed it can starve a fast rerun. Task 5 must measure per-seat speed, and
 * this comment is where the decision to keep or drop the reserve lands.
 */
const attemptBudgetMs = () => Math.max(0, remainingBudgetMs())

/** Name which term bound the decision, so calibration can see whether the floor or the ratio bit. */
const rerunSkippedReason = () => {
  const threshold = rerunThresholdMs()
  const binding = threshold === MIN_RERUN_BUDGET_SECONDS * 1000 ? "absolute floor" : "ratio"
  return `rerun skipped: ${Math.round(remainingBudgetMs() / 1000)}s remained, below the `
    + `${Math.round(threshold / 1000)}s threshold (${binding})`
}
```

Wire it so that: the first attempt arms its timer with `attemptBudgetMs()`; on a settled failure or a timeout, the rerun is attempted only when `rerunWorthAttempting()`, with its own timer at `attemptBudgetMs()` read **at that moment**; when it is not attempted, the result carries `rerunSkippedReason` naming the remaining seconds and the floor. Keep the existing composition of `exec.signal` with the per-attempt `AbortController`, the `finally` teardown race, and the unified `fallback`/`unavailable` outcomes. Do not change what counts as a failure.

- [ ] **Step 5: Run the tests to verify they pass**

Run: `python -m unittest tests.test_dsh_review_tool -q`
Expected: PASS, including the four new tests.

- [ ] **Step 6: Regenerate, validate, commit**

```bash
python scripts/build_codex_plugin.py && python scripts/build_zcode_plugin.py && python scripts/build_dsh_plugin.py
python scripts/validate_kit.py .
python -m unittest discover -s tests -q
git add docs/superpowers/specs/2026-09-18-review-budget-redesign-design.md targets/dsh/src/index.js tests/test_dsh_review_tool.py plugins/ skills/
git commit -m "fix: spend one total review budget sequentially instead of one per attempt"
```

---

## Task 2: Instrument the call so the next budget is measured, not guessed

**Files:**
- Modify: `targets/dsh/src/index.js`
- Test: `tests/test_dsh_review_tool.py`

**Interfaces:**
- Consumes: Task 1's result fields.
- Produces: result fields `elapsedMs`, `attempts[]` (each `{route, budgetSeconds, elapsedMs, failure, effort}`), `remainingSeconds`, `killedWhileProgressing`, and — **only if the investigation in Step 1 shows it is cheaply observable** — `child.turns` and `child.tokensPerSecond`. Two of these exist for specific reasons:
  - `killedWhileProgressing` (`true | false | "unknown"`) is the datum that makes the report actionable: it is the difference between "raise the budget, it was working" and "it produced nothing, raise nothing". When the investigation cannot establish it, it must be the string `"unknown"` — **never** inferred from elapsed time.
  - `attempts[].effort` closes a known gap: today a rerun reports only the final seat's effort, so a failed first attempt's reasoning level vanishes from the record.

- [ ] **Step 1: Establish what is observable, before writing any of it**

The child run exposes `run.localAgent` (`packages/subagent/subagent/src/types.ts`), so its session may be readable. Determine, by reading the harness, whether a per-child **turn count**, **output-token count**, or **first-token latency** can be obtained from the host half cheaply and without subscribing to anything unbounded. Write the finding into the report and into the spec. **If it cannot, implement the timing fields only and state plainly which measurements are missing** — do not approximate a turn count from elapsed time, because that is the kind of assertion this plan exists to remove.

- [ ] **Step 2: Write the failing tests**

```python
    def test_the_result_reports_what_was_spent_and_where(self):
        calls = run_review(total_budget_s=600, route_fails_after_s=5, rerun_needs_s=1)
        self.assertEqual([a["route"] for a in calls.attempts], ["route", "session"])
        for attempt in calls.attempts:
            self.assertGreater(attempt["elapsedMs"], 0)
        self.assertLess(calls.remainingSeconds, 600)

    def test_an_unobserved_measurement_is_absent_rather_than_zero(self):
        calls = run_review(total_budget_s=600, route=None, rerun_needs_s=0)
        self.assertNotIn("tokensPerSecond", getattr(calls, "child", None) or {})

    def test_an_unobservable_progress_verdict_is_unknown_not_a_guess(self):
        # Whether the child was still producing output when the clock ran out is the
        # datum that tells the user whether raising the budget would help. When the
        # harness cannot observe it, say "unknown" — never infer it from elapsed time.
        calls = run_review(total_budget_s=600, route_fails_after_s=600, rerun_needs_s=0,
                           child_progress_observable=False)
        self.assertEqual(calls.killedWhileProgressing, "unknown")

    def test_a_budget_kill_records_whether_the_child_was_still_working(self):
        calls = run_review(total_budget_s=600, route_fails_after_s=600, rerun_needs_s=0,
                           child_progress_observable=True, child_was_producing=True)
        self.assertIs(calls.killedWhileProgressing, True)
```

- [ ] **Step 3: Run to verify they fail, implement, run to verify they pass**

Run: `python -m unittest tests.test_dsh_review_tool -q`
Expected: FAIL, then PASS after the fields are added. Keep the field set flat and documented in the tool description's returned shape.

- [ ] **Step 4: Regenerate, validate, commit**

```bash
python scripts/build_codex_plugin.py && python scripts/build_zcode_plugin.py && python scripts/build_dsh_plugin.py
python scripts/validate_kit.py . && python -m unittest discover -s tests -q
git add -A && git commit -m "feat: report where a review spent its budget"
```

---

## Task 3: Constants, the card, a per-call override, and the guard rewritten

**Files:**
- Modify: `targets/dsh/src/index.js`, `targets/dsh/client/client.js`
- Modify: `tests/test_dsh_review_tool.py`, `tests/dsh_client_card_harness.cjs`, `tests/test_dsh_client_card_behaviour.py`
- Modify: `targets/dsh/README.md`, `README.md` (zh + en)

**Interfaces:**
- Consumes: Tasks 1–2.
- Produces: `MIN_TOTAL_BUDGET_SECONDS = 60`, `DEFAULT_TOTAL_BUDGET_SECONDS = 1800`, `MAX_TOTAL_BUDGET_SECONDS = 7200`, `REVIEW_TOOL_TIMEOUT_MARGIN_SECONDS = 60`; the tool's declared `timeoutMs = (MAX_TOTAL_BUDGET_SECONDS + REVIEW_TOOL_TIMEOUT_MARGIN_SECONDS) * 1000`; the optional tool parameter `budgetSeconds`.

- [ ] **Step 1: Rewrite the arithmetic guard, then make it pass**

The current guard reads MIN/MAX/DEFAULT/MARGIN from the source and asserts `declared > 2 * MAX` and `declared < 600`. Both clauses encode the retracted premise: one attempt may now consume the whole budget, and 600 s is not a total-duration ceiling. Replace it with:

```python
    def test_the_declared_deadline_covers_the_whole_call(self):
        declared = read_constant("REVIEW_TOOL_TIMEOUT_MS")
        margin = read_constant("REVIEW_TOOL_TIMEOUT_MARGIN_SECONDS")
        maximum = read_constant("MAX_TOTAL_BUDGET_SECONDS")
        self.assertEqual(declared, (maximum + margin) * 1000,
                         "the declared deadline must be derived from the constants")
        self.assertLess(read_constant("MIN_TOTAL_BUDGET_SECONDS"),
                        read_constant("DEFAULT_TOTAL_BUDGET_SECONDS"))
        self.assertLessEqual(read_constant("DEFAULT_TOTAL_BUDGET_SECONDS"), maximum)
        source = (ROOT / "targets" / "dsh" / "src" / "index.js").read_text(encoding="utf-8")
        # Assert the retracted CLAIM is gone, never that the digits are gone: the
        # comment recording the retraction legitimately contains the number, and a
        # digits-are-absent assertion would fail on the very documentation Task 1
        # requires. Match the claim, not the constant.
        for retracted in ("合计仍低于", "600s ceiling", "600 秒的上限", "2 * MAX"):
            self.assertNotIn(retracted, source,
                             f"a retracted premise resurfaced in the shipped source: {retracted}")
        self.assertIn("idle", source.lower(),
                      "the constants must document that silence, not duration, is the host's business")
        self.assertIn("provisional", source.lower(),
                      "a threshold with no measurement behind it must be labelled provisional")
```

Run it first and watch it fail against the current constants, so the guard is known to bite.

- [ ] **Step 2: Set the constants and the derived deadline**

`MIN 60`, `DEFAULT 1800`, `MAX 7200`, `MARGIN 60` → declared `7_260_000`. A comment beside each states: the budget bounds non-convergence and hung tool calls, **not** stream silence, which the provider's idle watchdog owns.

- [ ] **Step 3: Add the per-call override**

Optional tool parameter `budgetSeconds` (integer, clamped to `[MIN, MAX]`, defaulting to the configured value). Rationale, recorded in the description: the card is a deployment-wide setting, while the workflow knows how large this particular review is. Reject a non-integer or out-of-range value with a clear message rather than clamping silently.

- [ ] **Step 4: Update the card**

Range and default (`min 60`, `max 7200`, default 1800), and replace the hint copy. The rejected sentence was: *"工具会把该值限制在 30–270 秒之间（一次评审最多两次尝试，合计仍低于宿主约 600 秒的上限）"*. The replacement must say: the value is the whole call's budget including any rerun; a rerun happens only if enough of it remains; a genuinely silent provider stream is cut by the host's own idle timeout, which this value does not substitute for. It must **also warn what the maximum means in practice** — 7200 s is two hours, and a tool call holding a seat that long should be a deliberate choice, not a default someone scrolls past. Update the harness's pinned range behaviour and record the pin change deliberately.

- [ ] **Step 5: Update the contract text**

`targets/dsh/README.md` and both `README.md` editions: state what the budget bounds and what it does not, and delete the 600 s ceiling sentence wherever it survives. Verify by scanning every carrier for the retracted phrases rather than by editing the ones you remember.

- [ ] **Step 6: Real-browser evidence, then gates and commit**

Capture per-state screenshots of the card **from the same run that writes the JSON**: the field showing the new default and range, the hint copy, and a rejected out-of-range entry. Then:

```bash
python scripts/build_codex_plugin.py && python scripts/build_zcode_plugin.py && python scripts/build_dsh_plugin.py
python scripts/validate_kit.py . && python -m unittest discover -s tests -q
python scripts/build_codex_plugin.py --check && python scripts/build_zcode_plugin.py --check && python scripts/build_dsh_plugin.py --check
git status --porcelain
git add -A && git commit -m "feat: budget the whole review call, with a per-call override and honest copy"
```

---

## Task 4: Cut the work, not just the clock

**Files:**
- Modify: `targets/dsh/src/index.js` (tool description), `skills/charter-workflow/SKILL.md` ×3, both `README.md` editions
- Test: `tests/test_workflow_contract.py`

**Interfaces:**
- Consumes: nothing.
- Produces: the guidance that at slow throughput the dominant cost is turns × tokens.

- [ ] **Step 1: Write the failing test**

Reuse that module's content-discovery helper (glob by content, with a floor so a shrunken discovery fails).

```python
def test_the_brief_contract_names_the_diff(self):
    carriers = discover_carriers("self-contained brief")
    self.assertGreaterEqual(len(carriers), 3)
    for text in carriers:
        self.assertIn("candidate diff", text)
        self.assertIn("turns", text)
```

- [ ] **Step 2: Run to verify it fails, then write the guidance**

State, in the tool description and in every `SKILL.md` copy: a review is a **multi-turn** agent run, so the brief must be **self-contained — the leaf contract, the spec, and the candidate diff**, because a child that has to discover the diff itself pays for it in turns; and at a slow seat's throughput, turns × tokens is the whole cost. Add the routing note: a slow seat belongs on a **narrow, risk-triggered** review, not on every leaf.

- [ ] **Step 2b: Settle the override's caller, or delete the parameter**

Task 3 adds `budgetSeconds` so a caller can size a review the deployment-wide card cannot know about. **A parameter nobody passes is the `declared-but-unused` pattern this repository has already recorded as a lesson**, so this task must either give it a trigger or remove it:

- Give it a trigger: state in every carrier that when the candidate diff exceeds a named threshold — provisional: **more than 400 changed lines or more than 20 files** — the caller **must** pass an explicit `budgetSeconds`, and say why (at a slow seat's throughput the default may not cover it).
- Or delete the parameter here and rely on the card alone.

Record which of the two happened and why. Do not ship it unused, and do not leave the decision implicit.

- [ ] **Step 3: Run to verify it passes, regenerate, commit**

```bash
python -m unittest tests.test_workflow_contract -q
python scripts/build_codex_plugin.py && python scripts/build_zcode_plugin.py && python scripts/build_dsh_plugin.py
python scripts/validate_kit.py .
sha256sum skills/charter-workflow/SKILL.md targets/*/skills/charter-workflow/SKILL.md plugins/*/skills/charter-workflow/SKILL.md
git add -A && git commit -m "docs: make the review brief self-contained, because turns are the cost"
```

---

## Task 5: The calibration recipe

**Files:**
- Create: `docs/superpowers/calibration/2026-09-18-review-budget.md`
- Test: `tests/test_workflow_contract.py` (presence + required content only)

**Interfaces:**
- Consumes: Task 2's result fields.
- Produces: the procedure that turns the shipped defaults into measured ones.

- [ ] **Step 1: Write the recipe, as commands and a table to fill**

The recipe must specify: pick three review sizes (small / medium / large diff) in a real project; run each **N ≥ 5** times per seat; record from each call the reported `elapsedMs`, `attempts`, observed tokens/s, and child turns (when available); compute **p95, not the median**, per size; set `DEFAULT_TOTAL_BUDGET_SECONDS` from the largest p95 plus margin and `MAX` from the worst observed; then update the constants in one commit, which the Task 3 guard re-derives the declared deadline from. It must also state the honesty rule: **do not tune the constants to make a preferred story true, and record the raw numbers beside the derived ones.**

**Why the constants ship before this task, and why that is not a contradiction.** Calibration needs a live instance, and the Global Constraints forbid activating one during these tasks. The defaults therefore ship as **labelled provisional hypotheses**, and this task is the thing that closes them. If you catch yourself defending `1800`/`7200` as though they were measured, stop — the spec's open-questions section lists them as unmeasured, and that section is what this task edits.

**Success is a defensible number from whatever is observable — not a specific field set.** Task 2 Step 1 may conclude that throughput or turn counts cannot be read from the host half. Then calibrate from what you do have: per-size wall-clock p95 and the attempt records, with rate information taken from the provider's own logs or usage reporting if such a thing exists. If no rate measurement is available anywhere, **say so explicitly** and set the defaults from wall-clock p95 alone, labelled as such. Do not substitute an assumed tokens/second figure, and do not let a missing measurement block the task — an honest wall-clock-only calibration beats an invented rate.

- [ ] **Step 2: Test, commit**

```python
def test_calibration_recipe_states_its_method(self):
    text = (ROOT / "docs" / "superpowers" / "calibration" / "2026-09-18-review-budget.md").read_text(encoding="utf-8")
    for required in ("p95", "N ≥ 5", "tokens/s", "do not tune"):
        self.assertIn(required, text)
```

```bash
python -m unittest tests.test_workflow_contract -q
git add -A && git commit -m "docs: how to measure the review budget instead of asserting it"
```

---

## Activation checklist (not part of these tasks)

Nothing below happens until the user approves it, and none of it is performed by an implementer working through the tasks above.

- [ ] **Step A1: Verify the idle-watchdog handover before trusting the new defaults.** This is the plan's one unmeasured premise. Configure a seat to a route that will go **silent** (a deliberately wrong model id produces a fast error, so instead use a route known to hang, or point at an endpoint that accepts and never streams). Set the budget high (e.g. 1800 s). Run one review and record **when** the failure arrives and **which** component reported it.
  - Arrives in roughly 300 s naming a stream idle timeout → the premise holds; the host owns silence and the budget may stay wide.
  - Runs the full 1800 s → **the premise is false.** Do not lower the budget back: that reinstates the defect this plan fixes. Build the deferred progress probe first, because in that world nothing but our clock detects a hang.
- [ ] **Step A2: Sync the two install copies** from the built tree (`D:\workspace\dsh-plugin-src\charter-kit-release\pkg`, `%USERPROFILE%\.agents\skills\charter-workflow`), preserving the install-specific `package.json` and `cordis.patch.yml`.
- [ ] **Step A3: Reload the plugin** and confirm the card shows the new range, default, and hint copy.
- [ ] **Step A4: Run Task 5's calibration in the real project** and commit the measured constants; the guard re-derives the declared deadline automatically.
- [ ] **Step A5: Record in the ledger** what A1 showed, whatever it showed.

## Out of scope (deliberately)

- **Progress probe (phase 2).** Killing on *no activity* rather than on elapsed time is the correct long-term control, and it is the only thing that fully covers a hung **tool call** (no stream is outstanding, so the provider's idle watchdog never arms). It is deferred until its entry conditions hold: (a) the child session is confirmed observable cheaply from the host half, including tool-call activity, not just LLM output; (b) a probe that samples it cannot itself leak a timer or hold the child open. Task 2 Step 1 is the reconnaissance that unblocks it.
- **Non-blocking review.** Dispatching the review as a background job and collecting it later would remove the wait entirely rather than bounding it. It changes the tool's contract and is a separate design.
- **Activation.** Syncing the two install copies, reloading the plugin, and any live verification happen only when the user approves, in that order, and are never performed as part of these tasks.
- **Automatic budget adaptation.** Deriving the budget from measured throughput automatically is attractive and premature: it would need the same observability phase 2 requires.

## What this plan is actually for

One sentence, to keep every later edit honest: **it stops our clock from failing reviews that are working, and makes the next number come from measurement instead of arithmetic on a premise we have already retracted.** It does not make reviews faster, and it does not detect a hung tool call — the deferred progress probe under *Out of scope* is what does that.
