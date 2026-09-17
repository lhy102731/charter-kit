"""Structural assertions over the DSH adapter source.

Every test here reads ``targets/dsh/src/index.js`` as text. Source text can pin
a literal's spelling, the presence of a field read, and the shape of a return
site. It cannot execute the tool, so these tests are NOT evidence that
``charter_review`` behaves correctly; the live re-run on a DSH host is that
evidence. They exist to catch a regression in the shape the fix established.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "targets/dsh/src/index.js"


class DshReviewToolTest(unittest.TestCase):
    def setUp(self):
        self.text = SOURCE.read_text(encoding="utf-8")

    def test_declares_review_settings_namespace(self):
        self.assertIn("charter-kit-review", self.text)

    def test_registers_settings_section(self):
        self.assertIn("installSection", self.text)

    def test_declares_the_settings_fields(self):
        for field in (
            "reviewAProvider",
            "reviewAModel",
            "reviewBProvider",
            "reviewBModel",
            "reviewTimeoutSeconds",
            # One selected reasoning-effort level per seat (task 16). '' is the
            # no-selection value, so the field has to exist for the reader to
            # see it at all.
            "reviewAEffort",
            "reviewBEffort",
        ):
            self.assertIn(field, self.text, field)

    def test_registers_charter_review_tool(self):
        self.assertIn("charter_review", self.text)
        self.assertIn("scope.tools.register", self.text)

    def test_tool_output_provides_render(self):
        # Spike finding: output without render fails after a successful execute.
        self.assertIn("render:", self.text)

    def test_wires_model_override_through_agent_options(self):
        self.assertIn("agentOptions", self.text)
        self.assertIn("scope.subagents.start", self.text)

    def test_declares_only_the_skill_as_a_required_service(self):
        # A missing injected service leaves this plugin's fiber pending, so the
        # Skill registration must not depend on any other service: naming
        # `tools`, `settings`, or `subagents` here withholds `charter-workflow`
        # from a host that lacks one.
        self.assertIn("export const inject = ['skills']", self.text)

    def test_waits_for_the_tool_half_services_in_the_optional_idiom(self):
        # The namespace and the tool need these three. `ctx.inject` waits for
        # them without holding the Skill registration behind them.
        self.assertIn("ctx.inject(['tools', 'settings', 'subagents'], (scope) => {", self.text)

    def test_declares_the_kind_enum_so_a_bad_kind_cannot_run_review_a(self):
        # Without the enum the tool read `kind: 'b'` as A, so a caller asking for
        # the RVB-required adversarial review silently got a coverage review.
        self.assertIn("enum: ['A', 'B']", self.text)

    def test_no_handler_style_slash_command(self):
        self.assertNotIn("ctx.commands.register", self.text)


class DshReviewToolFailureReportingTest(unittest.TestCase):
    """Structural only. See the module docstring for what these can claim."""

    def setUp(self):
        self.text = SOURCE.read_text(encoding="utf-8")

    def test_reads_the_child_stop_reason_and_diagnostic(self):
        # A child that fails without throwing settles here, so both fields have
        # to be read from the settled result rather than assumed.
        self.assertIn("result.stopReason", self.text)
        self.assertIn("result.diagnostic", self.text)

    def test_pins_the_provider_completed_stop_reason_value(self):
        # The literal comes from SubagentStopReasonMap in the DSH subagent
        # types. Pinning it here fails the suite if anyone guesses a spelling.
        self.assertIn("COMPLETED_STOP_REASON = 'completed'", self.text)
        self.assertIn("stopReason !== COMPLETED_STOP_REASON", self.text)

    def test_classifies_every_child_run_before_reading_its_text(self):
        self.assertIn("classifyRun(outcome.value, elapsedMs())", self.text)
        # The defect shape was a raw extraction returned straight as a review.
        self.assertNotIn("outputText(await", self.text)

    def test_empty_text_is_a_failure_rather_than_a_success(self):
        self.assertIn("child completed with an empty review", self.text)

    def test_reuses_the_unavailable_outcome_for_a_failed_rerun(self):
        self.assertIn("the session-model rerun also failed", self.text)
        self.assertIn("outcome: 'unavailable'", self.text)
        self.assertIn("review: ''", self.text)

    def test_fallback_reason_names_the_route_the_failure_and_the_duration(self):
        # One renderer, so route + what happened + how long cannot be applied to
        # two of the three failure shapes and forgotten on the third.
        self.assertIn("const failureReason = (label, attempt) => {", self.text)
        self.assertIn("timed out after ${seconds} (budget ${budgetSeconds}s)", self.text)
        self.assertIn("returned an empty review after ${seconds}", self.text)
        self.assertIn("failed after ${seconds}: ${attempt.detail}", self.text)

    def test_keeps_the_child_guard_in_a_finally_block(self):
        # The child is still released on every path — including the deadline
        # path — but the release is now bounded, so what is pinned is the guard
        # call inside the `finally` rather than a bare `await run.dispose()`.
        self.assertIn("} finally {", self.text)
        self.assertIn("disposal = await releaseRun(run)", self.text)
        self.assertIn("run.dispose()", self.text)

    def test_still_skips_a_route_the_provider_cannot_carry(self):
        self.assertIn("capabilities?.agentOptions === true", self.text)

    def test_routes_every_attempt_through_one_guarded_wrapper(self):
        # Dispatch, the deadline, classification, disposal, and error mapping
        # live in one place, so no call site — the configured one, the recovery
        # rerun, or the session-route branch — can leak a raw rejection out of
        # `execute`.
        #
        # The count changed in task 16, deliberately: the three call sites now
        # go through `runWithEffort`, which records the effort each dispatch
        # carries before delegating, so the result can report the level of the
        # run that produced the review rather than of an earlier attempt. The
        # guarded wrapper is still the only place that dispatches.
        self.assertIn("const runReview = async (agentOptions) => {", self.text)
        # One dispatch, inside the wrapper: the only place `runReview` is called
        # is the wrapper's own `return runReview(options)`.
        self.assertEqual(self.text.count("runReview("), 1)
        self.assertEqual(self.text.count("return runReview(options)"), 1)
        self.assertIn("const runWithEffort = async (options, applied) => {", self.text)
        self.assertEqual(self.text.count("await runWithEffort("), 3)
        self.assertNotIn("runOnce", self.text)

    def test_reaches_the_llm_runtime_in_its_own_optional_scope(self):
        """Pin the scope shape the degrade depends on.

        Two independent failures live in one line here. Naming `llm` in the
        top-level `inject` array would leave this plugin's fiber PENDING on a
        host without an LLM runtime, and the skill registration would go down
        with it. Naming it beside `tools`/`settings`/`subagents` in the outer
        optional scope is the same failure one level in: the whole tool would
        wait for a service it is required to degrade without. So `llm` waits in
        its own inner scope, and the tool keeps running when that scope never
        fires.
        """
        self.assertIn("export const inject = ['skills']", self.text)
        self.assertIn("scope.inject(['llm'], (llmScope) => {", self.text)
        self.assertIn("typeof llm.resolveModelInfo !== 'function'", self.text)
        # The lookup is bounded, and every answer that is not a declaration —
        # absent service, rejection, timeout, a route with no reasoning — has a
        # defined result instead of a throw out of the tool.
        self.assertIn("const LLM_CAPABILITY_TIMEOUT_MS = 5000", self.text)
        self.assertIn("return { available: false, ids: null }", self.text)
        self.assertIn("return { available: true, ids: null }", self.text)


class DshReviewTimeoutTest(unittest.TestCase):
    """Structural only. See the module docstring for what these can claim."""

    def setUp(self):
        self.text = SOURCE.read_text(encoding="utf-8")

    def test_declares_a_deadline_the_harness_cannot_preempt(self):
        # The setting is dynamic and `timeoutMs` is fixed at registration, so the
        # declared value has to cover the worst case the clamp can express. It is
        # DERIVED from that clamp rather than written as a second literal, so the
        # two cannot drift apart when either is edited.
        self.assertIn("timeoutMs: REVIEW_TOOL_TIMEOUT_MS,", self.text)
        self.assertIn(
            "const REVIEW_TOOL_TIMEOUT_MS = "
            "(MAX_REVIEW_TIMEOUT_SECONDS * 2 + REVIEW_TOOL_TIMEOUT_MARGIN_SECONDS) * 1000",
            self.text,
        )

    def test_clamps_the_configured_budget_between_the_two_bounds(self):
        self.assertIn("const MIN_REVIEW_TIMEOUT_SECONDS = 30", self.text)
        self.assertIn("const MAX_REVIEW_TIMEOUT_SECONDS = 270", self.text)
        self.assertIn("const DEFAULT_REVIEW_TIMEOUT_SECONDS = 240", self.text)
        # A non-number defaults; anything numeric is floored into [MIN, MAX].
        self.assertIn("typeof raw === 'number' && Number.isFinite(raw)", self.text)
        self.assertIn(
            "Math.min(MAX_REVIEW_TIMEOUT_SECONDS, Math.max(MIN_REVIEW_TIMEOUT_SECONDS, seconds))",
            self.text,
        )

    def test_the_declared_deadline_covers_the_two_attempt_worst_case(self):
        """The defect this pins: a clamp dimensioned against ONE attempt.

        A call may spend the configured attempt and then a session-model rerun,
        so the quantity that has to fit under the host's ~600 s ceiling is
        ``2 * MAX``, not ``MAX``. Sized at the ceiling itself, a full-budget
        attempt plus a full-budget rerun overruns it and the call is killed from
        outside with nothing rendered — the exact failure this budget exists to
        remove. The numbers are read out of the shipped source rather than
        restated here, so editing a constant without redoing the arithmetic
        fails this test instead of passing it.
        """
        numbers = {
            name: int(value)
            for name, value in re.findall(
                r"^const (MIN_REVIEW_TIMEOUT_SECONDS|MAX_REVIEW_TIMEOUT_SECONDS"
                r"|DEFAULT_REVIEW_TIMEOUT_SECONDS|REVIEW_TOOL_TIMEOUT_MARGIN_SECONDS"
                r"|REVIEW_TEARDOWN_GRACE_SECONDS) = (\d+)$",
                self.text,
                re.MULTILINE,
            )
        }
        self.assertEqual(
            sorted(numbers),
            [
                "DEFAULT_REVIEW_TIMEOUT_SECONDS",
                "MAX_REVIEW_TIMEOUT_SECONDS",
                "MIN_REVIEW_TIMEOUT_SECONDS",
                "REVIEW_TEARDOWN_GRACE_SECONDS",
                "REVIEW_TOOL_TIMEOUT_MARGIN_SECONDS",
            ],
            f"could not read every bound out of the source: {numbers}",
        )
        minimum = numbers["MIN_REVIEW_TIMEOUT_SECONDS"]
        maximum = numbers["MAX_REVIEW_TIMEOUT_SECONDS"]
        default = numbers["DEFAULT_REVIEW_TIMEOUT_SECONDS"]
        margin = numbers["REVIEW_TOOL_TIMEOUT_MARGIN_SECONDS"]
        grace = numbers["REVIEW_TEARDOWN_GRACE_SECONDS"]

        # The default has to be a value the clamp leaves alone.
        self.assertLessEqual(minimum, default)
        self.assertLessEqual(default, maximum)

        # One attempt can spend its own timer AND a teardown grace, so the worst
        # case a single attempt contributes is MAX + GRACE, not MAX.
        per_attempt_s = maximum + grace
        worst_case_s = per_attempt_s * 2
        declared_s = maximum * 2 + margin
        # The agreed bounds: 2 * 270 + 30 = 570 s, over 2 * (270 + 10) = 560 s.
        self.assertEqual((minimum, maximum, default), (30, 270, 240))
        self.assertEqual(declared_s, 570)
        # The declared deadline covers the whole call, teardown included...
        self.assertGreaterEqual(declared_s, worst_case_s)
        # ...and still fires before the ~600 s ceiling the host enforces, so THIS
        # tool renders the fallback instead of being preempted by an opaque
        # TOOL_TIMEOUT.
        self.assertLess(declared_s, 600)

    def test_bounds_every_await_it_owns_not_only_the_child_result(self):
        """The residual defect: only `run.result` was inside a race.

        `start()` and `dispose()` were awaited outside every timer, so a provider
        that never publishes a run, or never reaches quiescence, held the call
        open past the deadline this tool declares. Nothing else stops that: the
        harness's tool deadline arms a signal and then awaits the tool's promise
        rather than racing or abandoning it, so the external ~600 s ceiling was
        the only backstop — and it kills the call with nothing rendered.
        """
        # Dispatch is raced against the attempt's own deadline, and both arms of
        # the dispatch promise are observed.
        self.assertIn("const published = await Promise.race([dispatch, deadline.then(() => null)])", self.text)
        self.assertIn("(value) => ({ run: value }),", self.text)
        self.assertIn("(error) => ({ error }),", self.text)
        # A run published after the deadline still gets released.
        self.assertIn("void dispatch.then((late) => {", self.text)
        # Teardown is raced against what is left of the declared call budget,
        # capped by the per-teardown grace.
        self.assertIn(
            "const window = Math.min(callBudgetLeftMs(), REVIEW_TEARDOWN_GRACE_SECONDS * 1000)",
            self.text,
        )
        self.assertIn("disposal = await releaseRun(run)", self.text)
        # The call budget is anchored once, at execute time.
        self.assertIn("const callDeadlineAt = Date.now() + REVIEW_TOOL_TIMEOUT_MS", self.text)
        self.assertIn("const callBudgetLeftMs = () => Math.max(0, callDeadlineAt - Date.now())", self.text)
        # The old unbounded teardown is gone.
        self.assertNotIn("await run.dispose()", self.text)

    def test_composes_its_own_controller_with_the_harness_signal(self):
        # The tool's budget has to be able to abort the child on its own terms,
        # so the signal it hands the provider is its own composed one and not
        # `exec.signal` directly.
        self.assertIn("const controller = new AbortController()", self.text)
        self.assertIn("signal: controller.signal,", self.text)
        self.assertNotIn("signal: exec.signal,", self.text)
        self.assertIn("exec.signal.addEventListener('abort', forwardAbort, { once: true })", self.text)
        self.assertIn("exec.signal.removeEventListener('abort', forwardAbort)", self.text)

    def test_arms_one_timer_and_disarms_it_on_every_path(self):
        self.assertIn("}, budgetMs)", self.text)
        self.assertIn("clearTimeout(timer)", self.text)

    def test_the_deadline_can_win_the_race_without_stranding_the_run(self):
        # A provider that ignores the abort must not be able to hang the call,
        # and a `run.result` nobody awaits must not surface as an unhandled
        # rejection: both arms of the race are observed.
        self.assertIn("await Promise.race([settled, deadline.then(() => null)])", self.text)
        self.assertIn("run.result.then(", self.text)

    def test_accepts_the_route_parameter_with_a_declared_enum(self):
        self.assertIn("enum: ['configured', 'session']", self.text)
        self.assertIn("const wantSessionRoute = args.route === 'session'", self.text)


class DshReviewBriefGuardTest(unittest.TestCase):
    """Structural only. See the module docstring for what these can claim."""

    def setUp(self):
        self.text = SOURCE.read_text(encoding="utf-8")

    def test_refuses_a_blank_brief_before_any_child_exists(self):
        self.assertIn("if (brief.trim() === '') {", self.text)
        self.assertIn("refusing an empty brief", self.text)
        # The guard has to precede the first dispatch, or a malformed call still
        # spawns a reviewer.
        self.assertLess(
            self.text.index("if (brief.trim() === '') {"),
            self.text.index("const runReview = async (agentOptions) => {"),
        )

    def test_the_configured_route_is_skipped_only_by_an_explicit_session_route(self):
        self.assertIn("if (configured === null || wantSessionRoute) {", self.text)
        self.assertIn(
            "`${label} skipped: the caller asked for the session route`",
            self.text,
        )


class DshReviewEffortTest(unittest.TestCase):
    """Structural only. See the module docstring for what these can claim.

    The claims that matter about the effort feature — which object the provider
    receives, and what the caller reads back — are behavioural and live in
    ``tests/dsh_review_tool_harness.cjs``. These pin the shape so the wiring
    cannot be moved or re-spelled without the change coming back through here.
    """

    def setUp(self):
        self.text = SOURCE.read_text(encoding="utf-8")

    def test_only_a_known_level_is_a_selection(self):
        # The list is the LLM layer's own escalation order, and the card's data
        # module carries the same list: a level the adapter cannot be asked for
        # must not be storable as a selection.
        self.assertIn(
            "const EFFORT_LEVELS = ['off', 'minimal', 'low', 'medium', 'high', 'xhigh', 'max']",
            self.text,
        )
        self.assertIn("function reviewEffort(value, kind) {", self.text)
        self.assertIn("EFFORT_LEVELS.includes(raw) ? raw : null", self.text)

    def test_attaches_the_effort_only_when_one_was_applied(self):
        # The no-selection path has to dispatch the same object it always did:
        # the spread only happens once a level survived the checks above.
        self.assertIn(
            "const childOptions = childEffort === null ? configured "
            ": { ...configured, reasoningEffort: childEffort }",
            self.text,
        )

    def test_drops_a_level_the_route_would_reject(self):
        # The LLM layer answers an undeclared id with UNSUPPORTED_REASONING_EFFORT,
        # so a stored-but-undeclared level is dropped rather than sent.
        self.assertIn("function appliedEffort(wanted, support) {", self.text)
        self.assertIn(
            "if (support.available && (support.ids === null || !support.ids.includes(wanted))) return null",
            self.text,
        )

    def test_reports_the_effort_beside_the_model(self):
        self.assertIn("const withEffort = ({ outcome, model, ...rest }) => ({", self.text)
        self.assertIn(
            "...readRouteEffort === undefined ? {} : { effort: effortApplied ?? 'default' },",
            self.text,
        )
        # The session-model paths pass no options, so they must not report the
        # level an earlier attempt carried.
        self.assertIn("const runWithEffort = async (options, applied) => {", self.text)
        self.assertIn("effortApplied = applied", self.text)

    def test_the_tool_half_still_waits_only_for_its_three_services(self):
        # The effort feature must not have widened the outer optional scope.
        self.assertIn("ctx.inject(['tools', 'settings', 'subagents'], (scope) => {", self.text)
        self.assertNotIn("ctx.inject(['tools', 'settings', 'subagents', 'llm']", self.text)


if __name__ == "__main__":
    unittest.main()
