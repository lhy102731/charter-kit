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

    def test_registers_into_the_plugins_page_slot(self):
        # DSH 0.1.7 removed the settings-page item slot; configuration pages
        # now register into the Plugins page's `plugins.item`.
        self.assertIn("plugins.item", self.text)
        self.assertNotIn("settings.plugin.item", self.text)
        self.assertIn("charter-kit-review", self.text)

    def test_registers_a_settings_section_of_its_own(self):
        # The card joins the Settings navigation through `settings.section`,
        # the surface third-party plugins (Better Display, Watcher) use for
        # their own pages, so it stays reachable from Settings itself.
        self.assertIn("settings.section", self.text)
        self.assertIn("charter-kit-review", self.text)

    def test_binds_config_forms_and_the_model_catalog(self):
        # DSH 0.1.7 removed the `settingsScope` service; the card binds
        # `ctx.configForms` to the namespace it discovers instead.
        self.assertIn("configForms", self.text)
        self.assertNotIn("settingsScope", self.text)
        self.assertIn("modelCatalog", self.text)

    def test_discovers_its_namespace_from_the_describe_answer(self):
        # The 0.1.7 namespace is the loader entry id, unknowable at build time
        # for a runtime-injected plugin. The card finds its own namespace by
        # the marker fields only its Host Config declares.
        self.assertIn("remote.settings.describe", self.text)
        self.assertIn("reviewTimeoutSeconds", self.text)
        self.assertIn("reviewAProvider", self.text)

    def test_declares_exported_face(self):
        self.assertIn("exports.apply", self.text)
        self.assertIn("exports.inject", self.text)

    def test_inject_list_declares_the_remote_service(self):
        """Pin the inject value live testing identified as required.

        The card reaches the model catalogue through ``ctx.remote.session``
        and the settings describe answer through ``ctx.remote.settings``, so
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
        # The whole list, not just the presence of `remote`: this is the value
        # live testing proved sufficient, so any edit to it -- a dropped
        # service, an added one, a reordering -- is a deliberate act that has
        # to come back through this assertion. A presence check would let a
        # differently-wrong list through.
        self.assertEqual(declared, ['slots', 'locale', 'remote', 'remote.settings', 'remote.session', 'configForms'], line)


if __name__ == "__main__":
    unittest.main()
