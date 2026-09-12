import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DshTargetTest(unittest.TestCase):
    def test_target_package_json_exists(self):
        self.assertTrue((ROOT / "targets/dsh/package.json").is_file())

    def test_target_plugin_entry_exists(self):
        self.assertTrue((ROOT / "targets/dsh/src/index.js").is_file())

    def test_target_build_script_exists(self):
        self.assertTrue((ROOT / "targets/dsh/scripts/build.sh").is_file())

    def test_package_manifest_valid(self):
        data = json.loads((ROOT / "targets/dsh/package.json").read_text(encoding="utf-8"))
        self.assertEqual(data["name"], "@dsh-external/dsh-charter-kit")
        self.assertEqual(data["main"], "./lib/index.js")

    def test_distribution_package_json_exists(self):
        self.assertTrue((ROOT / "plugins/dsh-charter-kit/package.json").is_file())

    def test_distribution_lib_exists(self):
        self.assertTrue((ROOT / "plugins/dsh-charter-kit/lib/index.js").is_file())

    def test_distribution_source_matches_target(self):
        source = (ROOT / "targets/dsh/src/index.js").read_bytes()
        distributed = (ROOT / "plugins/dsh-charter-kit/src/index.js").read_bytes()
        self.assertEqual(source, distributed)

    def test_distribution_ships_the_client_bundle(self):
        self.assertTrue((ROOT / "plugins/dsh-charter-kit/client/client.js").is_file())

    def test_distribution_client_matches_target(self):
        source = (ROOT / "targets/dsh/client/client.js").read_bytes()
        distributed = (ROOT / "plugins/dsh-charter-kit/client/client.js").read_bytes()
        self.assertEqual(source, distributed)

    def test_declares_the_client_bundle(self):
        data = json.loads((ROOT / "targets/dsh/package.json").read_text(encoding="utf-8"))
        self.assertEqual(data["exports"]["./client"], "./client/client.js")
        client = data["dsh"]["client"]
        self.assertEqual(client["platform"], "web")
        self.assertIsInstance(client["inject"], list)

    def test_target_version_is_0_3_0(self):
        data = json.loads((ROOT / "targets/dsh/package.json").read_text(encoding="utf-8"))
        self.assertEqual(data["version"], "0.3.0")


if __name__ == "__main__":
    unittest.main()
