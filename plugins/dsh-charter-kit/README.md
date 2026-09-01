# Charter Kit

## 解决什么问题

AI 开发经常在 Codex、DSH、Claude 等宿主间切换。目标、边界、任务状态、复用依据、证据和交接如果没有统一载体，换一个 agent 就会丢失上下文，导致重复劳动、越权改动和无法验证的“完成”。

## 它是什么

一个 host-neutral 的开发章程工作流。它可以从 empty directory 或已有项目开始，用 `.charter/` 统一保存项目章程、路线图、当前任务、复用发现、证据和交接信息；任何支持插件 / skill / AGENTS.md / CLAUDE.md 的宿主都能读取同一套事实。

## 实现了什么

- 从需求到交付的完整章程工程流程
- 项目章程 / 路线图 / 叶子任务 / 交接 / 决策 / 评审 / 证据模板
- 状态机：`DRAFT → APPROVED → READY → PASS_CLOSED`
- 只读复用发现门禁：要求 `immutable commit/tag/package version`，并且 high-value `UNKNOWN` / `DEFER` 在未解决前保持 unresolved
- 发现过程是只读的：不会 clone、build、run、import、copy 或 install；Discovery never clones, builds, runs, imports, copies, installs anything，也不读取 private source
- 依赖诊断：检查 superpowers、j-space、grill-me 与 design-interview 等 dependencies，输出 `MISSING` / `UNVERIFIED` / `FALLBACK`，并记录到 `dependency-check.log`
- Codex 插件与 DSH 插件两种目标封装，核心内容保持一份

## 怎么用

1. 新项目中执行 `charter-workflow`，或让 agent “start the charter workflow”。
2. 按引导完成目标、非目标、边界、资产审计和首叶子任务。
3. 项目章程批准后，先完成复用发现，再单独批准首叶子任务。
4. 每次只实现一个 `READY` 的叶子任务；跨宿主时读取 `.charter/handoff.md` 继续。

## 安装

### Codex

```text
codex plugin marketplace add lhy102731/charter-kit
codex plugin add charter-kit@charter-kit
```

### DSH

```text
dev_inject_plugin <repo>/plugins/dsh-charter-kit
# 或正式装配到 profile（重启后保留）
dev_install_package <repo>/plugins/dsh-charter-kit
```

## 依赖

superpowers、j-space、grill-me 都不是必需依赖。缺失时插件会检测并报告 fallback，不会自动安装或下载任何东西。