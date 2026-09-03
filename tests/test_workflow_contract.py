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
        architecture = read(
            "docs/superpowers/specs/2026-09-02-charter-kit-v1-architecture-design.md"
        )

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
        self.assertIn("重新进入 PENDING", architecture)
        self.assertNotIn("重新进入 IN_PROGRESS", architecture)

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

    def test_all_entry_points_use_context_router_before_change_triage(self) -> None:
        entry_points = (
            "portable/commands/charter-workflow.md",
            "portable/prompts/generic-bootstrap.md",
            "portable/prompts/codex-bootstrap.md",
            "portable/prompts/claude-bootstrap.md",
            "portable/prompts/gemini-bootstrap.md",
            "portable/prompts/deepseek-bootstrap.md",
            "skills/charter-workflow/SKILL.md",
            "skills/charter-workflow/references/tool-routing.md",
        )
        for relative in entry_points:
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
                self.assertIn("Do not invent a Change Triage event", text)
                self.assertNotIn("Change Triage` for every `INIT`, `RESUME`, and `CHANGE`", text)
                self.assertNotIn("Route every `INIT`, `RESUME`, and `CHANGE` request through `Change Triage`", text)
                self.assertIn("MISSING", text)
                self.assertIn("FALLBACK", text)

        for relative in (
            "skills/charter-workflow/SKILL.md",
            "skills/charter-workflow/references/tool-routing.md",
        ):
            with self.subTest(self_contained_reference=relative):
                text = read(relative)
                self.assertIn("references/change-triage.md", text)
                self.assertNotIn("portable/references/change-triage.md", text)

    def test_entry_points_use_the_three_state_reuse_gate(self) -> None:
        entry_points = (
            "portable/commands/charter-workflow.md",
            "portable/prompts/generic-bootstrap.md",
            "portable/prompts/codex-bootstrap.md",
            "portable/prompts/claude-bootstrap.md",
            "portable/prompts/gemini-bootstrap.md",
            "portable/prompts/deepseek-bootstrap.md",
            "skills/charter-workflow/SKILL.md",
            "skills/charter-workflow/references/tool-routing.md",
        )
        for relative in entry_points:
            with self.subTest(relative=relative):
                text = read(relative)
                self.assertIn("PENDING", text)
                self.assertIn("COMPLETE", text)
                self.assertIn("BLOCKED", text)
                self.assertNotIn(
                    "NOT_STARTED | IN_PROGRESS | COMPLETE | LIMITED | WAIVED | BLOCKED_TOOLING",
                    text,
                )
                self.assertNotIn(
                    "NOT_STARTED`, `IN_PROGRESS`, `BLOCKED_TOOLING`",
                    text,
                )
                self.assertRegex(
                    text,
                    r"(?i)high-value\s+`?UNKNOWN`?[^\n]{0,100}(?:remains?\s+unresolved|unresolved)",
                )

    def test_reuse_waiver_is_a_leaf_scoped_ready_exception(self) -> None:
        entry_points = (
            "portable/commands/charter-workflow.md",
            "portable/prompts/generic-bootstrap.md",
            "portable/prompts/codex-bootstrap.md",
            "portable/prompts/claude-bootstrap.md",
            "portable/prompts/gemini-bootstrap.md",
            "portable/prompts/deepseek-bootstrap.md",
            "skills/charter-workflow/SKILL.md",
            "skills/charter-workflow/references/tool-routing.md",
            "portable/templates/reuse-discovery.md",
        )
        for relative in entry_points:
            with self.subTest(relative=relative):
                text = read(relative)
                self.assertIn("A Leaf may enter `READY` only when", text)
                self.assertIn("bounded waiver", text)
                self.assertIn("not a fourth gate state", text.lower())

        for relative in (
            "portable/templates/roadmap.md",
            "portable/templates/leaf-task.md",
            "portable/templates/project-charter.md",
        ):
            with self.subTest(relative=relative):
                text = read(relative)
                self.assertIn("COMPLETE", text)
                self.assertIn("specific Leaf", text)
                self.assertIn("bounded waiver", text)

    def test_codex_manifest_describes_independent_host_use(self) -> None:
        for relative in (
            ".codex-plugin/plugin.json",
            "targets/codex/.codex-plugin/plugin.json",
        ):
            with self.subTest(relative=relative):
                payload = json.loads(read(relative))
                keywords = " ".join(payload.get("keywords", []))
                long_description = payload.get("interface", {}).get("longDescription", "")
                self.assertNotIn("cross-agent", keywords.lower())
                self.assertNotIn("across agents", long_description.lower())
                self.assertIn("independent", long_description.lower())

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
        self.assertIn("result, interface, acceptance, or boundary", text)
        self.assertIn("If you cannot prove that the event is already inside the current Leaf contract", text)

    def test_leaf_state_and_closure_sequence_match_the_approved_contract(self) -> None:
        charter = read("DEVELOPMENT_CHARTER.md")
        roadmap = read("portable/templates/roadmap.md")
        leaf = read("portable/templates/leaf-task.md")

        canonical_states = (
            "DRAFT → APPROVED → READY → IN_PROGRESS → REVIEW → VERIFIED → PASS_CLOSED"
        )
        for relative, text in (
            ("DEVELOPMENT_CHARTER.md", charter),
            ("portable/templates/roadmap.md", roadmap),
        ):
            with self.subTest(relative=relative):
                self.assertIn(canonical_states, text)
                self.assertNotIn("INTEGRATION_PENDING", text)
                self.assertNotIn("POST_MERGE_VERIFIED", text)

        self.assertIn("Pre-integration verification receipt", leaf)
        self.assertIn(
            "Review → Verification → target-branch integration → post-integration verification",
            leaf,
        )

    def test_unknown_is_a_search_result_not_a_candidate_disposition(self) -> None:
        charter = read("DEVELOPMENT_CHARTER.md")
        review = read("portable/templates/review.md")
        candidate_line = next(
            line for line in charter.splitlines() if line.startswith("候选行决定只能是")
        )

        self.assertIn(
            "候选行决定只能是 `ADOPT`、`ADAPT`、`REFERENCE_ONLY`、`REJECT` 或 `DEFER`",
            candidate_line,
        )
        self.assertNotIn("`DEFER` 或 `UNKNOWN`", candidate_line)
        self.assertIn("Result 为 `MATCH | NO_MATCH | UNKNOWN`", charter)
        self.assertIn("`UNKNOWN` result", review)
        self.assertNotIn("UNKNOWN` candidate", review)

    def test_working_set_roles_stay_lightweight_and_consistent(self) -> None:
        manifest = read("agentpack.yaml")
        readme = read("README.md")
        architecture = read(
            "docs/superpowers/specs/2026-09-02-charter-kit-v1-architecture-design.md"
        )
        plan = read("docs/superpowers/plans/2026-09-02-charter-kit-v1-implementation.md")

        for relative, text in (
            ("README.md", readme),
            ("architecture design", architecture),
            ("implementation plan", plan),
        ):
            with self.subTest(relative=relative):
                self.assertIn("core Resume files", text)
                self.assertIn("auxiliary receipts", text)

        required_block = manifest.split("working_set:", 1)[1].split("dependencies:", 1)[0]
        for path in (
            ".charter/project.md",
            ".charter/roadmap.md",
            ".charter/reuse-discovery.md",
            ".charter/current-task.md",
        ):
            self.assertIn(path, required_block)
        self.assertIn("auxiliary:", required_block)
        self.assertIn(".charter/evidence/", required_block)

    def test_resume_pressure_scenario_reads_reuse_before_current_task(self) -> None:
        pressure = read("tests/pressure-scenarios.md")
        self.assertIn(
            "project.md → roadmap.md → reuse-discovery.md → current-task.md → handoff.md (if present)",
            pressure,
        )

    def test_packaged_readme_uses_repository_links_for_unshipped_sources(self) -> None:
        readme = read("README.md")
        for repository_path in (
            "https://github.com/lhy102731/charter-kit/tree/main/.claude-plugin",
            "https://github.com/lhy102731/charter-kit/tree/main/targets/codex",
        ):
            self.assertIn(repository_path, readme)
        self.assertIn("In a source repository checkout", readme)

    def test_review_b_is_risk_triggered_instead_of_a_universal_blocker(self) -> None:
        charter = read("DEVELOPMENT_CHARTER.md")
        self.assertIn("Review B 只在", charter)
        self.assertIn("低风险叶任务可以记录有边界的省略理由", charter)

        for relative in (
            "portable/commands/charter-workflow.md",
            "portable/prompts/generic-bootstrap.md",
            "portable/prompts/codex-bootstrap.md",
            "portable/prompts/claude-bootstrap.md",
            "portable/prompts/gemini-bootstrap.md",
            "portable/prompts/deepseek-bootstrap.md",
            "skills/charter-workflow/SKILL.md",
        ):
            with self.subTest(relative=relative):
                text = read(relative)
                self.assertIn("Review B is required only for", text)
                self.assertIn("Low-risk leaves may record a bounded omission reason", text)

    def test_charter_independent_review_is_risk_triggered(self) -> None:
        charter = read("DEVELOPMENT_CHARTER.md")
        self.assertIn("CHARTER_INDEPENDENT 只在", charter)
        self.assertIn("低风险章程可以记录有边界的省略理由", charter)

        for relative in (
            "portable/commands/charter-workflow.md",
            "portable/prompts/generic-bootstrap.md",
            "portable/prompts/codex-bootstrap.md",
            "portable/prompts/claude-bootstrap.md",
            "portable/prompts/gemini-bootstrap.md",
            "portable/prompts/deepseek-bootstrap.md",
            "skills/charter-workflow/SKILL.md",
        ):
            with self.subTest(relative=relative):
                text = read(relative)
                self.assertIn("CHARTER_INDEPENDENT is required only for", text)
                self.assertIn("Low-risk charters may record a bounded omission reason", text)

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
