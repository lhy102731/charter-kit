# Lessons

> Copy this file to `.charter/lessons.md` at initialization. It records the pitfalls this
> project actually hit and the defense for the next time. It is bounded project knowledge,
> not a gate: citing a lesson is advice, and no lesson changes a gate state or an
> authorization.

**Bounded size.** This file is in the required-start read set whenever it exists, so every
resume pays for it. Keep it at or under 8 KB. When it exceeds the bound, archive the weakest
entries (lowest hit count first, then oldest) to `.charter/lessons-archive.md` — outside the
required-start read set — and leave one pointer line per archived entry in the Archive
pointers section. Never archive an entry that a leaf cites as its defense basis or that
carries an open `GENERALIZE` candidacy; that promotion sweep mirrors the handoff archive
rule.

**One pitfall, one entry.** Before adding an entry, check whether the pitfall already has
one: a repeat hit updates that entry (hit count +1, evidence appended, defense revised)
instead of creating a duplicate. `LS-NNN` IDs are frozen, including after archival, so one
ID never names two different pitfalls. An entry whose pitfall no longer applies is marked
`RETIRED` rather than deleted, so its ID stays meaningful.

## Entries

- LS-001 | Status: ACTIVE | Hits: 0 | Source: `<TASK-ID> Events / Review / Change Triage>` | Date: `<YYYY-MM-DD>`
  - Pitfall: `<what situation led to what cost, one scannable sentence>`
  - Evidence: `<path under .charter/evidence/ or commit>`
  - Next defense: `<at which decision point, check what, and do what>`
  - Generalize candidate: NO

## Archive pointers

- `<LS-NNN> : see .charter/lessons-archive.md` (kept only after the first archival)
