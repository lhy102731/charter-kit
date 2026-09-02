# Task 3 Report — Lightweight Reuse Check

## Scope

Task 3 simplified the canonical Reuse Check record and made the five optional
reuse providers explicit. Generated `plugins/` and `targets/` mirrors were not
edited; they are reserved for Task 5 regeneration.

## RED

Added focused contract tests before changing canonical files:

```text
pytest tests/test_workflow_contract.py::WorkflowContractTests::test_reuse_record_separates_coverage_result_and_route \
       tests/test_workflow_contract.py::WorkflowContractTests::test_reuse_provider_roles_are_explicit \
       tests/test_workflow_contract.py::WorkflowContractTests::test_reuse_provider_metadata_is_mirrored_in_dependency_manifest -q
```

Observed expected failures: the old template lacked `NO_MATERIAL_TARGET` and
the `PENDING | COMPLETE | BLOCKED` gate vocabulary; the manifest and dependency
declaration lacked the five provider IDs and roles.

## GREEN

```text
pytest tests/test_workflow_contract.py tests/test_dependencies.py -q
27 passed, 48 subtests passed

python -m json.tool dependencies.json
completed successfully
```

## Implementation

- Rewrote `portable/templates/reuse-discovery.md` as one append-only,
  project-local record with:
  - material-target check (`YES | NO_MATERIAL_TARGET`);
  - `FAST → STANDARD → DEEP` progressive search;
  - separate Gate, coverage, result, candidate disposition, and final-route
    vocabularies;
  - exact query/evidence, immutable revision, privacy, authorization, and
    no-auto-install boundaries.
- Updated the project, roadmap, and Leaf templates to project the same Reuse
  fields without adding a second state machine or registry.
- Added explicit optional-provider roles and fallbacks for `reuse-first`,
  `framework-first-coding`, `reduce-reinvention`, `find-skills`, and
  `repo-to-skill` in `agentpack.yaml`, `dependencies.json`, and
  `DEPENDENCIES.md`.
- Added metadata tests for provider roles and status vocabulary separation.
- Changed the package purpose/scope wording to project-local governance and
  project-local handoff.

## Commits

- Implementation: `414ac6a` (`feat: make reuse checks progressive and lightweight`)
- Report: pending (created after the implementation commit)

## Intentional limitation

Canonical changes are not mirrored into generated distributions in this task.
Task 5 must regenerate and verify those byte-identical mirrors.
