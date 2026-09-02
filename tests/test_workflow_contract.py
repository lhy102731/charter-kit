from __future__ import annotations

import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    path = PACKAGE_ROOT / relative
    return path.read_text(encoding="utf-8") if path.is_file() else ""


class WorkflowContractTests(unittest.TestCase):
    def test_change_triage_reference_defines_one_route_contract(self) -> None:
        text = read("portable/references/change-triage.md")
        self.assertIn("NEW_REQUIREMENT", text)
        self.assertIn("CHARTER > ROADMAP > LEAF > IN_CONTRACT", text)
        self.assertIn("New requirement must not silently expand the current Leaf", text)

    def test_runtime_working_set_has_single_state_authority(self) -> None:
        current = read("portable/templates/leaf-task.md")
        roadmap = read("portable/templates/roadmap.md")
        self.assertIn("current-task.md is the active Leaf state authority", roadmap)
        self.assertIn("Change Triage event", current)


if __name__ == "__main__":
    unittest.main()
