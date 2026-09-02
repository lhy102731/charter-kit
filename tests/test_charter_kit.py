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

    def write_marketplace_manifest(self, package: Path, *, name: str = "charter-kit", source: str = "./plugins/charter-kit") -> Path:
        manifest_path = package / ".agents" / "plugins" / "marketplace.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(
                {
                    "name": name,
                    "entry": {
                        "name": name,
                        "source": source,
                    },
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        return manifest_path

    def prepare_multi_target_layout(self, package: Path) -> None:
        (package / "targets" / "codex").mkdir(parents=True, exist_ok=True)
        (package / "plugins" / "charter-kit" / ".codex-plugin").mkdir(parents=True, exist_ok=True)
        (package / "plugins" / "charter-kit" / ".codex-plugin" / "plugin.json").write_text(
            json.dumps({"name": "charter-kit"}, indent=2),
            encoding="utf-8",
        )
        self.write_marketplace_manifest(package)

    def prepare_complete_distribution_layout(self, package: Path) -> None:
        """Create a minimal but complete target/distribution fixture.

        The fixture deliberately uses byte copies of the package's existing
        Codex manifest and Skill.  That keeps each validator test focused on
        one marketplace/distribution invariant instead of depending on the
        in-progress generated tree in the source checkout.
        """
        target = package / "targets" / "codex"
        target_manifest = target / ".codex-plugin" / "plugin.json"
        target_skill = target / "skills" / "charter-workflow"
        target_manifest.parent.mkdir(parents=True, exist_ok=True)
        target_manifest.write_bytes((package / ".codex-plugin" / "plugin.json").read_bytes())
        if target_skill.exists():
            shutil.rmtree(target_skill)
        shutil.copytree(package / "skills" / "charter-workflow", target_skill)

        distribution = package / "plugins" / "charter-kit"
        if distribution.exists():
            shutil.rmtree(distribution)
        distribution_manifest = distribution / ".codex-plugin" / "plugin.json"
        distribution_manifest.parent.mkdir(parents=True, exist_ok=True)
        distribution_manifest.write_bytes(target_manifest.read_bytes())
        shutil.copytree(target_skill, distribution / "skills" / "charter-workflow")

        marketplace_path = package / ".agents" / "plugins" / "marketplace.json"
        marketplace_path.parent.mkdir(parents=True, exist_ok=True)
        marketplace_path.write_text(
            json.dumps(
                {
                    "name": "charter-kit",
                    "interface": {"displayName": "Charter Kit"},
                    "plugins": [
                        {
                            "name": "charter-kit",
                            "source": {
                                "source": "local",
                                "path": "./plugins/charter-kit",
                            },
                            "policy": {
                                "installation": "AVAILABLE",
                                "authentication": "ON_INSTALL",
                            },
                            "category": "Developer Tools",
                        }
                    ],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    def prepare_codex_target_skill_mirror(self, package: Path) -> Path:
        target_skill = package / "targets" / "codex" / "skills" / "charter-workflow"
        if target_skill.exists():
            shutil.rmtree(target_skill)
        shutil.copytree(package / "skills" / "charter-workflow", target_skill)
        return target_skill

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

    def run_builder(self, package: Path, *arguments: object) -> subprocess.CompletedProcess[str]:
        return self.run_script(package / "scripts" / "build_codex_plugin.py", *arguments)

    def snapshot_tree_bytes(self, root: Path) -> dict[str, bytes]:
        snapshot: dict[str, bytes] = {}
        for path in sorted(root.rglob("*")):
            if path.is_file():
                snapshot[str(path.relative_to(root))] = path.read_bytes()
        return snapshot

    def assert_tree_is_link_free(self, root: Path) -> None:
        resolved_root = root.resolve()
        self.assertFalse(root.is_symlink(), f"{root} is a symlink")
        for path in sorted(root.rglob("*")):
            self.assertFalse(path.is_symlink(), f"{path} is a symlink")
            if path.exists():
                self.assertTrue(
                    path.resolve().is_relative_to(resolved_root),
                    f"{path} resolves outside {resolved_root}",
                )

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
        self.assertIn("`BUILD_NEW` is a capability-level route", reuse)
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
            "Coverage: `SEARCHED | NOT_SEARCHED | NOT_AUTHORIZED | BLOCKED_TOOLING`",
            "Result: `MATCH | NO_MATCH | UNKNOWN`",
            "`NO_MATCH` requires an evidence reference",
            "no unresolved high-value `UNKNOWN` or `DEFER`",
            "immutable Git commit/tag or package version",
        ):
            self.assertIn(phrase, reuse)

    def test_change_triage_reference_is_packaged_in_codex_skill_mirrors(self) -> None:
        package = self.make_package_copy()
        expected = (package / "portable" / "references" / "change-triage.md").read_bytes()
        for relative in (
            "skills/charter-workflow/references/change-triage.md",
            "targets/codex/skills/charter-workflow/references/change-triage.md",
            "plugins/charter-kit/skills/charter-workflow/references/change-triage.md",
        ):
            with self.subTest(relative=relative):
                self.assertEqual((package / relative).read_bytes(), expected)

    def test_validator_allows_unimplemented_experimental_target(self) -> None:
        package = self.make_package_copy()
        shutil.rmtree(package / "targets" / "dsh")
        shutil.rmtree(package / "plugins" / "dsh-charter-kit")

        result = self.run_validator(package)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("experimental", result.stdout.lower())

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

    def test_validator_requires_codex_target_source_directory(self) -> None:
        package = self.make_package_copy()
        self.prepare_multi_target_layout(package)
        shutil.rmtree(package / "targets" / "codex")

        result = self.run_validator(package)
        self.assertIn("targets/codex", result.stdout)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_validator_requires_generated_codex_plugin_directory(self) -> None:
        package = self.make_package_copy()
        self.prepare_multi_target_layout(package)
        shutil.rmtree(package / "plugins" / "charter-kit")

        result = self.run_validator(package)
        self.assertIn("plugins/charter-kit", result.stdout)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_validator_requires_repository_marketplace_manifest(self) -> None:
        package = self.make_package_copy()
        self.prepare_multi_target_layout(package)
        (package / ".agents" / "plugins" / "marketplace.json").unlink()

        result = self.run_validator(package)
        self.assertIn(".agents/plugins/marketplace.json", result.stdout)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_validator_requires_marketplace_entry_source_path(self) -> None:
        package = self.make_package_copy()
        self.prepare_multi_target_layout(package)
        manifest_path = package / ".agents" / "plugins" / "marketplace.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["entry"]["source"] = "./plugins/wrong-charter-kit"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        result = self.run_validator(package)
        self.assertIn("./plugins/charter-kit", result.stdout)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_validator_requires_marketplace_entry_name(self) -> None:
        package = self.make_package_copy()
        self.prepare_multi_target_layout(package)
        manifest_path = package / ".agents" / "plugins" / "marketplace.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["entry"]["name"] = "wrong-charter-kit"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        result = self.run_validator(package)
        self.assertIn("charter-kit", result.stdout)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_validator_rejects_duplicate_marketplace_plugin_names(self) -> None:
        package = self.make_package_copy()
        self.prepare_complete_distribution_layout(package)
        marketplace_path = package / ".agents" / "plugins" / "marketplace.json"
        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
        marketplace["plugins"].append(dict(marketplace["plugins"][0]))
        marketplace_path.write_text(json.dumps(marketplace, indent=2), encoding="utf-8")

        result = self.run_validator(package)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("duplicate plugin name", result.stdout.lower())

    def test_validator_rejects_marketplace_policy_and_unsafe_source(self) -> None:
        package = self.make_package_copy()
        self.prepare_complete_distribution_layout(package)
        marketplace_path = package / ".agents" / "plugins" / "marketplace.json"
        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
        entry = marketplace["plugins"][0]
        entry["source"]["path"] = "../outside"
        entry["policy"].pop("authentication")
        entry["policy"]["installation"] = "UNKNOWN"
        marketplace_path.write_text(json.dumps(marketplace, indent=2), encoding="utf-8")

        result = self.run_validator(package)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("source.path", result.stdout)
        self.assertIn("policy.installation", result.stdout)
        self.assertIn("policy.authentication", result.stdout)

    def test_validator_rejects_missing_codex_target_manifest(self) -> None:
        package = self.make_package_copy()
        self.prepare_complete_distribution_layout(package)
        (package / "targets" / "codex" / ".codex-plugin" / "plugin.json").unlink()

        result = self.run_validator(package)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("targets/codex/.codex-plugin/plugin.json", result.stdout)

    def test_validator_rejects_generated_distribution_newline_drift(self) -> None:
        package = self.make_package_copy()
        self.prepare_complete_distribution_layout(package)
        bundled = package / "plugins" / "charter-kit" / "skills" / "charter-workflow" / "templates" / "roadmap.md"
        original = bundled.read_bytes()
        modified = original.replace(b"\r\n", b"\n") if b"\r\n" in original else original.replace(b"\n", b"\r\n")
        self.assertNotEqual(original, modified)
        bundled.write_bytes(modified)

        result = self.run_validator(package)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("plugins/charter-kit", result.stdout)
        self.assertIn("differs", result.stdout.lower())

    def test_validator_rejects_generated_distribution_extra_entry(self) -> None:
        package = self.make_package_copy()
        self.prepare_complete_distribution_layout(package)
        (package / "plugins" / "charter-kit" / "unexpected.txt").write_text("not generated", encoding="utf-8")

        result = self.run_validator(package)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("unexpected top-level entry", result.stdout.lower())

    def test_validator_rejects_malformed_repository_marketplace_json(self) -> None:
        package = self.make_package_copy()
        self.prepare_complete_distribution_layout(package)
        marketplace_path = package / ".agents" / "plugins" / "marketplace.json"
        marketplace_path.write_bytes(b"{\n  \"plugins\": [\n")

        result = self.run_validator(package)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("marketplace.json: invalid JSON", result.stdout)

    def test_validator_rejects_missing_agentpack_distribution_declarations(self) -> None:
        package = self.make_package_copy()
        self.prepare_complete_distribution_layout(package)
        agentpack = package / "agentpack.yaml"
        text = agentpack.read_text(encoding="utf-8")
        text = text.replace("    source: targets/codex\n", "")
        agentpack.write_text(text, encoding="utf-8")

        result = self.run_validator(package)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("targets.codex.source", result.stdout)

    def test_builder_creates_self_contained_codex_package(self) -> None:
        package = self.make_package_copy()
        temporary = tempfile.TemporaryDirectory(prefix="charter-kit-output-")
        self.addCleanup(temporary.cleanup)
        output = Path(temporary.name) / "plugins" / "charter-kit"
        source_manifest = package / "targets" / "codex" / ".codex-plugin" / "plugin.json"

        result = self.run_builder(package, "--output", output)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((output / ".codex-plugin" / "plugin.json").is_file(), result.stdout + result.stderr)
        self.assertTrue((output / "skills" / "charter-workflow").is_dir(), result.stdout + result.stderr)
        self.assertEqual(
            (output / ".codex-plugin" / "plugin.json").read_bytes(),
            source_manifest.read_bytes(),
        )
        self.assert_tree_is_link_free(output)

    def test_builder_uses_codex_target_skill_mirror(self) -> None:
        package = self.make_package_copy()
        target_skill = self.prepare_codex_target_skill_mirror(package)
        roadmap = target_skill / "templates" / "roadmap.md"
        roadmap.write_text("TARGET MIRROR ROADMAP\n", encoding="utf-8")

        temporary = tempfile.TemporaryDirectory(prefix="charter-kit-output-")
        self.addCleanup(temporary.cleanup)
        output = Path(temporary.name) / "plugins" / "charter-kit"

        result = self.run_builder(package, "--output", output)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(
            (output / "skills" / "charter-workflow" / "templates" / "roadmap.md").read_text(encoding="utf-8"),
            "TARGET MIRROR ROADMAP\n",
        )

    def test_builder_check_is_deterministic_and_non_mutating(self) -> None:
        package = self.make_package_copy()
        temporary = tempfile.TemporaryDirectory(prefix="charter-kit-output-")
        self.addCleanup(temporary.cleanup)
        output = Path(temporary.name) / "plugins" / "charter-kit"

        built = self.run_builder(package, "--output", output)
        self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
        before = self.snapshot_tree_bytes(output)

        checked = self.run_builder(package, "--check", "--output", output)
        after = self.snapshot_tree_bytes(output)

        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        self.assertEqual(before, after, checked.stdout + checked.stderr)

    def test_builder_synchronizes_legacy_root_snapshot(self) -> None:
        package = self.make_package_copy()
        temporary = tempfile.TemporaryDirectory(prefix="charter-kit-output-")
        self.addCleanup(temporary.cleanup)
        output = Path(temporary.name) / "plugins" / "charter-kit"

        result = self.run_builder(package, "--output", output)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(
            (package / ".codex-plugin" / "plugin.json").read_bytes(),
            (output / ".codex-plugin" / "plugin.json").read_bytes(),
        )
        self.assertEqual(
            self.snapshot_tree_bytes(package / "skills" / "charter-workflow"),
            self.snapshot_tree_bytes(output / "skills" / "charter-workflow"),
        )
        self.assert_tree_is_link_free(output / "skills" / "charter-workflow")

    def test_builder_rejects_linked_output_root(self) -> None:
        package = self.make_package_copy()
        temporary = tempfile.TemporaryDirectory(prefix="charter-kit-output-")
        self.addCleanup(temporary.cleanup)
        base = Path(temporary.name)
        real_output = base / "real-output"
        real_output.mkdir()
        linked_output = base / "linked-output"
        try:
            linked_output.symlink_to(real_output, target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"symlink creation unavailable: {exc}")

        result = self.run_builder(package, "--output", linked_output)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertRegex(result.stderr.lower(), r"linked|symlink|junction")
        self.assertEqual(list(real_output.iterdir()), [])

    def test_builder_rejects_repository_root_output_without_deleting_source(self) -> None:
        package = self.make_package_copy()
        before = {
            relative: (package / relative).read_bytes()
            for relative in ("README.md", "scripts/build_codex_plugin.py", "targets/codex/.codex-plugin/plugin.json")
        }

        result = self.run_builder(package, "--output", package)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertRegex(result.stderr.lower(), r"repository|source|output")
        for relative, contents in before.items():
            self.assertEqual((package / relative).read_bytes(), contents)

    def test_builder_rejects_output_inside_canonical_source_tree(self) -> None:
        package = self.make_package_copy()
        source_tree = package / "portable"
        before = (source_tree / "templates" / "roadmap.md").read_bytes()

        result = self.run_builder(package, "--output", source_tree)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertRegex(result.stderr.lower(), r"source|canonical|output")
        self.assertEqual((source_tree / "templates" / "roadmap.md").read_bytes(), before)

    def test_builder_rejects_hardlinked_output_entry(self) -> None:
        package = self.make_package_copy()
        temporary = tempfile.TemporaryDirectory(prefix="charter-kit-output-")
        self.addCleanup(temporary.cleanup)
        base = Path(temporary.name)
        output = base / "plugins" / "charter-kit"
        output.mkdir(parents=True)
        external = base / "external.txt"
        external.write_text("DO_NOT_OVERWRITE", encoding="utf-8")
        try:
            os.link(external, output / "README.md")
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"hardlink creation unavailable: {exc}")

        result = self.run_builder(package, "--output", output)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("hard-linked", result.stderr.lower())
        self.assertEqual(external.read_text(encoding="utf-8"), "DO_NOT_OVERWRITE")

    def test_builder_rejects_dangling_output_link(self) -> None:
        package = self.make_package_copy()
        temporary = tempfile.TemporaryDirectory(prefix="charter-kit-output-")
        self.addCleanup(temporary.cleanup)
        base = Path(temporary.name)
        linked_output = base / "linked-output"
        missing_target = base / "missing-output"
        try:
            linked_output.symlink_to(missing_target, target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"symlink creation unavailable: {exc}")

        result = self.run_builder(package, "--output", linked_output)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertRegex(result.stderr.lower(), r"linked|symlink|junction")
        self.assertFalse(missing_target.exists())

    def test_builder_rejects_unsafe_target_manifest_skill_path(self) -> None:
        package = self.make_package_copy()
        manifest_path = package / "targets" / "codex" / ".codex-plugin" / "plugin.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["skills"] = "../../outside"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        temporary = tempfile.TemporaryDirectory(prefix="charter-kit-output-")
        self.addCleanup(temporary.cleanup)
        output = Path(temporary.name) / "plugins" / "charter-kit"

        result = self.run_builder(package, "--output", output)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("skills", result.stderr.lower())
        self.assertFalse(output.exists())

    def test_builder_rejects_output_that_contains_repository(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="charter-kit-ancestor-")
        self.addCleanup(temporary.cleanup)
        base = Path(temporary.name)
        package = base / "repo"
        shutil.copytree(
            PACKAGE_ROOT,
            package,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
        sentinel = base / "keep.txt"
        sentinel.write_text("DO_NOT_DELETE", encoding="utf-8")

        result = self.run_builder(package, "--output", base)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertRegex(result.stderr.lower(), r"contain|ancestor|repository|source")
        self.assertTrue((package / "README.md").is_file())
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "DO_NOT_DELETE")

    def test_builder_refuses_nonempty_external_output_without_deleting_it(self) -> None:
        package = self.make_package_copy()
        temporary = tempfile.TemporaryDirectory(prefix="charter-kit-output-")
        self.addCleanup(temporary.cleanup)
        output = Path(temporary.name) / "external-output"
        output.mkdir()
        sentinel = output / "keep.txt"
        sentinel.write_text("DO_NOT_DELETE", encoding="utf-8")

        result = self.run_builder(package, "--output", output)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertRegex(result.stderr.lower(), r"non-empty|existing|output")
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "DO_NOT_DELETE")

    def test_builder_rejects_default_output_through_linked_plugins_directory(self) -> None:
        package = self.make_package_copy()
        temporary = tempfile.TemporaryDirectory(prefix="charter-kit-linked-")
        self.addCleanup(temporary.cleanup)
        outside = Path(temporary.name) / "outside"
        outside.mkdir()
        plugins = package / "plugins"
        shutil.rmtree(plugins)
        try:
            plugins.symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"symlink creation unavailable: {exc}")

        result = self.run_builder(package)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertRegex(result.stderr.lower(), r"linked|symlink|junction")
        self.assertFalse((outside / "charter-kit").exists())

    def test_builder_rejects_hardlinked_source_manifest(self) -> None:
        package = self.make_package_copy()
        manifest_path = package / "targets" / "codex" / ".codex-plugin" / "plugin.json"
        external_manifest = manifest_path.parent.parent.parent.parent / "external-manifest.json"
        external_manifest.write_bytes(manifest_path.read_bytes())
        manifest_path.unlink()
        try:
            os.link(external_manifest, manifest_path)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"hardlink creation unavailable: {exc}")
        temporary = tempfile.TemporaryDirectory(prefix="charter-kit-output-")
        self.addCleanup(temporary.cleanup)
        output = Path(temporary.name) / "charter-kit"

        result = self.run_builder(package, "--output", output)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("hard-linked", result.stderr.lower())
        self.assertFalse(output.exists())

    def test_generated_package_omits_repository_maintenance_tools(self) -> None:
        package = self.make_package_copy()
        temporary = tempfile.TemporaryDirectory(prefix="charter-kit-output-")
        self.addCleanup(temporary.cleanup)
        output = Path(temporary.name) / "charter-kit"

        result = self.run_builder(package, "--output", output)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((output / "scripts" / "check_dependencies.py").is_file())
        self.assertTrue((output / "scripts" / "init_project.py").is_file())
        self.assertFalse((output / "scripts" / "build_codex_plugin.py").exists())
        self.assertFalse((output / "scripts" / "validate_kit.py").exists())

    def test_validator_rejects_hardlinked_target_tree_entry(self) -> None:
        package = self.make_package_copy()
        self.prepare_complete_distribution_layout(package)
        target_file = package / "targets" / "codex" / "skills" / "charter-workflow" / "SKILL.md"
        external_file = package.parent / "external-skill.md"
        external_file.write_bytes(target_file.read_bytes())
        target_file.unlink()
        try:
            os.link(external_file, target_file)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"hardlink creation unavailable: {exc}")

        result = self.run_validator(package)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("hard-linked file", result.stdout.lower())

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
        review_template = charter / "review.md"
        review_template.unlink()
        review_template.mkdir()

        result = self.run_script(init_script, project, "--force")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual((charter / "project.md").read_text(encoding="utf-8"), marker)


if __name__ == "__main__":
    unittest.main()
