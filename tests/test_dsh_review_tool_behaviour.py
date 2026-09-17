"""Behavioural coverage for the DSH review tool's Host half.

The structural tests beside this file read ``targets/dsh/src/index.js`` as text.
They can pin the spelling of the settings keys and the presence of a read, but
they cannot execute the tool, so they would keep passing if the effort selection
were wired to the wrong seat, if a level the route does not declare were sent,
or if the no-selection path started attaching an option it never used to attach.

This test drives the real adapter entry through
``tests/dsh_review_tool_harness.cjs``, against stub platform packages in a
temporary directory, and skips on machines without a Node runtime so the suite
stays runnable without one. It is signed evidence about ``agentOptions`` — the
object the delegation provider receives — and about the ``effort`` field the
caller reads back.
"""

import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "targets/dsh/src/index.js"
DISTRIBUTION = ROOT / "plugins/dsh-charter-kit/lib/index.js"
HARNESS = ROOT / "tests/dsh_review_tool_harness.cjs"

# Every behaviour the harness must actually have exercised. Asserted by label,
# so a harness that quietly stops checking one is a failure rather than a
# smaller pass.
REQUIRED_BEHAVIOURS = (
    "the entry exports the skill and the tool in the optional idiom",
    "the tool registers under the review namespace",
    "the namespace declares one effort field per seat, defaulting to none",
    "the result schema reports the effort as an optional field beside the model",
    # The no-selection contract: byte-for-byte the call this tool always made.
    "without a selection the child gets the route and nothing else",
    "without a selection the result reports the provider default",
    # The selection contract, and the levels it must refuse.
    "a declared selection is attached as the level id",
    "the result reports the level it sent, beside the model",
    "a level the route does not declare is not sent",
    "a dropped selection reports the provider default rather than the level",
    "a selection is dropped on a route that declares no reasoning",
    "a failing capability lookup still runs the review with the chosen level",
    "a failing capability lookup reports the level it sent",
    "an unknown stored level is not a selection",
    "the attached value is the level id, even where the table spells it differently",
    "kind B reads the B seat's level",
    # The degrade the optional `llm` scope exists for.
    "without an LLM runtime the tool still registers and still runs",
    "without an LLM runtime the chosen level is still dispatched",
    "without an LLM runtime the result reports no level at all",
    # The paths that must stay untouched.
    "an inheriting seat passes no agent options",
    "the session route passes no agent options and stays a fallback",
    "a failed configured route falls back to the session model",
    "the fallback result reports the provider default, not the failed attempt's level",
)


@unittest.skipUnless(shutil.which("node"), "node is required to drive the plugin entry")
class DshReviewToolBehaviourTest(unittest.TestCase):
    def test_harness_exercises_every_required_behaviour(self):
        completed = subprocess.run(
            ["node", str(HARNESS), str(SOURCE)],
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

    def test_the_distribution_ships_the_same_entry(self):
        """The harness runs the target source; this is what makes that the entry.

        ``plugins/dsh-charter-kit/lib/index.js`` is what a Host loads. It is a
        byte copy of the target source, written by the DSH builder, so the
        behaviours above are the shipped tool's — as long as the copy is really
        the same file.
        """
        self.assertTrue(DISTRIBUTION.is_file(), "run scripts/build_dsh_plugin.py")
        self.assertEqual(SOURCE.read_bytes(), DISTRIBUTION.read_bytes())


if __name__ == "__main__":
    unittest.main()
