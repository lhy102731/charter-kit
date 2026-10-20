"""Cross-file agreement guards for rules the kit states in more than one place.

validate_kit.py answers "does this claim still exist somewhere".  It cannot answer
"do the two places that state the same rule still agree", and that is the failure
mode that survives a green run: a check cited but not declared, an id renumbered
on one side, a record shape the migration table promises and the template does
not carry.  Every test below recomputes one side from the repository instead of
restating a literal, so it keeps working when the content legitimately changes.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
BT = chr(96)
CHARTER = "DEVELOPMENT_CHARTER.md"
MIGRATIONS = "portable/references/contract-migrations.md"
REVIEW = "portable/templates/review.md"
LEAF = "portable/templates/leaf-task.md"
CHANGER = "portable/templates/project-charter.md"
WORKFLOW = "portable/commands/charter-workflow.md"
POLICY = "portable/references/default-on-policy.md"
CHANGELOG = "changelog.md"
RECORDS_DIR = ".charter/records/"


def read(relative: str) -> str:
    path = PACKAGE_ROOT / relative
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def shipped_texts() -> dict:
    """Every hand-edited markdown source, keyed by repository-relative path.

    Generated mirrors are excluded on purpose: validate_kit.py already holds
    them byte-identical to these sources, so agreeing here means agreeing
    everywhere it is shipped.
    """
    texts = {}
    for path in sorted((PACKAGE_ROOT / "portable").rglob("*.md")):
        texts[path.relative_to(PACKAGE_ROOT).as_posix()] = path.read_text(encoding="utf-8")
    texts[CHARTER] = read(CHARTER)
    return texts


def row_ids(relative: str, prefix: str, row_prefix: str) -> list:
    """Ids of the form row_prefix`PREFIX7` declared as table or list rows, in order."""
    pattern = re.compile("^" + re.escape(row_prefix) + BT + prefix + r"(\d+)" + BT)
    found = []
    for line in read(relative).splitlines():
        match = pattern.match(line)
        if match:
            found.append(int(match.group(1)))
    return found


def cited(prefix: str) -> list:
    """(where, number) for every backticked PREFIX id anywhere in the sources."""
    pattern = re.compile(BT + prefix + r"(\d+)" + BT)
    hits = []
    for where, text in shipped_texts().items():
        for match in pattern.finditer(text):
            hits.append((where, match.group(1)))
    return hits


class ReviewCheckIds(unittest.TestCase):
    """CHK ids are append-only: declared once, cited by id, never renumbered."""

    def test_checks_are_a_contiguous_range(self):
        ids = row_ids(REVIEW, "CHK", "- [ ] ")
        self.assertTrue(ids, "review.md declares no numbered check")
        self.assertEqual(ids, list(range(1, len(ids) + 1)), "CHK ids must be 1..N with no gap and no reuse")

    def test_every_cited_check_is_declared(self):
        declared = set(row_ids(REVIEW, "CHK", "- [ ] "))
        for where, number in cited("CHK"):
            self.assertIn(int(number), declared, where + " cites CHK" + number + ", which review.md does not declare")

    def test_the_check_migration_table_names_only_declared_checks(self):
        declared = set(row_ids(REVIEW, "CHK", "- [ ] "))
        pattern = re.compile("^\\|\\s*" + BT + r"CHK(\d+)" + BT)
        rows = [match.group(1) for line in read(MIGRATIONS).splitlines() for match in [pattern.match(line)] if match]
        self.assertTrue(rows, "the check-level migration table names no CHK id")
        for number in rows:
            self.assertIn(int(number), declared, "the migration table names CHK" + number + ", which review.md does not declare")


class ClosureChecklist(unittest.TestCase):
    """CLS rows are the frozen closure account; none may arrive pre-answered."""

    ROW = re.compile("^\\|\\s*" + BT + r"CLS(\d+)" + BT + "\\s*\\|(.*)$")

    def rows(self) -> list:
        found = []
        for line in read(LEAF).splitlines():
            match = self.ROW.match(line)
            if match:
                found.append((int(match.group(1)), match.group(2)))
        return found

    def test_rows_are_the_frozen_range(self):
        numbers = [number for number, _rest in self.rows()]
        self.assertTrue(numbers, "leaf-task.md carries no CLS row")
        self.assertEqual(numbers, list(range(1, len(numbers) + 1)), "CLS ids must be 1..N with no gap and no reuse")

    def test_rows_ship_unanswered(self):
        for number, rest in self.rows():
            self.assertIn("<answer>", rest, "CLS" + str(number) + " ships pre-answered")
            self.assertIn("<raw ref>", rest, "CLS" + str(number) + " ships without an evidence slot")

    def test_every_cited_closure_id_is_declared(self):
        declared = set(number for number, _rest in self.rows())
        for where, number in cited("CLS"):
            self.assertIn(int(number), declared, where + " cites CLS" + number + ", which leaf-task.md does not declare")

    def test_the_migration_range_ends_at_the_last_declared_row(self):
        """The migration table range is the work order for old contracts.

        A lower bound alone is not enough: naming CLS1-CLS9 passes every
        "is it declared" check once CLS10 exists, and silently drops the newest
        row from the migration of every 0.1 contract.  Pin the upper bound.
        """
        declared = [number for number, _rest in self.rows()]
        self.assertTrue(declared, "leaf-task.md carries no CLS row")
        pattern = re.compile(
            r"Closure checklist\s*\(" + BT + r"CLS(\d+)" + BT + r"-" + BT + r"CLS(\d+)" + BT + r"\)"
        )
        ranges = []
        for line in read(MIGRATIONS).splitlines():
            match = pattern.search(line)
            if match:
                ranges.append((int(match.group(1)), int(match.group(2))))
        self.assertTrue(ranges, "the migration table states no closure checklist range")
        for low, high in ranges:
            self.assertEqual(low, 1, "the migration range must start at CLS1")
            self.assertEqual(
                high,
                max(declared),
                "the migration table names CLS1-CLS" + str(high)
                + ", but leaf-task.md declares up to CLS" + str(max(declared)),
            )


class AcceptanceItems(unittest.TestCase):
    """Every acceptance item names the check that can move the exit code."""

    ITEM = re.compile("^- \\[ \\] " + BT + r"AC(\d+)" + BT)

    def items(self) -> list:
        found = [line for line in read(LEAF).splitlines() if self.ITEM.match(line)]
        self.assertTrue(found, "leaf-task.md carries no numbered acceptance item")
        return found

    def test_items_are_numbered_without_gap(self):
        numbers = [int(self.ITEM.match(line).group(1)) for line in self.items()]
        self.assertEqual(numbers, list(range(1, len(numbers) + 1)), "AC ids must be 1..N with no gap and no reuse")

    def test_every_item_names_a_check_that_can_move_the_exit_code(self):
        for line in self.items():
            self.assertIn("- check:", line, "an acceptance item ships with no check slot: " + line)


class RecordScoping(unittest.TestCase):
    """The migration table promises an id shape and one file per record; hold the templates to it."""

    ROW = re.compile(
        "^\\|\\s*" + BT + r"([a-z-]+\.md)" + BT + "\\s*\\|\\s*" + BT
        + "[^" + BT + "]+" + BT + "\\s*\\|\\s*" + BT + r"([^" + BT + "]+)" + BT
    )

    def rows(self) -> list:
        found = [match.groups() for line in read(MIGRATIONS).splitlines() for match in [self.ROW.match(line)] if match]
        self.assertTrue(found, "the record-level migration table declares no record")
        return found

    def test_every_record_kind_files_one_file_per_record(self):
        for template, shape in self.rows():
            body = read("portable/templates/" + template)
            self.assertTrue(body, "the migration table names " + template + ", which is not a template")
            self.assertIn(shape, body, template + " does not carry the id shape " + shape + " the migration table requires")
            self.assertIn(RECORDS_DIR, body, template + " does not say where the record is filed")

    def test_no_unscoped_record_id_is_used_as_an_instruction(self):
        pattern = re.compile(r"\b(?:E|REV)-\d\d\b")
        for where, text in shipped_texts().items():
            for number, line in enumerate(text.splitlines(), 1):
                for match in pattern.finditer(line):
                    self.assertIn("bare", line, where + ":" + str(number) + " uses the unscoped id " + match.group(0) + " as an instruction")


class ReadSetAndHistory(unittest.TestCase):
    """History must be created and must stay out of the read every resume pays for."""

    HISTORY_MARKER = "never read on resume"

    def working_set_line(self) -> str:
        for line in read(WORKFLOW).splitlines():
            if self.HISTORY_MARKER in line:
                return line
        self.fail("charter-workflow.md no longer says which file is history: " + self.HISTORY_MARKER)

    def read_set_line(self) -> str:
        found = [line for line in read(WORKFLOW).splitlines() if "project.md" in line and "lessons.md" in line and "working set" not in line]
        self.assertEqual(len(found), 1, "the resume read set is not stated on exactly one line: " + repr(found))
        return found[0]

    def names(self, line: str) -> set:
        # Match a file name wherever it sits, so `.charter/handoff.md` and a bare
        # `handoff.md` both count. A parse that silently matches nothing would make
        # the assertions below vacuous, so their callers check the parse is not empty.
        return set(re.findall(r"\b([a-z][a-z-]*\.md)\b", line))

    def test_history_is_created_but_never_read_on_resume(self):
        working = self.names(self.working_set_line())
        resumed = self.names(self.read_set_line())
        self.assertIn(CHANGELOG, working, "the working set does not create " + CHANGELOG)
        # Non-vacuity: both parses must find the files the lines actually name,
        # otherwise the exclusion below passes without testing anything.
        self.assertIn("project.md", resumed, "the resume read set does not name project.md")
        self.assertIn("lessons.md", resumed, "the resume read set does not name lessons.md")
        self.assertGreaterEqual(len(resumed), 4, "the resume read set parsed to fewer files than it names")
        self.assertNotIn(CHANGELOG, resumed, CHANGELOG + " is history and must not be in the resume read set")

    def test_the_read_set_is_inside_the_working_set(self):
        working = self.names(self.working_set_line())
        resumed = self.names(self.read_set_line())
        self.assertGreaterEqual(len(working), 8, "the working set parsed to fewer files than it names")
        self.assertTrue(resumed, "the resume read set parsed to no file")
        for name in sorted(resumed):
            self.assertIn(name, working, "resume reads " + name + " and the working set does not create it")

    def test_the_init_script_creates_every_working_set_file(self):
        quote = chr(34)
        pairs = re.findall(quote + r"([a-z-]+\.md)" + quote + r":\s*" + quote + r"([a-z-]+\.md)" + quote, read("scripts/init_project.py"))
        created = set(target for _source, target in pairs)
        self.assertTrue(created, "init_project.py declares no file map")
        for name in self.names(self.working_set_line()):
            self.assertIn(name, created, "the working set names " + name + " and init_project.py does not create it")

    def test_section_12_is_a_pointer_and_not_a_history(self):
        text = read(CHANGER)
        self.assertIn("## 12.", text, "project-charter.md has no section 12")
        section = text[text.index("## 12."):]
        end = section.find("\n## ", 3)
        if end != -1:
            section = section[:end]
        self.assertIn(CHANGELOG, section, "section 12 does not name " + CHANGELOG)
        for line in section.splitlines():
            self.assertIsNone(re.match(r"^\|\s*v?\d+\.\d+", line), "section 12 still carries a version row: " + line)


class DefaultOnHooks(unittest.TestCase):
    """A hook that names a landing point which does not exist is text, not a gate."""

    ROW = re.compile("^\\|\\s*" + BT + r"(DOP\d+)" + BT + "\\s*\\|\\s*([^|]+?)\\s*\\|\\s*([^|]+?)\\s*\\|")

    def hooks(self) -> list:
        found = [match.groups() for line in read(POLICY).splitlines() for match in [self.ROW.match(line)] if match]
        self.assertTrue(found, "default-on-policy.md declares no hook")
        return found

    def resolve(self, token: str) -> str:
        for candidate in ("portable/" + token, "portable/templates/" + token, "portable/references/" + token, "scripts/" + token, token):
            if (PACKAGE_ROOT / candidate).is_file():
                return read(candidate)
        return ""

    def test_every_hook_lands_in_a_file_that_exists(self):
        for hook, _kind, landing in self.hooks():
            tokens = re.findall(BT + "([^" + BT + "]+)" + BT, landing)
            self.assertTrue(tokens, hook + " names no landing point")
            body = self.resolve(tokens[0])
            self.assertTrue(body, hook + " names " + tokens[0] + ", which is not a file in the kit")
            for anchor in tokens[1:]:
                self.assertIn(anchor, body, hook + " anchors on " + repr(anchor) + ", which " + tokens[0] + " does not carry")

    def test_every_cited_hook_is_declared(self):
        declared = set(hook for hook, _kind, _landing in self.hooks())
        for where, number in cited("DOP"):
            self.assertIn("DOP" + number, declared, where + " cites DOP" + number + ", which default-on-policy.md does not declare")



class DecisionRecordLanding(unittest.TestCase):
    """A decision may only be sent somewhere the templates also call a record file."""

    LEGACY = ".charter/decision.md"

    def record_path(self) -> str:
        """The decision record path the migration table promises, derived from that row."""
        for template, shape in RecordScoping().rows():
            if template == "decision.md":
                rows = [line for line in read(MIGRATIONS).splitlines() if template in line and shape in line]
                self.assertTrue(rows, "the migration table maps decision.md to no path")
                found = re.search(BT + r"\.charter/records/[^" + BT + "]+" + BT, rows[0])
                self.assertTrue(found, "the decision row names no records path: " + rows[0])
                return found.group(0).strip(BT)
        self.fail("the record-level migration table no longer declares decision.md")

    def test_no_shipped_file_sends_a_decision_to_the_shared_file(self):
        # contract-migrations.md is exempt: describing how to leave the legacy
        # shared file is its job, and it is the only file that may name it.
        for where, body in shipped_texts().items():
            if where == MIGRATIONS:
                continue
            self.assertNotIn(self.LEGACY, body, where + " still files a decision in " + self.LEGACY)

    def test_every_entry_point_that_writes_a_decision_names_the_record_path(self):
        path = self.record_path()
        for where in (CHANGER, REVIEW, WORKFLOW):
            body = read(where)
            self.assertIn("decision", body, where + " stopped mentioning decisions")
            self.assertIn(path, body, where + " writes a decision without naming " + path)


class WorkingSetVersusReadSet(unittest.TestCase):
    """A working-set file that is not read on resume must be declared as such."""

    EXCLUSION = re.compile(r"not on resume|never read on resume|stays out of the resume read set|rather than on resume")

    def names(self, line: str) -> set:
        return set(re.findall(r"\b([a-z][a-z-]*\.md)\b", line))

    def lines(self):
        working, resumed = [], []
        for line in read(WORKFLOW).splitlines():
            if "records/" in line and ".charter/" in line and "project.md" in line:
                working.append(line)
            elif "project.md" in line and "lessons.md" in line and "working set" not in line:
                resumed.append(line)
        self.assertEqual(len(working), 1, "the working-set line is not unique")
        self.assertEqual(len(resumed), 1, "the resume read-set line is not unique")
        return working[0], resumed[0]

    def test_no_line_claims_the_whole_working_set_is_resumed(self):
        working, _resumed = self.lines()
        self.assertIsNone(
            re.search(r"every other file[^.]*read on resume", working),
            "the working-set line claims every other file is read on resume, which the read set contradicts",
        )

    def test_each_excluded_file_is_named_with_a_reason(self):
        working, resumed = self.lines()
        excluded = self.names(working) - self.names(resumed)
        self.assertTrue(self.names(resumed), "the resume read set parsed to no file")
        self.assertTrue(excluded, "the working set and the read set parsed to the same files")
        clauses = [line for line in working.split(";") if self.EXCLUSION.search(line)]
        self.assertTrue(clauses, "the working-set line declares no exclusion at all")
        declared = set()
        for clause in clauses:
            declared |= self.names(clause)
        for name in sorted(excluded):
            self.assertIn(name, declared, name + " is in the working set, not in the read set, and no clause says why")


class MigrationVersionArithmetic(unittest.TestCase):
    """Migration guidance must name the version the template actually carries."""

    def current(self) -> str:
        found = re.search(r"Contract version: " + BT + r"(\d+\.\d+)" + BT, read(LEAF))
        self.assertTrue(found, "leaf-task.md declares no Contract version")
        return found.group(1)

    def test_the_version_step_names_the_current_template_version(self):
        step = [line for line in read(MIGRATIONS).splitlines() if "Bump " + BT + "Contract version" + BT in line]
        self.assertTrue(step, "the migration steps no longer bump Contract version")
        self.assertIn(BT + self.current() + BT, step[0], "the bump step does not name the current template version")

    def test_no_row_promises_a_version_newer_than_the_template(self):
        current = self.current()
        body = read(MIGRATIONS)
        for version in sorted(set(re.findall(BT + r"(\d+\.\d+)" + BT, body))):
            self.assertLessEqual(version, current, "contract-migrations.md promises template " + version + ", newer than " + current)


class PhaseCoverage(unittest.TestCase):
    """Every phase the charter defines is projected into the operating steps."""

    def test_every_phase_is_cited_outside_its_definition(self):
        body = read(CHARTER)
        numbers = sorted(set(int(n) for n in re.findall(r"LA(\d+)", body)))
        self.assertGreaterEqual(len(numbers), 10, "the charter defines too few phases to be the loop")
        # A phase is projected when a step names it, or when a step names a range
        # that contains it: the steps group neighbours, so a range is a citation.
        covered = set()
        for low, high in re.findall("LA(\\d+)" + BT + "?\\s*[–-]\\s*" + BT + "?LA(\\d+)", body):
            covered |= set(range(int(low), int(high) + 1))
        for number in numbers:
            token = re.compile("LA" + str(number) + r"(?!\d)")
            self.assertTrue(
                len(token.findall(body)) >= 2 or number in covered,
                "LA" + str(number) + " is defined and never projected into the eight steps",
            )


class EvidenceLayers(unittest.TestCase):
    """A checklist may not cite a definition the shipped files do not carry."""

    def test_the_layer_definition_lives_where_the_checklist_points(self):
        leaf = read(LEAF)
        if "evidence layers" not in leaf:
            return
        found = re.search(r"evidence layers of charter (\d+\.\d+)", leaf)
        self.assertTrue(found, "the closure checklist cites evidence layers without naming the section that defines them")
        section = found.group(1)
        body = read(CHARTER)
        start = body.find("### " + section)
        self.assertNotEqual(start, -1, "the charter has no section " + section)
        end = body.find("\n### ", start + 1)
        part = body[start:end if end != -1 else len(body)]
        self.assertIn("四层", part, "the charter section " + section + " does not define the four evidence layers")
        for marker in ("①", "②", "③", "④"):
            self.assertIn(marker, part, "the charter section " + section + " is missing layer " + marker)


class ClosureChecklistCoverage(unittest.TestCase):
    """Rows the procedures require must exist in the closure table, not only in prose."""

    ROW = re.compile(r"^\|\s*" + BT + r"CLS(\d+)" + BT + r"\s*\|\s*([^|]+?)\s*\|")

    def rows(self) -> dict:
        found = {}
        for line in read(LEAF).splitlines():
            match = self.ROW.match(line)
            if match:
                found[int(match.group(1))] = match.group(2)
        self.assertTrue(found, "leaf-task.md declares no closure row")
        return found

    def test_every_promise_to_confirm_the_acceptance_items_has_a_row(self):
        body = read(LEAF)
        cited_rows = re.findall(BT + r"CLS(\d+)" + BT + " confirms each " + BT + "AC" + BT, body)
        self.assertTrue(cited_rows, "no closure row claims to confirm the acceptance items")
        rows = self.rows()
        for number in cited_rows:
            self.assertIn(int(number), rows, "CLS" + number + " is cited and not declared")
            self.assertIn("AC", rows[int(number)], "CLS" + number + " is cited as confirming every AC and does not mention AC")

    def test_the_unchecked_boundary_rule_has_a_row(self):
        if "未检查" not in read(CHARTER):
            return
        rows = self.rows()
        self.assertTrue(
            any("unchecked" in question.lower() or "未检查" in question for question in rows.values()),
            "the charter requires unchecked boundaries to block closure and no CLS row asks about them",
        )


class ChangeLogTriggers(unittest.TestCase):
    """The list that decides whether a version row exists must live in the read set."""

    def test_the_trigger_rule_is_reachable_on_resume(self):
        if "When a row is required" not in read("portable/templates/" + CHANGELOG):
            return
        self.assertIn(
            "row is required", read(CHANGER).lower(),
            "changelog.md states when a row is required and the read-set charter carries no such rule",
        )


if __name__ == "__main__":
    unittest.main()
