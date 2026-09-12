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


if __name__ == "__main__":
    unittest.main()
