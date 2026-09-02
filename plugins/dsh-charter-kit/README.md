# Charter Kit

Charter Kit is a lightweight, project-local, host-neutral development workflow. It keeps
the goal, scope, current leaf task, reuse evidence, review results, and
verification receipts in ordinary files so that any compatible Harness can
read and continue the same work. Each Harness runs independently; Charter Kit
does not provide a shared service, live coordination, or an installer for the
Harness itself.

## 中文

### 这是什么

Charter Kit 是一个轻量、项目本地、可移植的开发工作流。它把目标、边界、当前叶任务、复用依据、评审结果和验证收据写入普通项目文件，让不同 Harness 可以独立读取并继续同一份工作集。它不是中央服务、实时协调器，也不会安装或打包任何外部 Harness。

核心语义只维护一份：`portable/` 和 `DEVELOPMENT_CHARTER.md`。Codex、Claude、Gemini 或其他宿主只需要提供入口和薄适配；宿主缺少可选能力时，工作流会明确记录 `MISSING`、`UNVERIFIED` 或 `FALLBACK`，不会假装调用成功。

### 主流程

```text
用户输入
  → 首启 / Resume / Change Triage
  → Charter → Roadmap → Leaf
  → Reuse Assessment / Reuse Check
  → READY（WIP = 1）
  → Design → Implement → Review → Verify
  → Git 集成与合并后验证 → PASS_CLOSED
```

新需求、新事实、缺陷和风险都进入 `Change Triage`；新需求不能静默扩大当前 Leaf。复用检查按需要从项目和历史资产逐步扩大到已安装能力与获准的外部资料。发现、采用、安装、复制和执行是不同的授权动作。

Reuse Check 只使用三个门状态：`PENDING`、`COMPLETE`、`BLOCKED`。叶任务只有在门为 `COMPLETE`，或有针对该叶、明确单独批准并记录范围/限制/批准人/复查条件的有界 waiver 时，才能进入 `READY`；waiver 不是第四种状态，也不改变项目级门状态或其他叶的授权。记录会把 Coverage（`SEARCHED` / `NOT_SEARCHED` / `NOT_AUTHORIZED` / `BLOCKED_TOOLING`）、Result（`MATCH` / `NO_MATCH` / `UNKNOWN`）和最终路线（`ADOPT` / `ADAPT` / `REFERENCE_ONLY` / `BUILD_NEW` / `REUSE_SPIKE` / `NEEDS_DECISION`）分开；`NO_MATCH` 必须有真实查询和证据。

### 使用方式

1. 在空目录或已有项目中运行 `charter-workflow`，或让宿主加载对应的 Bootstrap Prompt。
2. 首启时补齐 `.charter/`，完成目标访谈、项目章程、Roadmap 和首个叶任务；继续时按项目文件恢复唯一下一步。
3. 在叶任务进入 `READY` 前完成轻量 Reuse Check，并单独取得叶任务批准或匹配的 `AUTO_DEV` 预授权。
4. 按一个叶任务一个闭环执行；遇到范围、能力或安全边界变化，回到 `Change Triage`。

运行时的核心恢复文件（core Resume files）只有 `.charter/project.md`、`roadmap.md`、`reuse-discovery.md` 和 `current-task.md`；`handoff.md` 是可选恢复快照。初始化器还会准备 `decision.md`、`review.md`、`evidence-receipt.md` 和 `evidence/` 作为辅助收据（auxiliary receipts）及证据容器；它们只在被当前记录引用时读取，不构成第二套状态源。`current-task.md` 是活动叶状态的权威来源，`roadmap.md` 只是投影。

### 安装到 Codex（当前唯一已验证目标）

请先阅读 [Codex 插件文档](https://developers.openai.com/codex/plugins/)，再执行：

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

### 目标状态

Codex 是当前仓库唯一经过安装和启动 smoke test 验证的目标。其他 Harness 目录（如未来的 Claude、Gemini 或 DSH 适配）在完成真实宿主验证前只能标记为 `experimental` / `unverified`；本仓库不会为未验证目标提供正式安装承诺或安装命令。

### 依赖与安全

- `superpowers`、`j-space`、`grill-me`、便携 `design-interview` 以及五个可选 Reuse Skill 是增强插槽，不是核心硬依赖。
- 叶任务状态从 `DRAFT` → `APPROVED` → `READY` 开始，经过实现、Review 和 Verify 后才可 `PASS_CLOSED`。
- 缺少可选 provider 时使用便携 fallback，并把能力状态和影响写入 `.charter/evidence/dependency-check.log`。
- 依赖检查、复用发现和插件加载默认只读；不会自动安装 Skill、插件、包、模型、服务或 Harness。
- 复用发现不会 clone、build、run、import、copy 或 install 候选内容，也不会上传私有源代码、凭据或敏感数据。
- 生成的 `plugins/charter-kit/` 不要手工编辑；修改核心后由维护脚本重新生成并校验。

### 文档与贡献

- [通用开发章程](https://github.com/lhy102731/charter-kit/blob/main/DEVELOPMENT_CHARTER.md)
- [Portable Core](https://github.com/lhy102731/charter-kit/tree/main/portable)
- [Codex 目标源](https://github.com/lhy102731/charter-kit/tree/main/targets/codex)
- [Codex Marketplace 清单](https://github.com/lhy102731/charter-kit/blob/main/.agents/plugins/marketplace.json)
- [GitHub 仓库](https://github.com/lhy102731/charter-kit)

以下维护命令只在源码仓库 checkout 中运行：修改核心时先编辑 `portable/` 和 `DEVELOPMENT_CHARTER.md`；修改 Codex 入口时编辑 `targets/codex/`。发布前运行 `python scripts/validate_kit.py .` 和 `python scripts/build_codex_plugin.py --check`，并在 Codex 中确认安装状态。MIT License.

## English

### What it is

Charter Kit is a lightweight, project-local, host-neutral, portable development workflow. It works from an empty directory or an existing project and records the goal, scope, active leaf task, reuse evidence, review results, and verification receipts in ordinary project files so compatible Harnesses can independently read and continue the same working set. It is not a central service, live coordinator, or installer for the Harness itself.

The semantic core has one source of truth: `portable/` and `DEVELOPMENT_CHARTER.md`. Codex, Claude, Gemini, or another host only supplies an entry point and a thin adapter. If an optional capability is unavailable, the workflow records `MISSING`, `UNVERIFIED`, or `FALLBACK`; it never claims that a provider ran when it did not.

### Main flow

```text
User input
  → INIT / RESUME / Change Triage
  → Charter → Roadmap → Leaf
  → Reuse Assessment / Reuse Check
  → READY (WIP = 1)
  → Design → Implement → Review → Verify
  → Git integration and post-merge verification → PASS_CLOSED
```

New requirements, discovered facts, defects, and risks all enter `Change Triage`; a new requirement must not silently expand the current Leaf. Reuse checks escalate only as needed from project and history to installed capabilities and authorized external sources. Discovery, adoption, installation, copying, and execution are separate authorized actions. A high-value `UNKNOWN` or `DEFER` remains unresolved until it is decided, and selected reuse must cite an immutable commit/tag/package version.

Reuse Check has only three gate states: `PENDING`, `COMPLETE`, and `BLOCKED`. A Leaf may enter `READY` only when the gate is `COMPLETE`, or when that specific Leaf has an explicit, separately approved bounded waiver recording its scope, limitation, approver, and expiry/recheck. A waiver is not a fourth state, does not change the project-wide gate projection, and does not authorize another Leaf. Its record keeps Coverage (`SEARCHED` / `NOT_SEARCHED` / `NOT_AUTHORIZED` / `BLOCKED_TOOLING`), Result (`MATCH` / `NO_MATCH` / `UNKNOWN`), and the final route (`ADOPT` / `ADAPT` / `REFERENCE_ONLY` / `BUILD_NEW` / `REUSE_SPIKE` / `NEEDS_DECISION`) separate. `NO_MATCH` requires an actual query and evidence; a waiver must explicitly address any high-value `UNKNOWN`/`DEFER`.

### Use it

1. Run `charter-workflow` in an empty or existing project, or load the matching Bootstrap Prompt in the host.
2. On first start, complete the `.charter/` working set, intent interview, Charter, Roadmap, and first leaf. On Resume, read the project files and recover one exact next action.
3. Complete the lightweight Reuse Check before a leaf becomes `READY`, then obtain separate leaf approval or matching `AUTO_DEV` preauthorization.
4. Close one leaf at a time. If scope, capability, or safety boundaries change, return to `Change Triage`.

The four core Resume files are `.charter/project.md`, `roadmap.md`, `reuse-discovery.md`, and `current-task.md`; `handoff.md` is an optional recovery snapshot. The initializer also prepares `decision.md`, `review.md`, `evidence-receipt.md`, and `evidence/` as auxiliary receipts and an evidence container. Read those when the active records reference them; they are not another state authority. `current-task.md` is authoritative for the active leaf state, while `roadmap.md` is a projection.

### Install in Codex (the only verified target today)

Read the [Codex plugin documentation](https://developers.openai.com/codex/plugins/) first, then run:

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

### Target status

Codex is the only target in this repository with verified installation and startup smoke-test evidence. Any future Claude, Gemini, DSH, or other Harness adapter is `experimental` / `unverified` until tested in the real host; this repository makes no supported-install claim or install command for an unverified target.

### Dependencies and safety

- `superpowers`, `j-space`, `grill-me`, the portable `design-interview` fallback, and the five optional Reuse Skills are enhancement slots, not core hard dependencies.
- Leaf work starts at `DRAFT` → `APPROVED` → `READY` and reaches `PASS_CLOSED` only after implementation, Review, and Verification.
- Missing optional providers use a portable fallback and record capability status and impact in `.charter/evidence/dependency-check.log`.
- Dependency checks, reuse discovery, and plugin loading are read-only by default. Nothing automatically installs a Skill, plugin, package, model, service, or Harness.
- Reuse discovery never clones, builds, runs, imports, copies, installs anything, and never uploads private source, credentials, or sensitive data.
- The core remains readable from ordinary `AGENTS.md` or `CLAUDE.md` host instructions; those files are entry hints, not a second workflow source.
- Do not hand-edit generated `plugins/charter-kit/`; regenerate and validate it after changing the core.

### Documentation and contribution

- [Generic development charter](https://github.com/lhy102731/charter-kit/blob/main/DEVELOPMENT_CHARTER.md)
- [Portable Core](https://github.com/lhy102731/charter-kit/tree/main/portable)
- [Codex target source](https://github.com/lhy102731/charter-kit/tree/main/targets/codex)
- [Codex marketplace manifest](https://github.com/lhy102731/charter-kit/blob/main/.agents/plugins/marketplace.json)
- [GitHub repository](https://github.com/lhy102731/charter-kit)

In a source repository checkout, update `portable/` and `DEVELOPMENT_CHARTER.md` first when changing the core, and update `targets/codex/` when changing the Codex entry. Before publishing, run `python scripts/validate_kit.py .` and `python scripts/build_codex_plugin.py --check`, then confirm the installation state in Codex. These maintainer paths and commands are not expected inside an installed plugin package. MIT License.
