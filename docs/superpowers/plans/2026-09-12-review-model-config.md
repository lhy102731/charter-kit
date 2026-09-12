# Charter Kit DSH 评审模型配置 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让 DSH 用户在「插件配置」页为 Review A / Review B 各自指定模型，并由 `charter_review` 工具确定性地用该模型派发无上下文评审子代理。

**Architecture:** Charter Kit 的 DSH 插件宿主端注册一个设置命名空间 `charter-kit-review` 与一个 `charter_review` 工具；客户端新增一个手写的 closure-factory bundle，把一张卡片注册进 `settings.plugin.item`（key = 该命名空间）。工具读取配置，经 `ctx.subagents.start(...)` 的 `agentOptions` 覆盖模型，未配置时继承当前模型。Skill 文本改为 host-neutral 的条件分支，Codex / ZCode 行为不变。

**Tech Stack:** Node ESM（宿主插件，纯 JS，无构建步骤）、手写浏览器 closure-factory bundle（仅 `require('react')`）、`@deepseek-ai/schemastery`、`@deepseek-ai/dsh-tools`、Python 3（构建器与校验器、unittest）。

**Spec:** `docs/superpowers/specs/2026-09-12-review-model-config-design.md`

## Global Constraints

- **不新增构建步骤**：仓库的构建器是纯 Python，必须保持无需 Node 工具链即可运行。客户端 bundle 手写为 plain JS，直接提交。
- **不新增第三方依赖**：宿主端只允许 `@deepseek-ai/schemastery` 与 `@deepseek-ai/dsh-tools`（已由 spike 证明可从外部插件解析）；客户端只允许 `require('react')`。
- **客户端 bundle 的模块 id 必须是包名**：`@dsh-external/dsh-charter-kit`。
- **卡片必须按命名空间 key 注册**：`settings.plugin.item` 的 `key` 必须等于宿主注册的命名空间 `charter-kit-review`。
- **SKILL.md 有三份手工源，必须同一次改动全部编辑**：root `skills/charter-workflow/SKILL.md`、`targets/codex/skills/charter-workflow/SKILL.md`、`targets/zcode/skills/charter-workflow/SKILL.md`。
- **构建顺序固定**：codex → zcode → dsh → validate。DSH 构建器把 root `skills/` 当输入。
- **`targets/dsh/` 是手工源树，不得出现 `GENERATED.md`**；`plugins/**` 是生成树，永不手工编辑。
- **`defineTool` 的 `output` 必须提供 `render`**（spike 实测：缺失会在执行成功后报 `output.render failed`）。
- **版本号**：DSH 包版本从 `0.2.0` 升到 `0.3.0`。
- 命名空间：`charter-kit-review`；工具名：`charter_review`；设置字段：`reviewAProvider` / `reviewAModel` / `reviewBProvider` / `reviewBModel`，空字符串表示「跟随当前模型」。

---

## File Structure

| 文件 | 职责 |
| --- | --- |
| `targets/dsh/src/index.js`（改） | 宿主：注册命名空间 + `charter_review` 工具；保留 skill 注册 |
| `targets/dsh/client/client.js`（新建） | 浏览器：卡片 bundle（手写，提交） |
| `targets/dsh/package.json`（改） | `dsh.client` 声明、`exports["./client"]`、版本号 |
| `targets/dsh/README.md`（改） | 说明卡片与工具 |
| `scripts/build_dsh_plugin.py`（改） | 把 `client/` 复制进发行包 |
| `scripts/validate_kit.py`（改） | 发行包必须含客户端产物且字节一致 |
| `skills/charter-workflow/SKILL.md`（改） | Review A/B 条件分支与记录语义 |
| `targets/codex/skills/charter-workflow/SKILL.md`（改） | 同上（手工源） |
| `targets/zcode/skills/charter-workflow/SKILL.md`（改） | 同上（手工源） |
| `tests/test_dsh_review_tool.py`（新建） | 宿主端结构契约测试 |
| `tests/test_dsh_client_card.py`（新建） | 客户端 bundle 结构契约测试 |
| `tests/test_workflow_contract.py`（改） | SKILL 文本条件分支断言 |

---

### Task 1: 宿主端命名空间与 `charter_review` 工具

**Files:**
- Modify: `targets/dsh/src/index.js`
- Test: `tests/test_dsh_review_tool.py`

**Interfaces:**
- Consumes: 无（本任务是链路的起点）
- Produces: 环境变量无；导出常量 `REVIEW_SETTINGS_NAMESPACE = 'charter-kit-review'`；工具 `charter_review(kind: 'A'|'B', brief: string)` 返回 `{ outcome, model, routeFallbackReason?, review }`

- [ ] **Step 1: 写失败测试**

创建 `tests/test_dsh_review_tool.py`：

```python
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "targets/dsh/src/index.js"


class DshReviewToolTest(unittest.TestCase):
    def setUp(self):
        self.text = SOURCE.read_text(encoding="utf-8")

    def test_declares_review_settings_namespace(self):
        self.assertIn("charter-kit-review", self.text)

    def test_registers_settings_section(self):
        self.assertIn("installSection", self.text)

    def test_declares_the_four_settings_fields(self):
        for field in ("reviewAProvider", "reviewAModel", "reviewBProvider", "reviewBModel"):
            self.assertIn(field, self.text)

    def test_registers_charter_review_tool(self):
        self.assertIn("charter_review", self.text)
        self.assertIn("ctx.tools.register", self.text)

    def test_tool_output_provides_render(self):
        # Spike finding: output without render fails after a successful execute.
        self.assertIn("render:", self.text)

    def test_wires_model_override_through_agent_options(self):
        self.assertIn("agentOptions", self.text)
        self.assertIn("ctx.subagents.start", self.text)

    def test_injects_required_services(self):
        for service in ("'skills'", "'tools'", "'settings'", "'subagents'"):
            self.assertIn(service, self.text)

    def test_no_handler_style_slash_command(self):
        self.assertNotIn("ctx.commands.register", self.text)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m unittest tests.test_dsh_review_tool -v`
Expected: FAIL — `test_registers_charter_review_tool` 等因当前源码没有这些符号而失败。

- [ ] **Step 3: 实现宿主端**

用以下内容整体替换 `targets/dsh/src/index.js`：

```js
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'
import z from '@deepseek-ai/schemastery'
import { defineTool } from '@deepseek-ai/dsh-tools'

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')
const SKILL_DIR = join(ROOT, 'skills', 'charter-workflow')
const SKILL_FILE = join(SKILL_DIR, 'SKILL.md')

/** Settings namespace keying the Review A/B model card. Its key IS the card key. */
export const REVIEW_SETTINGS_NAMESPACE = 'charter-kit-review'

/** Empty provider or model means "inherit the calling session's model". */
const REVIEW_SETTINGS_SCHEMA = z.object({
  reviewAProvider: z.string().default(''),
  reviewAModel: z.string().default(''),
  reviewBProvider: z.string().default(''),
  reviewBModel: z.string().default(''),
})

const REVIEW_SETTINGS_DEFAULTS = {
  reviewAProvider: '',
  reviewAModel: '',
  reviewBProvider: '',
  reviewBModel: '',
}

/**
 * Read one review route out of the settings value.
 * @param value - effective settings value.
 * @param kind - review kind, 'A' or 'B'.
 * @returns the route, or null when the review inherits the current model.
 */
function reviewRoute(value, kind) {
  const provider = value[kind === 'B' ? 'reviewBProvider' : 'reviewAProvider']
  const model = value[kind === 'B' ? 'reviewBModel' : 'reviewAModel']
  return provider === '' || model === '' ? null : { provider, model }
}

/**
 * Pick the delegation provider: the deployment's spawn provider, else a sole one.
 * @param ctx - host plugin context.
 * @returns provider name, or undefined when the choice is ambiguous or empty.
 */
function pickSubagentProvider(ctx) {
  const names = ctx.subagents.list()
  if (names.includes('spawn')) return 'spawn'
  return names.length === 1 ? names[0] : undefined
}

/**
 * Flatten one settled child result into its assistant text.
 * @param result - settled SubagentResult.
 * @returns trimmed text of every text block.
 */
function outputText(result) {
  return (result.output ?? [])
    .filter(part => part.type === 'text')
    .map(part => part.text)
    .join('')
    .trim()
}

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

export const name = 'dsh-charter-kit'
export const inject = ['skills', 'tools', 'settings', 'subagents']

export function apply(ctx) {
  const skill = parseFrontmatter(readFileSync(SKILL_FILE, 'utf8'))

  let reviewSettings = () => REVIEW_SETTINGS_DEFAULTS
  ctx.settings.installSection(
    ctx,
    REVIEW_SETTINGS_NAMESPACE,
    REVIEW_SETTINGS_SCHEMA,
    REVIEW_SETTINGS_DEFAULTS,
    {
      setSource: (source) => { reviewSettings = source },
      validate: () => {},
      onChange: () => {},
    },
  )

  // No handler-style slash command is registered. A typed line such as
  // `/charter-workflow <requirement>` therefore reaches the model as an
  // ordinary user message (matching Codex behavior); the model loads the
  // `charter-workflow` skill below and actually starts the workflow.
  ctx.effect(() => ctx.skills.register({
    name: 'charter-workflow',
    description: skill.description,
    ...(skill.whenToUse ? { whenToUse: skill.whenToUse } : {}),
    source: 'runtime',
    provider: 'dsh-charter-kit',
    resourceBase: { kind: 'directory', path: SKILL_DIR },
    content: skill.body,
  }), 'charter-kit: skill')

  ctx.tools.register(defineTool({
    name: 'charter_review',
    description: 'Run one context-free Charter Kit review with the model configured for that review kind. '
      + 'Use kind "A" for every leaf\'s contract and implementation coverage review, and kind "B" for the '
      + 'adversarial review required by a hit RVB trigger. The reviewer receives only the brief you pass — '
      + 'never the session history — and the returned model names the model that actually ran.',
    parameters: {
      kind: {
        type: 'string',
        required: true,
        description: 'Review kind: "A" for coverage review, "B" for the RVB-triggered adversarial review.',
      },
      brief: {
        type: 'string',
        required: true,
        description: 'Self-contained review brief: the leaf contract, the spec, and the candidate diff. '
          + 'The reviewer sees nothing else, so never include session history.',
      },
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          outcome: { type: 'string', required: true },
          model: { type: 'string', required: true },
          routeFallbackReason: { type: 'string' },
          review: { type: 'string', required: true },
        },
      },
      render: (_args, value) => [{ type: 'text', text: JSON.stringify(value) }],
    },
    async execute(args, exec) {
      const kind = args.kind === 'B' ? 'B' : 'A'
      const configured = reviewRoute(reviewSettings(), kind)
      const parent = exec.agent
      const providerName = pickSubagentProvider(ctx)
      const prompt = [{ type: 'text', text: args.brief }]

      const runOnce = async (agentOptions) => {
        const run = await ctx.subagents.start(providerName, {
          prompt,
          parent,
          signal: exec.signal,
          ...(agentOptions === null ? {} : { agentOptions }),
        })
        try {
          return await run.result
        } finally {
          await run.dispose()
        }
      }

      if (parent === undefined || providerName === undefined) {
        return {
          outcome: 'unavailable',
          model: 'inherited',
          review: '',
          routeFallbackReason: parent === undefined
            ? 'no calling agent'
            : 'no unambiguous subagent provider',
        }
      }

      if (configured === null) {
        return { outcome: 'reviewed', model: 'inherited', review: outputText(await runOnce(null)) }
      }

      const label = `${configured.provider}/${configured.model}`
      const capable = ctx.subagents.getProvider(providerName)?.capabilities?.agentOptions === true
      if (!capable) {
        return {
          outcome: 'fallback',
          model: 'inherited',
          review: outputText(await runOnce(null)),
          routeFallbackReason: `${label} not used: provider does not support child agent options`,
        }
      }
      try {
        return { outcome: 'reviewed', model: label, review: outputText(await runOnce(configured)) }
      } catch (error) {
        return {
          outcome: 'fallback',
          model: 'inherited',
          review: outputText(await runOnce(null)),
          routeFallbackReason: `${label} unavailable: ${error instanceof Error ? error.message : String(error)}`,
        }
      }
    },
  }))
}
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m unittest tests.test_dsh_review_tool -v`
Expected: PASS（8 个测试）。

- [ ] **Step 5: 提交**

```bash
git add targets/dsh/src/index.js tests/test_dsh_review_tool.py
git commit -m "feat: add charter_review tool and review-model settings namespace"
```

---

### Task 2: 客户端卡片 bundle

**Files:**
- Create: `targets/dsh/client/client.js`
- Test: `tests/test_dsh_client_card.py`

**Interfaces:**
- Consumes: Task 1 的命名空间 `charter-kit-review` 与四个字段名。
- Produces: 一个 closure-factory bundle，注册 `settings.plugin.item` 且 `key === 'charter-kit-review'`。

- [ ] **Step 1: 写失败测试**

创建 `tests/test_dsh_client_card.py`：

```python
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "targets/dsh/client/client.js"


class DshClientCardTest(unittest.TestCase):
    def setUp(self):
        self.text = BUNDLE.read_text(encoding="utf-8")

    def test_bundle_exists(self):
        self.assertTrue(BUNDLE.is_file())

    def test_registers_under_the_package_module_id(self):
        self.assertIn("window.__ModuleLoader__.load(", self.text)
        self.assertIn("@dsh-external/dsh-charter-kit", self.text)

    def test_requires_only_platform_modules(self):
        for specifier in ("react",):
            self.assertIn(f"require('{specifier}')", self.text)
        self.assertNotIn("require('@deepseek-ai/dsh-client-ui-settings", self.text)

    def test_registers_the_plugin_card_by_namespace_key(self):
        self.assertIn("settings.plugin.item", self.text)
        self.assertIn("charter-kit-review", self.text)

    def test_binds_the_settings_scope_and_model_catalog(self):
        self.assertIn("settingsScope", self.text)
        self.assertIn("modelCatalog", self.text)

    def test_declares_exported_face(self):
        self.assertIn("exports.apply", self.text)
        self.assertIn("exports.inject", self.text)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m unittest tests.test_dsh_client_card -v`
Expected: FAIL — 文件不存在。

- [ ] **Step 3: 写客户端 bundle**

创建 `targets/dsh/client/client.js`：

```js
/**
 * Charter Kit review-model card: the browser half of the DSH adapter.
 *
 * Hand-written closure-factory bundle in the DSH client-module convention.
 * It is committed as source (the repository's builders are pure Python and
 * must stay runnable without a Node toolchain), so keep it plain ES2020 and
 * require only modules from the shell's frozen platform table:
 * react, react/jsx-runtime, react-dom, react-dom/client, @deepseek-ai/cordis,
 * @deepseek-ai/dsh-client-store, @deepseek-ai/dsh-client-ui-slots,
 * @deepseek-ai/dsh-client-ui-primitives, @deepseek-ai/dsh-client-ui-dockkit.
 *
 * The card is keyed by the settings namespace the Host half registers, which
 * is what lets a plugin distributed outside the harness contribute a card.
 */
window.__ModuleLoader__.load({
  id: '@dsh-external/dsh-charter-kit',
  factory: (require) => {
    const module = { exports: {} }
    const exports = module.exports
    const React = require('react')
    const h = React.createElement

    const NS = 'charter-kit-review'
    const INHERIT = ''

    const zh = {
      title: 'Charter Kit 评审模型',
      description: '为 Review A / Review B 指定模型；未指定时跟随当前会话模型。',
      reviewA: 'Review A（契约与实现覆盖）',
      reviewB: 'Review B（对抗性评审）',
      inherit: '默认（跟随当前模型）',
      unavailable: '不可用',
      saving: '保存中…',
      saved: '已保存',
      failed: '保存失败',
      loadFailed: '模型目录加载失败',
      sameModel: 'A 与 B 使用同一模型；Review B 要求独立评审者，建议选不同模型。',
    }
    const en = {
      title: 'Charter Kit review models',
      description: 'Choose the model for Review A / Review B. Unset follows the current session model.',
      reviewA: 'Review A (contract and implementation coverage)',
      reviewB: 'Review B (adversarial review)',
      inherit: 'Default (follow current model)',
      unavailable: 'Unavailable',
      saving: 'Saving…',
      saved: 'Saved',
      failed: 'Save failed',
      loadFailed: 'Could not load the model catalog',
      sameModel: 'A and B share one model; Review B expects an independent reviewer — consider two models.',
    }

    /** @param route - provider/model route, or null for inherit. */
    function optionValue(route) {
      return route === null ? INHERIT : `${route.provider}\u0000${route.model}`
    }

    /** @param value - option value. */
    function parseOptionValue(value) {
      if (value === INHERIT) return null
      const at = value.indexOf('\u0000')
      if (at < 0) return null
      return { provider: value.slice(0, at), model: value.slice(at + 1) }
    }

    /** Read one stored route out of the settings value. */
    function storedRoute(value, providerField, modelField) {
      if (value[providerField] === '' || value[modelField] === '') return null
      return { provider: value[providerField], model: value[modelField] }
    }

    function ReviewModelCard(props) {
      const { scope, loadCatalog, t } = props
      const [snapshot, setSnapshot] = React.useState(() => scope.getSnapshot())
      const [groups, setGroups] = React.useState(null)
      const [catalogFailed, setCatalogFailed] = React.useState(false)
      const [status, setStatus] = React.useState('')

      React.useEffect(() => scope.subscribe(() => { setSnapshot(scope.getSnapshot()) }), [scope])
      React.useEffect(() => {
        let live = true
        loadCatalog().then(
          (value) => { if (live) setGroups(value) },
          () => { if (live) setCatalogFailed(true) },
        )
        return () => { live = false }
      }, [loadCatalog])

      // A card renders nothing while its namespace is unavailable, matching
      // the shell's own cards: no trace beats a card nobody can act on.
      if (snapshot.status !== 'ready') return null

      const value = snapshot.value ?? {}
      const writable = snapshot.writable === true
      const routeA = storedRoute(value, 'reviewAProvider', 'reviewAModel')
      const routeB = storedRoute(value, 'reviewBProvider', 'reviewBModel')

      const options = [h('option', { key: '__inherit', value: INHERIT }, t('inherit'))]
      const seen = new Set([INHERIT])
      for (const group of groups ?? []) {
        for (const model of group.models) {
          const key = optionValue({ provider: group.id, model: model.id })
          seen.add(key)
          options.push(h('option', { key, value: key }, `${model.name} — ${group.name}`))
        }
      }
      for (const route of [routeA, routeB]) {
        if (route === null) continue
        const key = optionValue(route)
        if (seen.has(key)) continue
        seen.add(key)
        options.push(h('option', { key, value: key }, `${route.provider}/${route.model} — ${t('unavailable')}`))
      }

      const write = (providerField, modelField, selected) => {
        const route = parseOptionValue(selected)
        setStatus(t('saving'))
        scope.mutate([
          { op: 'set', path: [providerField], value: route === null ? '' : route.provider },
          { op: 'set', path: [modelField], value: route === null ? '' : route.model },
        ], snapshot.revision).then(
          () => { setStatus(t('saved')) },
          () => { setStatus(t('failed')) },
        )
      }

      const select = (label, providerField, modelField, route) => h(
        'label',
        { className: 'ck-row' },
        h('span', { className: 'ck-label' }, label),
        h('select', {
          className: 'ck-select',
          value: optionValue(route),
          disabled: !writable,
          onChange: (event) => { write(providerField, modelField, event.target.value) },
        }, options),
      )

      const sameModel = routeA !== null && routeB !== null
        && routeA.provider === routeB.provider && routeA.model === routeB.model

      return h(
        'li',
        { className: 'ck-card' },
        h('div', { className: 'ck-head' },
          h('span', { className: 'ck-title' }, t('title')),
          h('span', { className: 'ck-desc' }, t('description'))),
        h('div', { className: 'ck-body' },
          select(t('reviewA'), 'reviewAProvider', 'reviewAModel', routeA),
          select(t('reviewB'), 'reviewBProvider', 'reviewBModel', routeB),
          catalogFailed ? h('p', { className: 'ck-note' }, t('loadFailed')) : null,
          sameModel ? h('p', { className: 'ck-note' }, t('sameModel')) : null,
          status === '' ? null : h('p', { className: 'ck-status' }, status)),
      )
    }

    const STYLE = [
      '.ck-card{list-style:none;border:1px solid var(--dsw-alias-border-l2,#e5e5e5);border-radius:8px;padding:12px 14px;margin-bottom:8px}',
      '.ck-head{display:flex;flex-direction:column;gap:2px;margin-bottom:10px}',
      '.ck-title{font-size:14px;font-weight:600;color:var(--dsw-alias-label-primary,#111)}',
      '.ck-desc{font-size:12px;color:var(--dsw-alias-label-secondary,#666)}',
      '.ck-body{display:flex;flex-direction:column;gap:10px}',
      '.ck-row{display:flex;align-items:center;gap:10px}',
      '.ck-label{flex:0 0 210px;font-size:13px;color:var(--dsw-alias-label-primary,#111)}',
      '.ck-select{flex:1;min-width:0;padding:6px 8px;border-radius:6px;font-size:13px;'
        + 'border:1px solid var(--dsw-alias-border-l2,#ccc);background:var(--dsw-alias-bg-base,#fff);'
        + 'color:var(--dsw-alias-label-primary,#111)}',
      '.ck-note{margin:0;font-size:12px;color:var(--dsw-alias-label-secondary,#666)}',
      '.ck-status{margin:0;font-size:12px;color:var(--dsw-alias-label-secondary,#666)}',
    ].join('')

    exports.inject = ['slots', 'settingsScope', 'remote.session', 'locale']

    exports.apply = function apply(ctx) {
      ctx.effect(
        () => ctx.locale.register(NS, { zh, en }),
        'charter-kit: review card dictionaries',
      )
      const t = ctx.locale.bind(NS)
      const scope = ctx.settingsScope.bind({ namespace: NS })
      const styleId = `charter-kit-review-card`
      if (document.querySelector(`style[data-plugin-css="${styleId}"]`) === null) {
        const tag = document.createElement('style')
        tag.dataset.plugin = 'dsh-charter-kit'
        tag.dataset.pluginCss = styleId
        tag.textContent = STYLE
        document.head.appendChild(tag)
      }
      ctx.slots.inject('settings.plugin.item', () => ctx.slots.register({
        name: 'settings.plugin.item',
        key: NS,
        locale: NS,
        inject: () => ({
          scope,
          loadCatalog: () => ctx.remote.session.modelCatalog().then((response) => {
            if (!response.ok) throw new Error('model catalog unavailable')
            return response.value.groups
          }),
          t,
        }),
      }, ReviewModelCard))
    }

    return module.exports
  },
})
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m unittest tests.test_dsh_client_card -v`
Expected: PASS（6 个测试）。

- [ ] **Step 5: 语法自检**

Run: `node --check targets/dsh/client/client.js`
Expected: 无输出，退出码 0。

- [ ] **Step 6: 提交**

```bash
git add targets/dsh/client/client.js tests/test_dsh_client_card.py
git commit -m "feat: add the review-model settings card bundle"
```

---

### Task 3: 包清单声明

**Files:**
- Modify: `targets/dsh/package.json`
- Test: `tests/test_dsh_target.py`（追加用例）

**Interfaces:**
- Consumes: Task 2 的 `client/client.js` 路径。
- Produces: `exports["./client"]`、`dsh.client.inject`、`dsh.client.platform`、版本 `0.3.0`。

- [ ] **Step 1: 写失败测试**

向 `tests/test_dsh_target.py` 的 `DshTargetTest` 类追加：

```python
    def test_declares_the_client_bundle(self):
        data = json.loads((ROOT / "targets/dsh/package.json").read_text(encoding="utf-8"))
        self.assertEqual(data["exports"]["./client"], "./client/client.js")
        client = data["dsh"]["client"]
        self.assertEqual(client["platform"], "web")
        self.assertIsInstance(client["inject"], list)

    def test_target_version_is_0_3_0(self):
        data = json.loads((ROOT / "targets/dsh/package.json").read_text(encoding="utf-8"))
        self.assertEqual(data["version"], "0.3.0")
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m unittest tests.test_dsh_target -v`
Expected: FAIL — `KeyError: './client'`。

- [ ] **Step 3: 更新清单**

修改 `targets/dsh/package.json`：

```json
{
  "name": "@dsh-external/dsh-charter-kit",
  "version": "0.3.0",
  "description": "DSH plugin distribution for Charter Kit: portable charter workflow, the model-driven charter-workflow skill, and the Review A/B model card.",
  "private": true,
  "type": "module",
  "main": "./lib/index.js",
  "exports": {
    ".": "./lib/index.js",
    "./client": "./client/client.js",
    "./package.json": "./package.json"
  },
  "files": [
    "lib",
    "src",
    "client",
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
  },
  "dsh": {
    "client": {
      "inject": [
        "@deepseek-ai/dsh-client-ui-settings-plugins"
      ],
      "platform": "web"
    }
  }
}
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m unittest tests.test_dsh_target -v`
Expected: PASS。

- [ ] **Step 5: 提交**

```bash
git add targets/dsh/package.json tests/test_dsh_target.py
git commit -m "feat: declare the dsh client bundle in the DSH target manifest"
```

---

### Task 4: 构建器与校验器接线

**Files:**
- Modify: `scripts/build_dsh_plugin.py`
- Modify: `scripts/validate_kit.py`
- Test: `tests/test_dsh_target.py`（追加分发断言）

**Interfaces:**
- Consumes: `targets/dsh/client/client.js`。
- Produces: `plugins/dsh-charter-kit/client/client.js` 与目标树字节一致，且出现在 `--check` 比对中。

- [ ] **Step 1: 写失败测试**

向 `tests/test_dsh_target.py` 追加：

```python
    def test_distribution_ships_the_client_bundle(self):
        self.assertTrue((ROOT / "plugins/dsh-charter-kit/client/client.js").is_file())

    def test_distribution_client_matches_target(self):
        source = (ROOT / "targets/dsh/client/client.js").read_bytes()
        distributed = (ROOT / "plugins/dsh-charter-kit/client/client.js").read_bytes()
        self.assertEqual(source, distributed)
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m unittest tests.test_dsh_target -v`
Expected: FAIL — 分发目录还没有 `client/`。

- [ ] **Step 3: 让构建器复制客户端产物**

在 `scripts/build_dsh_plugin.py` 中：

1. 在 `TARGET_FILES` 之后新增声明：

```python
CLIENT_DIR_NAME = "client"
CLIENT_ENTRY_NAME = "client.js"
```

2. 在 `DISTRIBUTION_ROOT_ITEMS` 里加入 `"client"`。

3. 在构建流程中，`TARGET_FILES` 复制完成之后、写 `GENERATED.md` 之前，加入客户端整目录复制：

```python
    client_source = source_root / TARGET_RELATIVE / CLIENT_DIR_NAME
    if not (client_source / CLIENT_ENTRY_NAME).is_file():
        raise OSError(
            f"DSH target is missing {CLIENT_DIR_NAME}/{CLIENT_ENTRY_NAME}; "
            "the package declares dsh.client and would fail to load without it"
        )
    copy_tree(client_source, stage_root / CLIENT_DIR_NAME)
```

- [ ] **Step 4: 让校验器比较客户端产物**

在 `scripts/validate_kit.py` 的 `check_dsh_target_and_distribution` 中，紧随现有的 `DSH_TARGET_SRC_RELATIVE` / `DSH_DISTRIBUTION_SRC_RELATIVE` 字节比较之后加入：

```python
        self._compare_file_bytes(
            DSH_TARGET_CLIENT_RELATIVE,
            DSH_DISTRIBUTION_CLIENT_RELATIVE,
            label="DSH target/distribution client bundle",
        )
```

并在常量区（`DSH_TARGET_SRC_RELATIVE` 附近）新增：

```python
DSH_TARGET_CLIENT_RELATIVE = "targets/dsh/client/client.js"
DSH_DISTRIBUTION_CLIENT_RELATIVE = "plugins/dsh-charter-kit/client/client.js"
```

同时把 `plugins/dsh-charter-kit/` 的顶层允许集合补上 `client`——即在该方法已有的 `expected_top_level` 集合里加入 `"client"`。

- [ ] **Step 5: 重新生成并跑测试**

```bash
python scripts/build_codex_plugin.py
python scripts/build_zcode_plugin.py
python scripts/build_dsh_plugin.py
python -m unittest tests.test_dsh_target -v
```

Expected: 构建输出 `built .../plugins/dsh-charter-kit`；测试 PASS。

- [ ] **Step 6: 提交**

```bash
git add scripts/build_dsh_plugin.py scripts/validate_kit.py plugins/dsh-charter-kit tests/test_dsh_target.py
git commit -m "feat: ship the DSH client bundle through the builder and validator"
```

---

### Task 5: Skill 文本（三份手工源）

**Files:**
- Modify: `skills/charter-workflow/SKILL.md`
- Modify: `targets/codex/skills/charter-workflow/SKILL.md`
- Modify: `targets/zcode/skills/charter-workflow/SKILL.md`
- Test: `tests/test_workflow_contract.py`（追加用例）

**Interfaces:**
- Consumes: Task 1 的工具名 `charter_review` 与 Task 1 的返回字段 `outcome` / `model` / `routeFallbackReason`。
- Produces: 三份 SKILL.md 中一致的 Review A/B 条件分支与记录语义。

- [ ] **Step 1: 写失败测试**

向 `tests/test_workflow_contract.py` 追加（沿用该文件已有的 `ROOT` 约定）：

```python
    def test_skill_names_the_host_review_tool_conditionally(self):
        for relative in (
            "skills/charter-workflow/SKILL.md",
            "targets/codex/skills/charter-workflow/SKILL.md",
            "targets/zcode/skills/charter-workflow/SKILL.md",
        ):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("charter_review", text, relative)
            self.assertIn("REVIEW_MODEL", text, relative)
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m unittest tests.test_workflow_contract -v`
Expected: FAIL — 三份文本都还没有这两个记号。

- [ ] **Step 3: 编辑三份 SKILL.md**

在每份文件的 Review 段落（含 `Use Review A for every Leaf's contract/implementation coverage` 的那一段）**之前**插入一段，并在该段末尾追加一句路由记录要求。三份必须逐字一致。

插入段落：

```markdown
Run Review A and Review B through the host's `charter_review` tool when the host provides one: pass the review kind (`A` or `B`) and a self-contained brief holding the leaf contract, the spec, and the candidate diff, and nothing else. When the host provides no such tool, dispatch a fresh reviewer through the host's ordinary delegation path instead. Independence is required either way; which model ran the review is recorded separately.

Record the review's model as `REVIEW_MODEL` alongside the independence result: the exact `<provider>/<model>` the tool reports, or `inherited` when the review followed the session model. When a configured route could not be used, record `inherited (configured route unavailable: <reason>)` from the tool's `routeFallbackReason`. A missing review tool or an unused route is **not** a loss of independence: it never turns into `FALLBACK`, never blocks the leaf, and never gets recorded as one.
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m unittest tests.test_workflow_contract -v`
Expected: PASS。

- [ ] **Step 5: 重新生成下游镜像**

```bash
python scripts/build_codex_plugin.py
python scripts/build_zcode_plugin.py
python scripts/build_dsh_plugin.py
```

Expected: 三个构建器都输出 `built ...`。

- [ ] **Step 6: 提交**

```bash
git add skills targets/codex/skills targets/zcode/skills plugins
git commit -m "feat: route reviews through the host review tool and record the model"
```

---

### Task 6: 全量校验与发行物刷新

**Files:**
- Modify: `README.md`（DSH 段落补充卡片与工具说明）
- Modify: `targets/dsh/README.md`
- Regenerate: `plugins/**`、`skills/**`

- [ ] **Step 1: 更新文档**

在 `targets/dsh/README.md` 末尾追加：

```markdown
The plugin also registers the Host settings namespace `charter-kit-review` and
the `charter_review` tool. The namespace keys a card in the DSH
plugin-configuration page where Review A and Review B each pick a configured
model; an unset pick follows the session model. The tool runs one context-free
review with the configured model and reports the model that actually ran.
```

在 `README.md` 的 DSH 安装段落之后追加对应中文说明。

- [ ] **Step 2: 按顺序全量再生成**

```bash
python scripts/build_codex_plugin.py
python scripts/build_zcode_plugin.py
python scripts/build_dsh_plugin.py
```

- [ ] **Step 3: 跑校验器与全量测试**

```bash
python scripts/validate_kit.py .
python -m unittest discover -s tests -q
python scripts/build_codex_plugin.py --check
python scripts/build_zcode_plugin.py --check
python scripts/build_dsh_plugin.py --check
```

Expected: 校验器 PASS；全部测试 OK；三个 `--check` 均 PASS。

- [ ] **Step 4: 提交**

```bash
git add -A
git commit -m "docs: describe the review-model card and refresh generated trees"
```

---

### Task 7: DSH 运行时冒烟

**Files:** 无（运行时验证；必要时用 `dev_reload_package`）

**Interfaces:**
- Consumes: 已装配的 `@dsh-external/dsh-charter-kit`。
- Produces: 卡片与工具在真实 DSH 中工作的证据。

- [ ] **Step 1: 重载插件**

调用 `dev_reload_package`，参数 `dsh-charter-kit`。
Expected: `before: [active]` → `after: [active]`，且无 client 预检失败。

- [ ] **Step 2: 验证卡片出现**

在 DSH 打开「设置 → 插件 → 插件配置」。
Expected: 出现「Charter Kit 评审模型」卡片，展开后有 Review A / Review B 两个下拉，选项含「默认（跟随当前模型）」与部署中已配置的模型。

- [ ] **Step 3: 验证工具按配置使用模型**

1. 把 Review A 配成某个具体模型。
2. 调用 `charter_review`，`kind: "A"`，`brief` 用一个最小自包含简报。
Expected: 返回 `outcome: "reviewed"`，`model` 等于所配 `<provider>/<model>`，`review` 非空。

- [ ] **Step 4: 验证默认回退**

把 Review A 改回「默认（跟随当前模型）」后再调用一次。
Expected: `outcome: "reviewed"`，`model: "inherited"`。

- [ ] **Step 5: 验证不可用回退**

把 Review A 配成一个部署中不存在的 provider/model（例如手工写入设置文档），再调用。
Expected: `outcome: "fallback"`，`model: "inherited"`，`routeFallbackReason` 非空且含 `<provider>/<model>`。

---

## Self-Review

**1. Spec coverage**

| Spec 章节 | 覆盖任务 |
| --- | --- |
| 设置命名空间 `charter-kit-review` | Task 1 |
| `charter_review` 工具与降级矩阵 | Task 1 |
| 客户端卡片与下拉选项 | Task 2 |
| `dsh.client` 声明与 `exports["./client"]` | Task 3 |
| 构建器／校验器接线 | Task 4 |
| Skill host-neutral 条件分支 | Task 5 |
| 两个独立记录轴 | Task 5 |
| 版本号 0.3.0 | Task 3 |
| 验证计划六项 | Task 6（1–2、5、6 项）与 Task 7（2–5 项） |

**2. Placeholder scan**

已逐节检查：无 `TBD`／`TODO`／「add error handling」类占位；每个代码步骤都给出可直接写入的内容。

**3. Type consistency**

- 命名空间常量 `charter-kit-review` 在 Task 1（宿主）、Task 2（客户端 `NS`）、Global Constraints 中一致。
- 四个字段名 `reviewAProvider` / `reviewAModel` / `reviewBProvider` / `reviewBModel` 在 Task 1 的 schema 与 `reviewRoute()`、Task 2 的 `storedRoute()` 与 `write()` 中一致。
- 工具返回字段 `outcome` / `model` / `routeFallbackReason` / `review` 在 Task 1 的 output schema 与 Task 5 的记录语义中一致。
- 客户端模块 id `@dsh-external/dsh-charter-kit` 与 Task 3 的包名一致。
- **已知偏差（需知会）：** spec 第 4 节写的是「tsdown 构建 + 提交产物」，本计划改为**手写 plain-JS bundle 并提交**——同样满足「产物提交、无安装期构建」，同时避免在纯 Python 仓库引入 Node 工具链。这是对 spec 的简化，不影响任何对外接口。
