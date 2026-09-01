from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]


class GenericBootstrapTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (PACKAGE_ROOT / relative).read_text(encoding="utf-8")

    def run_script(self, script: Path, *arguments: object) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(script), *(str(argument) for argument in arguments)],
            cwd=PACKAGE_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_core_documents_are_domain_neutral(self) -> None:
        core_files = [
            "DEVELOPMENT_CHARTER.md",
            "portable/templates/project-charter.md",
            "portable/templates/leaf-task.md",
            "portable/prompts/generic-bootstrap.md",
        ]
        forbidden = (
            "KBase",
            "AG2",
            "ExperimentSpec",
            "NextQuestion",
            "daily_run.py",
            "daily_select.py",
            "a-share-quant-selector",
            "个人版",
        )
        for relative in core_files:
            content = self.read(relative)
            for token in forbidden:
                self.assertNotIn(token, content, f"{relative} contains {token}")

    def test_project_template_uses_configurable_success_levels(self) -> None:
        template = self.read("portable/templates/project-charter.md")
        self.assertIn("Define project-specific success levels", template)
        self.assertNotIn("Current success level: `COMPONENT | SYNTHETIC | BUSINESS | PRODUCTION_AUTHORIZED`", template)

    def test_project_template_records_intent_interview_evidence(self) -> None:
        template = self.read("portable/templates/project-charter.md")
        self.assertIn("Intent interview evidence:", template)
        self.assertIn("Intent interview mode:", template)

    def test_portable_design_interview_reference_is_available(self) -> None:
        reference = PACKAGE_ROOT / "portable" / "references" / "design-interview.md"
        self.assertTrue(reference.is_file())

    def test_zero_start_prompt_prioritizes_grill_me_and_has_fallback(self) -> None:
        for relative in (
            "portable/commands/charter-workflow.md",
            "portable/prompts/generic-bootstrap.md",
            "skills/charter-workflow/SKILL.md",
        ):
            content = self.read(relative)
            self.assertIn("no `.charter/project.md`", content, relative)
            self.assertIn("grill-me", content, relative)
            self.assertIn("design-interview", content, relative)
            self.assertIn("fallback", content.lower(), relative)
            self.assertIn("dependency", content.lower(), relative)

    def test_dependency_checker_reports_missing_capability_and_writes_log(self) -> None:
        script = PACKAGE_ROOT / "scripts" / "check_dependencies.py"
        self.assertTrue(script.is_file())
        with tempfile.TemporaryDirectory(prefix="charter-deps-") as directory:
            log = Path(directory) / "dependency.log"
            result = self.run_script(
                script,
                "--project",
                directory,
                "--require",
                "missing-capability",
                "--log-file",
                log,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            combined = result.stdout + result.stderr
            self.assertIn("MISSING", combined)
            self.assertIn("impact", combined.lower())
            self.assertIn("fallback", combined.lower())
            self.assertTrue(log.is_file())
            log_text = log.read_text(encoding="utf-8")
            self.assertIn("MISSING", log_text)
            self.assertIn("missing-capability", log_text)

    def test_dependency_checker_optional_missing_is_non_blocking(self) -> None:
        script = PACKAGE_ROOT / "scripts" / "check_dependencies.py"
        with tempfile.TemporaryDirectory(prefix="charter-deps-") as directory:
            result = self.run_script(
                script,
                "--project",
                directory,
                "--optional",
                "missing-optional",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("MISSING", result.stdout)
            self.assertIn("FALLBACK", result.stdout)

    def test_initializer_writes_dependency_log_without_installing(self) -> None:
        script = PACKAGE_ROOT / "scripts" / "init_project.py"
        with tempfile.TemporaryDirectory(prefix="charter-init-") as directory:
            project = Path(directory) / "project"
            result = self.run_script(script, project)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            log = project / ".charter" / "evidence" / "dependency-check.log"
            self.assertTrue(log.is_file(), result.stdout + result.stderr)
            text = log.read_text(encoding="utf-8")
            self.assertIn("Charter Kit dependency check", text)
            self.assertIn("[AVAILABLE] python", text)
            self.assertIn("grill-me", text)
            self.assertIn("action:", text)
            self.assertNotIn("pip install", text.lower())

    def test_skill_bundle_is_self_contained_for_zero_start(self) -> None:
        skill = PACKAGE_ROOT / "skills" / "charter-workflow"
        with tempfile.TemporaryDirectory(prefix="charter-skill-") as directory:
            bundle = Path(directory) / "charter-workflow"
            import shutil

            shutil.copytree(skill, bundle)
            script = bundle / "scripts" / "init_project.py"
            self.assertTrue(script.is_file())
            project = Path(directory) / "project"
            result = self.run_script(script, project)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((project / ".charter" / "project.md").is_file())
            self.assertTrue((project / ".charter" / "evidence" / "dependency-check.log").is_file())

    def test_dependency_manifest_is_machine_readable_and_documents_provider_ids(self) -> None:
        manifest = PACKAGE_ROOT / "dependencies.json"
        data = json.loads(manifest.read_text(encoding="utf-8"))
        self.assertIn("capabilities", data)
        ids = {entry["id"] for entry in data["capabilities"]}
        self.assertTrue({"python", "git", "grill-me", "design-interview"}.issubset(ids))
        document = self.read("DEPENDENCIES.md")
        for phrase in ("check_dependencies.py", "MISSING", "UNVERIFIED", "FALLBACK", "不会自动安装"):
            self.assertIn(phrase, document)

    def test_dependency_manifest_covers_document_and_project_access_capabilities(self) -> None:
        manifest = PACKAGE_ROOT / "dependencies.json"
        data = json.loads(manifest.read_text(encoding="utf-8"))
        ids = {entry["id"] for entry in data["capabilities"]}
        self.assertIn("readable-markdown", ids)
        self.assertIn("project-directory-access", ids)

    def test_project_dependency_manifest_is_used_by_initializer(self) -> None:
        script = PACKAGE_ROOT / "scripts" / "init_project.py"
        with tempfile.TemporaryDirectory(prefix="charter-init-") as directory:
            project = Path(directory) / "project"
            first = self.run_script(script, project)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            project_config = project / ".charter" / "dependencies.json"
            project_config.write_text(
                json.dumps(
                    {
                        "commands": [
                            {
                                "id": "project-required-tool",
                                "command": "definitely-not-installed-charter-kit",
                                "required": True,
                                "impact": "project capability is unavailable",
                                "fallback": "stop for a decision",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            second = self.run_script(script, project, "--add-missing")
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            log = (project / ".charter" / "evidence" / "dependency-check.log").read_text(
                encoding="utf-8"
            )
            self.assertIn("project-required-tool", log)


if __name__ == "__main__":
    unittest.main()
