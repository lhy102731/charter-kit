"""Behavioral checks for the ZCode target and its generated distribution."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
TARGET_MANIFEST = PACKAGE_ROOT / "targets" / "zcode" / ".zcode-plugin" / "plugin.json"
TARGET_COMMAND = PACKAGE_ROOT / "targets" / "zcode" / "commands" / "charter-workflow.md"
TARGET_SKILL = PACKAGE_ROOT / "targets" / "zcode" / "skills" / "charter-workflow" / "SKILL.md"
DISTRIBUTION = PACKAGE_ROOT / "plugins" / "zcode-charter-kit"


class ZcodeTargetTests(unittest.TestCase):
    def test_target_manifest_declares_skill_and_command_components(self) -> None:
        data = json.loads(TARGET_MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(data.get("name"), "charter-kit")
        self.assertEqual(data.get("skills"), "skills")
        self.assertEqual(data.get("commands"), "commands")
        self.assertEqual(data.get("license"), "MIT")

    def test_target_command_mounts_the_skill(self) -> None:
        text = TARGET_COMMAND.read_text(encoding="utf-8")
        self.assertIn("skills: charter-workflow", text)
        self.assertIn("bootstrap mode", text.lower())

    def test_target_skill_matches_codex_skill_bytes(self) -> None:
        codex_skill = (PACKAGE_ROOT / "targets" / "codex" / "skills" / "charter-workflow" / "SKILL.md").read_bytes()
        self.assertEqual(codex_skill, TARGET_SKILL.read_bytes())

    def test_distribution_matches_fresh_build(self) -> None:
        result = subprocess.run(
            [sys.executable, str(PACKAGE_ROOT / "scripts" / "build_zcode_plugin.py"), "--check"],
            cwd=PACKAGE_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_distribution_carries_manifest_command_and_skill(self) -> None:
        manifest = json.loads((DISTRIBUTION / ".zcode-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest.get("name"), "charter-kit")
        command = (DISTRIBUTION / "commands" / "charter-workflow.md").read_text(encoding="utf-8")
        self.assertIn("skills: charter-workflow", command)
        self.assertTrue((DISTRIBUTION / "skills" / "charter-workflow" / "SKILL.md").is_file())
        self.assertTrue((DISTRIBUTION / "DEVELOPMENT_CHARTER.md").is_file())

    def test_validator_covers_zcode_target(self) -> None:
        result = subprocess.run(
            [sys.executable, str(PACKAGE_ROOT / "scripts" / "validate_kit.py"), "."],
            cwd=PACKAGE_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ZCode target and generated distribution valid", result.stdout)


if __name__ == "__main__":
    unittest.main()
