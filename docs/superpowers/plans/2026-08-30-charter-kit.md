# Charter Kit Implementation Plan

> Status: complete. All package and smoke checks below were performed. The surrounding workspace is not a Git repository, so the listed commit steps were recorded as not applicable rather than fabricated.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a lightweight, cross-agent development charter kit with a portable source of truth and an optional thin Codex entry point.

**Architecture:** The portable layer is Markdown/YAML templates and a practical development charter that can be read by any agent. The Codex layer contains only a short skill that routes an agent to the project `.charter/` files and the portable workflow. Optional Superpowers and J-space providers are documented, never required, and never installed silently.

**Tech Stack:** Markdown, YAML, JSON, Python standard library for an optional validator, Codex plugin manifest.

**Spec:** `DEVELOPMENT_CHARTER.md` and `agentpack.yaml` in this package.

## Global Constraints

- The core must work without Codex, Superpowers, J-space, a server, MCP, or a package manager.
- A host entry may route to the core but must not duplicate or redefine the charter.
- Dependency installation is explicit and user-controlled; plugin loading is read-only.
- The methodology must preserve goal correction, asset audit, leaf-task boundaries, evidence, review, integration, and post-merge verification.
- Missing optional providers must have a portable fallback.
- No production, real-data, holdout, or external side effect is authorized by this package.

---

### Task 1: Create package skeleton and portable metadata

**Files:**
- Create: `.codex-plugin/plugin.json`
- Create: `README.md`
- Create: `agentpack.yaml`
- Create: `docs/superpowers/plans/2026-08-30-charter-kit.md`

- [x] **Step 1: Write the failing structure check**

Record the required paths and manifest fields in `tests/structure-checklist.md`; the check should fail until the paths exist.

- [x] **Step 2: Run the structure check to verify it fails**

Run the package validator against the empty scaffold and confirm it reports missing portable files.

- [x] **Step 3: Write the minimal package metadata**

Add the manifest, package README, and provider metadata without adding an installer or service.

- [x] **Step 4: Run the structure check**

Run the validator and confirm the metadata paths are recognized.

- [x] **Step 5: Record completion**

The surrounding workspace is not a Git repository, so no commit was created.

### Task 2: Write the portable charter and templates

**Files:**
- Create: `DEVELOPMENT_CHARTER.md`
- Create: `portable/templates/project-charter.md`
- Create: `portable/templates/leaf-task.md`
- Create: `portable/templates/handoff.md`
- Create: `portable/templates/review.md`
- Create: `portable/templates/decision.md`

- [x] **Step 1: Write failing content checks**

Require the charter to contain both loops, success levels, effect boundaries, state transitions, evidence rules, tool routing, and the product/research distinction. Require each template to contain its required fields.

- [x] **Step 2: Run the checks and observe missing sections**

Run the validator before writing the documents; it must report missing sections.

- [x] **Step 3: Write the smallest complete charter and templates**

Use plain language, stable headings, explicit stop conditions, and examples that do not depend on a particular host.

- [x] **Step 4: Run the content checks**

Confirm all required sections and template fields are present and no placeholder markers remain.

- [x] **Step 5: Record completion**

The surrounding workspace is not a Git repository, so no commit was created.

### Task 3: Add host-neutral and host-specific entry prompts

**Files:**
- Create: `portable/prompts/generic-bootstrap.md`
- Create: `portable/prompts/codex-bootstrap.md`
- Create: `portable/prompts/claude-bootstrap.md`
- Create: `portable/prompts/gemini-bootstrap.md`
- Create: `portable/prompts/deepseek-bootstrap.md`
- Create: `skills/charter-workflow/SKILL.md`
- Create: `skills/charter-workflow/references/tool-routing.md`

- [x] **Step 1: Write failing routing checks**

Require each prompt to point to `.charter/project.md`, `.charter/current-task.md`, and `.charter/handoff.md`, and require the Skill to state that Superpowers/J-space are optional.

- [x] **Step 2: Run checks before implementation**

Confirm the routing files are absent or incomplete.

- [x] **Step 3: Write concise routing entries**

Keep the host files short; put the full method in the portable charter and map optional tools in the reference.

- [x] **Step 4: Run skill validation**

Run `quick_validate.py` on the skill and the package validator on all prompts.

- [x] **Step 5: Record completion**

The surrounding workspace is not a Git repository, so no commit was created.

### Task 4: Add an optional dependency/structure validator

**Files:**
- Create: `scripts/validate_kit.py`
- Create: `tests/structure-checklist.md`
- Create: `tests/pressure-scenarios.md`

- [x] **Step 1: Write failing validator tests**

Define checks for required paths, manifest identity, required charter headings, template fields, and no unfinished placeholders.

- [x] **Step 2: Run the validator in RED**

Run it before the final documents exist and record the expected failures in the test notes.

- [x] **Step 3: Implement a standard-library-only validator**

Make it read-only, return nonzero on missing or malformed package content, and print actionable messages. It must not install dependencies or modify files.

- [x] **Step 4: Run the validator in GREEN**

Run `python scripts/validate_kit.py .` and confirm exit code 0 with a summary of checked paths.

- [x] **Step 5: Record completion**

The surrounding workspace is not a Git repository, so no commit was created.

### Task 5: Verify plugin and package delivery

**Files:**
- Modify: `.codex-plugin/plugin.json` if metadata needs correction
- Modify: `README.md` if usage or dependency instructions are incomplete

- [x] **Step 1: Run the Codex plugin validator**

Run `python <plugin-creator>/scripts/validate_plugin.py <package-path>`.

- [x] **Step 2: Run the skill validator**

Run `python <skill-creator>/scripts/quick_validate.py skills/charter-workflow`.

- [x] **Step 3: Run the package validator and smoke scenarios**

Run the standard-library validator and manually exercise a new project, a blocked task, and a cross-agent handoff using only the portable files.

- [x] **Step 4: Review the final tree and dependency claims**

Confirm there is no installer, hook, network call, hidden global write, or mandatory Superpowers/J-space assumption.

- [x] **Step 5: Record completion**

The surrounding workspace is not a Git repository, so no commit was created.
