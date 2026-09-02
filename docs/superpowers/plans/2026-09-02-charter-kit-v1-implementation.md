# Charter Kit v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Align the portable Charter Kit workflow with the approved lightweight architecture by adding a canonical Change Triage entry, a proportional Reuse Check, unified working-set terminology, and thin independent Harness adapters.

**Architecture:** Keep one Portable Core expressed as Markdown, templates, prompts, and small standard-library scripts. Treat Change Triage as the only route for scope or fact changes and Reuse Check as a READY gate attached to a Leaf, not as a parallel platform. Generate the Codex distribution from the canonical source and leave other Harnesses as independently installable adapters.

**Tech Stack:** Markdown, Mermaid diagrams, YAML/JSON metadata, Python 3 standard library, unittest/pytest, and the existing Codex packaging scripts.

**Spec:** docs/superpowers/specs/2026-09-02-charter-kit-v1-architecture-design.md

## Global Constraints

- Portable Core is the only semantic source of truth.
- .charter/ is project-local persistent state; it is not a cross-Agent or cross-Harness communication service.
- The normal Leaf states are DRAFT → APPROVED → READY → IN_PROGRESS → REVIEW → VERIFIED → PASS_CLOSED.
- Change routes are IN_CONTRACT, LEAF_CHANGE, ROADMAP_CHANGE, CHARTER_CHANGE, and OUT_OF_SCOPE; routes are not states.
- Every Leaf performs a local Reuse Assessment; external search is progressive and authorized, not mandatory.
- NO_MATCH requires an executed search and evidence; UNKNOWN never silently becomes BUILD_NEW.
- Discovery, adoption, installation, copying, and execution require separate authorization.
- Review A and Verification are required for every Leaf; independent Review B is risk-triggered or explicitly required.
- AUTO_DEV covers only predeclared tasks, paths, effects, dependencies, repair budget, and stop conditions.
- Preserve the existing untracked $null file and all unrelated user changes.
- Do not install dependencies, contact external services, or delete existing DSH files as part of this plan.

---

### Task 1: Add the canonical Change Triage contract and normalize runtime templates

**Files:**
- Create: portable/references/change-triage.md
- Modify: portable/templates/project-charter.md
- Modify: portable/templates/roadmap.md
- Modify: portable/templates/leaf-task.md
- Modify: portable/templates/handoff.md
- Modify: portable/templates/decision.md
- Modify: portable/templates/review.md
- Modify: portable/templates/evidence-receipt.md
- Test: tests/test_workflow_contract.py

**Interfaces:**
- The reference defines event kinds NEW_REQUIREMENT, CLARIFICATION, DEFECT, DISCOVERED_CONSTRAINT, and RISK.
- The reference defines routes IN_CONTRACT, LEAF_CHANGE, ROADMAP_CHANGE, CHARTER_CHANGE, and OUT_OF_SCOPE, with precedence CHARTER > ROADMAP > LEAF > IN_CONTRACT.
- The runtime working set remains project.md, roadmap.md, current-task.md, reuse-discovery.md, decision.md, handoff.md, and evidence/.
- current-task.md is the active Leaf state authority; roadmap.md is a projection.

- [ ] **Step 1: Write failing contract tests**

Add tests that read the portable templates and assert:

~~~python
def test_change_triage_reference_defines_one_route_contract():
    text = read("portable/references/change-triage.md")
    assert "NEW_REQUIREMENT" in text
    assert "CHARTER > ROADMAP > LEAF > IN_CONTRACT" in text
    assert "New requirement must not silently expand the current Leaf" in text

def test_runtime_working_set_has_single_state_authority():
    current = read("portable/templates/leaf-task.md")
    roadmap = read("portable/templates/roadmap.md")
    assert "current-task.md is the active Leaf state authority" in roadmap
    assert "Change Triage event" in current
~~~

- [ ] **Step 2: Run the focused tests and confirm they fail**

Run: pytest tests/test_workflow_contract.py -q

Expected: FAIL because the reference file and canonical statements do not yet exist.

- [ ] **Step 3: Write the canonical reference and template sections**

Add one concise Change Triage section to the project, roadmap, Leaf, decision, review, handoff, and evidence templates. Keep useful acceptance and safety fields, but remove wording that treats handoff as communication or creates a second state machine. Make runtime file names unambiguous; template files are not runtime state files.

- [ ] **Step 4: Run focused tests and existing template tests**

Run: pytest tests/test_workflow_contract.py tests/test_generic_bootstrap.py -q

Expected: PASS.

- [ ] **Step 5: Commit the canonical contract**

~~~text
git add portable/references/change-triage.md portable/templates tests/test_workflow_contract.py
git commit -m "feat: add canonical change triage contract"
~~~

### Task 2: Integrate the single entry flow into commands, prompts, and the Skill

**Files:**
- Modify: portable/commands/charter-workflow.md
- Modify: portable/prompts/generic-bootstrap.md
- Modify: portable/prompts/codex-bootstrap.md
- Modify: portable/prompts/claude-bootstrap.md
- Modify: portable/prompts/gemini-bootstrap.md
- Modify: portable/prompts/deepseek-bootstrap.md
- Modify: skills/charter-workflow/SKILL.md
- Modify: skills/charter-workflow/references/tool-routing.md
- Test: tests/test_workflow_contract.py

**Interfaces:**
- Every entry point uses the same INIT, RESUME, and CHANGE routing.
- Every entry point names portable/references/change-triage.md as the fallback contract.
- Provider states remain AVAILABLE, MISSING, UNVERIFIED, and FALLBACK.
- A missing optional provider never becomes a silent claim that the provider ran.

- [ ] **Step 1: Extend failing tests for entry behavior**

Add assertions for every entry point:

~~~python
def test_all_entry_points_route_changes_through_change_triage():
    for relative in ENTRY_POINTS:
        text = read(relative)
        assert "Change Triage" in text
        assert "New requirement" in text
        assert "do not silently expand" in text.lower()
        assert "MISSING" in text
        assert "FALLBACK" in text
~~~

- [ ] **Step 2: Run the focused test and confirm the entry failures**

Run: pytest tests/test_workflow_contract.py::test_all_entry_points_route_changes_through_change_triage -q

Expected: FAIL for entries that do not yet mention the canonical route.

- [ ] **Step 3: Update the canonical command and generic prompt**

Describe Bootstrap, Resume, and Change Triage as one flow. State that Context Router is a workflow step, not a service. Make first start converge to the same READY Leaf loop as Resume. Add the four Change Triage questions and the targeted-Reuse trigger.

- [ ] **Step 4: Regenerate or mirror host prompts**

Update Codex, Claude, Gemini, DeepSeek, and generic prompts with the same semantic text. Host-specific files may differ only in entry syntax and resource lookup. They must not contain cross-Harness synchronization or cross-Agent dispatch claims.

- [ ] **Step 5: Update the bundled Skill and routing reference**

Keep the Skill self-contained. Route grill-me, j-space, Superpowers, and the five Reuse Skills by need; document the portable fallback for each. State that repo-to-skill is a separate authorized follow-up action.

- [ ] **Step 6: Run tests and commit**

Run: pytest tests/test_workflow_contract.py tests/test_generic_bootstrap.py tests/test_dependencies.py -q

~~~text
git add portable/commands portable/prompts skills/charter-workflow
git commit -m "feat: route every entry through change triage"
~~~

### Task 3: Simplify the Reuse Check record and provider metadata

**Files:**
- Modify: portable/templates/reuse-discovery.md
- Modify: portable/templates/project-charter.md
- Modify: portable/templates/roadmap.md
- Modify: portable/templates/leaf-task.md
- Modify: agentpack.yaml
- Modify: dependencies.json
- Modify: DEPENDENCIES.md
- Test: tests/test_workflow_contract.py
- Test: tests/test_dependencies.py

**Interfaces:**
- Reuse Gate states are PENDING, COMPLETE, and BLOCKED.
- Coverage values are SEARCHED, NOT_SEARCHED, NOT_AUTHORIZED, and BLOCKED_TOOLING.
- Result values are MATCH, NO_MATCH, and UNKNOWN.
- Final routes are ADOPT, ADAPT, REFERENCE_ONLY, BUILD_NEW, REUSE_SPIKE, and NEEDS_DECISION.

- [ ] **Step 1: Add failing Reuse contract tests**

Add tests requiring the template and manifest to contain separated field vocabulary and the five provider IDs:

~~~python
def test_reuse_record_separates_coverage_result_and_route():
    text = read("portable/templates/reuse-discovery.md")
    for phrase in ("SEARCHED", "NOT_AUTHORIZED", "MATCH", "NO_MATCH", "UNKNOWN",
                   "BUILD_NEW", "NO_MATERIAL_TARGET"):
        assert phrase in text
    assert "PENDING" in text and "COMPLETE" in text and "BLOCKED" in text

def test_reuse_provider_roles_are_explicit():
    manifest = read("agentpack.yaml")
    for provider in ("reuse-first", "framework-first-coding", "reduce-reinvention",
                     "find-skills", "repo-to-skill"):
        assert provider in manifest
~~~

- [ ] **Step 2: Run the focused tests and confirm they fail**

Run: pytest tests/test_workflow_contract.py::test_reuse_record_separates_coverage_result_and_route -q

Expected: FAIL until the simplified vocabulary is present.

- [ ] **Step 3: Rewrite the Reuse Discovery template around one record**

Keep one project-level file and append bounded records. Add the material-target test, FAST → STANDARD → DEEP search order, exact-query/evidence fields, fixed revision rule, and explicit authorization boundary. Remove requirements for a registry, scoring board, or separate memory database.

- [ ] **Step 4: Update manifest and dependency documentation**

Declare the five Reuse Skills as optional providers with their precise roles. Keep installation explicit-user-action-only. Change wording that calls cross-Agent handoff or a non-Codex Harness a required core feature.

- [ ] **Step 5: Run focused dependency and template tests**

Run: pytest tests/test_workflow_contract.py tests/test_dependencies.py -q

Expected: PASS with no secret-install or provider-simulation regressions.

- [ ] **Step 6: Commit the Reuse contract**

~~~text
git add portable/templates/project-charter.md portable/templates/roadmap.md portable/templates/leaf-task.md portable/templates/reuse-discovery.md agentpack.yaml dependencies.json DEPENDENCIES.md tests
git commit -m "feat: make reuse checks progressive and lightweight"
~~~

### Task 4: Update the canonical Charter and documentation boundary

**Files:**
- Modify: DEVELOPMENT_CHARTER.md
- Modify: README.md
- Modify: targets/codex/README.md
- Modify: plugins/charter-kit/README.md
- Modify: tests/pressure-scenarios.md
- Modify: tests/structure-checklist.md
- Test: tests/test_workflow_contract.py

**Interfaces:**
- The generic Charter describes project-local portability, not cross-Agent collaboration.
- README explains Codex as the currently verified adapter and labels unverified targets experimental.
- README remains bilingual where the release contract requires it.

- [ ] **Step 1: Add failing documentation-boundary tests**

Assert that the canonical Charter and README contain Change Triage, project-local wording, Reuse Assessment, and the no-automatic-install rule, and do not describe cross-Harness synchronization as a product feature.

- [ ] **Step 2: Run the documentation tests and confirm current drift**

Run: pytest tests/test_workflow_contract.py -q

Expected: FAIL on old cross-Agent wording or missing bilingual sections.

- [ ] **Step 3: Update the Charter**

Rewrite affected sections to match the approved v1 architecture while preserving authority, effects, evidence, Git, TDD, and closure rules. Keep domain-neutral language.

- [ ] **Step 4: Restore the bilingual release documentation**

Document the core workflow, Codex install/update/uninstall path, optional provider behavior, security boundary, and experimental-target policy. Do not advertise an unverified DSH install command as supported.

- [ ] **Step 5: Update pressure scenarios and structure checklist**

Add scenarios for first start, Resume, Change Triage, NO_MATCH versus UNKNOWN, and a new capability triggering a targeted Reuse Check.

- [ ] **Step 6: Run tests and commit**

Run: pytest tests/test_workflow_contract.py tests/test_generic_bootstrap.py -q

~~~text
git add DEVELOPMENT_CHARTER.md README.md targets/codex/README.md plugins/charter-kit/README.md tests/pressure-scenarios.md tests/structure-checklist.md tests/test_workflow_contract.py
git commit -m "docs: align charter kit with lightweight portable architecture"
~~~

### Task 5: Regenerate Codex mirrors and add adapter consistency checks

**Files:**
- Modify: scripts/build_codex_plugin.py
- Modify: scripts/validate_kit.py
- Modify: tests/test_charter_kit.py
- Modify: tests/test_dsh_target.py only if the target is explicitly marked experimental
- Generated: targets/codex/skills/charter-workflow/*
- Generated: plugins/charter-kit/*
- Generated: root legacy Codex snapshot when the builder requires it

**Interfaces:**
- Portable templates and references are copied byte-for-byte into the self-contained Codex Skill and generated distribution.
- Adapter and distribution versions are independent from the portable protocol version.
- DSH files remain untouched unless a separate explicit target decision is made; they cannot be used as evidence of supported installation.

- [ ] **Step 1: Add failing mirror and adapter assertions**

Require the new Change Triage reference to exist in the target Skill and generated distribution, require no cross-Harness sync claims in adapter README files, and require the builder to preserve canonical portable bytes.

- [ ] **Step 2: Run the focused assertions and confirm missing mirror failures**

Run: pytest tests/test_charter_kit.py -q

Expected: FAIL until the canonical changes are regenerated.

- [ ] **Step 3: Update builder and validator where the canonical file set requires it**

Include the new reference in the explicit package input list. Keep link, hardlink, traversal, and non-mutating checks. Replace old hard requirements that treat every target as a supported distribution with an explicit supported/experimental distinction.

- [ ] **Step 4: Run the deterministic builder**

Run: python scripts/build_codex_plugin.py

Expected: the target Skill, distribution, and legacy snapshot contain the same canonical bytes; no DSH source is modified.

- [ ] **Step 5: Run mirror and structure tests**

Run: pytest tests/test_charter_kit.py tests/test_dsh_target.py -q

Expected: PASS, with DSH tests limited to structural/experimental claims if retained.

- [ ] **Step 6: Commit generated mirrors**

~~~text
git add scripts/build_codex_plugin.py scripts/validate_kit.py targets/codex plugins/charter-kit .codex-plugin skills/charter-workflow tests
git commit -m "chore: regenerate portable codex adapter mirrors"
~~~

### Task 6: Full verification and independent review

**Files:**
- Modify: docs/superpowers/plans/2026-09-02-charter-kit-v1-implementation.md only for checklist status
- Review: all changed files
- Evidence: .charter/evidence/ when a project working set is used for the validation run

- [ ] **Step 1: Run the complete test suite**

Run: pytest -q

Expected: zero failures and no unexpected warnings.

- [ ] **Step 2: Run the repository validator and builder check**

Run: python scripts/validate_kit.py

Run: python scripts/build_codex_plugin.py --check

Expected: both exit successfully and report canonical mirror equality.

- [ ] **Step 3: Run the workflow pressure scenarios**

Exercise first start, Resume, new requirement triage, contract defect, Reuse UNKNOWN, and successful close. Record observed behavior and uncovered limits in the test or evidence record.

- [ ] **Step 4: Perform Review A and risk-triggered Review B**

Review scope: terminology consistency, single source of truth, no silent scope expansion, Reuse evidence semantics, authorization boundaries, adapter isolation, and domain neutrality.

- [ ] **Step 5: Re-read the specification and plan**

Mark every requirement covered, record any intentional limitation, and ensure no completion claim is made without fresh test and validator outputs.

- [ ] **Step 6: Commit the final verification record**

~~~text
git add docs/superpowers/plans/2026-09-02-charter-kit-v1-implementation.md
git commit -m "test: verify charter kit v1 workflow contract"
~~~
