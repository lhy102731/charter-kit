# Charter Kit

Charter Kit is a small, host-neutral development governance workflow. It can start a project from an empty directory, guide the owner through an intent interview, turn the result into a project charter and a bounded task tree, and carry one leaf from approval to verified closure. The same Markdown/JSON working set can be read by different agents, hosts, CI jobs, or people.

## What it contains

- `DEVELOPMENT_CHARTER.md`: the method from requirements archaeology to delivery;
- `portable/templates/`: project charter, roadmap, leaf-task, reuse, handoff, review, decision, and evidence templates;
- `portable/prompts/`: a host-neutral bootstrap plus optional host adapters;
- `portable/commands/charter-workflow.md`: an explicit start/resume command;
- `skills/charter-workflow/`: a self-contained Skill with its own templates, charter, design interview, dependency checker, and manifest;
- `scripts/init_project.py`: safe local working-set initializer;
- `scripts/check_dependencies.py`: read-only capability probe with redacted logs;
- `scripts/validate_kit.py`: standard-library structural and consistency validator;
- `dependencies.json`: machine-readable capability declarations;
- `.codex-plugin/plugin.json`: an optional Codex packaging layer, not the portable protocol.

The core has no required model, vendor, framework, or network service. Superpowers, J-space, and grill-me/grilling are optional providers. When a provider is missing, the workflow reports the limitation and uses its portable fallback.

## Start a new project

You can start with the Skill, the command, a copied host prompt, or the portable files. None requires an existing `.charter/` directory.

1. When there is no `.charter/project.md`, create the standard working set and an empty `.charter/evidence/`. Preserve any existing file and add only missing templates.
2. Run the dependency checker and save its report. Use `grill-me`/`grilling` first for a multi-round intent interview; if it is unavailable, record `MISSING` and use the bundled design-interview checklist as `FALLBACK`.
3. Draft the project charter, roadmap, and one first `DRAFT` leaf. Complete self-review and a fresh independent charter review, then stop for project approval.
4. After project approval, complete the bounded reuse/prior-art discovery record before leaf approval. Search existing workspace assets, installed skills/plugins, approved internal resources, official/upstream resources, and authorized public sources in that order; record exact queries and raw evidence. Discovery never clones, builds, runs, imports, copies, installs, or loads candidate instructions. A `COMPLETE` record has no unresolved high-value `UNKNOWN`/`DEFER` remains unresolved.
5. Obtain separate approval for the first leaf (or matching `AUTO_DEV` preauthorization), move the task and roadmap together `DRAFT → APPROVED → READY`, and implement only that leaf.

For a new project, the product-specific answers belong in `.charter/project.md`; this package does not assume a particular domain or product loop.

## Dependency check and log

From the package root or a self-contained Skill directory:

```text
python scripts/check_dependencies.py --project <project-dir> --log-file <project-dir>/.charter/evidence/dependency-check.log
```

The checker performs local metadata-only probes and emits:

- `AVAILABLE`: detected and usable;
- `MISSING`: explicitly not found;
- `UNVERIFIED`: a host/human capability cannot be proven locally;
- `FALLBACK`: the portable replacement to use.

Every record includes capability, reason, impact, fallback, and user action. Required `MISSING`/`UNVERIFIED` results return a non-zero exit and keep the relevant object `BLOCKED_TOOLING`; optional gaps return zero and allow the fallback. No credentials, secrets, private source, or sensitive data should be supplied to the checker. It never installs, executes, imports, contacts the network, or writes a global directory.

If Python is unavailable, write the same fields manually in the evidence log. Dependency installation is always a separate, explicit user action.

## Explicit local initializer

With Python 3:

```text
python scripts/init_project.py <project-dir>
python scripts/init_project.py --add-missing <project-dir>
```

The initializer creates the eight working files and `evidence/`. It refuses to overwrite an existing working set. `--add-missing` only fills absent entries. `--force` is an exceptional migration mode: it validates links, makes a complete timestamped backup, and then replaces generated files. Review the backup before continuing.

## Continue an existing project

Read, in order: `.charter/project.md`, `.charter/roadmap.md`, `.charter/reuse-discovery.md`, `.charter/current-task.md`, then `.charter/handoff.md` if present. State the goal, active leaf/status, reuse gate, allowed effects, authorization reference, open finding, and one exact next action. If a required file is missing, add only that file and stop until the working set is readable.

Keep one active leaf (`WIP = 1`). Use RED → GREEN for code, preserve negative checks, use Review A for coverage, and use Review B only with a genuinely different reviewer in a fresh context/process. `PASS_CLOSED` requires final-candidate evidence, review, target-branch integration, and post-integration verification. A `NEXT_CANDIDATE` is not authorization.

## Host adapters

`portable/prompts/generic-bootstrap.md` is the canonical entry for an unknown host. The named prompts are optional adapters for hosts that have a conventional instruction file. Copy the matching text into the host's project-instruction location using its own documented mechanism; this copy is only an entry-point convenience, while the project `.charter/` files remain the shared source of truth.

| Adapter | Typical placement (verify with the host) |
|---|---|
| Generic | the host's project instruction mechanism |
| Codex-compatible | `AGENTS.md` or the host's configured instruction file |
| Claude-compatible | `CLAUDE.md` or the host's configured instruction file |
| Other hosts | paste or reference `generic-bootstrap.md` |

The `charter-workflow` Skill and the optional `/charter-workflow` command have the same name by design: the command is an explicit start/resume entry, while the Skill supplies trigger-based guidance. They read the same working set and are not separate workflows. A host that cannot load either can still use the portable templates and prompt.

## Optional providers

| Provider | Native help | Portable fallback |
|---|---|---|
| Superpowers | brainstorming, planning, TDD, debugging, review, verification | Charter checklists |
| J-space | long-task ledger, seam refresh, resume | handoff and ledger sections |
| grill-me / grilling | iterative intent and design questioning | `references/design-interview.md` |

Do not silently simulate a missing provider. Re-run the dependency checker after a user explicitly installs one and record the detected version/limitation.

## Reuse discovery

After the direction is approved and before the first leaf is authorized, complete `.charter/reuse-discovery.md`. Use the fixed scopes `LOCAL_ONLY`, `LOCAL_ECOSYSTEM`, or `FULL_EXTERNAL`; require `External read authorization` for non-local tiers. Record exact queries, raw outputs under `.charter/evidence/`, `NO_MATCH` evidence, out-of-scope `NOT_SEARCHED`/`NOT_AUTHORIZED`, license/security/maintenance/portability checks, and an immutable commit/tag/package version for every selected candidate. Candidate decisions are `ADOPT`, `ADAPT`, `REFERENCE_ONLY`, `REJECT`, `DEFER`, `UNKNOWN`, or `REUSE_SPIKE`; `BUILD_NEW` is a capability-level conclusion after the search. `COMPLETE` is unavailable while a high-value `UNKNOWN`/`DEFER` remains unresolved. Discovery is read-only and never clones, builds, runs, imports, copies, installs, loads candidate instructions, writes global directories, or uploads private source, secrets, or real data.

## Validate the package

With Python 3:

```text
python scripts/validate_kit.py .
```

The validator is read-only. It checks the portable core, optional host/plugin adapters, dependency manifest, bundled Skill mirrors, and required workflow language. It does not install packages or modify project state.

## Scope boundary

Project-specific runtimes, data sources, services, credentials, domain terminology, and production policies belong in that project's charter or a separate extension. They are not bundled into the generic core and are never authorized merely by mentioning them in a template.
