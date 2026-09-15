# Charter Kit DSH 评审模型配置设计

## 背景

Charter Kit 的 Review A / Review B 目前由「不持有实现上下文的新鲜子代理」执行，这条独立性要求写在 `charter-workflow` skill 里，宿主只负责提供派发能力。子代理的模型因此始终继承当前会话模型，用户无法为评审单独指定模型——例如用便宜模型跑覆盖性 Review A、用更强模型跑对抗性 Review B。

DSH 的「插件配置」页已经有一套成熟的宿主设置卡片机制（`settings.plugin.item`），其中的 `Subagent` 卡片会列出部署中已配置的模型目录。本设计让 Charter Kit 的 DSH 插件贡献一张同类卡片，配置 Review A / Review B 各自使用的模型，并由插件提供一个确定性执行的评审工具。

本设计只影响 DSH 目标封装，不改变 Charter Kit 的核心协议语义，也不改变 Codex 目标的行为。

## 目标

- DSH「插件配置」页出现一张 Charter Kit 卡片，包含 Review A 和 Review B 两个模型下拉框。
- 下拉选项来自 DSH 当前已配置的模型目录，每个下拉都含一个「默认（跟随当前模型）」选项。
- 未配置任何模型时，评审子代理继承当前会话模型。
- 宿主插件提供 `charter_review` 工具，按配置**确定性**地用指定模型派发无上下文评审子代理。
- Codex 等不提供该工具的宿主，行为与今天完全一致（skill 走条件分支）。
- 「评审独立性」与「模型路由」作为两个互相独立的记录轴，偏离必须留痕但不误报。

## 非目标

- 不做项目级覆盖：本期只提供 DSH 插件级的全局配置。
- 不配置模型之外的参数（reasoning effort、温度、输出 token 上限等）。
- 不修改 `deepseek-harness` 核心源码。
- 不引入自动依赖安装，不 vendor 第三方包，不要求插件自带 `node_modules`。
- 不改变 Review A / Review B 的触发条件、`RVB1`–`RVB5` 判定，以及 Charter / Leaf 状态机。
- 不改变 `charter_review` 之外任何现有工具的语义。

## 已验证事实（spike 结论）

正式设计前用一个一次性探针插件验证了四个未知项，随后已完全清理（目录、junction、工具注册、注入清单均已移除）：

| 验证项 | 结果 |
| --- | --- |
| 外部插件（无 `node_modules`）解析 `@deepseek-ai/schemastery` | ✅ |
| 解析 `@deepseek-ai/dsh-tools` | ✅ |
| `ctx.settings.installSection(...)` 注册命名空间 | ✅ |
| `ctx.tools.register(defineTool(...))` 注册工具 | ✅ 工具进入目录并可执行 |

补充发现：`defineTool` 的 `output` **必须提供 `render` 函数**，否则工具执行成功也会以 `output.render failed` 报错。

其它已确认的宿主契约：

- `settings.plugin.item` 是 `keyed` 插槽，**按设置命名空间 key**；`slot-contract.ts` 明确说明这是为仓库外插件贡献卡片而设计的。卡片只在该命名空间已被宿主注册时才会被渲染。
- `ctx.subagents.start(providerName, { prompt, parent, signal, agentOptions })` 是正规的派发入口，`agentOptions` 支持 `{ provider, model }` 覆盖，子代理缺省继承父会话模型。
- 客户端卡片通过 `ctx.settingsScope.bind({ namespace })` 读写宿主设置，通过 `ctx.remote.session.modelCatalog()` 获取模型目录。
- `PluginCard` 组件未对外导出（只导出了类型），外部卡片的卡片外壳需要自绘。

## 设计

### 1. 设置命名空间 `charter-kit-review`

宿主插件注册：

```text
reviewA: { provider: string, model: string } | null   // 默认 null
reviewB: { provider: string, model: string } | null   // 默认 null
```

`null` 表示「跟随当前模型」。命名空间是卡片的 key，也是设置页派发卡片的依据。

### 2. 宿主工具 `charter_review`

```text
入参：
  kind:  'A' | 'B'
  brief: string        // 自包含评审简报：叶子契约要点、规格、候选 diff。
                       // 子代理只拿到它，永远不拿会话历史。

返回：
  outcome: 'reviewed' | 'fallback' | 'unavailable'
  model:   '<provider>/<model>' | 'inherited'
  routeFallbackReason?: string   // 仅当配置了路由却没用上
  review:  string                // 评审者输出；不可用时为空
```

执行链路：

1. 读 `kind` 对应的配置路由。
2. 路由存在 → `agentOptions = { provider, model }`；路由为 `null` → 省略 `agentOptions`（子代理继承当前模型）。
3. `ctx.subagents.start(provider, { prompt, parent: exec.agent, signal: exec.signal, agentOptions })`。
4. 等待并返回评审文本与**实际使用的模型**。

降级矩阵：

| 情况 | outcome | 行为 |
| --- | --- | --- |
| 未配置该评审 | `reviewed` | 继承当前模型，正常评审 |
| 配置了且可用 | `reviewed` | 用配置的 provider/model |
| 配置了但模型已下线／路由被拒 | `fallback` | 回退当前模型，`routeFallbackReason` 说明原因 |
| 子代理能力缺失（provider 不支持 `agentOptions`） | `fallback` | 同上 |
| 无法派发子代理 | `unavailable` | 不改用同上下文评审；由调用方按既有规则处理 |

### 3. 客户端卡片

- 注册到 `settings.plugin.item`，`key: 'charter-kit-review'`。
- 两个下拉框，选项 = `modelCatalog()` 的 `groups`（按 provider 分组）+ 每框一个「默认（跟随当前模型）」。
- 读写走 `ctx.settingsScope.bind({ namespace: 'charter-kit-review' })`，沿用宿主既有的暂存／保存／丢弃语义。
- 已保存但目录中不再存在的路由显示为「不可用」，且仍可被清回默认。
- 两个框配成同一模型时给出独立性提示（不阻塞保存）。
- 卡片外壳自绘，视觉上与宿主内置卡片保持一致（标题、描述、状态、保存/丢弃）。

### 4. 构建与发行

- `targets/dsh` 新增客户端源码与 `tsdown.config.ts`，沿用仓库外插件的 closure-factory 约定（`window.__ModuleLoader__.load({ id, factory })`，`react` 等平台种子作为 external）。
- 构建产物 `client/client.js` **提交进仓库**（发行包必须自包含，无构建步骤即可安装），并带生成标记。
- `targets/dsh/package.json` 增加 `dsh.client` 声明与 `build:client` 脚本。
- `scripts/build_dsh_plugin.py` 增加客户端产物复制；`scripts/validate_kit.py` 增加对应字节校验，沿用仓库既有的「生成树 + 标记」纪律。

### 5. Skill 措辞（host-neutral）

Review A / Review B 段落改为条件分支：

> 若宿主提供 `charter_review` 工具，Review A/B 必须经它执行；否则按本文原路径直接派发新鲜子代理。两种情况下**独立性要求不变**。

模型路由作为独立字段记录，不改变评审有效性的判定。Codex 目标因此完全不受影响。

### 6. 记录语义（两个独立轴）

**独立性轴**（现有语义，不新增状态）：

- 新鲜子代理评审 → 正常
- 只能在同上下文评审 → `FALLBACK`，写明丢失的独立性
- 宿主根本给不出新鲜评审者 → `BLOCKED_TOOLING` 或用户批准的 bounded waiver

**模型路由轴**（新增，非阻塞）：

- `REVIEW_MODEL: <provider>/<model>` — 按配置执行
- `REVIEW_MODEL: inherited` — 未配置，跟随当前模型（正常默认）
- `REVIEW_MODEL: inherited (configured route unavailable: <reason>)` — 配置未生效，必须写明原因

关键约定：**工具不存在／路由不可用不等于独立性丢失**，因此不记 `FALLBACK`、不阻塞流程，只按路由轴留痕，避免「以为 Review B 用的是 Opus、其实不是」这类静默偏离。

## 影响面

| 文件 | 变更 |
| --- | --- |
| `targets/dsh/src/index.js` | 扩展 inject；注册 `charter-kit-review` 命名空间与 `charter_review` 工具 |
| `targets/dsh/src/client/*`（新增） | 卡片控制器与渲染 |
| `targets/dsh/client/client.js`（新增，生成并提交） | 客户端产物 |
| `targets/dsh/tsdown.config.ts`（新增） | 客户端打包配置 |
| `targets/dsh/package.json` | `dsh.client`、`build:client`、版本号 |
| `targets/dsh/README.md` | 说明卡片与工具 |
| `scripts/build_dsh_plugin.py` | 复制客户端产物 |
| `scripts/validate_kit.py` | 校验客户端产物与一致性 |
| `portable/`（权威源）+ skill 镜像链 | Review 段落条件分支与记录语义 |
| `README.md` / `DEPENDENCIES.md`（如涉及） | 用户可见说明 |

## 验证计划

1. `python scripts/validate_kit.py .`、两个 builder `--check` 全绿。
2. 重新生成 DSH 发行包并装入 profile，打开「设置 → 插件 → 插件配置」，确认 Charter Kit 卡片与两个下拉出现，选项与 DSH 模型目录一致。
3. 配置 Review A 与 Review B 各自一个模型 → 调用 `charter_review` → 确认子代理确实运行在指定模型上，且返回值中的 `model` 与配置一致。
4. 清空两项配置 → 确认回退当前模型且 `model: 'inherited'`。
5. 构造「配置的模型不可用」场景 → 确认返回 `fallback` 且带 `routeFallbackReason`，评审仍然完成。
6. Codex 路径回归：确认无 `charter_review` 时 skill 仍走原派发路径（文本条件分支存在且可达）。

## 风险与缓解

| 风险 | 缓解 |
| --- | --- |
| 客户端 bundle 无法注入 `settingsScope` / `remote.session` | 卡片机制已由 `slot-contract.ts` 明确支持仓库外插件；spike 已验证宿主侧注册通路。若客户端注入受限，回落方案是卡片改走插件自有 `settings.section` 页面 |
| 配置的模型长期不可用却无人察觉 | 卡片显式标「不可用」；工具返回 `fallback` 并写明原因；路由轴记录保证可回看 |
| 客户端产物与源码漂移 | 产物提交 + validator 字节校验 + builder `--check` |
| 评审独立性被模型配置弱化 | 独立性轴与路由轴分离；同模型配置仅提示，Review B 仍要求独立评审者 |
