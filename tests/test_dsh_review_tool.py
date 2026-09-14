"""Structural assertions over the DSH adapter source.

Every test here reads ``targets/dsh/src/index.js`` as text. Source text can pin
a literal's spelling, the presence of a field read, and the shape of a return
site. It cannot execute the tool, so these tests are NOT evidence that
``charter_review`` behaves correctly; the live re-run on a DSH host is that
evidence. They exist to catch a regression in the shape the fix established.
"""

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

    def test_declares_the_five_settings_fields(self):
        for field in (
            "reviewAProvider",
            "reviewAModel",
            "reviewBProvider",
            "reviewBModel",
            "reviewTimeoutSeconds",
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
        self.assertIn("} finally {", self.text)
        self.assertIn("await run.dispose()", self.text)

    def test_still_skips_a_route_the_provider_cannot_carry(self):
        self.assertIn("capabilities?.agentOptions === true", self.text)

    def test_routes_every_attempt_through_one_guarded_wrapper(self):
        # Dispatch, the deadline, classification, disposal, and error mapping
        # live in one place, so no call site — the configured one, the recovery
        # rerun, or the session-route branch — can leak a raw rejection out of
        # `execute`.
        self.assertIn("const runReview = async (agentOptions) => {", self.text)
        self.assertEqual(self.text.count("await runReview("), 3)
        self.assertNotIn("runOnce", self.text)


class DshReviewTimeoutTest(unittest.TestCase):
    """Structural only. See the module docstring for what these can claim."""

    def setUp(self):
        self.text = SOURCE.read_text(encoding="utf-8")

    def test_declares_a_deadline_the_harness_cannot_preempt(self):
        # The setting is dynamic and `timeoutMs` is fixed, so the declared value
        # has to cover the worst case the setting can express: both attempts at
        # the ceiling plus margin. A smaller literal would let the harness
        # deadline replace this tool's fallback with an opaque TOOL_TIMEOUT.
        self.assertIn("timeoutMs: REVIEW_TOOL_TIMEOUT_MS,", self.text)
        self.assertIn(
            "const REVIEW_TOOL_TIMEOUT_MS = (MAX_REVIEW_TIMEOUT_SECONDS * 2 + 60) * 1000",
            self.text,
        )

    def test_clamps_the_configured_budget_between_the_two_bounds(self):
        self.assertIn("const MIN_REVIEW_TIMEOUT_SECONDS = 30", self.text)
        self.assertIn("const MAX_REVIEW_TIMEOUT_SECONDS = 540", self.text)
        self.assertIn("const DEFAULT_REVIEW_TIMEOUT_SECONDS = 240", self.text)
        # A non-number defaults; anything numeric is floored into [MIN, MAX].
        self.assertIn("typeof raw === 'number' && Number.isFinite(raw)", self.text)
        self.assertIn(
            "Math.min(MAX_REVIEW_TIMEOUT_SECONDS, Math.max(MIN_REVIEW_TIMEOUT_SECONDS, seconds))",
            self.text,
        )

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


if __name__ == "__main__":
    unittest.main()
