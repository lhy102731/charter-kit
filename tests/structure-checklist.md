# Package Structure Check

The lightweight kit is valid only when these paths exist:

- `DEVELOPMENT_CHARTER.md`
- `LICENSE` — matches the MIT declaration in `.codex-plugin/plugin.json`
- `README.md`
- `DEPENDENCIES.md`
- `dependencies.json` — matches the dependency guide and is diagnostic metadata only
- `agentpack.yaml`
- `portable/templates/project-charter.md`
- `portable/templates/leaf-task.md`
- `portable/templates/reuse-discovery.md`
- `portable/templates/handoff.md`
- `portable/templates/review.md`
- `portable/templates/decision.md`
- `portable/templates/roadmap.md`
- `portable/templates/evidence-receipt.md`
- `portable/prompts/generic-bootstrap.md`
- `portable/prompts/codex-bootstrap.md`
- `portable/prompts/claude-bootstrap.md`
- `portable/prompts/gemini-bootstrap.md`
- `portable/prompts/deepseek-bootstrap.md`
- `portable/commands/charter-workflow.md`
- `targets/codex/` — Codex target source for the adapter layout
- `plugins/charter-kit/` — generated Codex distribution snapshot
- `.agents/plugins/marketplace.json` — repository marketplace manifest
- marketplace entry `charter-kit` with source path `./plugins/charter-kit`
- `skills/charter-workflow/SKILL.md`
- `skills/charter-workflow/references/tool-routing.md`
- `skills/charter-workflow/references/DEVELOPMENT_CHARTER.md`
- `skills/charter-workflow/references/design-interview.md`
- `skills/charter-workflow/templates/` — byte-identical copies of all eight `portable/templates/` files
- `scripts/validate_kit.py`
- `scripts/init_project.py`
- `tests/test_charter_kit.py` — standard-library behavior tests for backup, refusal, safe `--add-missing` migration, and validator gates

The generated `plugins/charter-kit/` includes only runtime helpers (`scripts/check_dependencies.py` and `scripts/init_project.py`); the repository-only builder and validator stay at the source root. The bundled copies under `skills/charter-workflow/` must never diverge from their package-root originals; `scripts/validate_kit.py` enforces real byte identity, including newline differences. The behavior tests cover complete `--force` backups, refusal without `--force`, safe `--add-missing` migration, safe handling of links and hardlinks, output-boundary protection, invalid plugin interface data, missing-roadmap blocking, separate project/leaf approval, reuse-discovery gate presence, `DRAFT → APPROVED` state mirroring, unresolved-review blocking, first-leaf state, the Codex target source, the generated plugin distribution, and the repository marketplace entry contract. The legacy root `.codex-plugin/` and `skills/` snapshot remains a migration compatibility copy until the new marketplace path is stable; maintainers do not hand-edit both layouts. The check is intentionally independent of a host plugin. A missing optional provider is not a package-structure failure.

## Documentation boundary checks

- `DEVELOPMENT_CHARTER.md` and `README.md` describe a project-local workflow and a single Portable Core; they do not promise cross-Agent communication, cross-Harness synchronization, a central service, or automatic installation.
- `README.md` contains both Chinese and English sections, links to the GitHub repository and official Codex documentation, and identifies Codex as the only currently verified target. Unverified targets are labeled `experimental` / `unverified` and have no supported-install command.
- The documented lifecycle includes `Change Triage`, `Reuse Assessment / Reuse Check`, `DRAFT → APPROVED → READY`, `Review`, `Verify`, and `PASS_CLOSED`. A new requirement must not silently expand the current Leaf.
- Reuse documentation separates gate status (`PENDING | COMPLETE | BLOCKED`), coverage, result, and final route. `NO_MATCH` requires evidence; `UNKNOWN`, `NOT_AUTHORIZED`, and `BLOCKED_TOOLING` cannot be silently converted to `BUILD_NEW`.
- Pressure scenarios include first start and Resume convergence, scope changes, stale reuse evidence, `NO_MATCH` versus `UNKNOWN`, and a new capability that returns to Change Triage.
