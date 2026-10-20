from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]


class ScratchHygieneTests(unittest.TestCase):
    """The scratch rule has to be enforced where it is declared, not in prose."""

    def make_repository(self) -> Path:
        temporary = tempfile.TemporaryDirectory(prefix="charter-kit-scratch-")
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name) / "project"
        root.mkdir()
        self.git(root, "init", "-q")
        self.git(root, "config", "user.email", "kit@example.invalid")
        self.git(root, "config", "user.name", "Charter Kit")
        (root / ".gitignore").write_text(".scratch/\n", encoding="utf-8")
        (root / "README.md").write_text("deliverable\n", encoding="utf-8")
        self.git(root, "add", "-A")
        self.git(root, "commit", "-q", "-m", "baseline")
        return root

    def git(self, root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(root), *arguments],
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )

    def run_checker(self, root: Path, *arguments: object) -> subprocess.CompletedProcess[str]:
        environment = {**os.environ, "PYTHONIOENCODING": "utf-8"}
        return subprocess.run(
            [sys.executable, str(PACKAGE_ROOT / "scripts" / "check_scratch.py"), str(root), *(str(a) for a in arguments)],
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
            env=environment,
        )

    def test_a_clean_tree_passes(self):
        root = self.make_repository()
        result = self.run_checker(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("RESULT PASS", result.stdout)

    def test_junk_nothing_ignores_is_reported_before_it_is_committed(self):
        root = self.make_repository()
        (root / "session.log").write_text("captured output\n", encoding="utf-8")
        result = self.run_checker(root)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("session.log", result.stdout)
        self.assertIn("nothing ignores it", result.stdout)

    def test_junk_version_control_already_excludes_is_counted_not_reported(self):
        root = self.make_repository()
        gitignore = root / ".gitignore"
        gitignore.write_text(".scratch/\n*.log\n", encoding="utf-8")
        (root / "coverage-run.log").write_text("noise\n", encoding="utf-8")
        result = self.run_checker(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("excluded=1", result.stdout)

    def test_committed_junk_is_reported_whatever_the_ignore_rule_says(self):
        root = self.make_repository()
        gitignore = root / ".gitignore"
        gitignore.write_text(".scratch/\n*.pyc\n", encoding="utf-8")
        (root / "stale.pyc").write_bytes(b"bytecode")
        self.git(root, "add", "-f", "stale.pyc")
        self.git(root, "commit", "-q", "-m", "committed by accident")
        result = self.run_checker(root)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("already committed", result.stdout)

    def test_a_tracked_file_inside_the_scratch_root_is_reported(self):
        root = self.make_repository()
        (root / ".scratch").mkdir()
        (root / ".scratch" / "probe.py").write_text("# probe\n", encoding="utf-8")
        self.git(root, "add", "-f", ".scratch/probe.py")
        self.git(root, "commit", "-q", "-m", "scratch leaked into history")
        result = self.run_checker(root)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("tracked file inside the scratch root", result.stdout)

    def test_a_scratch_root_version_control_does_not_exclude_is_reported(self):
        root = self.make_repository()
        (root / ".gitignore").write_text("# nothing here yet\n", encoding="utf-8")
        self.git(root, "add", "-A")
        self.git(root, "commit", "-q", "-m", "drop the rule")
        result = self.run_checker(root)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("the scratch root is not ignored", result.stdout)

    def test_the_contract_can_name_a_different_scratch_root(self):
        root = self.make_repository()
        charter = root / ".charter"
        charter.mkdir()
        (charter / "current-task.md").write_text(
            "- Scratch root: `_work` - the one place this leaf may write anything that is not a deliverable.\n",
            encoding="utf-8",
        )
        (root / "_work").mkdir()
        (root / "_work" / "probe.pyc").write_bytes(b"bytecode")
        result = self.run_checker(root)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("SCRATCH _work", result.stdout)
        self.assertNotIn("probe.pyc", result.stdout)
        self.assertIn("_work/", result.stdout)

    def test_init_creates_the_scratch_root(self):
        root = self.make_repository()
        result = self.run_checker(root, "--init")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((root / ".scratch").is_dir())

    def test_init_project_ignores_the_scratch_root_and_creates_it(self):
        root = self.make_repository()
        (root / ".gitignore").unlink()
        completed = subprocess.run(
            [sys.executable, str(PACKAGE_ROOT / "scripts" / "init_project.py"), str(root)],
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        gitignore = (root / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(".scratch/", gitignore)
        self.assertIn(".jspace/", gitignore)
        self.assertTrue((root / ".scratch").is_dir())
        self.assertEqual(gitignore.count(".scratch/"), 1)

        again = subprocess.run(
            [sys.executable, str(PACKAGE_ROOT / "scripts" / "init_project.py"), str(root), "--add-missing"],
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        self.assertEqual(again.returncode, 0, again.stdout + again.stderr)
        self.assertIn("UNCHANGED - .scratch/ is already ignored", again.stdout)
        self.assertEqual((root / ".gitignore").read_text(encoding="utf-8").count(".scratch/"), 1)

    def test_the_kit_itself_is_clean(self):
        result = self.run_checker(PACKAGE_ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class ScratchRuleDeclarationTests(unittest.TestCase):
    """Every hand-maintained tree states the rule, and the migration list keeps up."""

    TEMPLATE_TREES = (
        Path("portable/templates/leaf-task.md"),
        Path("targets/codex/skills/charter-workflow/templates/leaf-task.md"),
        Path("targets/zcode/skills/charter-workflow/templates/leaf-task.md"),
    )
    MIGRATION_TREES = (
        Path("portable/references/contract-migrations.md"),
        Path("targets/codex/skills/charter-workflow/references/contract-migrations.md"),
        Path("targets/zcode/skills/charter-workflow/references/contract-migrations.md"),
    )

    def read(self, relative: Path) -> str:
        return (PACKAGE_ROOT / relative).read_text(encoding="utf-8")

    def test_every_leaf_template_declares_a_scratch_root(self):
        for relative in self.TEMPLATE_TREES:
            with self.subTest(template=str(relative)):
                text = self.read(relative)
                self.assertIn("### Scratch root", text)
                self.assertRegex(text, r"- Scratch root: `\.scratch`")
                self.assertIn("CLS11", text)
                self.assertIn("check_scratch.py", text)
                self.assertIn("- Contract version: `0.5`", text)

    def test_every_leaf_template_states_the_order_of_evidence_cleanup_and_closure(self):
        for relative in self.TEMPLATE_TREES:
            with self.subTest(template=str(relative)):
                text = self.read(relative)
                self.assertIn("evidence is written first, then the root is emptied, then closure is signed", text)
                self.assertIn("Three lifetimes are decided when an artifact is produced", text)
                self.assertIn("Load-bearing output", text)
                self.assertIn("Answered after the evidence the other rows cite is written", text)

    def test_every_migration_table_covers_the_scratch_row(self):
        for relative in self.MIGRATION_TREES:
            with self.subTest(table=str(relative)):
                text = self.read(relative)
                self.assertIn("`CLS1`-`CLS11`", text)
                self.assertIn("Scratch root", text)
                self.assertNotIn("`CLS1`-`CLS10`", text)


if __name__ == "__main__":
    unittest.main()
