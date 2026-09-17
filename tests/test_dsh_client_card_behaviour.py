"""Behavioural coverage for the DSH review-model card bundle.

The card is a browser artifact, and the text-presence tests beside this file
cannot regress it: they would keep passing if a write were wired to the wrong
field pair, if a write the Host refused were reported as saved, or if a second
selection inside one mirror round-trip were reported as failed. This test drives
the real bundle through a dependency-free Node harness instead
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
    "a write delegates its revision to the scope",
    "review B never offers review A's rescued route",
    "review A never offers review B's rescued route",
    "a landed write reports saved",
    "a refused write reports failure",
    "a transport rejection reports failure",
    "inherit reports saved once it lands",
    "two selections in one round-trip both land",
    "both of the round-trip selections are stored",
    # The timeout control: the tool's budget has to be editable from this card,
    # and the card must not turn a typo into a silently clamped write.
    "the timeout control is one number input beside the two dropdowns",
    "the timeout control reads the stored value",
    "the timeout control advertises the tool's clamped range",
    "a timeout edit writes only the timeout field",
    "a landed timeout edit reports saved",
    "a refused timeout edit reports failure",
    "a refused timeout edit leaves the stored value standing",
    "a blank timeout entry writes nothing",
    "a non-numeric timeout entry writes nothing",
    "a rejected timeout entry is reported rather than silently dropped",
    # The draft-then-commit contract. These pin the card's shape only: the
    # harness drives the handlers with a synthetic `target.value`, so it cannot
    # see whether a real browser can clear the field. That is a headless-Chromium
    # probe recorded in the task report, and the harness says so at the scenario.
    "an emptied field is reachable while editing",
    "typing does not write until the edit is committed",
    "leaving the field commits the draft",
    "the committed field shows the stored value again",
    "leaving an emptied field writes nothing and restores the stored value",
    # The effort area (task 16): one single-choice panel per seat, its rows
    # gated by the model's OWN declaration, and the copied table's string shown
    # read-only beside each level. Same blind spot as above: these drive React
    # elements, not a DOM, so the headless-browser probe is the evidence that a
    # browser renders these states.
    "the effort area renders one panel per seat",
    "each panel lists the reference editor's levels in its order",
    "a level the model does not declare is not selectable",
    "a refused row carries a visible reason",
    "the model declaration decides, not the knowledge base",
    "the disagreement between the table and the model is stated",
    "the value column shows the table's string for each level",
    "a level the table does not carry says so instead of inventing a value",
    "no text input was added for the value column",
    "the at-rest panel says nothing is sent",
    "ticking a level writes only that seat's effort field",
    "a landed selection reports saved",
    "the selected row is the only checked one in its seat",
    "the panel states the value it will send",
    "the other seat writes its own field",
    "both seats hold their own selection",
    "the panel offers a clear-selection affordance",
    "clearing writes the empty selection",
    "the cleared panel says nothing is sent",
    "the panel offers the auto-adapt prefill",
    "auto-adapt writes the table's default level",
    "auto-adapt says which level it took and from where",
    "auto-adapt refuses a default the model does not declare",
    "a stored level the model does not declare is not shown as selected",
    "the stale selection is left in the settings rather than rewritten",
    "a seat with no model has no selectable level",
    "auto-adapt is unavailable without a model",
    "a refused effort write reports failure",
    "a refused effort write leaves the stored selection standing",
    "the value column and the id are different strings for this level",
    "a selected level is stored as its id, never as the table's wire string",
    "the embedded table resolves the live routes",
    "the copied entries keep their upstream notes",
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
