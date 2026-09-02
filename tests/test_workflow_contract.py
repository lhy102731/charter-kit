from __future__ import annotations

import json
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    path = PACKAGE_ROOT / relative
    return path.read_text(encoding="utf-8") if path.is_file() else ""


class WorkflowContractTests(unittest.TestCase):
    def test_reuse_record_separates_coverage_result_and_route(self) -> None:
        text = read("portable/templates/reuse-discovery.md")

        for phrase in (
            "SEARCHED",
            "NOT_SEARCHED",
            "NOT_AUTHORIZED",
            "BLOCKED_TOOLING",
            "MATCH",
            "NO_MATCH",
            "UNKNOWN",
            "BUILD_NEW",
            "NO_MATERIAL_TARGET",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

        self.assertIn("Gate status: `PENDING | COMPLETE | BLOCKED`", text)
        self.assertIn("Coverage", text)
        self.assertIn("Result", text)
        self.assertIn("Final route", text)

    def test_reuse_provider_roles_are_explicit(self) -> None:
        manifest = read("agentpack.yaml")
        for provider in (
            "reuse-first",
            "framework-first-coding",
            "reduce-reinvention",
            "find-skills",
            "repo-to-skill",
        ):
            with self.subTest(provider=provider):
                self.assertIn(f"id: {provider}", manifest)
                self.assertRegex(manifest, rf"id: {provider}[\s\S]{{0,240}}role:")

    def test_reuse_provider_metadata_is_mirrored_in_dependency_manifest(self) -> None:
        payload = json.loads(read("dependencies.json"))
        entries = [
            *payload.get("providers", []),
            *payload.get("capabilities", []),
        ]
        by_id = {entry.get("id"): entry for entry in entries}
        for provider in (
            "reuse-first",
            "framework-first-coding",
            "reduce-reinvention",
            "find-skills",
            "repo-to-skill",
        ):
            with self.subTest(provider=provider):
                entry = by_id.get(provider)
                self.assertIsNotNone(entry)
                assert entry is not None
                self.assertFalse(entry.get("required"))
                self.assertTrue(entry.get("role"))
                self.assertTrue(entry.get("fallback"))

    def test_all_entry_points_route_changes_through_change_triage(self) -> None:
        for relative in (
            "portable/commands/charter-workflow.md",
            "portable/prompts/generic-bootstrap.md",
            "portable/prompts/codex-bootstrap.md",
            "portable/prompts/claude-bootstrap.md",
            "portable/prompts/gemini-bootstrap.md",
            "portable/prompts/deepseek-bootstrap.md",
            "skills/charter-workflow/SKILL.md",
            "skills/charter-workflow/references/tool-routing.md",
        ):
            with self.subTest(relative=relative):
                text = read(relative)
                self.assertIn("Change Triage", text)
                self.assertIn("INIT", text)
                self.assertIn("RESUME", text)
                self.assertIn("CHANGE", text)
                self.assertIn("Context Router is a workflow step", text)
                self.assertIn("same READY Leaf loop", text)
                self.assertIn("four Change Triage questions", text)
                self.assertIn("targeted Reuse Check", text)
                self.assertIn("repo-to-skill is a separate authorized follow-up action", text)
                self.assertIn("new requirement", text.lower())
                self.assertIn("must not silently expand", text.lower())
                self.assertIn("MISSING", text)
                self.assertIn("FALLBACK", text)

    def test_change_triage_reference_defines_event_and_route_contract(self) -> None:
        text = read("portable/references/change-triage.md")
        for event_kind in (
            "NEW_REQUIREMENT",
            "CLARIFICATION",
            "DEFECT",
            "DISCOVERED_CONSTRAINT",
            "RISK",
        ):
            with self.subTest(event_kind=event_kind):
                self.assertIn(event_kind, text)

        for route in (
            "IN_CONTRACT",
            "LEAF_CHANGE",
            "ROADMAP_CHANGE",
            "CHARTER_CHANGE",
            "OUT_OF_SCOPE",
        ):
            with self.subTest(route=route):
                self.assertIn(route, text)

        self.assertIn("CHARTER > ROADMAP > LEAF > IN_CONTRACT", text)
        self.assertIn("New requirement must not silently expand the current Leaf", text)

    def test_template_mirrors_keep_canonical_change_triage_language_in_sync(self) -> None:
        paired_templates = (
            (
                "portable/templates/roadmap.md",
                "skills/charter-workflow/templates/roadmap.md",
                "current-task.md is the active Leaf state authority",
            ),
            (
                "portable/templates/leaf-task.md",
                "skills/charter-workflow/templates/leaf-task.md",
                "Change Triage event kind and route",
            ),
            (
                "portable/templates/decision.md",
                "skills/charter-workflow/templates/decision.md",
                "CHARTER > ROADMAP > LEAF > IN_CONTRACT",
            ),
            (
                "portable/templates/review.md",
                "skills/charter-workflow/templates/review.md",
                "New requirement must not silently expand the current Leaf",
            ),
            (
                "portable/templates/handoff.md",
                "skills/charter-workflow/templates/handoff.md",
                "New requirement must not silently expand the current Leaf",
            ),
            (
                "portable/templates/evidence-receipt.md",
                "skills/charter-workflow/templates/evidence-receipt.md",
                "New requirement must not silently expand the current Leaf",
            ),
        )

        for portable_relative, skill_relative, phrase in paired_templates:
            with self.subTest(template=portable_relative):
                portable_text = read(portable_relative)
                skill_text = read(skill_relative)
                self.assertIn(phrase, portable_text)
                self.assertIn(phrase, skill_text)

    def test_bootstrap_prompts_use_canonical_runtime_names(self) -> None:
        for relative in (
            "portable/prompts/generic-bootstrap.md",
            "portable/prompts/codex-bootstrap.md",
            "portable/prompts/claude-bootstrap.md",
            "portable/prompts/gemini-bootstrap.md",
            "portable/prompts/deepseek-bootstrap.md",
        ):
            text = read(relative)
            self.assertIn("decision.md", text)
            self.assertIn("review.md", text)
            self.assertIn("evidence-receipt.md", text)
            self.assertNotIn("decision-template.md", text)
            self.assertNotIn("review-template.md", text)
            self.assertNotIn("evidence-template.md", text)

    def test_runtime_working_set_has_single_state_authority(self) -> None:
        for relative in (
            "portable/templates/roadmap.md",
            "skills/charter-workflow/templates/roadmap.md",
        ):
            text = read(relative)
            self.assertIn("current-task.md is the active Leaf state authority", text)
            self.assertIn("New requirement must not silently expand the current Leaf", text)
            self.assertIn("portable/references/change-triage.md", text)

        for relative in (
            "portable/templates/leaf-task.md",
            "skills/charter-workflow/templates/leaf-task.md",
        ):
            text = read(relative)
            self.assertIn("Change Triage event kind and route", text)
            self.assertIn("New requirement must not silently expand the current Leaf", text)

        for relative in (
            "portable/templates/decision.md",
            "skills/charter-workflow/templates/decision.md",
        ):
            text = read(relative)
            self.assertIn("CHARTER > ROADMAP > LEAF > IN_CONTRACT", text)
            self.assertIn("New requirement must not silently expand the current Leaf", text)

        for relative in (
            "portable/templates/review.md",
            "skills/charter-workflow/templates/review.md",
        ):
            text = read(relative)
            self.assertIn("Record the observed event kind and route", text)
            self.assertIn("New requirement must not silently expand the current Leaf", text)



if __name__ == "__main__":
    unittest.main()
