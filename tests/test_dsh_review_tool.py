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

    def test_declares_the_four_settings_fields(self):
        for field in ("reviewAProvider", "reviewAModel", "reviewBProvider", "reviewBModel"):
            self.assertIn(field, self.text)

    def test_registers_charter_review_tool(self):
        self.assertIn("charter_review", self.text)
        self.assertIn("ctx.tools.register", self.text)

    def test_tool_output_provides_render(self):
        # Spike finding: output without render fails after a successful execute.
        self.assertIn("render:", self.text)

    def test_wires_model_override_through_agent_options(self):
        self.assertIn("agentOptions", self.text)
        self.assertIn("ctx.subagents.start", self.text)

    def test_injects_required_services(self):
        for service in ("'skills'", "'tools'", "'settings'", "'subagents'"):
            self.assertIn(service, self.text)

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
        self.assertIn("classifyRun(await run.result)", self.text)
        # The defect shape was a raw extraction returned straight as a review.
        self.assertNotIn("outputText(await", self.text)

    def test_empty_text_is_a_failure_rather_than_a_success(self):
        self.assertIn("child completed with an empty review", self.text)

    def test_reuses_the_unavailable_outcome_for_a_failed_rerun(self):
        self.assertIn("the session-model rerun also failed", self.text)
        self.assertIn("outcome: 'unavailable'", self.text)
        self.assertIn("review: ''", self.text)

    def test_fallback_reason_names_the_route_and_carries_the_failure(self):
        self.assertIn("`${label} unavailable: ${attempt.failure}`", self.text)

    def test_keeps_the_child_guard_in_a_finally_block(self):
        self.assertIn("} finally {", self.text)
        self.assertIn("await run.dispose()", self.text)

    def test_still_skips_a_route_the_provider_cannot_carry(self):
        self.assertIn("capabilities?.agentOptions === true", self.text)


if __name__ == "__main__":
    unittest.main()
