"""Behavioural coverage for the DSH review-model card bundle.

The card is a browser artifact, and the text-presence tests beside this file
cannot regress it: they would keep passing if a write were wired to the wrong
field pair, or if a write the Host refused were reported as saved. This test
drives the real bundle through a dependency-free Node harness instead
(``tests/dsh_client_card_harness.cjs``), and skips on machines without a Node
runtime so the suite stays runnable without one.
"""

import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "targets/dsh/client/client.js"
HARNESS = ROOT / "tests/dsh_client_card_harness.cjs"

# Every behaviour the harness must actually have exercised. Asserted by label,
# so a harness that quietly stops checking one is a failure rather than a
# smaller pass.
REQUIRED_BEHAVIOURS = (
    "module id is the package name",
    "exports carry apply and inject",
    "card registers into settings.plugin.item",
    "card key and locale are the namespace",
    "options come from the model catalog",
    "an unserved stored route stays selectable for its own review",
    "review A selection writes only review A's field pair",
    "review B selection writes only review B's field pair",
    "review B never offers review A's rescued route",
    "review A never offers review B's rescued route",
    "a landed write reports saved",
    "a refused write reports failure",
    "a transport rejection reports failure",
    "inherit reports saved once it lands",
)


@unittest.skipUnless(shutil.which("node"), "node is required to drive the client bundle")
class DshClientCardBehaviourTest(unittest.TestCase):
    def test_harness_exercises_every_required_behaviour(self):
        completed = subprocess.run(
            ["node", str(HARNESS), str(BUNDLE)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )
        output = completed.stdout + completed.stderr
        self.assertEqual(completed.returncode, 0, output)
        self.assertNotIn("FAIL", output)
        self.assertIn("HARNESS: ALL PASS", output)
        for behaviour in REQUIRED_BEHAVIOURS:
            self.assertIn(f"PASS  {behaviour}", output)


if __name__ == "__main__":
    unittest.main()
