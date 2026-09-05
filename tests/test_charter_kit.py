from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
# Generated trees carry this marker; hand-edited trees must not.  Fixtures
# that copy one kind of tree into the other have to say which side they are
# building, or the validator reports the fixture instead of the test.
GENERATED_MARKER_NAME = "GENERATED.md"
# Mirrors LEAF_CONTRACT_CEILING_KB in scripts/validate_kit.py.  Duplicated on
# purpose: a test that read the constant out of the validator would pass no
# matter what number the shipped documents state.
LEAF_CONTRACT_CEILING_KB = 36


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
        # The source of that copy is a generated tree and carries the marker
        # saying so; the destination is hand-edited and must not, or the marker
        # would tell a maintainer to edit the tree they are already editing.
        (target_skill / GENERATED_MARKER_NAME).unlink(missing_ok=True)

        distribution = package / "plugins" / "charter-kit"
        # Recreating the package root drops the builder-written marker the
        # validator requires there, so carry it across the rebuild.
        distribution_marker = distribution / GENERATED_MARKER_NAME
        marker_bytes = distribution_marker.read_bytes() if distribution_marker.is_file() else None
        if distribution.exists():
            shutil.rmtree(distribution)
        distribution_manifest = distribution / ".codex-plugin" / "plugin.json"
        distribution_manifest.parent.mkdir(parents=True, exist_ok=True)
        distribution_manifest.write_bytes(target_manifest.read_bytes())
        shutil.copytree(target_skill, distribution / "skills" / "charter-workflow")
        if marker_bytes is not None:
            distribution_marker.write_bytes(marker_bytes)

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
        (target_skill / GENERATED_MARKER_NAME).unlink(missing_ok=True)
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

    def test_init_ignores_the_session_ledger_once_without_rewriting_user_lines(self) -> None:
        """The ledger stays untracked by repository rule, not by discipline.

        A sentence in a template does not stop `git add -A`, so the initializer
        appends one entry. It must be append-only and idempotent: a rewritten
        user `.gitignore` would be a worse defect than the habit it replaces.
        """
        package = self.make_package_copy()
        project = package.parent / "ledger-project"
        project.mkdir()
        (project / ".git").mkdir()
        (project / ".gitignore").write_text("node_modules\n", encoding="utf-8")
        init_script = package / "scripts" / "init_project.py"

        first = self.run_script(init_script, project)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        ignore_text = (project / ".gitignore").read_text(encoding="utf-8")
        self.assertTrue(ignore_text.startswith("node_modules\n"), ignore_text)
        self.assertIn(".jspace/", ignore_text)
        self.assertIn("ADDED", first.stdout)

        second = self.run_script(init_script, project, "--add-missing")
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        repeated = (project / ".gitignore").read_text(encoding="utf-8")
        self.assertEqual(repeated.count(".jspace/"), 1, repeated)
        self.assertIn("UNCHANGED", second.stdout)

    def test_init_preserves_an_explicit_decision_to_track_the_ledger(self) -> None:
        """A negation is a user decision; convenience must not overrule it."""
        package = self.make_package_copy()
        project = package.parent / "tracked-ledger-project"
        project.mkdir()
        (project / ".git").mkdir()
        original = "!.jspace\n"
        (project / ".gitignore").write_text(original, encoding="utf-8")

        result = self.run_script(package / "scripts" / "init_project.py", project)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((project / ".gitignore").read_text(encoding="utf-8"), original)
        self.assertIn("UNCHANGED", result.stdout)

    def test_init_does_not_create_a_gitignore_outside_a_repository(self) -> None:
        """Without a repository there is nothing to keep out of version control."""
        package = self.make_package_copy()
        project = package.parent / "bare-project"

        result = self.run_script(package / "scripts" / "init_project.py", project)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse((project / ".gitignore").exists())
        self.assertIn("SKIPPED", result.stdout)
        self.assertTrue((project / ".charter" / "project.md").is_file())

    def test_initializer_output_stays_ascii_for_restricted_stdout_encodings(self) -> None:
        """A host with an ASCII stdout must not crash after files are created.

        The initializer writes the working set first and reports afterwards, so a
        non-encodable character in a status line would fail the run at the point
        where the user can least tell what happened.
        """
        package = self.make_package_copy()
        for relative in (
            Path("scripts") / "init_project.py",
            Path("skills") / "charter-workflow" / "scripts" / "init_project.py",
        ):
            text = (package / relative).read_text(encoding="utf-8")
            for number, line in enumerate(text.splitlines(), 1):
                if not re.match(r"\s*(print|handle\.write)\b", line):
                    continue
                offending = [character for character in line if ord(character) > 127]
                self.assertEqual(
                    offending,
                    [],
                    f"{relative}:{number} emits non-ASCII {offending!r}: {line.strip()}",
                )

    def test_validator_requires_initializer_ledger_ignore_rule(self) -> None:
        """Dropping the helper returns the ledger to relying on discipline."""
        package = self.make_package_copy()
        for relative in (
            Path("scripts") / "init_project.py",
            Path("skills") / "charter-workflow" / "scripts" / "init_project.py",
            Path("targets") / "codex" / "skills" / "charter-workflow" / "scripts" / "init_project.py",
            Path("targets") / "zcode" / "skills" / "charter-workflow" / "scripts" / "init_project.py",
        ):
            initializer = package / relative
            if not initializer.is_file():
                continue
            initializer.write_text(
                initializer.read_text(encoding="utf-8").replace(
                    "ensure_ledger_ignored", "skip_ledger_rule"
                ),
                encoding="utf-8",
            )

        result = self.run_validator(package)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("missing 'ensure_ledger_ignored'", result.stdout)

    def test_validator_rejects_python_declared_as_a_required_capability(self) -> None:
        """Requiring an interpreter blocks a host that can run the kit by hand.

        The governance core is Markdown and the manual initialization path
        produces the same working set, so a missing interpreter is an optional
        miss with a documented fallback, never BLOCKED_TOOLING.  All four copies
        are flipped so the failure is the requiredness rule and not mirror drift.
        """
        package = self.make_package_copy()
        for relative in (
            Path("dependencies.json"),
            Path("skills") / "charter-workflow" / "dependencies.json",
            Path("targets") / "codex" / "skills" / "charter-workflow" / "dependencies.json",
            Path("targets") / "zcode" / "skills" / "charter-workflow" / "dependencies.json",
        ):
            manifest = package / relative
            if not manifest.is_file():
                continue
            lines = manifest.read_text(encoding="utf-8").splitlines(keepends=True)
            for number, line in enumerate(lines):
                if '"command": "python"' in line:
                    lines[number + 1] = lines[number + 1].replace("false", "true")
                    break
            else:
                self.fail(f"{relative}: python entry not found")
            manifest.write_text("".join(lines), encoding="utf-8", newline="")

        result = self.run_validator(package)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("dependencies.json: python must remain optional", result.stdout)

    def test_validator_requires_the_manual_ledger_ignore_instruction(self) -> None:
        """Without the initializer, only this sentence keeps the ledger untracked.

        Python is optional, so the Skill must tell a host taking the manual path
        to add the .jspace/ entry itself; dropping the sentence leaves the rule
        to discipline on exactly the hosts that cannot run the helper.
        """
        package = self.make_package_copy()
        for relative in (
            Path("skills") / "charter-workflow" / "SKILL.md",
            Path("targets") / "codex" / "skills" / "charter-workflow" / "SKILL.md",
            Path("targets") / "zcode" / "skills" / "charter-workflow" / "SKILL.md",
        ):
            skill = package / relative
            if not skill.is_file():
                continue
            original = skill.read_text(encoding="utf-8")
            patched = original.replace(
                " Python is optional, so on the manual path add that "
                "`.jspace/` entry to `.gitignore` by hand: nothing else "
                "keeps the session ledger out of version control.",
                "",
            )
            self.assertNotEqual(original, patched, f"{relative}: manual path sentence not found")
            skill.write_text(patched, encoding="utf-8")

        result = self.run_validator(package)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("missing 'Python is optional'", result.stdout)
        self.assertIn(
            "missing 'on the manual path add that `.jspace/` entry to "
            "`.gitignore` by hand'",
            result.stdout,
        )

    def test_validator_names_the_hand_edited_source_for_generated_trees(self) -> None:
        """A mismatch must point at the tree an edit survives in.

        The root skill tree is the Codex builder's writeback destination, so
        several comparisons cite it as the reference side.  Without the hint the
        message reads as if that tree were authoritative, and an edit made there
        is deleted by the next build instead of being reported.
        """
        package = self.make_package_copy()
        skill = package / "skills" / "charter-workflow" / "SKILL.md"
        skill.write_text(
            skill.read_text(encoding="utf-8") + "<!-- local drift -->" + chr(10),
            encoding="utf-8",
            newline="",
        )

        result = self.run_validator(package)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(
            "hand-edit targets/codex/skills/charter-workflow",
            result.stdout,
        )
        self.assertIn(
            "hand-edit targets/zcode/skills/charter-workflow",
            result.stdout,
        )

    def test_validator_requires_the_two_level_capability_recording_rule(self) -> None:
        """Every entry document must carry both halves of the recording rule.

        A project records a capability gap once, but each leaf that works around
        it has to say so in its own record.  The second half is the one that
        decays: after the leaf that first found the gap, later leaves have no new
        failed call to report, so their evidence reads as if the capability had
        been available.
        """
        package = self.make_package_copy()
        entries = [
            Path("skills") / "charter-workflow" / "SKILL.md",
            Path("targets") / "codex" / "skills" / "charter-workflow" / "SKILL.md",
            Path("targets") / "zcode" / "skills" / "charter-workflow" / "SKILL.md",
            Path("portable") / "commands" / "charter-workflow.md",
            Path("targets") / "zcode" / "commands" / "charter-workflow.md",
        ]
        entries.extend(
            Path("portable") / "prompts" / f"{host}-bootstrap.md"
            for host in ("claude", "codex", "deepseek", "gemini", "generic")
        )
        for relative in entries:
            document = package / relative
            if not document.is_file():
                continue
            original = document.read_text(encoding="utf-8")
            patched = original.replace(
                " `AVAILABLE`, `MISSING`, and `UNVERIFIED` are project-level facts: record each "
                "capability once here and update it when the state changes, instead of restating "
                "it in every leaf.",
                "",
            ).replace(
                "including when the gap was already known and no call failed in this session. ",
                "",
            )
            self.assertNotEqual(original, patched, f"{relative}: recording rule not found")
            document.write_text(patched, encoding="utf-8", newline="")

        result = self.run_validator(package)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("missing 'are project-level facts'", result.stdout)
        self.assertIn(
            "missing 'including when the gap was already known and no call failed'",
            result.stdout,
        )

    def test_validator_requires_the_charter_two_level_recording_rule(self) -> None:
        """The charter is where the two levels are defined, not just applied.

        The entry documents state the rule in one clause each; a reader deciding
        whether a leaf needs its own FALLBACK entry is sent to the charter, so
        the discriminating case has to survive there too.
        """
        package = self.make_package_copy()
        for relative in (
            Path("DEVELOPMENT_CHARTER.md"),
            Path("skills") / "charter-workflow" / "references" / "DEVELOPMENT_CHARTER.md",
            Path("targets") / "codex" / "skills" / "charter-workflow" / "references" / "DEVELOPMENT_CHARTER.md",
            Path("targets") / "zcode" / "skills" / "charter-workflow" / "references" / "DEVELOPMENT_CHARTER.md",
        ):
            charter = package / relative
            if not charter.is_file():
                continue
            original = charter.read_text(encoding="utf-8")
            patched = original.replace("是项目级事实", "").replace(
                "本叶没有任何新的失败调用", ""
            )
            self.assertNotEqual(original, patched, f"{relative}: charter recording rule not found")
            charter.write_text(patched, encoding="utf-8", newline="")

        result = self.run_validator(package)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("missing '是项目级事实'", result.stdout)
        self.assertIn("missing '本叶没有任何新的失败调用'", result.stdout)

    # ------------------------------------------------------------------
    # Contract migrations
    # ------------------------------------------------------------------
    CONTRACT_MIGRATIONS_COPIES = (
        "portable/references/contract-migrations.md",
        "skills/charter-workflow/references/contract-migrations.md",
        "targets/codex/skills/charter-workflow/references/contract-migrations.md",
        "targets/zcode/skills/charter-workflow/references/contract-migrations.md",
        "plugins/charter-kit/portable/references/contract-migrations.md",
        "plugins/charter-kit/skills/charter-workflow/references/contract-migrations.md",
        "plugins/dsh-charter-kit/portable/references/contract-migrations.md",
        "plugins/dsh-charter-kit/skills/charter-workflow/references/contract-migrations.md",
        "plugins/zcode-charter-kit/portable/references/contract-migrations.md",
        "plugins/zcode-charter-kit/skills/charter-workflow/references/contract-migrations.md",
    )

    def test_contract_migration_steps_live_in_one_reference(self) -> None:
        reference = (PACKAGE_ROOT / "portable" / "references" / "contract-migrations.md").read_text(
            encoding="utf-8"
        )
        for phrase in (
            "Long-task ledger",
            "Ledger reconciliation",
            "## 8. Execution record",
            "## 9. Review and closure",
            "Contract version",
            "CLARIFICATION",
            "before the first state transition",
            "not migrated",
            "bounded waiver",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, reference)

        expected = (PACKAGE_ROOT / self.CONTRACT_MIGRATIONS_COPIES[0]).read_bytes()
        for relative in self.CONTRACT_MIGRATIONS_COPIES[1:]:
            with self.subTest(relative=relative):
                self.assertEqual((PACKAGE_ROOT / relative).read_bytes(), expected)

    def test_the_entry_document_points_at_the_migration_reference_instead_of_repeating_it(self) -> None:
        """The one-time procedure must not be charged to every session start."""

        skill = (PACKAGE_ROOT / "skills" / "charter-workflow" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/contract-migrations.md", skill)
        self.assertIn("before any state transition", skill)
        self.assertNotIn("Long-task ledger", skill)

        leaf = (PACKAGE_ROOT / "portable" / "templates" / "leaf-task.md").read_text(encoding="utf-8")
        self.assertIn("portable/references/contract-migrations.md", leaf)
        self.assertIn("before the next state transition", leaf)

    def test_validator_rejects_migration_detail_returning_to_the_entry_document(self) -> None:
        package = self.make_package_copy()
        skill = package / "skills" / "charter-workflow" / "SKILL.md"
        body = skill.read_text(encoding="utf-8")
        skill.write_text(
            body.replace(
                "`references/contract-migrations.md` lists each field",
                "add the `Long-task ledger` line to section 8; "
                "`references/contract-migrations.md` lists each field",
            ),
            encoding="utf-8",
        )

        result = self.run_validator(package)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("not the entry document", result.stdout)

    def test_validator_rejects_a_missing_contract_migrations_reference(self) -> None:
        package = self.make_package_copy()
        (package / "portable" / "references" / "contract-migrations.md").unlink()

        result = self.run_validator(package)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("portable/references/contract-migrations.md", result.stdout)

    def test_validator_rejects_a_migration_reference_that_drops_a_field(self) -> None:
        package = self.make_package_copy()
        for relative in self.CONTRACT_MIGRATIONS_COPIES:
            reference = package / relative
            reference.write_text(
                reference.read_text(encoding="utf-8").replace("Ledger reconciliation", "closure note"),
                encoding="utf-8",
            )

        result = self.run_validator(package)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Ledger reconciliation", result.stdout)

    # ------------------------------------------------------------------
    # Generated-tree markers
    # ------------------------------------------------------------------
    GENERATED_TREES = (
        ("plugins/charter-kit", "targets/codex/skills/charter-workflow", "scripts/build_codex_plugin.py"),
        ("skills/charter-workflow", "targets/codex/skills/charter-workflow", "scripts/build_codex_plugin.py"),
        ("plugins/zcode-charter-kit", "targets/zcode", "scripts/build_zcode_plugin.py"),
        ("plugins/dsh-charter-kit", "targets/dsh", "scripts/build_dsh_plugin.py"),
    )

    def test_every_generated_tree_carries_a_marker_naming_its_hand_edited_source(self) -> None:
        for tree, source, command in self.GENERATED_TREES:
            with self.subTest(tree=tree):
                marker = PACKAGE_ROOT / tree / GENERATED_MARKER_NAME
                self.assertTrue(marker.is_file(), f"{tree} has no {GENERATED_MARKER_NAME}")
                body = marker.read_text(encoding="utf-8")
                self.assertIn("do not hand-edit", body)
                self.assertIn(source, body)
                self.assertIn(command, body)
                self.assertIn("docs/MIRROR-TOPOLOGY.md", body)
                # A build time here would make every rebuild a byte change, so
                # --check would stop distinguishing drift from noise.
                self.assertIsNone(re.search(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", body))

    def test_hand_edited_trees_carry_no_generated_marker(self) -> None:
        # A marker in a hand-edited tree would send a maintainer away from the
        # one tree their edit actually survives in.
        for tree in (
            "portable",
            "targets/codex/skills/charter-workflow",
            "targets/zcode",
            "targets/dsh",
            # Copied from a tree that has a marker; the copy step drops it
            # because the content names one destination.
            "plugins/charter-kit/skills/charter-workflow",
            "plugins/dsh-charter-kit/skills/charter-workflow",
            "plugins/zcode-charter-kit/skills/charter-workflow",
        ):
            with self.subTest(tree=tree):
                self.assertFalse((PACKAGE_ROOT / tree / GENERATED_MARKER_NAME).exists())

    def test_validator_rejects_a_generated_tree_without_its_marker(self) -> None:
        package = self.make_package_copy()
        (package / "plugins" / "zcode-charter-kit" / GENERATED_MARKER_NAME).unlink()

        result = self.run_validator(package)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(f"plugins/zcode-charter-kit/{GENERATED_MARKER_NAME}", result.stdout)
        self.assertIn("build_zcode_plugin.py", result.stdout)

    def test_validator_rejects_a_generated_marker_in_a_hand_edited_tree(self) -> None:
        package = self.make_package_copy()
        (package / "targets" / "zcode" / GENERATED_MARKER_NAME).write_bytes(
            (package / "plugins" / "zcode-charter-kit" / GENERATED_MARKER_NAME).read_bytes()
        )

        result = self.run_validator(package)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(f"targets/zcode/{GENERATED_MARKER_NAME}", result.stdout)
        self.assertIn("hand-edited", result.stdout)

    def test_validator_rejects_a_marker_that_names_the_wrong_source(self) -> None:
        package = self.make_package_copy()
        marker = package / "skills" / "charter-workflow" / GENERATED_MARKER_NAME
        body = marker.read_text(encoding="utf-8")
        marker.write_text(
            body.replace("targets/codex/skills/charter-workflow", "portable/templates"),
            encoding="utf-8",
        )

        result = self.run_validator(package)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("targets/codex/skills/charter-workflow", result.stdout)

    def test_validator_rejects_a_marker_that_records_a_build_time(self) -> None:
        package = self.make_package_copy()
        marker = package / "plugins" / "charter-kit" / GENERATED_MARKER_NAME
        body = marker.read_text(encoding="utf-8")
        marker.write_text(
            body.replace("edit survives in.", "edit survives in. Built 2026-09-05."),
            encoding="utf-8",
        )

        result = self.run_validator(package)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("timestamp-free", result.stdout)

    def test_validator_rejects_markers_pointing_at_a_missing_topology_map(self) -> None:
        package = self.make_package_copy()
        (package / "docs" / "MIRROR-TOPOLOGY.md").unlink()

        result = self.run_validator(package)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("docs/MIRROR-TOPOLOGY.md", result.stdout)

    def test_builders_rewrite_every_deleted_marker(self) -> None:
        """The markers are build output, not a committed convention.

        A marker that had to be committed by hand would be deleted by the next
        build of its own tree, which is the exact failure it exists to warn
        about.
        """

        package = self.make_package_copy()
        for tree, _source, _command in self.GENERATED_TREES:
            (package / tree / GENERATED_MARKER_NAME).unlink()

        for builder in (
            "build_codex_plugin.py",
            "build_zcode_plugin.py",
            "build_dsh_plugin.py",
        ):
            result = self.run_script(package / "scripts" / builder)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        for tree, _source, _command in self.GENERATED_TREES:
            with self.subTest(tree=tree):
                self.assertTrue((package / tree / GENERATED_MARKER_NAME).is_file())
        validated = self.run_validator(package)
        self.assertEqual(validated.returncode, 0, validated.stdout + validated.stderr)

    def test_the_writeback_marker_tells_the_truth_about_hand_edits(self) -> None:
        """Root skills/ really does discard edits, so the marker is not advice."""

        package = self.make_package_copy()
        sentinel = package / "skills" / "charter-workflow" / "HAND-EDIT.md"
        sentinel.write_text("edited by hand", encoding="utf-8")

        result = self.run_builder(package)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(sentinel.exists(), "the marker claims this edit is deleted")
        self.assertTrue(
            (package / "skills" / "charter-workflow" / GENERATED_MARKER_NAME).is_file()
        )

    # ------------------------------------------------------------------
    # Uniform --sync and full --check coverage
    # ------------------------------------------------------------------
    # Every (builder, destination) pair in the repository.  The Codex builder
    # owns three because it writes a distribution and then writes back two more
    # copies; what decides which trees --check compares and --sync repairs is
    # that ownership, not the number of builders.
    SYNC_DESTINATIONS = (
        ("build_codex_plugin.py", "plugins/charter-kit"),
        ("build_codex_plugin.py", "skills/charter-workflow"),
        ("build_codex_plugin.py", ".codex-plugin/plugin.json"),
        ("build_zcode_plugin.py", "plugins/zcode-charter-kit"),
        ("build_dsh_plugin.py", "plugins/dsh-charter-kit"),
    )

    def snapshot_generated_destinations(self, package: Path) -> dict[str, bytes]:
        """Snapshot every generated destination, keyed by declaring path."""

        snapshot: dict[str, bytes] = {}
        for _builder, relative in self.SYNC_DESTINATIONS:
            path = package / relative
            if path.is_dir():
                for name, payload in self.snapshot_tree_bytes(path).items():
                    snapshot[f"{relative}/{name}"] = payload
            else:
                snapshot[relative] = path.read_bytes()
        return snapshot

    def corrupt_destination(self, destination: Path) -> Path:
        """Make one destination differ from its source, the way a hand edit does.

        A JSON destination is rewritten as valid JSON so that the byte
        comparison is what fails, rather than a parse error on the way to it.
        """

        if destination.is_dir():
            for path in sorted(destination.rglob("*.md")):
                if path.name != GENERATED_MARKER_NAME:
                    path.write_text(
                        path.read_text(encoding="utf-8") + "\nHAND EDIT\n",
                        encoding="utf-8",
                    )
                    return path
            raise AssertionError(f"no markdown file under {destination}")
        payload = json.loads(destination.read_text(encoding="utf-8"))
        destination.write_text(json.dumps(payload, indent=4) + "\n", encoding="utf-8")
        return destination

    def test_sync_restores_every_destination_a_builder_declares(self) -> None:
        """--check names the drift and --sync repairs it, for all five pairs.

        The two writeback destinations used to have neither: a hand edit to root
        skills/ passed --check, and DSH then packaged the edited bytes.
        """

        for builder, relative in self.SYNC_DESTINATIONS:
            with self.subTest(builder=builder, destination=relative):
                package = self.make_package_copy()
                script = package / "scripts" / builder
                clean = self.snapshot_generated_destinations(package)
                sources = self.snapshot_tree_bytes(package / "targets")

                self.corrupt_destination(package / relative)
                checked = self.run_script(script, "--check")
                self.assertNotEqual(checked.returncode, 0, checked.stdout + checked.stderr)
                self.assertIn("differs from freshly generated bytes", checked.stderr)
                # The message has to name the side that drifted, not the first
                # destination the builder happens to compare.
                self.assertIn(str(Path(relative)), checked.stderr)

                synced = self.run_script(script, "--sync")
                self.assertEqual(synced.returncode, 0, synced.stdout + synced.stderr)
                rechecked = self.run_script(script, "--check")
                self.assertEqual(rechecked.returncode, 0, rechecked.stdout + rechecked.stderr)
                self.assertEqual(
                    self.snapshot_generated_destinations(package),
                    clean,
                    "--sync must restore the corrupted destination and leave the rest alone",
                )
                self.assertEqual(
                    self.snapshot_tree_bytes(package / "targets"),
                    sources,
                    "--sync repairs generated trees; it must not write a hand-edited source",
                )

    def test_sync_refuses_a_destination_a_builder_does_not_declare(self) -> None:
        """The allow-list is what keeps --sync from inventing a fourth copy."""

        package = self.make_package_copy()
        clean = self.snapshot_generated_destinations(package)
        for builder in (
            "build_codex_plugin.py",
            "build_zcode_plugin.py",
            "build_dsh_plugin.py",
        ):
            with self.subTest(builder=builder):
                outside = package.parent / f"not-generated-{builder}"
                result = self.run_script(
                    package / "scripts" / builder, "--sync", "--output", outside
                )
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("--sync refreshes only", result.stderr)
                self.assertFalse(outside.exists(), "a refused --sync must write nothing")
        self.assertEqual(self.snapshot_generated_destinations(package), clean)

    def test_sync_and_check_cannot_be_combined(self) -> None:
        """One asks whether the trees are fresh; the other answers by writing."""

        package = self.make_package_copy()
        for builder in (
            "build_codex_plugin.py",
            "build_zcode_plugin.py",
            "build_dsh_plugin.py",
        ):
            with self.subTest(builder=builder):
                result = self.run_script(package / "scripts" / builder, "--check", "--sync")
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("not allowed with", result.stderr)

    def test_validator_rejects_a_builder_without_sync(self) -> None:
        """A builder that can only report drift leaves the repair to memory.

        A fourth host entry will be added by copying one of these three, so the
        flag has to be part of what the validator considers a builder.
        """

        package = self.make_package_copy()
        script = package / "scripts" / "build_dsh_plugin.py"
        script.write_text(
            script.read_text(encoding="utf-8").replace("--sync", "--refresh"),
            encoding="utf-8",
        )

        result = self.run_validator(package)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("scripts/build_dsh_plugin.py: missing '--sync'", result.stdout)

    def test_validator_rejects_a_builder_that_stops_naming_a_destination_it_owns(self) -> None:
        """The declaration is what --check iterates and what --sync writes."""

        package = self.make_package_copy()
        script = package / "scripts" / "build_codex_plugin.py"
        script.write_text(
            script.read_text(encoding="utf-8").replace(
                '"skills/charter-workflow/"', '"skills/charter-workflow-unused/"'
            ),
            encoding="utf-8",
        )

        result = self.run_validator(package)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(
            'scripts/build_codex_plugin.py: missing \'"skills/charter-workflow/"\'',
            result.stdout,
        )

    def test_validator_requires_the_topology_map_to_document_sync(self) -> None:
        """The map is where a maintainer looks when --check turns red."""

        package = self.make_package_copy()
        topology = package / "docs" / "MIRROR-TOPOLOGY.md"
        topology.write_text(
            topology.read_text(encoding="utf-8").replace("--sync", "--refresh"),
            encoding="utf-8",
        )

        result = self.run_validator(package)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("docs/MIRROR-TOPOLOGY.md: missing '--sync'", result.stdout)

    def test_validator_requires_both_readme_languages_to_name_sync(self) -> None:
        """A repair documented in one language is missing for half the readers."""

        package = self.make_package_copy()
        for relative in (
            "README.md",
            "plugins/charter-kit/README.md",
            "plugins/zcode-charter-kit/README.md",
            "plugins/dsh-charter-kit/README.md",
        ):
            readme = package / relative
            readme.write_text(
                readme.read_text(encoding="utf-8").replace("--sync", "--refresh"),
                encoding="utf-8",
            )

        result = self.run_validator(package)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(
            "both the Chinese and the English maintainer section must name --sync",
            result.stdout,
        )

    def test_validator_rejects_a_zcode_command_that_drifts_from_its_source(self) -> None:
        """The shipped adapter command is a derivative, so drift is a defect.

        It is hand-maintained and was byte-identical to its own generated copy
        while several rules its source had gained were missing, so the only gate
        that can catch this compares it to the portable command it derives from.
        """
        package = self.make_package_copy()
        command = package / "targets" / "zcode" / "commands" / "charter-workflow.md"
        command.write_text(
            command.read_text(encoding="utf-8").replace(
                "- Version control and read-set size:", "- Housekeeping:"
            ),
            encoding="utf-8",
        )

        result = self.run_validator(package)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(
            "targets/zcode/commands/charter-workflow.md: must equal "
            "portable/commands/charter-workflow.md",
            result.stdout,
        )

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

    def test_validator_requires_dsh_target(self) -> None:
        package = self.make_package_copy()
        shutil.rmtree(package / "targets" / "dsh")
        shutil.rmtree(package / "plugins" / "dsh-charter-kit")

        result = self.run_validator(package)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

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

    def test_validator_rejects_duplicate_session_ledger_declaration(self) -> None:
        """A second declaration re-opens the ordering hole the rule closes.

        Presence checks pass while one copy still says "before the first state
        transition of the first leaf", which lets an executor declare the mode
        after the transition it is supposed to guard.
        """
        package = self.make_package_copy()
        prompt = package / "portable" / "prompts" / "generic-bootstrap.md"
        prompt.write_text(
            prompt.read_text(encoding="utf-8").replace(
                "## Resume mode",
                "**Session ledger declaration:** before the first state transition of the "
                "first leaf, declare the ledger mode.\n\n## Resume mode",
            ),
            encoding="utf-8",
        )

        result = self.run_validator(package)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(
            "generic-bootstrap.md: first-start section must declare the session ledger exactly once",
            result.stdout,
        )

    def test_validator_requires_ledger_declaration_before_first_transition(self) -> None:
        package = self.make_package_copy()
        prompt = package / "portable" / "prompts" / "generic-bootstrap.md"
        prompt.write_text(
            prompt.read_text(encoding="utf-8").replace(
                "Before moving `DRAFT` to `APPROVED` — the first state transition of this "
                "session — declare the session ledger mode",
                "After moving `DRAFT` to `APPROVED`, declare the session ledger mode",
            ),
            encoding="utf-8",
        )

        result = self.run_validator(package)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(
            "generic-bootstrap.md: session ledger declaration must precede DRAFT to APPROVED",
            result.stdout,
        )

    def test_validator_requires_bounded_handoff_packet(self) -> None:
        """The resume packet is re-read on every start, so its bound is a rule.

        Without it the packet accumulates one block per closed leaf and every
        later actor pays for finished work on every resume.
        """
        package = self.make_package_copy()
        for handoff in (
            package / "portable" / "templates" / "handoff.md",
            package / "skills" / "charter-workflow" / "templates" / "handoff.md",
        ):
            handoff.write_text(
                handoff.read_text(encoding="utf-8").replace("**Bounded size.**", "**Size.**"),
                encoding="utf-8",
            )

        result = self.run_validator(package)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(
            "portable/templates/handoff.md: missing '**Bounded size.**'",
            result.stdout,
        )

    def test_validator_requires_handoff_overflow_target(self) -> None:
        """A size bound with nowhere to put the overflow deletes history."""
        package = self.make_package_copy()
        for handoff in (
            package / "portable" / "templates" / "handoff.md",
            package / "skills" / "charter-workflow" / "templates" / "handoff.md",
        ):
            handoff.write_text(
                handoff.read_text(encoding="utf-8").replace(".charter/handoff-archive.md", "elsewhere"),
                encoding="utf-8",
            )

        result = self.run_validator(package)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(
            "portable/templates/handoff.md: missing '.charter/handoff-archive.md'",
            result.stdout,
        )

    def test_validator_requires_delta_rule_to_keep_its_limits(self) -> None:
        """Delta-writing without its limit becomes a way to hide a deviation.

        The headline permission is cheap to keep and useless alone: the gate has
        to hold the two sentences that forbid referencing away a narrowing,
        widening, or contradiction, and any leaf-specific field.
        """
        package = self.make_package_copy()
        for leaf in (
            package / "portable" / "templates" / "leaf-task.md",
            package / "skills" / "charter-workflow" / "templates" / "leaf-task.md",
        ):
            leaf.write_text(
                leaf.read_text(encoding="utf-8").replace(
                    "Anything that narrows, widens, or contradicts that baseline is written out here in full.",
                    "Use judgement.",
                ),
                encoding="utf-8",
            )

        result = self.run_validator(package)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("leaf-task.md: missing 'Anything that narrows", result.stdout)

    def test_validator_requires_version_control_rule_in_shared_entry_doc(self) -> None:
        """An untracked charter cannot be cited as authoritative history."""
        package = self.make_package_copy()
        skill = package / "skills" / "charter-workflow" / "SKILL.md"
        skill.write_text(
            skill.read_text(encoding="utf-8").replace(
                "- Version control and read-set size:", "- Housekeeping:"
            ),
            encoding="utf-8",
        )

        result = self.run_validator(package)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(
            "skills/charter-workflow/SKILL.md: missing 'Version control and read-set size'",
            result.stdout,
        )

    def test_every_shared_entry_document_carries_the_read_set_rules(self) -> None:
        """All seven entry documents, not just the one the gate names."""
        package = self.make_package_copy()
        entries = [
            package / "portable" / "prompts" / name
            for name in (
                "generic-bootstrap.md",
                "claude-bootstrap.md",
                "codex-bootstrap.md",
                "deepseek-bootstrap.md",
                "gemini-bootstrap.md",
            )
        ] + [
            package / "portable" / "commands" / "charter-workflow.md",
            package / "skills" / "charter-workflow" / "SKILL.md",
        ]
        for entry in entries:
            text = entry.read_text(encoding="utf-8")
            for phrase in (
                "Version control and read-set size",
                "cannot be cited as authoritative",
                "`.gitignore` entry",
                ".charter/handoff-archive.md",
                f"`.charter/current-task.md` under {LEAF_CONTRACT_CEILING_KB} KB",
            ):
                self.assertIn(phrase, text, f"{entry.name} is missing {phrase!r}")

    def test_every_leaf_contract_template_states_its_size_bound(self) -> None:
        """The bound has to travel in the template, in every copy of it.

        The file that outgrows the bound is a copy some project made months
        earlier, so a rule that lived only in the workflow document would never
        reach it.
        """

        for relative in (
            "portable/templates/leaf-task.md",
            "targets/codex/skills/charter-workflow/templates/leaf-task.md",
            "targets/zcode/skills/charter-workflow/templates/leaf-task.md",
            "skills/charter-workflow/templates/leaf-task.md",
        ):
            with self.subTest(template=relative):
                body = (PACKAGE_ROOT / relative).read_text(encoding="utf-8")
                self.assertIn("**Bounded size.**", body)
                self.assertIn(f"{LEAF_CONTRACT_CEILING_KB} KB", body)
                # A ceiling with no destination for the overflow is an
                # instruction to delete the contract instead of moving material.
                self.assertIn(".charter/evidence/", body)
                self.assertIn("Never buy the reduction by deleting", body)

    def test_validator_requires_the_leaf_contract_size_bound(self) -> None:
        """Every resume re-reads the contract, so the bound is a rule."""

        package = self.make_package_copy()
        for leaf in (
            package / "portable" / "templates" / "leaf-task.md",
            package / "skills" / "charter-workflow" / "templates" / "leaf-task.md",
        ):
            leaf.write_text(
                leaf.read_text(encoding="utf-8").replace("**Bounded size.**", "**Size.**"),
                encoding="utf-8",
            )

        result = self.run_validator(package)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("leaf-task.md: missing '**Bounded size.**'", result.stdout)

    def test_validator_rejects_a_template_that_outgrows_half_its_own_ceiling(self) -> None:
        """A template near the bound spends the project's budget before it starts.

        The ceiling is only useful while a real contract can hold the leaf's own
        material inside it, so the starting point is held to half.
        """

        package = self.make_package_copy()
        leaves = (
            package / "portable" / "templates" / "leaf-task.md",
            package / "skills" / "charter-workflow" / "templates" / "leaf-task.md",
        )
        padded = leaves[0].read_text(encoding="utf-8")
        while len(padded.encode("utf-8")) * 2 <= LEAF_CONTRACT_CEILING_KB * 1024:
            padded += "Absorbed prose whose source is already in the read set.\n"
        for leaf in leaves:
            leaf.write_text(padded, encoding="utf-8")

        result = self.run_validator(package)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("portable/templates/leaf-task.md: the template is", result.stdout)
        self.assertIn(f"more than half the {LEAF_CONTRACT_CEILING_KB} KB ceiling", result.stdout)

    def test_validator_requires_the_contract_bound_in_shared_entry_doc(self) -> None:
        """The template states the bound; the workflow says what to do about it."""

        package = self.make_package_copy()
        skill = package / "skills" / "charter-workflow" / "SKILL.md"
        skill.write_text(
            skill.read_text(encoding="utf-8").replace(
                f"and keep `.charter/current-task.md` under {LEAF_CONTRACT_CEILING_KB} KB",
                "and keep the leaf contract short",
            ),
            encoding="utf-8",
        )

        result = self.run_validator(package)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(
            "skills/charter-workflow/SKILL.md: missing '`.charter/current-task.md` under "
            f"{LEAF_CONTRACT_CEILING_KB} KB'",
            result.stdout,
        )

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
        legacy = self.snapshot_tree_bytes(package / "skills" / "charter-workflow")
        built = self.snapshot_tree_bytes(output / "skills" / "charter-workflow")
        # The writeback destination is a generated tree living at a canonical
        # path, so it carries its own marker.  That marker names this tree and
        # this destination, which is exactly why it is not part of the mirror:
        # comparing it would demand that two destinations describe themselves
        # identically.
        self.assertIn(GENERATED_MARKER_NAME, legacy)
        self.assertNotIn(GENERATED_MARKER_NAME, built)
        marker = legacy.pop(GENERATED_MARKER_NAME)
        self.assertIn(b"skills/charter-workflow", marker)
        self.assertIn(b"targets/codex/skills/charter-workflow", marker)
        self.assertEqual(legacy, built)
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
