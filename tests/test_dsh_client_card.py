import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "targets/dsh/client/client.js"


class DshClientCardTest(unittest.TestCase):
    def setUp(self):
        self.text = BUNDLE.read_text(encoding="utf-8")

    def test_bundle_exists(self):
        self.assertTrue(BUNDLE.is_file())

    def test_registers_under_the_package_module_id(self):
        self.assertIn("window.__ModuleLoader__.load(", self.text)
        self.assertIn("@dsh-external/dsh-charter-kit", self.text)

    def test_requires_only_platform_modules(self):
        for specifier in ("react",):
            self.assertIn(f"require('{specifier}')", self.text)
        self.assertNotIn("require('@deepseek-ai/dsh-client-ui-settings", self.text)

    def test_registers_the_plugin_card_by_namespace_key(self):
        self.assertIn("settings.plugin.item", self.text)
        self.assertIn("charter-kit-review", self.text)

    def test_binds_the_settings_scope_and_model_catalog(self):
        self.assertIn("settingsScope", self.text)
        self.assertIn("modelCatalog", self.text)

    def test_declares_exported_face(self):
        self.assertIn("exports.apply", self.text)
        self.assertIn("exports.inject", self.text)

    def test_inject_list_declares_the_remote_service(self):
        """Pin the inject value live testing identified as required.

        The card reaches the model catalogue through ``ctx.remote.session``, so
        the module must declare the literal service name ``remote``. Inject
        names are service names, not property paths: only ``remote`` makes the
        shell wait for that service before it materializes this client at all,
        and ``'remote.session'`` names nothing, so it waits for nothing.

        The failure this pins is silent: a wrong list raises nowhere, the shell
        simply never mounts the card, which is exactly the bug this line fixed.

        Live evidence, from the probe run that diagnosed it (artifacts under
        ``.superpowers/sdd/2026-09-12-review-model-config/``): probe-card4.json
        captured the old list at this line and found no card
        (``ckCardPresent: false``, no selects) after driving ``设置 → 插件 →
        插件配置`` in headless Chromium, while probe-card5 recorded this exact
        corrected line and reported ``cardPresent: true`` with two selects,
        both dropdowns read back and saved.

        This assertion pins the value that live testing identified. It cannot
        prove the card mounts: it reads source text and never runs the shell's
        inject machinery. Only driving a live shell proves the mount; do not
        cite this test as evidence that it does.
        """
        line = next(
            (entry.strip() for entry in self.text.splitlines() if "exports.inject" in entry),
            None,
        )
        self.assertIsNotNone(line, "the bundle declares no exports.inject")
        declared = re.findall(r"'([^']*)'", line)
        self.assertIn("remote", declared, line)
        # The property path is not a service name, so it does not satisfy the
        # requirement above; keeping it is harmless, replacing `remote` with it
        # is not.
        self.assertNotIn("remote.session", [name for name in declared if "." not in name], line)


if __name__ == "__main__":
    unittest.main()
