from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]

# The trees a maintainer hand-edits for the reuse routing rule.  The guard
# discovers its carriers inside them by content rather than listing them, so an
# artifact added later is covered by the same assertions.
CARRIER_TREES = ("portable", "targets", "skills")
# The probe that only a decision-point routing rule can carry.
REUSE_PROBE_COMMAND = (
    "--optional reuse-first --optional find-skills "
    "--optional framework-first-coding "
    "--optional reduce-reinvention --json"
)


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
        self.assertIn(".charter/lessons.md", required_block)
        self.assertIn(".charter/evidence/", required_block)

    def test_resume_pressure_scenario_reads_reuse_before_current_task(self) -> None:
        pressure = read("tests/pressure-scenarios.md")
        self.assertIn(
            "project.md → roadmap.md → reuse-discovery.md → current-task.md → handoff.md → lessons.md (if present)",
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
        self.assertIn("Review B 的触发项由 kit 拥有、按编号引用、只增不改", charter)
        self.assertIn("`NOT_REQUIRED` 点名所考虑的编号并记录有边界的省略理由", charter)
        # The distinction the old wording lost: a leaf that hit nothing is not
        # waiving a review, it is recording that none was triggered.
        self.assertIn("未命中任何触发项的低风险叶记 `NOT_REQUIRED`，不记 `WAIVED`", charter)

        entry_points = (
            "portable/commands/charter-workflow.md",
            "portable/prompts/generic-bootstrap.md",
            "portable/prompts/codex-bootstrap.md",
            "portable/prompts/claude-bootstrap.md",
            "portable/prompts/gemini-bootstrap.md",
            "portable/prompts/deepseek-bootstrap.md",
        )
        for relative in (*entry_points, "skills/charter-workflow/SKILL.md"):
            with self.subTest(relative=relative):
                text = read(relative)
                for phrase in (
                    "kit-owned",
                    "`RVB1`",
                    "`RVB5`",
                    "`NOT_REQUIRED`",
                    "fresh context/process",
                    # An undecided reviewer is a question asked at the first
                    # leaf that needs it, not a gate that silently passes.
                    "stop and ask the user",
                ):
                    self.assertIn(phrase, text, f"{relative} lacks {phrase!r}")

        for relative in entry_points:
            with self.subTest(relative=relative):
                self.assertIn(
                    "Review B triggers are kit-owned and append-only", read(relative)
                )
        skill = read("skills/charter-workflow/SKILL.md")
        self.assertIn("Review B is required when any kit-owned trigger is hit", skill)
        self.assertIn("a leaf that hit no trigger is `NOT_REQUIRED`, not `WAIVED`", skill)

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

    def test_every_review_brief_carrier_names_the_diff_and_the_turn_cost(self) -> None:
        """The brief contract, guarded across the space rather than a list.

        A review is a multi-turn agent run: the child reads files, runs
        `git diff`, then writes. In a real project a single completion on one
        seat took 85 s and 5 702 reasoning tokens, which makes turns x tokens the
        entire cost of a review — so a brief that leaves the candidate diff for
        the child to find buys that discovery with turns. Every carrier that
        states the brief contract therefore has to say both things: the diff
        belongs IN the brief, and the reason is the turn cost. The carriers are
        discovered by content, so a carrier added later is covered and a carrier
        that quietly drops the guidance is a failure rather than a smaller pass.
        """

        carrier_trees = ("targets", "skills")
        carriers = sorted(
            path
            for tree in carrier_trees
            for path in (PACKAGE_ROOT / tree).rglob("*")
            if path.is_file()
            and path.suffix in {".md", ".js"}
            and "candidate diff" in path.read_text(encoding="utf-8")
            and (
                "self-contained brief" in path.read_text(encoding="utf-8")
                or "SELF-CONTAINED: the leaf contract" in path.read_text(encoding="utf-8")
                or "SELF-CONTAINED review brief" in path.read_text(encoding="utf-8")
            )
        )
        # A discovery that silently found nothing would pass everything below,
        # and a shrunken one must fail rather than assert over fewer files.
        self.assertGreaterEqual(
            len(carriers), 5, f"carrier discovery found too few files: {carriers}"
        )
        # The five carriers this contract actually lives on, named so that one
        # going missing is visible rather than a thinner discovery.
        relatives = {path.relative_to(PACKAGE_ROOT).as_posix() for path in carriers}
        for expected in (
            "targets/dsh/src/index.js",
            "targets/dsh/README.md",
            "skills/charter-workflow/SKILL.md",
            "targets/codex/skills/charter-workflow/SKILL.md",
            "targets/zcode/skills/charter-workflow/SKILL.md",
        ):
            self.assertIn(expected, relatives, sorted(relatives))

        # Each carrier must name the diff and the turn cost it saves.
        for path in carriers:
            relative = path.relative_to(PACKAGE_ROOT).as_posix()
            flat = " ".join(path.read_text(encoding="utf-8").split())
            with self.subTest(relative=relative):
                # The diff is named as something the brief carries, and the
                # reason given for carrying it is the turn cost — in the same
                # sentence, so a carrier cannot satisfy this with an unrelated
                # mention of either word somewhere else in the file.
                self.assertRegex(
                    flat,
                    r"candidate diff.{0,240}?(multi-turn|turn cost|in turns|turns)",
                    f"{relative}: the brief contract no longer ties the diff to the turn cost",
                )
                # The routing note travels with it: at a slow seat's throughput a
                # review belongs on a narrow, risk-triggered leaf, not on all of
                # them.
                self.assertRegex(
                    flat,
                    r"(?i)(narrow,? risk-triggered|risk-triggered review)",
                    f"{relative}: the slow-seat routing note is gone",
                )

        # And the retracted premise must not be how the budget is explained: a
        # carrier that re-derives a host ceiling on total duration from the
        # adapter's idle watchdog re-creates the defect this change retracts.
        for tree in CARRIER_TREES:
            for path in (PACKAGE_ROOT / tree).rglob("*"):
                if not path.is_file() or path.suffix not in {".md", ".js"}:
                    continue
                text = path.read_text(encoding="utf-8")
                relative = path.relative_to(PACKAGE_ROOT).as_posix()
                with self.subTest(relative=relative):
                    self.assertNotIn("600 秒的上限", text)
                    self.assertNotIn("600-second ceiling", text)
                    self.assertNotIn("external ~600", text)

    def test_skill_names_the_host_review_tool_conditionally(self) -> None:
        for relative in (
            "skills/charter-workflow/SKILL.md",
            "targets/codex/skills/charter-workflow/SKILL.md",
            "targets/zcode/skills/charter-workflow/SKILL.md",
        ):
            text = (PACKAGE_ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("charter_review", text, relative)
            self.assertIn("REVIEW_MODEL", text, relative)


    def test_provider_branches_bind_to_a_probe_taken_at_the_decision_point(self) -> None:
        """A provider branch must read a probe taken now, not an earlier log.

        The dependency log is written at the start of the session, while the
        intent interview and the reuse discovery can run later.  In a real
        project the reuse discovery ran on 2026-09-01 and the dependency check
        first ran on 2026-09-03, so `AVAILABLE` had no truth value at the
        decision point and the workflow silently took the portable path.
        """

        for relative in (
            "skills/charter-workflow/SKILL.md",
            "targets/codex/skills/charter-workflow/SKILL.md",
            "targets/zcode/skills/charter-workflow/SKILL.md",
        ):
            with self.subTest(relative=relative):
                text = read(relative)
                # Step 3 probes for the interview provider at the interview.
                self.assertIn("--optional grill-me --json", text)
                # Step 6 probes every reuse-tier provider before routing.
                self.assertIn(
                    "--optional reuse-first --optional find-skills "
                    "--optional framework-first-coding "
                    "--optional reduce-reinvention --json",
                    text,
                )
                self.assertNotIn("when probed `AVAILABLE`", text)
                self.assertIn("not from an earlier log", text)
                self.assertIn("`AVAILABLE` in this probe", text)
                # Which record is current: the run just executed, never a
                # section the reader happened to find first.
                self.assertIn("the last section", text)
                self.assertIn("the one whose header timestamp is this run", text)
                self.assertIn("stale exactly like an absent log", text)
                self.assertIn("first matching line", text)
                # Why the probe is taken here rather than read from the log.
                self.assertIn("may be absent or stale", text)
                self.assertIn("a stale log is indistinguishable", text)
                # The emitted record, never the exit code: optional gaps exit 0.
                self.assertIn("never the exit code", text)
                self.assertIn("still exits 0", text)
                # An installed-but-broken provider must not deadlock the leaf.
                self.assertIn("record `FALLBACK` naming the failure and continue", text)


    def test_every_reuse_routing_artifact_probes_at_the_decision_point(self) -> None:
        """Guard the space, not a snapshot of it.

        `SKILL.md` was fixed first, but the record a leaf actually fills in is
        the reuse-discovery template, and every entry point repeats the routing
        rule. One surviving log-bound copy re-creates the defect this change
        exists to remove: the log may not exist yet, and because it is appended
        to, its newest section may still predate the decision. The carriers are
        therefore discovered by content, so an artifact cannot evade the guard
        merely by being absent from a hand-written list.
        """

        carriers = sorted(
            path
            for tree in CARRIER_TREES
            for path in (PACKAGE_ROOT / tree).rglob("*.md")
            if REUSE_PROBE_COMMAND in path.read_text(encoding="utf-8")
        )
        # A discovery that silently found nothing would pass everything below.
        self.assertGreaterEqual(
            len(carriers), 12, f"carrier discovery found too few files: {carriers}"
        )

        for path in carriers:
            relative = path.relative_to(PACKAGE_ROOT).as_posix()
            text = path.read_text(encoding="utf-8")
            with self.subTest(relative=relative):
                # Probe at the decision point, not from an earlier log.
                self.assertIn("not from an earlier log", text)
                # Which record is current: the run just executed, identified by
                # its own section, never "some section of the file".
                self.assertIn("the last section", text)
                self.assertIn("the one whose header timestamp is this run", text)
                # Never the exit code: an absent optional provider still exits 0.
                self.assertIn("never the exit code", text)
                self.assertIn("still exits 0", text)
                # An earlier section is stale, and grepping for the first match
                # is exactly how a reader lands on it.
                self.assertIn("stale exactly like an absent log", text)
                self.assertIn("first matching line", text)
                # The AVAILABLE-then-call-fails escape hatch.
                self.assertIn(
                    "record `FALLBACK` naming the failure and continue", text
                )

        # The retired phrasings, and the log-bound idioms generally, must not
        # survive anywhere in the space - including in a reworded form.
        for tree in CARRIER_TREES:
            for path in (PACKAGE_ROOT / tree).rglob("*.md"):
                relative = path.relative_to(PACKAGE_ROOT).as_posix()
                text = path.read_text(encoding="utf-8")
                with self.subTest(relative=relative):
                    self.assertNotIn("as probed in `dependency-check.log`", text)
                    self.assertNotIn("When the probed status in", text)
                    if "reuse-first" in text:
                        self.assertIsNone(
                            re.search(r"(?i)probed status|as probed", text),
                            f"{relative}: reuse routing is log-bound again",
                        )


    def test_entry_documents_wire_the_lessons_layer(self) -> None:
        for relative in (
            "portable/commands/charter-workflow.md",
            "targets/zcode/commands/charter-workflow.md",
            "targets/codex/skills/charter-workflow/SKILL.md",
            "targets/zcode/skills/charter-workflow/SKILL.md",
        ):
            with self.subTest(relative=relative):
                text = read(relative)
                self.assertIn(".charter/lessons.md", text)
                self.assertIn("references/lessons.md", text)
                self.assertIn("GENERALIZE", text)

        skill = read("targets/codex/skills/charter-workflow/SKILL.md")
        self.assertIn("nine templates", skill)
        self.assertIn("nine files", skill)

    def test_bootstrap_prompts_read_and_create_lessons(self) -> None:
        for relative in (
            "portable/prompts/generic-bootstrap.md",
            "portable/prompts/codex-bootstrap.md",
            "portable/prompts/claude-bootstrap.md",
            "portable/prompts/gemini-bootstrap.md",
            "portable/prompts/deepseek-bootstrap.md",
        ):
            with self.subTest(relative=relative):
                text = read(relative)
                self.assertIn("lessons.md", text)
                self.assertIn("GENERALIZE", text)


if __name__ == "__main__":
    unittest.main()
