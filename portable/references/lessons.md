# Lessons rules

This reference defines the lesson layer: how a pitfall becomes an entry, how entries are
cited, reported, archived, and promoted into the kit itself. The layer is project-local
knowledge with a bounded budget; it is advice, not a gate. This file (or
`references/lessons.md` in the self-contained Skill) is the single definition; entry
documents cite it instead of restating it.

## Distill — when an event becomes an entry

Run the distill sweep at three moments: when a leaf reaches `PASS_CLOSED`, during the
promotion sweep before archiving a handoff block, and on the defect route of Change Triage.
Sweep the leaf Events table (`FALLBACK`, rework, over-budget repair), Review A/B findings,
and expired waivers. A qualifying event names a pitfall, a cost, and evidence under
`.charter/evidence/` or a commit. One pitfall keeps one entry: a repeat hit updates the
existing entry — hit count +1, evidence appended, defense revised — and never creates a
duplicate. Zero output is a legal result: a leaf with no qualifying event adds nothing, and
an entry created to fill a quota is a defect, not a lesson.

## Cite — where an entry is used

At the Design step, the Reuse Check, and Change Triage, read `.charter/lessons.md` (when it
exists) and cite every relevant `LS-NNN` with one line saying why it applies. A citation
raises that entry's hit count whether it prevented the pitfall or not. Stepping on a
registered pitfall anyway is a defect signal for this layer, not an excuse: record the
event in the leaf Events table and let the next distill sweep revise the defense. A defense
that failed despite being cited must be re-distilled with the new evidence; the count still
rises.

## Report — how the user sees the layer

The layer reports at the moments the workflow already reports; the user never polls disk.
On resume, the status line names the active and archived entry counts, the newest entry,
and every open `GENERALIZE` candidacy: `lessons: 3 active / 1 archived | newest LS-012
(TASK-007, 09-14) | 1 GENERALIZE candidate awaiting your decision: LS-009`. At leaf
closure, the distill sweep result appears in the closure report: `distilled: 1 new
(LS-012), 2 updated (repeat LS-004), 3 cited this leaf`. A candidacy is decided, not
parked: the user promotes it, keeps it project-local, or drops it, and the decision is
recorded on the entry.

## Decay — how the file stays bounded

`.charter/lessons.md` is capped at 8 KB because every resume re-reads it. Over the cap,
archive the weakest entries — lowest hit count first, then oldest — to
`.charter/lessons-archive.md`, leaving one pointer line each. Before archiving any entry,
run the promotion sweep: an entry cited as a defense basis by any leaf, or carrying an open
`GENERALIZE` candidacy, is not archivable. Archiving without the sweep silently deletes a
live rule from every later reader — the same defect as archiving a handoff block by leaf ID
alone.

## Generalize — how the kit itself improves

A generalizable pitfall is promoted only by an explicit user action. The agent proposes by
marking the entry `GENERALIZE` and presenting the candidacy in the resume report. The user
confirms; the promotion is then a hand edit to `portable/` (or the equivalent Skill tree)
plus a rebuild — never an automatic write. A candidacy without a detectable failure mode
and the decision point that catches it is rejected, not escalated; a promotion that cannot
name a clause it replaces or strengthens is prompt bloat and is rejected too. After
promotion the entry is `GENERALIZED` and keeps one pointer line so the same pitfall is not
re-proposed.

## What this layer is not

It is not a gate: no lesson blocks `READY`, changes a gate state, or alters an
authorization. It is not cross-project: entries live in this project's `.charter/`, and
only a user-confirmed promotion reaches the kit. And it is not a transcript: evidence is a
pointer, never a copy. An unhooked ledger dies — records that no workflow step reads or
reports become an empty directory of `.gitkeep` files; the distill, cite, and report hooks
above are what keep this one alive.
