# Charter Kit

> 轻量、项目本地、宿主无关的开发工作流：用普通文件保存目标、范围、当前叶任务、复用依据、评审结果与验证收据，让任何兼容的 Harness 都能读取并继续同一份工作。
>
> A lightweight, project-local, host-neutral development workflow that keeps the goal, scope, active leaf task, reuse evidence, review results, and verification receipts in ordinary files, so any compatible Harness can read and continue the same work.

**语言 / Language**：[中文](#中文) ｜ [English](#english)

---

## 中文

**目录**

- [这是什么](#这是什么)
- [工作流程](#工作流程)
- [使用方式](#使用方式)
- [安装指南](#安装指南)
- [目标状态](#目标状态)
- [可选依赖安装](#可选依赖安装显式)
- [依赖与安全](#依赖与安全)
- [文档与贡献](#文档与贡献)

### 这是什么

Charter Kit 是一个轻量、项目本地、可移植的开发工作流。它把目标、边界、当前叶任务、复用依据、评审结果和验证收据写入普通项目文件，让不同 Harness 可以独立读取并继续同一份工作集。

它**不是**中央服务或实时协调器，也不会安装或打包任何外部 Harness；每个 Harness 各自独立运行。

核心设计：

- **单一事实源**：核心语义只维护一份，即 `portable/` 和 `DEVELOPMENT_CHARTER.md`。
- **薄适配**：Codex、Claude、Gemini 或其他宿主只需提供入口和薄适配。
- **不伪造结果**：宿主缺少可选能力时，工作流显式记录 `MISSING`、`UNVERIFIED` 或 `FALLBACK`，不会假装调用成功。

### 工作流程

```text
用户输入
  → 首启 / Resume / Change Triage
  → Charter → Roadmap → Leaf
  → Reuse Assessment / Reuse Check
  → READY（WIP = 1）
  → Design → Implement → Review → Verify
  → Git 集成与合并后验证 → PASS_CLOSED
```

#### Change Triage（变更分诊）

- 新需求、新事实、缺陷和风险都进入 `Change Triage`；新需求不能静默扩大当前 Leaf。
- 复用检查按需逐步扩大范围：项目与历史资产 → 已安装能力 → 获准的外部资料。
- 发现、采用、安装、复制和执行是五种不同的授权动作。

#### Reuse Gate（复用门）

Reuse Check 只有三个门状态：

| 状态 | 含义 |
| --- | --- |
| `PENDING` | 检查尚未完成 |
| `COMPLETE` | 检查完成，叶任务可进入 `READY` |
| `BLOCKED` | 检查受阻 |

叶任务进入 `READY` 的条件（满足其一即可）：

1. 门状态为 `COMPLETE`；或
2. 该叶带有**单独批准的有界 waiver**，并记录范围、限制、批准人与复查条件。

> waiver 不是第四种状态：它不改变项目级门状态，也不授权其他叶任务。

每次 Reuse Check 的记录把三个维度分开：

| 维度 | 取值 |
| --- | --- |
| Coverage（覆盖） | `SEARCHED`、`NOT_SEARCHED`、`NOT_AUTHORIZED`、`BLOCKED_TOOLING` |
| Result（结果） | `MATCH`、`NO_MATCH`、`UNKNOWN` |
| Route（最终路线） | `ADOPT`、`ADAPT`、`REFERENCE_ONLY`、`BUILD_NEW`、`REUSE_SPIKE`、`NEEDS_DECISION` |

`NO_MATCH` 必须有真实查询和证据支撑。

#### 叶契约（Contract version `0.2`）

0.2 版本新增三个字段：

- **Rulings 协议**：停止清单之外的分歧当场裁决，记录为 `Ruling: 决定 — 为什么 — 代价`。
- **Review focus**：spec 隐含但验收未覆盖的输入，逐条配钉住检查（pinning check）。
- **Suite verification**：全项目套件验证；未报告的红测试视同虚假记录。

此外：

- j-space SV1 控制器加入 ledger 模式枚举（旧 `jspace.py` 模式继续合法）。
- `0.1` 契约可按 `portable/references/contract-migrations.md` 迁移，也可继续有效。
- 已关闭的契约永不迁移。

### 使用方式

1. 在空目录或已有项目中运行 `charter-workflow`，或让宿主加载对应的 Bootstrap Prompt。
2. **首启**：补齐 `.charter/`，完成目标访谈、项目章程、Roadmap 和首个叶任务；**继续**时按项目文件恢复唯一下一步。
3. 叶任务进入 `READY` 前，Reuse Gate 必须为 `COMPLETE`，或该叶带有单独批准的有界 waiver；然后单独取得叶任务批准，或匹配的 `AUTO_DEV` 预授权。
4. 按「一个叶任务一个闭环」执行；遇到范围、能力或安全边界变化，回到 `Change Triage`。

> **注意**：Change Triage 可触发的定向 Reuse Check 是范围更窄的另一件事——它只在变更涉及能力、依赖、版本、技术栈、安全、许可、隐私或外部影响时启动，不能代替第 3 步的门。

#### 会话恢复文件（Resume files）

核心恢复文件：

| 文件 | 读取时机 | 作用 |
| --- | --- | --- |
| `.charter/project.md` | 必读 | 项目章程 |
| `roadmap.md` | 必读 | Roadmap，只是当前状态的投影 |
| `reuse-discovery.md` | 必读 | 复用发现记录 |
| `current-task.md` | 必读 | 活动叶状态的**权威来源** |
| `handoff.md` | 存在即必读（第五项） | 跨会话交接、手动五行账本落点 |
| `lessons.md` | 存在即读（第六项） | 实战教训的有界知识层（≤ 64 KB） |

关于 `handoff.md`：

- 承载跨会话交接：活动叶 + 最近关闭的那一个叶；更早的块移入 `handoff-archive.md`。
- 在没有账本控制器时，也是手动五行账本的落点。

关于 `lessons.md`：

- 叶关闭时从 Events 表提炼教训，在 Design / Reuse Check / Change Triage 引用，随 Resume 与叶关闭汇报状态。
- 它是建议性知识，不是门状态。
- 教训要进入套件本体必须经用户显式确认，规则见 `portable/references/lessons.md`。

辅助收据（仅在被当前记录引用时读取，不构成第二套状态源）：

- `decision.md`、`review.md`、`evidence-receipt.md`
- `evidence/`（证据容器）

### 安装指南

#### Claude Code

安装：

```bash
claude plugin marketplace add lhy102731/charter-kit
claude plugin install charter-kit@charter-kit
```

重启 Claude Code 后，用 `/charter-kit:charter-workflow` 调用。

更新：

```bash
claude plugin marketplace update charter-kit
claude plugin update charter-kit
```

卸载：

```bash
claude plugin uninstall charter-kit@charter-kit
claude plugin marketplace remove charter-kit
```

#### Codex

请先阅读 [Codex 插件文档](https://developers.openai.com/codex/plugins/)，再执行：

安装：

```text
codex plugin marketplace add lhy102731/charter-kit
codex plugin add charter-kit@charter-kit
```

更新：

```text
codex plugin marketplace upgrade charter-kit
codex plugin add charter-kit@charter-kit
```

卸载：

```text
codex plugin remove charter-kit@charter-kit
```

#### ZCode

ZCode 插件发行包位于 `plugins/zcode-charter-kit/`。

1. 打开 **Settings → Plugin Management → Discover**，点 `+`。
2. 添加本仓库（`lhy102731/charter-kit`）或本地目录（仓库根的 `.agents/plugins/marketplace.json` 已注册 `zcode-charter-kit` 条目）。
3. 安装。安装后：
   - `/charter-workflow` 出现在命令菜单（`commands/charter-workflow.md`，自动挂载技能）；
   - `charter-workflow` 技能进入 Skills 分组（触发式发现）。

同名资源优先级：用户级 `~/.zcode/skills` / `~/.agents/skills` 高于插件根——若此前手动复制过副本，请删除旧副本以免遮蔽插件版本。

不想用市场时，可手动复制：

- `skills/charter-workflow` → `~/.agents/skills/`
- `commands/charter-workflow.md` → `~/.agents/commands/`

市场安装是主路径，二者不要同时使用。

#### DSH

DSH 插件发行包位于 `plugins/dsh-charter-kit/`。

**安装方式**（三选一）：

- **Bundle 层装配（主路径，重启保留）**：把发行包目录以 link 依赖 + `dsh.profile.bundles` 条目接入 profile。包内自带的 `cordis.patch.yml` 已声明插件行，profile 的 `node_modules` 需要有指向发行包的链接。
- **Market 安装**：经由 market 安装同样有效。
- **运行时注入（开发路径，免重启）**：`dev_inject_plugin`。

插件注册 `charter-workflow` skill 与 `charter_review` 工具，并导出 `Config` schema：

- 宿主把它投影为设置命名空间（key 是本插件的 loader entry id，卡片从宿主的 settings describe 应答中动态发现）。
- 评审模型卡片在两处各有一个入口：侧边栏 **插件 → 官方** 分组、设置导航；两处共用同一份配置。

<details>
<summary>评审模型卡片与超时机制（详细说明）</summary>

**模型选择**

- Review A 与 Review B 各自选择模型；留空则跟随当前会话模型。

**超时语义**

- 「单次评审超时（秒）」默认 600，工具钳制在 30–1800 秒。
- 这是**一次尝试**的预算，不是整次调用的预算：一次评审最多两次尝试——先配置的路由，再会话模型；超时的尝试会被中止。
- 真正不出字的流由宿主自己的**每流空闲**看门狗切断，与这个值无关。
- 选最大值 1800 秒意味着两次尝试最多可占用评审席位约一小时，请有意为之。

**路由与 fallback**

- 工具用配置的模型执行一次无上下文评审并报告实际路由；跟随会话模型时报告 `inherited`。
- 配置的路由只要没产出评审——子代理失败、空结果或超时——都用**同一份简报**在会话模型的新子代理里重跑，返回 `outcome: "fallback"` 并在 `routeFallbackReason` 写明细节。
- 简报必须自包含：评审是多轮运行，请把叶契约、规格与候选 diff 一并放进简报。
- 派发、结果与释放各自与尝试截止时间竞速。
- 空评审只会以 `outcome: "unavailable"` 带原因返回。
- 可选参数 `route: "session"` 跳过配置的路由。

**思考强度（reasoning effort）**

- 卡片上的「思考强度」区域为两个座位各提供一块单选面板。
- 可选档位以模型自己的声明为准（模型目录 `reasoning.efforts`）；未声明档位灰显并写明原因。
- 发送的是档位 id（`agentOptions.reasoningEffort`），不选则不发送。
- 知识库（来自 MIT 许可的 dsh-better-reasoning-effort 0.3.9）提供目录未声明时的参考档位与自动适配；模型声明与知识库冲突时以声明为准。

</details>

### 目标状态

- **已验证**：Claude Code、Codex 与 DSH 是经过真实宿主验证的目标。
  - DSH 已在 dsh 0.1.7-rc.2 上完成端到端部署验证：bundle 层装配、`charter-workflow` skill、`charter_review` 工具与评审模型卡片均实测可用。
- **实验性**：其余 Harness 目录仍为 `experimental` / `unverified`。

### 可选依赖安装（显式）

superpowers、j-space、grill-me 以及 Reuse Skills **不是**自动安装项。安装 Charter Kit 后，如希望补齐可选依赖，可运行：

```text
python scripts/install_dependencies.py --list                          # 查看可安装项
python scripts/install_dependencies.py --yes                           # 全部安装
python scripts/install_dependencies.py --only j-space grill-me         # 只装指定项
```

该命令从 `dependencies.install.json` 记录的 GitHub 仓库安装到 `~/.agents/skills`，需要 Git；不会在插件加载时自动执行。

### 依赖与安全

- `superpowers`、`j-space`、`grill-me`、便携 `design-interview` 以及五个可选 Reuse Skill 是增强插槽，不是核心硬依赖。
- 叶任务状态流转：`DRAFT` → `APPROVED` → `READY`，经过实现、Review 和 Verify 后才可 `PASS_CLOSED`。
- 缺少可选 provider 时使用便携 fallback，并把能力状态和影响写入 `.charter/evidence/dependency-check.log`。
- 依赖检查、复用发现和插件加载默认只读；不会自动安装 Skill、插件、包、模型、服务或 Harness。
- 复用发现不会 clone、build、run、import、copy 或 install 候选内容，也不会上传私有源代码、凭据或敏感数据。
- 生成的 `plugins/charter-kit/` 和 `plugins/dsh-charter-kit/` 不要手工编辑；修改核心后由维护脚本重新生成并校验。

### 文档与贡献

- [通用开发章程](https://github.com/lhy102731/charter-kit/blob/main/DEVELOPMENT_CHARTER.md)
- [Portable Core](https://github.com/lhy102731/charter-kit/tree/main/portable)
- [Claude Code 目标源](https://github.com/lhy102731/charter-kit/tree/main/.claude-plugin)
- [Codex 目标源](https://github.com/lhy102731/charter-kit/tree/main/targets/codex)
- [ZCode 目标源](https://github.com/lhy102731/charter-kit/tree/main/targets/zcode)
- [DSH 目标源](https://github.com/lhy102731/charter-kit/tree/main/targets/dsh)
- [GitHub 仓库](https://github.com/lhy102731/charter-kit)

<details>
<summary>维护者：构建与发布命令（仅源码仓库）</summary>

以下命令只在源码仓库 checkout 中运行，已安装的插件包内不需要：

- **改哪里**：
  - 修改核心 → 先编辑 `portable/` 和 `DEVELOPMENT_CHARTER.md`；
  - 修改 Codex 入口 → 编辑 `targets/codex/`；
  - 修改 ZCode 入口 → 编辑 `targets/zcode/`；
  - 修改 DSH 入口 → 编辑 `targets/dsh/`。
- 同一份内容在仓库中存在多份拷贝，且根目录 `skills/` 由 Codex 构建器生成并回写；动手前先读 `docs/MIRROR-TOPOLOGY.md`。
- **发布前校验**（按顺序运行）：
  1. `python scripts/validate_kit.py .`
  2. `python scripts/build_codex_plugin.py --check`
  3. `python scripts/build_zcode_plugin.py --check`
  4. `python scripts/build_dsh_plugin.py --check`（DSH 构建器读取根目录 `skills/`，必须最后运行）
- `--check` 比对每个构建器声明的**全部**生成目的地（Codex 构建器的声明包含它回写的根目录 `skills/` 与 `.codex-plugin/plugin.json`）。
- 某一项变红时：改那棵树 `GENERATED.md` 指名的手工源，再跑同一个构建器的 `--sync`——它只刷新声明过的目的地，不写别处。

</details>

MIT License.

---

## English

**Contents**

- [What it is](#what-it-is)
- [How it works](#how-it-works)
- [Use it](#use-it)
- [Installation](#installation)
- [Target status](#target-status)
- [Optional dependency installation](#optional-dependency-installation-explicit)
- [Dependencies and safety](#dependencies-and-safety)
- [Documentation and contribution](#documentation-and-contribution)

### What it is

Charter Kit is a lightweight, project-local, host-neutral, portable development workflow. It works from an empty directory or an existing project and records the goal, scope, active leaf task, reuse evidence, review results, and verification receipts in ordinary project files so compatible Harnesses can independently read and continue the same working set.

It is **not** a central service, live coordinator, or installer for the Harness itself; each Harness runs independently.

Core design:

- **One source of truth**: the semantic core lives only in `portable/` and `DEVELOPMENT_CHARTER.md`.
- **Thin adapters**: Codex, Claude, Gemini, or another host only supplies an entry point and a thin adapter.
- **Never fake results**: if an optional capability is unavailable, the workflow records `MISSING`, `UNVERIFIED`, or `FALLBACK`; it never claims that a provider ran when it did not.

### How it works

```text
User input
  → INIT / RESUME / Change Triage
  → Charter → Roadmap → Leaf
  → Reuse Assessment / Reuse Check
  → READY (WIP = 1)
  → Design → Implement → Review → Verify
  → Git integration and post-merge verification → PASS_CLOSED
```

#### Change Triage

- New requirements, discovered facts, defects, and risks all enter `Change Triage`; a new requirement must not silently expand the current Leaf.
- Reuse checks escalate only as needed: project and history assets → installed capabilities → authorized external sources.
- Discovery, adoption, installation, copying, and execution are separate authorized actions.
- A high-value `UNKNOWN` or `DEFER` remains unresolved until it is decided, and selected reuse must cite an immutable commit/tag/package version.

#### Reuse Gate

Reuse Check has only three gate states:

| State | Meaning |
| --- | --- |
| `PENDING` | The check is not complete |
| `COMPLETE` | The check is complete; the leaf may enter `READY` |
| `BLOCKED` | The check is blocked |

A leaf may enter `READY` when either:

1. The gate is `COMPLETE`; or
2. That specific leaf has an explicit, separately approved **bounded waiver** recording its scope, limitation, approver, and expiry/recheck conditions.

> A waiver is not a fourth state: it does not change the project-wide gate projection, it does not authorize another leaf, and it must explicitly address any high-value `UNKNOWN`/`DEFER`.

Each Reuse Check record keeps three dimensions separate:

| Dimension | Values |
| --- | --- |
| Coverage | `SEARCHED`, `NOT_SEARCHED`, `NOT_AUTHORIZED`, `BLOCKED_TOOLING` |
| Result | `MATCH`, `NO_MATCH`, `UNKNOWN` |
| Route (final) | `ADOPT`, `ADAPT`, `REFERENCE_ONLY`, `BUILD_NEW`, `REUSE_SPIKE`, `NEEDS_DECISION` |

`NO_MATCH` requires an actual query and evidence.

#### Leaf contracts (Contract version `0.2`)

Version 0.2 adds three fields:

- **Rulings protocol**: disagreements outside the stop list are decided on the spot and recorded as `Ruling: <decision> — <why> — <cost if wrong>`.
- **Review focus**: spec-implied inputs no acceptance check covers, each with a pinning check.
- **Suite verification**: the project's own full test command; an unreported red test falsifies the record.

In addition:

- The j-space SV1 controller is added to the ledger-mode enum (the legacy `jspace.py` mode stays valid).
- A `0.1` contract migrates through `portable/references/contract-migrations.md` or remains valid as written.
- Closed contracts are never migrated.

### Use it

1. Run `charter-workflow` in an empty or existing project, or load the matching Bootstrap Prompt in the host.
2. **First start**: complete the `.charter/` working set, intent interview, Charter, Roadmap, and first leaf. **Resume**: read the project files and recover one exact next action.
3. Before a leaf becomes `READY`, the Reuse Gate must be `COMPLETE`, or that leaf must carry the separately approved bounded waiver described above; then obtain separate leaf approval or matching `AUTO_DEV` preauthorization.
4. Close one leaf at a time. If scope, capability, or safety boundaries change, return to `Change Triage`.

> **Note**: the targeted Reuse Check that Change Triage can trigger is a narrower, separate event — it runs only when a change touches capability, dependency, version, technology stack, security, license, privacy, or external effects — and it does not stand in for the gate in step 3.

#### Resume files

Core resume files:

| File | When it is read | Role |
| --- | --- | --- |
| `.charter/project.md` | Always | Project charter |
| `roadmap.md` | Always | Roadmap; a projection of current state |
| `reuse-discovery.md` | Always | Reuse discovery record |
| `current-task.md` | Always | **Authoritative** source for the active leaf state |
| `handoff.md` | Read whenever it exists (fifth item) | Cross-session handoff; home of the manual five-line ledger |
| `lessons.md` | Read whenever it exists (sixth item) | Bounded (≤ 64 KB) knowledge layer of project lessons |

About `handoff.md`:

- Carries the cross-session handoff: the active leaf plus the most recently closed one; older blocks are appended to `handoff-archive.md`.
- It is also where the manual five-line ledger lives when no ledger controller is available.

About `lessons.md`:

- Lessons are distilled from the leaf Events table at closure, cited at Design / Reuse Check / Change Triage, and reported on resume and closure.
- It is advisory knowledge, not a gate state.
- A lesson reaches the kit itself only through an explicit user-confirmed promotion; the rules live in `portable/references/lessons.md`.

Auxiliary receipts (read only when the active records reference them; they are not another state authority):

- `decision.md`, `review.md`, `evidence-receipt.md`
- `evidence/` (evidence container)

### Installation

#### Claude Code

Install:

```bash
claude plugin marketplace add lhy102731/charter-kit
claude plugin install charter-kit@charter-kit
```

Restart Claude Code, then invoke with `/charter-kit:charter-workflow`.

Update:

```bash
claude plugin marketplace update charter-kit
claude plugin update charter-kit
```

Uninstall:

```bash
claude plugin uninstall charter-kit@charter-kit
claude plugin marketplace remove charter-kit
```

#### Codex

Read the [Codex plugin documentation](https://developers.openai.com/codex/plugins/) first, then run:

Install:

```text
codex plugin marketplace add lhy102731/charter-kit
codex plugin add charter-kit@charter-kit
```

Update:

```text
codex plugin marketplace upgrade charter-kit
codex plugin add charter-kit@charter-kit
```

Uninstall:

```text
codex plugin remove charter-kit@charter-kit
```

#### ZCode

The ZCode plugin distribution lives in `plugins/zcode-charter-kit/`.

1. Open **Settings → Plugin Management → Discover** and press `+`.
2. Add this repository (`lhy102731/charter-kit`) or a local checkout directory (the repository root `.agents/plugins/marketplace.json` already registers the `zcode-charter-kit` entry).
3. Install. After installation:
   - `/charter-workflow` appears in the command menu (`commands/charter-workflow.md`, with the skill auto-mounted);
   - the `charter-workflow` skill is listed under Skills (trigger-based discovery).

Same-name resource precedence: user-level `~/.zcode/skills` / `~/.agents/skills` outrank the plugin root — if you previously copied a manual snapshot, delete it so it cannot shadow the plugin copy.

Without the marketplace, copy manually:

- `skills/charter-workflow` → `~/.agents/skills/`
- `commands/charter-workflow.md` → `~/.agents/commands/`

The marketplace is the primary path, so do not use both.

#### DSH

The DSH plugin distribution lives at `plugins/dsh-charter-kit/`.

**Installation options** (pick one):

- **Bundle-layer mount (primary, survives restart)**: wire the distribution directory into the profile as a link dependency plus a `dsh.profile.bundles` entry. The package's own `cordis.patch.yml` declares the plugin row, and the profile's `node_modules` needs a link to the distribution.
- **Market install**: installing through the market works too.
- **Runtime injection (development path, no restart)**: `dev_inject_plugin`.

The plugin registers the `charter-workflow` skill and the `charter_review` tool, and exports a `Config` schema:

- The host projects it into a settings namespace keyed by the plugin's loader entry id (the card discovers it dynamically from the host's settings describe answer).
- The review-model card renders in two surfaces — the Plugins page's **Official** group and its own Settings navigation entry — sharing one configuration.

<details>
<summary>Review-model card and timeout mechanics (details)</summary>

**Model selection**

- Review A and Review B each pick a configured model; an unset pick follows the session model.

**Timeout semantics**

- The per-review timeout defaults to 600 seconds; the tool clamps it to 30–1800 seconds.
- That value is the budget for **ONE ATTEMPT**, not for the whole call: a review makes at most two attempts — the configured route, then the session model — and an attempt that outruns its budget is aborted.
- A genuinely silent provider stream is cut by the host's own **per-stream idle** watchdog, which this value neither replaces nor is sized against.
- At the 1800 s maximum, two attempts can hold the reviewer seat for about an hour, so that setting should be deliberate.

**Routing and fallback**

- The tool runs one context-free review with the configured model and reports the route it used, or `inherited` when it followed the session model.
- Every way the configured route fails to produce a review — a failed child, an empty result, or that timeout — reruns the **same brief** on the session model in a fresh child, returns `outcome: "fallback"`, and names the details in `routeFallbackReason`.
- The brief must be self-contained: a review is a multi-turn agent run, so include the leaf contract, the spec, and the candidate diff.
- Dispatch, the child's result, and teardown are each raced against the attempt's deadline.
- An empty `review` comes back only as an explicit `outcome: "unavailable"` carrying a reason.
- The optional `route: "session"` argument skips the configured route.

**Reasoning effort**

- The card's reasoning-effort area gives each seat a single-choice panel.
- Selectable levels follow the model's own declaration (the model catalog's `reasoning.efforts`); undeclared levels are greyed out with the reason.
- The value sent is the level id (`agentOptions.reasoningEffort`); selecting none sends nothing.
- The knowledge base (from MIT-licensed dsh-better-reasoning-effort 0.3.9) supplies reference levels and auto-adapt when the catalog declares none; the model declaration wins disagreements.

</details>

### Target status

- **Verified**: Claude Code, Codex, and DSH are verified targets.
  - DSH is deployed and exercised end to end on dsh 0.1.7-rc.2: the bundle-layer mount, the `charter-workflow` skill, the `charter_review` tool, and the review-model card are all live-tested.
- **Experimental**: any other Harness adapter remains `experimental` / `unverified`.

### Optional dependency installation (explicit)

superpowers, j-space, grill-me, and the Reuse Skills are not auto-installed. After installing Charter Kit, run this command to install missing optional providers:

```text
python scripts/install_dependencies.py --list                    # list what is available
python scripts/install_dependencies.py --yes                     # install all
python scripts/install_dependencies.py --only j-space grill-me   # install selected providers
```

The command installs into `~/.agents/skills` from the GitHub repositories recorded in `dependencies.install.json` and requires Git. It never runs automatically on plugin load.

### Dependencies and safety

- `superpowers`, `j-space`, `grill-me`, the portable `design-interview` fallback, and the five optional Reuse Skills are enhancement slots, not core hard dependencies.
- Leaf work starts at `DRAFT` → `APPROVED` → `READY` and reaches `PASS_CLOSED` only after implementation, Review, and Verification.
- Missing optional providers use a portable fallback and record capability status and impact in `.charter/evidence/dependency-check.log`.
- Dependency checks, reuse discovery, and plugin loading are read-only by default. Nothing automatically installs a Skill, plugin, package, model, service, or Harness.
- Reuse discovery never clones, builds, runs, imports, copies, installs anything, and never uploads private source, credentials, or sensitive data.
- The core remains readable from ordinary `AGENTS.md` or `CLAUDE.md` host instructions; those files are entry hints, not a second workflow source.
- Do not hand-edit generated `plugins/charter-kit/` or `plugins/dsh-charter-kit/`; regenerate and validate them after changing the core.

### Documentation and contribution

- [Generic development charter](https://github.com/lhy102731/charter-kit/blob/main/DEVELOPMENT_CHARTER.md)
- [Portable Core](https://github.com/lhy102731/charter-kit/tree/main/portable)
- [Claude Code target source](https://github.com/lhy102731/charter-kit/tree/main/.claude-plugin)
- [Codex target source](https://github.com/lhy102731/charter-kit/tree/main/targets/codex)
- [ZCode target source](https://github.com/lhy102731/charter-kit/tree/main/targets/zcode)
- [DSH target source](https://github.com/lhy102731/charter-kit/tree/main/targets/dsh)
- [GitHub repository](https://github.com/lhy102731/charter-kit)

<details>
<summary>Maintainers: build and release commands (source checkout only)</summary>

These commands run only in a source repository checkout; they are not expected inside an installed plugin package:

- **What to edit**:
  - Core changes → edit `portable/` and `DEVELOPMENT_CHARTER.md` first;
  - Codex entry changes → edit `targets/codex/`;
  - ZCode entry changes → edit `targets/zcode/`;
  - DSH entry changes → edit `targets/dsh/`.
- Several trees hold copies of the same files, and the root `skills/` tree is generated by the Codex builder, so read `docs/MIRROR-TOPOLOGY.md` before editing.
- **Checks before publishing** (run in this order):
  1. `python scripts/validate_kit.py .`
  2. `python scripts/build_codex_plugin.py --check`
  3. `python scripts/build_zcode_plugin.py --check`
  4. `python scripts/build_dsh_plugin.py --check` (the DSH builder reads root `skills/`, so it runs last)
- Then confirm the installation state in each host.
- `--check` covers **every** destination its builder declares, including the root `skills/` tree and `.codex-plugin/plugin.json` that the Codex builder writes back.
- When one of them is red: edit the hand-edited source named in that tree's `GENERATED.md` and run the same builder with `--sync`, which refreshes those declared destinations and refuses to write anywhere else.

</details>

MIT License.
