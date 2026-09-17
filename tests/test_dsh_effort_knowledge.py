"""The copied reasoning-effort table: provenance, content, and byte identity.

Task 16 copies the knowledge base out of the third-party plugin
``dsh-better-reasoning-effort`` (MIT) rather than paraphrasing it, because the
entries carry the official-source citations the table's claims rest on. That
copy exists twice in this package — as ``effort-knowledge.js`` (the shipped data
module, regenerable from upstream by the extraction script) and inside
``client.js`` (the browser bundle, which the shell's client module table cannot
load a sibling file into) — and two copies of one table are only safe when
something compares them.

These tests do exactly that, and nothing here needs Node: both sentinel regions
are plain text in committed files, so byte identity and content are checkable
without a runtime. What they CANNOT prove is that the table is right about a
model — only the note's cited source can, which is why the notes are preserved
and asserted rather than summarised.
"""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_MODULE = ROOT / "targets/dsh/client/effort-knowledge.js"
BUNDLE = ROOT / "targets/dsh/client/client.js"
HOST = ROOT / "targets/dsh/src/index.js"

KNOWLEDGE_BEGIN = "/* CK-EFFORT-KNOWLEDGE:BEGIN */"
KNOWLEDGE_END = "/* CK-EFFORT-KNOWLEDGE:END */"
MATCH_BEGIN = "/* CK-EFFORT-MATCH:BEGIN */"
MATCH_END = "/* CK-EFFORT-MATCH:END */"

# Upstream provenance this copy has to carry, for the licence and for the next
# maintainer who has to decide whether the table is still current.
UPSTREAM_NAME = "dsh-better-reasoning-effort"
UPSTREAM_VERSION = "0.3.9"
UPSTREAM_URL = "https://github.com/HaoyueQin/dsh-better-reasoning-effort"
EXTRACTION_COMMAND = (
    "node .superpowers/sdd/2026-09-12-review-model-config/extract-effort-knowledge.mjs --write --embed"
)

# The upstream array's length. Pinned so a truncated extraction — the failure
# mode that would silently drop the entries at the end of the table — fails
# here instead of shrinking the shipped data.
ENTRY_COUNT = 60


def region(text: str, begin: str, end: str) -> str:
    start = text.index(begin) + len(begin)
    return text[start:text.index(end, start)].strip()


class EffortKnowledgeProvenanceTest(unittest.TestCase):
    def setUp(self):
        self.module = DATA_MODULE.read_text(encoding="utf-8")
        self.bundle = BUNDLE.read_text(encoding="utf-8")

    def test_the_data_module_ships_with_the_plugin(self):
        self.assertTrue(DATA_MODULE.is_file())

    def test_the_header_records_the_upstream_and_the_extraction(self):
        header = self.module.split(KNOWLEDGE_BEGIN)[0]
        for expected in (
            UPSTREAM_NAME,
            UPSTREAM_VERSION,
            UPSTREAM_URL,
            "MIT",
            "Copyright (c) 2026 HaoyueQin",
            EXTRACTION_COMMAND,
        ):
            self.assertIn(expected, header, expected)
        # The date the copy was taken, so a reader can judge its age without
        # diffing two repositories.
        self.assertRegex(header, r"Extracted: \d{4}-\d{2}-\d{2}")

    def test_the_licence_notice_travels_with_the_copy(self):
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertIn(UPSTREAM_NAME, license_text)
        self.assertIn(UPSTREAM_URL, license_text)
        self.assertIn("Copyright (c) 2026 HaoyueQin", license_text)
        self.assertIn("Permission is hereby granted", license_text)

    def test_the_two_copies_are_byte_identical(self):
        """The check that makes the duplication safe.

        `client.js` cannot `require` a sibling file — the client module table
        answers platform specifiers and registered packages only — so the table
        has to be embedded there as well as shipped as a module. If the two
        regions ever differ, the card renders one table and this package
        documents another.
        """
        for begin, end in ((KNOWLEDGE_BEGIN, KNOWLEDGE_END), (MATCH_BEGIN, MATCH_END)):
            self.assertEqual(
                region(self.module, begin, end),
                region(self.bundle, begin, end),
                f"{begin} differs between effort-knowledge.js and client.js",
            )


class EffortKnowledgeContentTest(unittest.TestCase):
    def setUp(self):
        self.module = DATA_MODULE.read_text(encoding="utf-8")
        self.payload = json.loads(region(self.module, KNOWLEDGE_BEGIN, KNOWLEDGE_END))

    def test_every_upstream_entry_survived_the_extraction(self):
        self.assertEqual(len(self.payload["entries"]), ENTRY_COUNT)

    def test_every_entry_keeps_its_upstream_fields_and_note(self):
        # `id`, `patterns`, `efforts` and `note` are on every upstream entry;
        # the remaining fields are per-entry by design (`input`, `compat`,
        # `defaultEffort`, and the capacities are absent where upstream had
        # nothing to say), so requiring them wholesale would demand a rewrite of
        # the data rather than a faithful copy of it.
        required = {"id", "patterns", "efforts", "note"}
        for entry in self.payload["entries"]:
            self.assertTrue(required <= set(entry), f"{entry.get('id')} is missing {required - set(entry)}")
            self.assertIsInstance(entry["patterns"], list)
            self.assertTrue(entry["patterns"], entry["id"])
            # The note is the citation the entry's claim rests on. An entry
            # without one is a claim this package cannot stand behind.
            self.assertTrue(entry["note"].strip(), entry["id"])

    def test_the_level_order_is_the_llm_layers_own(self):
        self.assertEqual(
            self.payload["levels"],
            ["off", "minimal", "low", "medium", "high", "xhigh", "max"],
        )

    def test_the_host_half_carries_the_same_level_list(self):
        """The host validates a stored level against its own list.

        It cannot import this module (`lib/index.js` is a flat copy of the
        adapter entry, and a sibling import would not resolve there), so the two
        lists are compared here instead: a level added on one side has to be
        added on the other.
        """
        host = HOST.read_text(encoding="utf-8")
        match = re.search(r"^const EFFORT_LEVELS = (\[[^\]]*\])$", host, re.MULTILINE)
        self.assertIsNotNone(match, "the host half no longer declares EFFORT_LEVELS")
        self.assertEqual(json.loads(match.group(1).replace("'", '"')), self.payload["levels"])

    def test_the_two_live_routes_this_task_was_verified_against(self):
        """Pin what the table resolves for the routes the report names.

        The routes are `tt/z-ai/glm-5.3-free` and `tt/qwen3.8-flash` from the
        live settings file. The table's answer for the second one DISAGREES with
        that route's own declaration, which is the case the card has to state
        rather than hide — so both answers are pinned here.
        """
        by_id = {entry["id"]: entry for entry in self.payload["entries"]}
        glm = by_id["glm-5-3"]
        self.assertEqual(glm["efforts"], {"low": "low", "high": "high", "max": "max"})
        self.assertEqual(glm["defaultEffort"], "max")
        qwen = by_id["qwen-3-8"]
        self.assertEqual(qwen["efforts"], {"off": None, "low": "low", "medium": "medium", "xhigh": "xhigh"})
        self.assertEqual(qwen["defaultEffort"], "xhigh")

    def test_the_match_rules_came_with_the_table(self):
        # The longest-boundary-match rule is what makes `glm-5.3-free` resolve to
        # the GLM-5.3 entry rather than to the plain `glm` one, so the rule is
        # part of the copied data and travels in its own region.
        rules = region(self.module, MATCH_BEGIN, MATCH_END)
        for fragment in ("isAlnum", "normalizeLoose", "onBoundary", "matchKnowledgeBase", "return best?.entry;"):
            self.assertIn(fragment, rules, fragment)


if __name__ == "__main__":
    unittest.main()
