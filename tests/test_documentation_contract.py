from __future__ import annotations

import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (PACKAGE_ROOT / relative).read_text(encoding="utf-8")


class DocumentationContractTests(unittest.TestCase):
    def test_charter_defines_project_local_single_flow_and_change_triage(self) -> None:
        text = read("DEVELOPMENT_CHARTER.md")
        for phrase in (
            "项目本地",
            "独立遵循同一份协议",
            "一个主控制流",
            "Change Triage",
            "NEW_REQUIREMENT",
            "CHARTER > ROADMAP > LEAF > IN_CONTRACT",
            "New requirement must not silently expand the current Leaf",
            "PENDING | COMPLETE | BLOCKED",
            "SEARCHED | NOT_SEARCHED | NOT_AUTHORIZED | BLOCKED_TOOLING",
            "MATCH | NO_MATCH | UNKNOWN",
            "NO_MATERIAL_TARGET",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

        self.assertIn("不提供 Agent 间通信、Harness 间同步或中央服务", text)
        self.assertIn("不是跨 Agent 通道、消息队列或同步服务", text)

    def test_readme_is_bilingual_and_sets_verified_target_boundary(self) -> None:
        text = read("README.md")
        for phrase in (
            "## 中文",
            "## English",
            "host-neutral",
            "empty directory",
            "Change Triage",
            "Reuse Assessment / Reuse Check",
            "new requirement must not silently expand the current Leaf",
            "Claude Code and Codex are the targets",
            "experimental",
            "unverified",
            "不会自动安装",
            "Nothing automatically installs a Skill",
            "https://github.com/lhy102731/charter-kit",
            "https://developers.openai.com/codex/plugins/",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

        self.assertIn("dev_inject_plugin", text)
        self.assertIn("dev_install_package", text)

    def test_codex_target_readme_is_an_adapter_not_a_harness_installer(self) -> None:
        text = read("targets/codex/README.md")
        for phrase in (
            "thin Codex adapter",
            "portable",
            "not a host installer",
            "plugins/charter-kit/",
            "Change Triage",
            "Reuse Assessment / Reuse Check",
            "experimental",
            "unverified",
            "does not install any Harness",
            "不安装 Codex 以外的 Harness",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

        self.assertNotIn("dev_inject_plugin", text)
        self.assertNotIn("dev_install_package", text)

    def test_pressure_and_structure_docs_cover_new_boundaries(self) -> None:
        pressure = read("tests/pressure-scenarios.md")
        for phrase in (
            "First start and Resume converge",
            "Change Triage",
            "PENDING",
            "NO_MATCH",
            "UNKNOWN",
            "New capability",
            "targeted Reuse Check",
        ):
            with self.subTest(document="pressure", phrase=phrase):
                self.assertIn(phrase, pressure)

        structure = read("tests/structure-checklist.md")
        for phrase in (
            "Documentation boundary checks",
            "single Portable Core",
            "Codex",
            "experimental",
            "PENDING | COMPLETE | BLOCKED",
            "NO_MATCH",
            "Change Triage",
        ):
            with self.subTest(document="structure", phrase=phrase):
                self.assertIn(phrase, structure)

    def test_lessons_template_defines_bounded_advisory_entries(self) -> None:
        text = read("portable/templates/lessons.md")
        for phrase in (
            "# Lessons",
            "## Entries",
            "## Archive pointers",
            "Status: ACTIVE",
            "Hits:",
            "Pitfall:",
            "Evidence:",
            "Next defense:",
            "Generalize candidate:",
            "8 KB",
            "lessons-archive.md",
            "not a gate",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_lessons_reference_keeps_the_five_rules_in_one_place(self) -> None:
        text = read("portable/references/lessons.md")
        for phrase in (
            "# Lessons rules",
            "## Distill",
            "## Cite",
            "## Report",
            "## Decay",
            "## Generalize",
            "8 KB",
            "Zero output is a legal result",
            "detectable failure",
            "not a gate",
            "unhooked ledger",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_charter_and_readme_carry_the_lessons_layer(self) -> None:
        charter = read("DEVELOPMENT_CHARTER.md")
        self.assertIn("handoff.md → lessons.md（如存在）", charter)
        self.assertIn("建议性知识而非门", charter)
        self.assertIn("用户显式确认", charter)

        readme = read("README.md")
        chinese, _, english = readme.partition("## English")
        self.assertIn("lessons.md", chinese)
        self.assertIn("lessons.md", english)


if __name__ == "__main__":
    unittest.main()
