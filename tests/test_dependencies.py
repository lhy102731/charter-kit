from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PACKAGE_ROOT / "scripts" / "check_dependencies.py"


class DependencyDiagnosticTests(unittest.TestCase):
    def test_package_manifest_declares_optional_reuse_providers_with_roles(self) -> None:
        payload = json.loads((PACKAGE_ROOT / "dependencies.json").read_text(encoding="utf-8"))
        providers = {entry["id"]: entry for entry in payload.get("providers", [])}
        expected = {
            "reuse-first",
            "framework-first-coding",
            "reduce-reinvention",
            "find-skills",
            "repo-to-skill",
        }
        self.assertTrue(expected.issubset(providers))
        for provider in expected:
            with self.subTest(provider=provider):
                declaration = providers[provider]
                self.assertFalse(declaration["required"])
                self.assertTrue(declaration["role"])
                self.assertTrue(declaration["fallback"])

    def test_reuse_provider_gaps_remain_distinct_from_dependency_statuses(self) -> None:
        payload = json.loads((PACKAGE_ROOT / "dependencies.json").read_text(encoding="utf-8"))
        self.assertEqual(
            set(payload.get("reuse_check", {}).get("coverage_values", [])),
            {"SEARCHED", "NOT_SEARCHED", "NOT_AUTHORIZED", "BLOCKED_TOOLING"},
        )
        self.assertEqual(
            set(payload.get("reuse_check", {}).get("result_values", [])),
            {"MATCH", "NO_MATCH", "UNKNOWN"},
        )
        self.assertEqual(
            set(payload.get("reuse_check", {}).get("gate_states", [])),
            {"PENDING", "COMPLETE", "BLOCKED"},
        )

    def run_checker(self, *arguments: object) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *(str(argument) for argument in arguments)],
            cwd=PACKAGE_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def write_config(self, directory: Path, payload: dict) -> Path:
        path = directory / "dependencies.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_missing_optional_provider_reports_impact_fallback_and_log(self) -> None:
        with tempfile.TemporaryDirectory(prefix="charter-deps-") as raw:
            directory = Path(raw)
            config = self.write_config(
                directory,
                {
                    "commands": [
                        {
                            "id": "python",
                            "command": sys.executable,
                            "required": True,
                            "impact": "core diagnostics",
                            "fallback": "manual checklist",
                        }
                    ],
                    "providers": [
                        {
                            "id": "grill-me",
                            "paths": [str(directory / "missing-grill-me")],
                            "required": False,
                            "impact": "interactive design interview unavailable",
                            "fallback": "references/design-interview.md",
                        }
                    ],
                },
            )
            log_file = directory / "evidence" / "dependency-check.log"

            result = self.run_checker(directory, "--config", config, "--log-file", log_file)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("[AVAILABLE] python", result.stdout)
            self.assertIn("[MISSING] grill-me", result.stdout)
            self.assertIn("impact: interactive design interview unavailable", result.stdout)
            self.assertIn("fallback: references/design-interview.md", result.stdout)
            self.assertIn("action:", result.stdout)
            self.assertIn("[FALLBACK] grill-me", result.stdout)
            self.assertTrue(log_file.is_file())
            log = log_file.read_text(encoding="utf-8")
            self.assertIn("[MISSING] grill-me", log)
            self.assertIn("[FALLBACK] grill-me", log)

    def test_missing_required_command_returns_nonzero(self) -> None:
        with tempfile.TemporaryDirectory(prefix="charter-deps-") as raw:
            directory = Path(raw)
            config = self.write_config(
                directory,
                {
                    "commands": [
                        {
                            "id": "required-tool",
                            "command": "definitely-not-installed-charter-kit",
                            "required": True,
                            "impact": "the required check cannot run",
                            "fallback": "stop and request installation",
                        }
                    ]
                },
            )

            result = self.run_checker(directory, "--config", config)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("[MISSING] required-tool", result.stdout)
            self.assertIn("impact: the required check cannot run", result.stdout)
            self.assertIn("[FALLBACK] required-tool", result.stdout)
            self.assertIn("action:", result.stdout)

    def test_optional_switch_cannot_downgrade_required_manifest_capability(self) -> None:
        with tempfile.TemporaryDirectory(prefix="charter-deps-") as raw:
            directory = Path(raw)
            config = self.write_config(
                directory,
                {
                    "commands": [
                        {
                            "id": "required-tool",
                            "command": "definitely-not-installed-charter-kit",
                            "required": True,
                            "impact": "required capability is unavailable",
                            "fallback": "stop for an explicit waiver",
                        }
                    ]
                },
            )

            result = self.run_checker(
                directory,
                "--config",
                config,
                "--optional",
                "required-tool",
            )

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("[MISSING] required-tool (required, command)", result.stdout)

    def test_empty_provider_directory_is_not_reported_available(self) -> None:
        with tempfile.TemporaryDirectory(prefix="charter-deps-") as raw:
            directory = Path(raw)
            empty_provider = directory / "empty-provider"
            empty_provider.mkdir()

            result = self.run_checker(
                directory,
                "--provider-dir",
                f"empty-provider={empty_provider}",
                "--optional",
                "empty-provider",
                "--json",
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            records = json.loads(result.stdout)
            primary = next(
                record
                for record in records
                if record["id"] == "empty-provider" and record["status"] != "FALLBACK"
            )
            self.assertNotEqual(primary["status"], "AVAILABLE")
            self.assertIn("reason", primary)

    def test_json_records_include_reason_alongside_message(self) -> None:
        with tempfile.TemporaryDirectory(prefix="charter-deps-") as raw:
            directory = Path(raw)
            result = self.run_checker(directory, "--optional", "missing-optional", "--json")

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            records = json.loads(result.stdout)
            for record in records:
                self.assertIn("reason", record)
                self.assertEqual(record["reason"], record["message"])

    def test_unverified_environment_provider_is_explicit(self) -> None:
        with tempfile.TemporaryDirectory(prefix="charter-deps-") as raw:
            directory = Path(raw)
            config = self.write_config(
                directory,
                {
                    "providers": [
                        {
                            "id": "custom-provider",
                            "paths": ["{env:CHARTER_KIT_TEST_ENV_NOT_SET}"],
                            "required": False,
                            "impact": "provider location could not be determined",
                            "fallback": "portable provider contract",
                        }
                    ]
                },
            )

            result = self.run_checker(directory, "--config", config)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("[UNVERIFIED] custom-provider", result.stdout)
            self.assertIn("[FALLBACK] custom-provider", result.stdout)

    def test_environment_token_can_appear_inside_a_path(self) -> None:
        with tempfile.TemporaryDirectory(prefix="charter-deps-") as raw:
            directory = Path(raw)
            provider = directory / "from-env"
            provider.mkdir()
            (provider / "SKILL.md").write_text("# provider", encoding="utf-8")
            config = self.write_config(
                directory,
                {
                    "providers": [
                        {
                            "id": "env-provider",
                            "paths": ["{env:CHARTER_KIT_TEST_PROVIDER_ROOT}/from-env"],
                            "required": True,
                            "impact": "provider is needed",
                            "fallback": "stop for waiver",
                        }
                    ]
                },
            )
            environment = os.environ.copy()
            environment["CHARTER_KIT_TEST_PROVIDER_ROOT"] = str(directory)
            result = subprocess.run(
                [sys.executable, str(SCRIPT), directory, "--config", config],
                cwd=PACKAGE_ROOT,
                text=True,
                capture_output=True,
                check=False,
                env=environment,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("[AVAILABLE] env-provider", result.stdout)

    def test_provider_directory_can_be_supplied_on_command_line(self) -> None:
        with tempfile.TemporaryDirectory(prefix="charter-deps-") as raw:
            directory = Path(raw)
            provider_dir = directory / "skills" / "custom-provider"
            provider_dir.mkdir(parents=True)
            (provider_dir / "SKILL.md").write_text("# provider", encoding="utf-8")

            result = self.run_checker(
                directory,
                "--provider-dir",
                f"custom-provider={provider_dir}",
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("[AVAILABLE] custom-provider", result.stdout)

    def test_secret_like_values_are_redacted_from_output_and_log(self) -> None:
        with tempfile.TemporaryDirectory(prefix="charter-deps-") as raw:
            directory = Path(raw)
            config = self.write_config(
                directory,
                {
                    "providers": [
                        {
                            "id": "safe-provider",
                            "paths": ["https://user:super-secret@example.invalid/provider"],
                            "required": False,
                            "impact": "token=super-secret must not be logged",
                            "fallback": "offline fallback",
                        }
                    ]
                },
            )
            log_file = directory / "dependency.log"

            result = self.run_checker(directory, "--config", config, "--log-file", log_file)

            self.assertTrue(log_file.is_file(), result.stdout + result.stderr)
            combined = result.stdout + log_file.read_text(encoding="utf-8")
            self.assertNotIn("super-secret", combined)
            self.assertIn("[UNVERIFIED] safe-provider", result.stdout)

    def test_json_output_contains_status_and_fallback_records(self) -> None:
        with tempfile.TemporaryDirectory(prefix="charter-deps-") as raw:
            directory = Path(raw)
            config = self.write_config(
                directory,
                {
                    "providers": [
                        {
                            "id": "missing-provider",
                            "paths": [str(directory / "missing")],
                            "required": False,
                            "impact": "provider unavailable",
                            "fallback": "portable fallback",
                        }
                    ]
                },
            )

            result = self.run_checker(directory, "--config", config, "--json")

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            records = json.loads(result.stdout)
            statuses = {(record["id"], record["status"]) for record in records}
            self.assertIn(("missing-provider", "MISSING"), statuses)
            self.assertIn(("missing-provider", "FALLBACK"), statuses)

    def test_relative_config_can_be_resolved_from_project_directory(self) -> None:
        with tempfile.TemporaryDirectory(prefix="charter-deps-") as raw:
            directory = Path(raw)
            config_dir = directory / ".charter"
            config_dir.mkdir()
            config = self.write_config(
                config_dir,
                {
                    "capabilities": [
                        {
                            "id": "project-capability",
                            "required": False,
                            "impact": "project-specific capability is not locally probeable",
                            "fallback": "manual confirmation",
                        }
                    ]
                },
            )

            result = self.run_checker(
                "--project",
                directory,
                "--config",
                ".charter/dependencies.json",
                "--json",
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            records = json.loads(result.stdout)
            self.assertIn(
                "project-capability",
                {record["id"] for record in records},
            )

    def test_project_manifest_is_auto_discovered_and_merged_with_package_defaults(self) -> None:
        with tempfile.TemporaryDirectory(prefix="charter-deps-") as raw:
            directory = Path(raw)
            config_dir = directory / ".charter"
            config_dir.mkdir()
            (config_dir / "dependencies.json").write_text(
                json.dumps(
                    {
                        "capabilities": [
                            {
                                "id": "project-required-tool",
                                "required": True,
                                "impact": "project tool is required",
                                "fallback": "stop for an explicit waiver",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            result = self.run_checker(directory, "--json")

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            records = json.loads(result.stdout)
            ids = {record["id"] for record in records}
            self.assertIn("python", ids)
            project_record = next(
                record
                for record in records
                if record["id"] == "project-required-tool" and record["status"] != "FALLBACK"
            )
            self.assertTrue(project_record["required"])
            self.assertEqual(project_record["status"], "UNVERIFIED")

    def test_capability_manifest_accepts_singular_path_for_a_provider(self) -> None:
        with tempfile.TemporaryDirectory(prefix="charter-deps-") as raw:
            directory = Path(raw)
            provider = directory / "provider"
            provider.mkdir()
            (provider / "SKILL.md").write_text("# provider", encoding="utf-8")
            config = self.write_config(
                directory,
                {
                    "capabilities": [
                        {
                            "id": "single-path-provider",
                            "kind": "provider",
                            "path": str(provider),
                            "required": True,
                            "impact": "provider is required",
                            "fallback": "stop for an explicit waiver",
                        }
                    ]
                },
            )

            result = self.run_checker(directory, "--config", config)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("[AVAILABLE] single-path-provider", result.stdout)

    def test_current_interpreter_satisfies_python_when_alias_is_not_on_path(self) -> None:
        with tempfile.TemporaryDirectory(prefix="charter-deps-") as raw:
            directory = Path(raw)
            config = self.write_config(
                directory,
                {
                    "commands": [
                        {
                            "id": "python",
                            "command": "python-alias-that-is-not-installed",
                            "required": True,
                            "impact": "core checker unavailable",
                            "fallback": "manual check",
                        }
                    ]
                },
            )

            result = self.run_checker(directory, "--config", config)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("[AVAILABLE] python", result.stdout)

    def test_bearer_and_query_secrets_are_redacted(self) -> None:
        with tempfile.TemporaryDirectory(prefix="charter-deps-") as raw:
            directory = Path(raw)
            config = self.write_config(
                directory,
                {
                    "capabilities": [
                        {
                            "id": "safe-provider",
                            "required": False,
                            "impact": "Authorization: Bearer top-secret-token",
                            "fallback": "https://example.invalid/?api_key=top-secret-token",
                        }
                    ]
                },
            )
            log_file = directory / "dependency.log"

            result = self.run_checker(directory, "--config", config, "--log-file", log_file)

            combined = result.stdout + log_file.read_text(encoding="utf-8")
            self.assertNotIn("top-secret-token", combined)
            self.assertIn("[UNVERIFIED] safe-provider", result.stdout)

    def test_log_parent_symlink_is_rejected_without_writing_outside(self) -> None:
        with tempfile.TemporaryDirectory(prefix="charter-deps-") as raw:
            directory = Path(raw)
            outside = directory / "outside"
            outside.mkdir()
            linked_parent = directory / "linked-evidence"
            try:
                linked_parent.symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symlink creation unavailable: {exc}")

            result = self.run_checker(
                directory,
                "--optional",
                "missing-optional",
                "--log-file",
                linked_parent / "dependency.log",
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((outside / "dependency.log").exists())
            self.assertIn("unable to write log", result.stderr.lower())

    def test_invalid_config_is_logged_with_impact_fallback_and_action(self) -> None:
        with tempfile.TemporaryDirectory(prefix="charter-deps-") as raw:
            directory = Path(raw)
            config = directory / "broken.json"
            config.write_text("{not-json", encoding="utf-8")
            log_file = directory / "dependency.log"

            result = self.run_checker(directory, "--config", config, "--log-file", log_file)

            self.assertNotEqual(result.returncode, 0)
            combined = result.stdout + log_file.read_text(encoding="utf-8")
            self.assertIn("impact:", combined.lower())
            self.assertIn("fallback:", combined.lower())
            self.assertIn("action:", combined.lower())


if __name__ == "__main__":
    unittest.main()
