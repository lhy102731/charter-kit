# Charter Kit Codex Target
This directory is the Codex target source. It adapts the portable Charter Kit core for Codex, but it is not the installable package itself. The installable artifact is generated at `plugins/charter-kit/`. You can begin from an empty directory, use the built-in workflow entry, and keep the same working set across hosts such as Codex, Claude, or any AGENTS.md/CLAUDE.md-based setup.

Links:

- GitHub repository: [lhy102731/charter-kit](https://github.com/lhy102731/charter-kit)
- Core charter path: [DEVELOPMENT_CHARTER.md](../../DEVELOPMENT_CHARTER.md)
- Target source path: [targets/codex/](.)
- Marketplace path: [`.agents/plugins/marketplace.json`](../../.agents/plugins/marketplace.json)
- Codex target distribution: [plugins/charter-kit/](../../plugins/charter-kit/)
- Official Codex docs: [Codex plugins](https://developers.openai.com/codex/plugins/) or the stable fallback [Codex docs](https://developers.openai.com/codex/)

Dependency checks are recorded for dependencies in `.charter/evidence/dependency-check.log` and capabilities are classified as `AVAILABLE`, `MISSING`, `UNVERIFIED`, and `FALLBACK`. If `grill-me` or `grilling` is unavailable, the portable `design-interview` fallback is used instead. The project lifecycle keeps charter work explicit with `DRAFT`, `APPROVED`, `READY`, and `PASS_CLOSED`; the reuse gate remains unresolved while any high-value `UNKNOWN` or `DEFER` remains unresolved, and each selected reuse record must include an immutable commit/tag/package version reference. Discovery is read-only and never clones, builds, runs, imports, copies, installs anything, and it never exposes private source.

## 中文

### 这是什么

`targets/codex/` 是 Codex 的目标封装源。它描述 Codex 如何进入、加载并分发 Charter Kit 核心，但它本身不是可安装包。真正可安装的产物是 `plugins/charter-kit/`。你可以从空目录开始，使用内置工作流入口，在 Codex、Claude 或基于 AGENTS.md/CLAUDE.md 的宿主中保持同一份工作集。

### 可移植核心与目标封装

`portable/` 仍然是唯一的语义事实源。这个目录只负责 Codex 适配，所以它可以包含生成所需的本地镜像，但不能把镜像当成独立维护的第二份核心。它也不会把宿主当成产品来安装或分发。

依赖检查会写入 `.charter/evidence/dependency-check.log`，能力状态使用 `AVAILABLE`、`MISSING`、`UNVERIFIED` 和 `FALLBACK`。如果 `grill-me` 或 `grilling` 不可用，就改用 portable 的 `design-interview` 备选方案。项目生命周期明确使用 `DRAFT`、`APPROVED`、`READY` 和 `PASS_CLOSED`，复用门禁会一直保持打开，直到所有高价值 `UNKNOWN` 或 `DEFER` 都被清除，并且为固定的 `immutable commit/tag/package version` 留下依据。发现过程只读，绝不会 clone、build、run、import、copy 或 install 任何内容。

### 安装到 Codex

先把 marketplace 加到 Codex，再安装插件。

```text
codex plugin marketplace add lhy102731/charter-kit
codex plugin add charter-kit@charter-kit
```

### 更新与卸载

更新时，刷新 marketplace，再重新安装：

```text
codex plugin marketplace upgrade charter-kit
codex plugin add charter-kit@charter-kit
```

卸载时，移除已安装插件：

```text
codex plugin remove charter-kit@charter-kit
```

### 未来目标状态

当前仓库只准备了 Codex 目标。后续新增目标也会是适配器源，而不是外部 harness 安装器。它们只适配对应宿主的入口和分发方式，不会安装宿主本身。

### 验证

仓库维护者在源码仓库中先做仓库级验证，再在 Codex 中确认插件状态。构建器和仓库校验器属于维护工具，不会被放进可安装插件。

```text
python scripts/validate_kit.py .
```

验证通过后，再在 Codex 里确认插件状态。

### 安全

- 不要手工编辑生成的发行包。
- 不要把未审阅的远程脚本直接管道进 shell。
- 不要让目标封装依赖仓库外的核心目录。
- 不要把目标封装当成宿主安装器或外部服务代理。
- 不要把发现过程当成安装许可。
- 发现过程绝不会 clone、build、run、import、copy 或 install 候选内容。

### 贡献

- 改核心时，优先改 `portable/` 和 `DEVELOPMENT_CHARTER.md`。
- 改 Codex 适配时，优先改这里。
- 分发前，重新生成 `plugins/charter-kit/` 并运行验证。
- 提交前确保中英文本、命令和链接都一致。
- 如果宿主使用 `AGENTS.md` 或 `CLAUDE.md`，请把它们视为宿主入口说明，而不是 Charter Kit 的事实来源。

### 许可证

MIT License.

## English

### What It Is

`targets/codex/` is the Codex target source. It describes how Codex enters, loads, and distributes the Charter Kit core, but it is not the installable package itself. The installable artifact is generated at `plugins/charter-kit/`. You can begin from an empty directory, use the built-in workflow entry, and keep the same working set across hosts such as Codex, Claude, or any AGENTS.md/CLAUDE.md-based setup.

### Portable Core vs Target Packaging

`portable/` remains the single semantic source of truth. This directory only handles Codex adaptation, so it may include generated local mirrors for packaging, but those mirrors are not a separately maintained second core. It also does not package or install the host itself.

Dependency checks are recorded in `.charter/evidence/dependency-check.log`, and capabilities are classified as `AVAILABLE`, `MISSING`, `UNVERIFIED`, and `FALLBACK`. If `grill-me` or `grilling` is unavailable, the portable `design-interview` fallback is used instead. The project lifecycle keeps charter work explicit with `DRAFT`, `APPROVED`, `READY`, and `PASS_CLOSED`, and the reuse gate stays unresolved until every high-value `UNKNOWN` or `DEFER` is cleared with an immutable commit/tag/package version reference. Discovery is read-only and never clones, builds, runs, imports, copies, or installs anything.

### Install in Codex

Add the marketplace to Codex first, then install the plugin.

```text
codex plugin marketplace add lhy102731/charter-kit
codex plugin add charter-kit@charter-kit
```

### Update and Uninstall

To update, refresh the marketplace and then reinstall:

```text
codex plugin marketplace upgrade charter-kit
codex plugin add charter-kit@charter-kit
```

To uninstall, remove the installed plugin:

```text
codex plugin remove charter-kit@charter-kit
```

### Future Target Status

This repository currently prepares only the Codex target. Any future target will also be an adapter source, not a host installer or external harness package. It only adapts the entry and distribution path for the host, not the host itself.

### Validation

From a source checkout, repository validation still comes first. The packager and repository validator are maintenance tools and are intentionally omitted from the installable plugin.

```text
python scripts/validate_kit.py .
```

After that passes, confirm the plugin state in Codex.

### Safety

- Do not hand-edit the generated distribution.
- Do not pipe unreviewed remote scripts into a shell or reveal private source.
- Do not let the target depend on a core directory outside the repository.
- Do not treat the target as a host installer or external service proxy.
- Do not treat discovery as installation permission.
- Discovery never clones, builds, runs, imports, copies, installs candidate content.

### Contribution

- When changing the core, update `portable/` and `DEVELOPMENT_CHARTER.md` first.
- When changing the Codex adapter, work here first.
- Before distributing, regenerate `plugins/charter-kit/` and rerun validation.
- Before opening a change, make sure the Chinese and English text, commands, and links still match.
- If the host uses `AGENTS.md` or `CLAUDE.md`, treat those as host-entry instructions, not the Charter Kit source of truth.

### License

MIT License.
