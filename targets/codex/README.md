# Charter Kit — Codex Target

This directory is the thin Codex adapter source. It maps the portable Charter
Kit workflow to a Codex plugin entry point; it is not a host installer or an
external harness installer, and it is not the installable package itself. The
self-contained installable distribution is
`plugins/charter-kit/`.

## 中文

### 目标边界

`portable/` 和根目录的 `DEVELOPMENT_CHARTER.md` 是唯一的语义来源。本目录只提供 Codex 的入口、Skill 映射和打包所需的宿主元数据，不重新定义 Charter、Change Triage、Reuse Check、授权或关闭语义，也不安装 Codex 以外的 Harness。

Codex 和 DSH 是当前仓库有真实安装与启动 smoke-test 记录的目标。未来的 Claude、Gemini 或其他目标必须在真实宿主完成验证后才能标记为 supported；在此之前只能标记为 `experimental` / `unverified`，不能从本仓库文档推导出正式安装命令。

### 工作流入口

首启、继续和变化都使用同一套 Portable Core：

```text
INIT / RESUME / CHANGE
  → Charter → Roadmap → Leaf
  → Reuse Assessment / Reuse Check
  → READY（WIP = 1）
  → Design → Implement → Review → Verify
  → Git 集成与合并后验证 → PASS_CLOSED
```

新需求不能静默扩大当前 Leaf；发现的新事实、缺陷和风险回到 `Change Triage`。复用发现默认只读，并把覆盖情况、结果、候选处置、最终路线和证据写入项目 `.charter/reuse-discovery.md`。

Reuse Check 的门状态只有 `PENDING`、`COMPLETE`、`BLOCKED`；Coverage、Result 和最终路线分开记录。只有有真实查询和证据时才可写 `NO_MATCH`。

### 安装、更新与卸载

请先阅读 [Codex 插件文档](https://developers.openai.com/codex/plugins/)。

```text
codex plugin marketplace add lhy102731/charter-kit
codex plugin add charter-kit@charter-kit
```

```text
# 更新
codex plugin marketplace upgrade charter-kit
codex plugin add charter-kit@charter-kit

# 卸载
codex plugin remove charter-kit@charter-kit
```

### 能力与安全

- `superpowers`、`j-space`、`grill-me` 和 Reuse Skills 是可选 provider；缺少时记录 `MISSING` / `UNVERIFIED` / `FALLBACK` 并使用便携替代。
- 依赖诊断、插件加载和 Reuse Discovery 默认只读，不会自动安装 Skill、插件、包、服务或 Harness。
- Discovery 不会 clone、build、run、import、copy 或 install 候选内容，也不会上传私有源代码、凭据或敏感数据。
- `plugins/charter-kit/` 与仓库根目录的 `skills/charter-workflow/`、`.codex-plugin/plugin.json` 都是生成产物，不要手工编辑：构建器会回写后两者。要改自足 Skill，请编辑 `targets/codex/skills/charter-workflow/`；完整的拷贝关系见 `docs/MIRROR-TOPOLOGY.md`。修改 Portable Core 后，从仓库根目录重新构建并运行校验：

```text
python scripts/validate_kit.py .
python scripts/build_codex_plugin.py --check
```

### 相关链接

- [通用开发章程](../../DEVELOPMENT_CHARTER.md)
- [Portable Core](../../portable/)
- [Marketplace 清单](../../.agents/plugins/marketplace.json)
- [GitHub 仓库](https://github.com/lhy102731/charter-kit)

## English

This directory is the thin Codex adapter source. It maps the portable
Charter Kit workflow to a Codex plugin entry point; it is not a host installer
or an external harness installer, and it is not the installable package
itself. The self-contained installable distribution is `plugins/charter-kit/`.

### Boundary

`portable/` and the root `DEVELOPMENT_CHARTER.md` are the only semantic source
of truth. This directory supplies the Codex entry point, Skill mapping, and
packaging metadata. It does not redefine Charter, Change Triage, Reuse Check,
authorization, or closure semantics, and it does not install any Harness.

Codex and DSH are the targets in this repository with real installation and
startup smoke-test evidence. A future Claude, Gemini, or other target may be
marked `supported` only after a real-host verification; until then it is
`experimental` / `unverified`, with no supported-install command implied by
this repository.

### Workflow entry

First start, resume, and change requests use the same Portable Core:

```text
INIT / RESUME / CHANGE
  → Charter → Roadmap → Leaf
  → Reuse Assessment / Reuse Check
  → READY (WIP = 1)
  → Design → Implement → Review → Verify
  → Git integration and post-merge verification → PASS_CLOSED
```

A new requirement must not silently expand the current Leaf. Discovered facts,
defects, and risks return to `Change Triage`. Reuse discovery is read-only by
default and records coverage, result, candidate disposition, final route, and
evidence in the project `.charter/reuse-discovery.md`. The Reuse Check has only
`PENDING`, `COMPLETE`, and `BLOCKED` gate states; Coverage, Result, and final
route remain separate, and `NO_MATCH` requires an actual query and evidence.

### Install, update, and uninstall

Read the [Codex plugin documentation](https://developers.openai.com/codex/plugins/)
first.

```text
codex plugin marketplace add lhy102731/charter-kit
codex plugin add charter-kit@charter-kit
```

```text
# Update
codex plugin marketplace upgrade charter-kit
codex plugin add charter-kit@charter-kit

# Uninstall
codex plugin remove charter-kit@charter-kit
```

### Capabilities and safety

- `superpowers`, `j-space`, `grill-me`, and the Reuse Skills are optional providers. Missing capabilities are recorded as `MISSING`, `UNVERIFIED`, or `FALLBACK` with a portable substitute.
- Dependency diagnostics, plugin loading, and Reuse Discovery are read-only by default. Nothing automatically installs a Skill, plugin, package, service, or Harness.
- Discovery never clones, builds, runs, imports, copies, or installs candidate content, and never uploads private source, credentials, or sensitive data.
- `plugins/charter-kit/` is generated, and so are the repository-root `skills/charter-workflow/` tree and `.codex-plugin/plugin.json`, which this builder writes back. Do not hand-edit any of them; edit `targets/codex/skills/charter-workflow/` to change the self-contained Skill. `docs/MIRROR-TOPOLOGY.md` maps every copy. After changing the Portable Core, rebuild and validate from the repository root:

```text
python scripts/validate_kit.py .
python scripts/build_codex_plugin.py --check
```

### Links

- [Generic development charter](../../DEVELOPMENT_CHARTER.md)
- [Portable Core](../../portable/)
- [Marketplace manifest](../../.agents/plugins/marketplace.json)
- [GitHub repository](https://github.com/lhy102731/charter-kit)
