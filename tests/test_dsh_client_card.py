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


if __name__ == "__main__":
    unittest.main()
