from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]


class CharterKitBehaviorTests(unittest.TestCase):
    def make_package_copy(self) -> Path:
        temporary = tempfile.TemporaryDirectory(prefix="charter-kit-test-")
        self.addCleanup(temporary.cleanup)
        destination = Path(temporary.name) / "charter-kit"
        shutil.copytree(
            PACKAGE_ROOT,
            destination,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
        return destination

    def run_script(self, script: Path, *arguments: object) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(script), *(str(argument) for argument in arguments)],
            cwd=script.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )

    def run_validator(self, package: Path) -> subprocess.CompletedProcess[str]:
        return self.run_script(package / "scripts" / "validate_kit.py", package)

    def test_force_backs_up_all_charter_data_before_overwrite(self) -> None:
        package = self.make_package_copy()
        project = package.parent / "project"
        init_script = package / "scripts" / "init_project.py"

        first = self.run_script(init_script, project)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)

        charter = project / ".charter"
        project_marker = "USER_FILLED_PROJECT"
        handoff_marker = "USER_FILLED_HANDOFF"
        (charter / "project.md").write_text(project_marker, encoding="utf-8")
        (charter / "handoff.md").write_text(handoff_marker, encoding="utf-8")
        (charter / "evidence" / "user-note.txt").write_text("KEEP_ME", encoding="utf-8")

        forced = self.run_script(init_script, project, "--force")
        self.assertEqual(forced.returncode, 0, forced.stdout + forced.stderr)

        backups = sorted(project.glob(".charter.backup-*"))
        self.assertEqual(len(backups), 1, forced.stdout + forced.stderr)
        backup = backups[0]
        self.assertEqual((backup / "project.md").read_text(encoding="utf-8"), project_marker)
        self.assertEqual((backup / "handoff.md").read_text(encoding="utf-8"), handoff_marker)
        self.assertEqual(
            (backup / "evidence" / "user-note.txt").read_text(encoding="utf-8"),
            "KEEP_ME",
        )
        self.assertNotIn(project_marker, (charter / "project.md").read_text(encoding="utf-8"))
        self.assertIn("Backup:", forced.stdout)
        self.assertIn("roadmap.md", forced.stdout)

    def test_init_creates_reuse_discovery_record(self) -> None:
        package = self.make_package_copy()
        project = package.parent / "project"
        init_script = package / "scripts" / "init_project.py"

        result = self.run_script(init_script, project)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        reuse = project / ".charter" / "reuse-discovery.md"
        self.assertTrue(reuse.is_file(), result.stdout + result.stderr)
        self.assertIn("Reuse Discovery", reuse.read_text(encoding="utf-8"))

    def test_add_missing_preserves_existing_charter_files(self) -> None:
        package = self.make_package_copy()
        project = package.parent / "project"
        init_script = package / "scripts" / "init_project.py"

        first = self.run_script(init_script, project)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        charter = project / ".charter"
        (charter / "project.md").write_text("USER_FILLED_PROJECT", encoding="utf-8")
        (charter / "reuse-discovery.md").unlink()

        migrated = self.run_script(init_script, project, "--add-missing")
        self.assertEqual(migrated.returncode, 0, migrated.stdout + migrated.stderr)
        self.assertEqual(
            (charter / "project.md").read_text(encoding="utf-8"),
            "USER_FILLED_PROJECT",
        )
        self.assertIn("Reuse Discovery", (charter / "reuse-discovery.md").read_text(encoding="utf-8"))
        self.assertIn("missing", migrated.stdout.lower())

    def test_reuse_route_distinguishes_build_new_from_candidate_decision(self) -> None:
        package = self.make_package_copy()
        reuse = (package / "portable" / "templates" / "reuse-discovery.md").read_text(encoding="utf-8")
        self.assertIn("BUILD_NEW is a capability-level route", reuse)
        candidate_header = next(line for line in reuse.splitlines() if line.startswith("| ID | Type"))
        self.assertNotIn("BUILD_NEW", candidate_header)

    def test_blocked_tooling_explicitly_blocks_leaf_readiness(self) -> None:
        package = self.make_package_copy()
        command = (package / "portable" / "commands" / "charter-workflow.md").read_text(encoding="utf-8")
        roadmap = (package / "portable" / "templates" / "roadmap.md").read_text(encoding="utf-8")
        self.assertIn("BLOCKED_TOOLING", command)
        self.assertIn("blocks leaf readiness", command.lower())
        self.assertIn("recheck trigger", roadmap.lower())

    def test_agentpack_uses_generic_codex_entry_and_explicit_discovery_restrictions(self) -> None:
        package = self.make_package_copy()
        pack = (package / "agentpack.yaml").read_text(encoding="utf-8")
        self.assertIn("host_neutral_entry: portable/prompts/generic-bootstrap.md", pack)
        for phrase in ("prohibited_actions:", "clone", "build", "import", "copy", "private_source"):
            self.assertIn(phrase, pack)

    def test_reuse_scope_results_and_complete_criteria_are_explicit(self) -> None:
        package = self.make_package_copy()
        reuse = (package / "portable" / "templates" / "reuse-discovery.md").read_text(encoding="utf-8")
        for phrase in (
            "LOCAL_ONLY = workspace/history",
            "LOCAL_ECOSYSTEM = workspace/history + installed/cache + approved internal",
            "FULL_EXTERNAL = LOCAL_ECOSYSTEM + official/upstream/registries + authorized public web",
            "MATCHES / NO_MATCH / NOT_SEARCHED / NOT_AUTHORIZED / BLOCKED_TOOLING",
            "NO_MATCH requires an evidence reference",
            "no unresolved high-value `UNKNOWN` or `DEFER`",
            "fixed immutable commit/tag/package version",
        ):
            self.assertIn(phrase, reuse)

    def test_entry_points_repeat_full_discovery_safety_and_immutable_revision_rule(self) -> None:
        package = self.make_package_copy()
        command = (package / "portable" / "commands" / "charter-workflow.md").read_text(encoding="utf-8")
        readme = (package / "README.md").read_text(encoding="utf-8")
        for text in (command, readme):
            for phrase in (
                "clone",
                "build",
                "import",
                "copy",
                "private source",
                "immutable commit/tag/package version",
            ):
                self.assertIn(phrase, text)

    def test_agentpack_declares_reuse_gate_completion_contract(self) -> None:
        package = self.make_package_copy()
        pack = (package / "agentpack.yaml").read_text(encoding="utf-8")
        for phrase in (
            "reuse_gate:",
            "candidate_decisions:",
            "completion_requirements:",
            "evidence_required: true",
            "no-unresolved-high-value-unknown-or-defer",
            "immutable-revision-required",
        ):
            self.assertIn(phrase, pack)

    def test_second_init_without_force_preserves_existing_files(self) -> None:
        package = self.make_package_copy()
        project = package.parent / "project"
        init_script = package / "scripts" / "init_project.py"

        first = self.run_script(init_script, project)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        marker = "DO_NOT_OVERWRITE"
        (project / ".charter" / "project.md").write_text(marker, encoding="utf-8")

        second = self.run_script(init_script, project)
        self.assertEqual(second.returncode, 1, second.stdout + second.stderr)
        self.assertIn("refusing to overwrite", second.stderr)
        self.assertEqual(
            (project / ".charter" / "project.md").read_text(encoding="utf-8"),
            marker,
        )

    def test_validator_rejects_newline_only_bundled_copy_drift(self) -> None:
        package = self.make_package_copy()
        bundled = package / "skills" / "charter-workflow" / "templates" / "roadmap.md"
        original = bundled.read_bytes()
        if b"\r\n" in original:
            modified = original.replace(b"\r\n", b"\n")
        else:
            modified = original.replace(b"\n", b"\r\n")
        self.assertNotEqual(original, modified)
        bundled.write_bytes(modified)

        result = self.run_validator(package)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("differs from portable/templates/roadmap.md", result.stdout)

    def test_validator_rejects_empty_bundled_copy_drift(self) -> None:
        package = self.make_package_copy()
        bundled = package / "skills" / "charter-workflow" / "templates" / "roadmap.md"
        bundled.write_bytes(b"")

        result = self.run_validator(package)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("differs from portable/templates/roadmap.md", result.stdout)

    def test_validator_rejects_invalid_plugin_interface(self) -> None:
        package = self.make_package_copy()
        manifest_path = package / ".codex-plugin" / "plugin.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["interface"]["capabilities"] = {"Read": True}
        manifest["interface"].pop("defaultPrompt")
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        result = self.run_validator(package)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("interface.capabilities must be an array of non-empty strings", result.stdout)
        self.assertIn("interface.defaultPrompt is required", result.stdout)

    def test_validator_reports_non_object_plugin_manifest(self) -> None:
        package = self.make_package_copy()
        manifest_path = package / ".codex-plugin" / "plugin.json"
        manifest_path.write_text("[]", encoding="utf-8")

        result = self.run_validator(package)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("top-level value must be an object", result.stdout)

    def test_validator_rejects_host_prompt_without_roadmap(self) -> None:
        package = self.make_package_copy()
        prompt = package / "portable" / "prompts" / "generic-bootstrap.md"
        prompt.write_text(
            prompt.read_text(encoding="utf-8").replace(".charter/roadmap.md", ""),
            encoding="utf-8",
        )

        result = self.run_validator(package)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("missing '.charter/roadmap.md'", result.stdout)

    def test_validator_rejects_ready_first_leaf(self) -> None:
        package = self.make_package_copy()
        roadmap = package / "portable" / "templates" / "roadmap.md"
        roadmap.write_text(
            roadmap.read_text(encoding="utf-8").replace("| `DRAFT` |", "| `READY` |"),
            encoding="utf-8",
        )

        result = self.run_validator(package)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("first leaf must start DRAFT", result.stdout)

    def test_validator_requires_declared_license_file(self) -> None:
        package = self.make_package_copy()
        license_path = package / "LICENSE"
        if license_path.exists():
            license_path.unlink()

        result = self.run_validator(package)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("missing file: LICENSE", result.stdout)

    def test_validator_requires_project_blocked_state(self) -> None:
        package = self.make_package_copy()
        for template in (
            package / "portable" / "templates" / "project-charter.md",
            package / "skills" / "charter-workflow" / "templates" / "project-charter.md",
        ):
            text = template.read_text(encoding="utf-8")
            template.write_text(
                text.replace(
                    "`DRAFT | APPROVED | BLOCKED | BLOCKED_TOOLING | NEEDS_DECISION | PARTIAL | PAUSED | SUPERSEDED | CLOSED`",
                    "`DRAFT | APPROVED`",
                ),
                encoding="utf-8",
            )

        result = self.run_validator(package)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("project-charter.md: missing 'Current status:", result.stdout)

    def test_validator_requires_blocked_tooling_leaf_closure(self) -> None:
        package = self.make_package_copy()
        for template in (
            package / "portable" / "templates" / "leaf-task.md",
            package / "skills" / "charter-workflow" / "templates" / "leaf-task.md",
        ):
            text = template.read_text(encoding="utf-8")
            template.write_text(
                text.replace("- `BLOCKED_TOOLING` —", "- `BLOCKED_REMOVED` —"),
                encoding="utf-8",
            )

        result = self.run_validator(package)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("leaf-task.md: missing '- `BLOCKED_TOOLING`", result.stdout)

    def test_validator_requires_missing_working_set_block_rule_in_each_prompt(self) -> None:
        package = self.make_package_copy()
        prompt = package / "portable" / "prompts" / "generic-bootstrap.md"
        prompt.write_text(
            prompt.read_text(encoding="utf-8").replace(
                "If any required working-set file is missing or unreadable, remain `BLOCKED`; repair or restore the working set only, and do not plan or implement.",
                "",
            ),
            encoding="utf-8",
        )

        result = self.run_validator(package)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("generic-bootstrap.md: missing required-file BLOCKED rule", result.stdout)

    def test_validator_requires_approved_state_mirroring(self) -> None:
        package = self.make_package_copy()
        for roadmap in (
            package / "portable" / "templates" / "roadmap.md",
            package / "skills" / "charter-workflow" / "templates" / "roadmap.md",
        ):
            roadmap.write_text(
                roadmap.read_text(encoding="utf-8").replace(
                    "When moving a leaf from `DRAFT` to `APPROVED`, update the task file and roadmap row together; then move both to `READY` together after readiness.",
                    "",
                ),
                encoding="utf-8",
            )

        result = self.run_validator(package)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("roadmap.md: APPROVED state must be mirrored", result.stdout)

    def test_validator_requires_unresolved_charter_finding_block(self) -> None:
        package = self.make_package_copy()
        command = package / "portable" / "commands" / "charter-workflow.md"
        command.write_text(
            command.read_text(encoding="utf-8").replace(
                "Unresolved findings keep the project `BLOCKED`; resolve each finding, record an explicit open decision or waiver with its limitation, and do not request or record project approval while one remains unhandled.",
                "",
            ),
            encoding="utf-8",
        )

        result = self.run_validator(package)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("charter-workflow.md: unresolved charter findings must block approval", result.stdout)

    def test_validator_does_not_combine_unrelated_finding_words_into_block_rule(self) -> None:
        """An unrelated open finding and a separate BLOCKED state are not enough."""
        package = self.make_package_copy()
        command = package / "portable" / "commands" / "charter-workflow.md"
        text = command.read_text(encoding="utf-8")
        text = text.replace(
            "Unresolved findings keep the project `BLOCKED`; resolve each finding, record an explicit open decision or waiver with its limitation, and do not request or record project approval while one remains unhandled.",
            "The project may be `BLOCKED` for tooling issues. Resume mode records an open finding.",
        )
        command.write_text(text, encoding="utf-8")

        result = self.run_validator(package)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("charter-workflow.md: unresolved charter findings must block approval", result.stdout)

    def test_validator_does_not_require_skill_before_zero_start_command(self) -> None:
        package = self.make_package_copy()
        command = package / "portable" / "commands" / "charter-workflow.md"
        command_text = command.read_text(encoding="utf-8")
        self.assertNotIn("Required prerequisite: install the `charter-workflow` Skill", command_text)
        self.assertNotIn("Required prerequisite: install the `charter-workflow` Skill", (package / "README.md").read_text(encoding="utf-8"))

        result = self.run_validator(package)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_validator_requires_separate_leaf_approval_in_each_prompt(self) -> None:
        package = self.make_package_copy()
        prompt = package / "portable" / "prompts" / "generic-bootstrap.md"
        prompt.write_text(
            prompt.read_text(encoding="utf-8").replace(
                "Project approval does not approve any leaf; in `MANUAL` obtain separate leaf approval, or in `AUTO_DEV` cite matching preauthorization, before moving the leaf beyond `DRAFT`.",
                "",
            ),
            encoding="utf-8",
        )

        result = self.run_validator(package)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("generic-bootstrap.md: project and leaf approval must be separate", result.stdout)

    def test_validator_requires_reuse_discovery_gate(self) -> None:
        package = self.make_package_copy()
        (package / "portable" / "templates" / "reuse-discovery.md").unlink()
        (package / "skills" / "charter-workflow" / "templates" / "reuse-discovery.md").unlink()

        result = self.run_validator(package)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("missing file: portable/templates/reuse-discovery.md", result.stdout)

    def test_validator_requires_reuse_gate_in_roadmap_and_prompts(self) -> None:
        package = self.make_package_copy()
        roadmap = package / "portable" / "templates" / "roadmap.md"
        roadmap.write_text(
            roadmap.read_text(encoding="utf-8").replace("reuse-discovery", "reuse-record-removed"),
            encoding="utf-8",
        )
        prompt = package / "portable" / "prompts" / "generic-bootstrap.md"
        prompt.write_text(
            prompt.read_text(encoding="utf-8").replace("reuse-discovery", "reuse-record-removed"),
            encoding="utf-8",
        )

        result = self.run_validator(package)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("reuse discovery", result.stdout.lower())

    def test_force_backs_up_unknown_charter_data(self) -> None:
        package = self.make_package_copy()
        project = package.parent / "project"
        charter = project / ".charter"
        charter.mkdir(parents=True)
        (charter / "custom-evidence.txt").write_text("KEEP_ME", encoding="utf-8")

        forced = self.run_script(package / "scripts" / "init_project.py", project, "--force")
        self.assertEqual(forced.returncode, 0, forced.stdout + forced.stderr)
        backups = sorted(project.glob(".charter.backup-*"))
        self.assertEqual(len(backups), 1, forced.stdout + forced.stderr)
        self.assertEqual(
            (backups[0] / "custom-evidence.txt").read_text(encoding="utf-8"),
            "KEEP_ME",
        )

    def test_init_rejects_charter_symlink_without_writing_through(self) -> None:
        package = self.make_package_copy()
        project = package.parent / "project"
        project.mkdir()
        outside = package.parent / "outside"
        outside.mkdir()
        try:
            (project / ".charter").symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"symlink creation unavailable: {exc}")

        result = self.run_script(package / "scripts" / "init_project.py", project)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("symlink", result.stderr.lower())
        self.assertEqual(list(outside.iterdir()), [])

    def test_init_rejects_charter_junction_without_writing_through(self) -> None:
        if sys.platform != "win32" or not hasattr(Path("."), "is_junction"):
            self.skipTest("directory junctions are Windows-only")
        package = self.make_package_copy()
        project = package.parent / "project"
        project.mkdir()
        outside = package.parent / "outside-junction"
        outside.mkdir()
        junction = project / ".charter"
        created = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(junction), str(outside)],
            text=True,
            capture_output=True,
            check=False,
        )
        if created.returncode != 0:
            self.skipTest(f"junction creation unavailable: {created.stdout}{created.stderr}")
        self.addCleanup(lambda: junction.rmdir() if junction.exists() else None)

        result = self.run_script(package / "scripts" / "init_project.py", project, "--force")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("junction", result.stderr.lower())
        self.assertEqual(list(outside.iterdir()), [])

    def test_force_replaces_hardlink_without_modifying_external_inode(self) -> None:
        package = self.make_package_copy()
        project = package.parent / "project"
        init_script = package / "scripts" / "init_project.py"
        project.mkdir()
        charter = project / ".charter"
        charter.mkdir()
        external = package.parent / "external.md"
        external.write_text("DO_NOT_OVERWRITE", encoding="utf-8")
        try:
            os.link(external, charter / "project.md")
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"hardlink creation unavailable: {exc}")

        result = self.run_script(init_script, project, "--force")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(external.read_text(encoding="utf-8"), "DO_NOT_OVERWRITE")

    def test_force_preflights_all_destination_types_before_replacing_any_file(self) -> None:
        package = self.make_package_copy()
        project = package.parent / "project"
        init_script = package / "scripts" / "init_project.py"
        first = self.run_script(init_script, project)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)

        charter = project / ".charter"
        marker = "PRESERVE_ON_PREFLIGHT_FAILURE"
        (charter / "project.md").write_text(marker, encoding="utf-8")
        review_template = charter / "review-template.md"
        review_template.unlink()
        review_template.mkdir()

        result = self.run_script(init_script, project, "--force")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual((charter / "project.md").read_text(encoding="utf-8"), marker)


if __name__ == "__main__":
    unittest.main()
