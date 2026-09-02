# DSH Target Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **Status (2026-09-02): DEFERRED / EXPERIMENTAL.** The adapter shell and
> structural packager are retained for future work, but no DSH runtime smoke
> test has been completed. DSH is `experimental` / `unverified`; this plan and
> its artifacts must not be read as a supported-install promise. The main v1
> release treats Codex as the only verified target.

**Goal:** Retain a small DSH adapter shell for future validation while keeping the portable core independent of DSH and making no supported-install claim.

**Architecture:** `portable/` remains the semantic source of truth, `targets/dsh/` is only an adapter-development shell, and `plugins/dsh-charter-kit/` is a generated structural artifact. The validator checks consistency when those optional trees are present, but does not treat them as a supported runtime.

**Tech Stack:** JavaScript (ESM) for the adapter shell, Node.js built-ins only, and Python standard library for structural packaging and validation. A real DSH plugin loader is not assumed or invoked by this plan.

**Spec:** `docs/superpowers/specs/2026-09-01-multi-target-distribution-design.md` and the shared `DEVELOPMENT_CHARTER.md`.

## Global Constraints

- `portable/` remains the single semantic source of truth; target trees do not redefine the workflow.
- Generated distribution `plugins/dsh-charter-kit/` must be self-contained and must not contain symlinks, junctions, hard links, `__pycache__`, `.pyc`, or nested `targets/`/`plugins/` trees.
- The DSH plugin runtime imports only Node.js built-ins; it must not require npm dependencies at runtime.
- The DSH plugin registers the `charter-workflow` skill into `ctx.skills` and the `/charter-workflow` command into `ctx.commands`, both through `ctx.effect()` so unload/reload cleans them up.
- The plugin does not install or download superpowers / j-space / grill-me; it only ships the dependency checker and documents them as optional providers.
- All checks must be read-only and use only the Python standard library.

---

### Task 1: Add DSH adapter source

**Files:**
- Create: `targets/dsh/package.json`
- Create: `targets/dsh/src/index.js`
- Create: `targets/dsh/scripts/build.sh`
- Create: `targets/dsh/README.md`

**Interfaces:**
- Produces: DSH target package that `scripts/build_dsh_plugin.py` copies and builds into `plugins/dsh-charter-kit`.

- [ ] **Step 1: Add the failing test**

Create `tests/test_dsh_target.py` with tests that assert the target files exist and the package manifest is valid. Run it to verify it fails (files do not exist yet).

```python
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class DshTargetTest(unittest.TestCase):
    def test_target_package_json_exists(self):
        self.assertTrue((ROOT / 'targets/dsh/package.json').is_file())

    def test_target_plugin_entry_exists(self):
        self.assertTrue((ROOT / 'targets/dsh/src/index.js').is_file())

    def test_target_build_script_exists(self):
        self.assertTrue((ROOT / 'targets/dsh/scripts/build.sh').is_file())

    def test_package_manifest_valid(self):
        data = json.loads((ROOT / 'targets/dsh/package.json').read_text(encoding='utf-8'))
        self.assertEqual(data['name'], '@dsh-external/dsh-charter-kit')
        self.assertEqual(data['main'], './lib/index.js')

if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Write `targets/dsh/package.json`**

```json
{
  "name": "@dsh-external/dsh-charter-kit",
  "version": "0.2.0",
  "description": "DSH plugin distribution for Charter Kit: portable charter workflow, charter-workflow skill, and /charter-workflow command.",
  "private": true,
  "type": "module",
  "main": "./lib/index.js",
  "exports": {
    ".": "./lib/index.js",
    "./package.json": "./package.json"
  },
  "files": [
    "lib",
    "src",
    "scripts",
    "portable",
    "skills",
    "DEVELOPMENT_CHARTER.md",
    "DEPENDENCIES.md",
    "dependencies.json",
    "agentpack.yaml",
    "README.md",
    "LICENSE"
  ],
  "license": "MIT",
  "scripts": {
    "build": "bash scripts/build.sh"
  }
}
```

- [ ] **Step 3: Write `targets/dsh/src/index.js`**

```js
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')
const SKILL_DIR = join(ROOT, 'skills', 'charter-workflow')
const SKILL_FILE = join(SKILL_DIR, 'SKILL.md')
const COMMAND_FILE = join(ROOT, 'portable', 'commands', 'charter-workflow.md')

function parseFrontmatter(text) {
  const match = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/.exec(text)
  if (!match) return { description: 'Charter Kit development workflow', body: text.trimEnd() + '\n' }
  const meta = {}
  for (const line of match[1].split(/\r?\n/)) {
    const index = line.indexOf(':')
    if (index === -1) continue
    const key = line.slice(0, index).trim()
    let value = line.slice(index + 1).trim()
    if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1)
    }
    meta[key] = value
  }
  return {
    description: meta.description || 'Charter Kit development workflow',
    whenToUse: meta['when-to-use'] || meta.whenToUse,
    body: (match[2] || '').trimEnd() + '\n',
  }
}

function readCommandText() {
  return parseFrontmatter(readFileSync(COMMAND_FILE, 'utf8')).body
}

export const name = 'dsh-charter-kit'
export const inject = ['commands', 'skills']

export function apply(ctx) {
  const skill = parseFrontmatter(readFileSync(SKILL_FILE, 'utf8'))

  ctx.effect(() => ctx.commands.register({
    name: 'charter-workflow',
    description: 'Start or resume the host-neutral Charter Kit development workflow',
    input: { hint: 'optional one-sentence requirement' },
    handler: () => ({ kind: 'success', text: readCommandText() }),
  }), 'charter-kit: /charter-workflow')

  ctx.effect(() => ctx.skills.register({
    name: 'charter-workflow',
    description: skill.description,
    ...(skill.whenToUse ? { whenToUse: skill.whenToUse } : {}),
    source: 'runtime',
    provider: 'dsh-charter-kit',
    resourceBase: { kind: 'directory', path: SKILL_DIR },
    content: skill.body,
  }), 'charter-kit: skill')
}
```

- [ ] **Step 4: Write `targets/dsh/scripts/build.sh`**

```bash
#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p lib
cp src/index.js lib/index.js
echo "DSH Charter Kit build complete"
```

- [ ] **Step 5: Write `targets/dsh/README.md`**

```markdown
# DSH target

This directory is the DSH adapter source for Charter Kit. The generated,
self-contained DSH plugin lives at `plugins/dsh-charter-kit/`.

Build the DSH distribution from the repository root:

```text
python scripts/build_dsh_plugin.py
```

The built plugin registers the `charter-workflow` skill and the
`/charter-workflow` command. It does not install or download
superpowers / j-space / grill-me.
```

- [ ] **Step 6: Run tests**

Run: `python -B -m unittest tests.test_dsh_target -v`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add targets/dsh tests/test_dsh_target.py
git commit -m "feat: add dsh adapter source"
```

---

### Task 2: Add DSH distribution builder

**Files:**
- Create: `scripts/build_dsh_plugin.py`
- Modify: `scripts/validate_kit.py` only after the builder exists (Task 3 keeps validation in sync)

**Interfaces:**
- Consumes: `targets/dsh/`, `portable/`, `skills/charter-workflow`, root package documents.
- Produces: `plugins/dsh-charter-kit/` with `lib/index.js` and copied core/target content.
- Later tasks consume the generated `plugins/dsh-charter-kit/` tree.

- [ ] **Step 1: Write failing distribution tests first**

Extend `tests/test_dsh_target.py` with assertions that `plugins/dsh-charter-kit/package.json`, `plugins/dsh-charter-kit/lib/index.js`, and `plugins/dsh-charter-kit/src/index.js` exist. Run to verify failure before the builder runs.

- [ ] **Step 2: Implement `scripts/build_dsh_plugin.py`**

Implement a standard-library Python builder that:
- validates source/destination trees reject symlinks, junctions, hard links, and caches;
- copies `PACKAGE_ROOT_ITEMS` from the repository root;
- copies `targets/dsh/package.json`, `targets/dsh/src/`, `targets/dsh/scripts/`, and `targets/dsh/README.md`;
- copies `skills/charter-workflow` into the stage;
- runs `bash scripts/build.sh` inside the stage to emit `lib/index.js`;
- supports `--check` to compare a fresh stage with the committed distribution;
- writes the canonical output transactionally via a temp directory.

- [ ] **Step 3: Run builder**

Run: `python -B scripts/build_dsh_plugin.py`
Expected: builds `plugins/dsh-charter-kit/`.

- [ ] **Step 4: Run tests**

Run: `python -B -m unittest tests.test_dsh_target -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/build_dsh_plugin.py plugins/dsh-charter-kit tests/test_dsh_target.py
git commit -m "feat: build self-contained dsh distribution"
```

---

### Task 3: Extend repository validator for DSH

**Files:**
- Modify: `scripts/validate_kit.py`

**Interfaces:**
- Consumes: the generated `plugins/dsh-charter-kit/` tree and `targets/dsh/` source.
- Produces: validation PASS/FAIL including DSH target/distribution consistency.

- [ ] **Step 1: Add failing validation in a test-friendly way**

Add DSH target/distribution constants and a `check_dsh_target_and_distribution()` method. Add a test that runs `python scripts/validate_kit.py .` and expects PASS after the new method is implemented.

- [ ] **Step 2: Implement checks**

The method must check:
- `targets/dsh/` and `plugins/dsh-charter-kit/` tree safety;
- `targets/dsh/package.json` is valid JSON with name `@dsh-external/dsh-charter-kit`, semver version, MIT license, and `main: ./lib/index.js`;
- `targets/dsh/package.json`, `src/index.js`, `scripts/build.sh` are byte-identical to the distribution counterparts;
- `skills/charter-workflow` is byte-identical to `plugins/dsh-charter-kit/skills/charter-workflow`;
- root package documents are mirrored into the DSH distribution;
- `plugins/dsh-charter-kit/lib/index.js` exists and contains the plugin marker `export const name = 'dsh-charter-kit'`;
- the DSH distribution contains no nested `targets/` or `plugins/` trees.

- [ ] **Step 3: Run validator**

Run: `python -B scripts/validate_kit.py .`
Expected: PASS.

- [ ] **Step 4: Run full tests**

Run: `python -B -m unittest discover -s tests -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/validate_kit.py tests
git commit -m "feat: validate dsh target and distribution"
```

---

### Task 4: Record experimental status and finalize

**Files:**
- Modify: `README.md`

- [x] **Step 1: Record DSH as experimental / unverified**

The main README and DSH adapter README explicitly state that DSH has only
structural checks, has no supported-install command, and must not be treated as
verified. Optional providers remain non-installing.

- [ ] **Step 2: Run validator and tests**

Run `python -B scripts/validate_kit.py .` and `python -B -m unittest discover -s tests -q`. Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: document dsh installation"
```

---

### Task 5: DSH runtime smoke test (deferred)

- [ ] **Step 1: Build final distribution**

Run: `python -B scripts/build_dsh_plugin.py` to ensure the committed distribution is fresh.

- [ ] **Step 2: Inject into DSH**

Blocked pending a documented DSH runtime and installation contract. Do not
invent or publish `dev_inject_plugin`, `dev_install_package`, or similar
commands as support evidence.

- [ ] **Step 3: Confirm no regression**

Also deferred with the runtime smoke test. The structural builder and
repository validator are the only current DSH evidence.
