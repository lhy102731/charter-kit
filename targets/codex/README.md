# Charter Kit Codex Target

This directory is the Codex target source. It adapts the portable Charter Kit core for Codex, but it is not the installable package itself. The installable artifact is generated at `plugins/charter-kit/`.

Links:

- GitHub repository: [lhy102731/charter-kit](https://github.com/lhy102731/charter-kit)
- Core charter path: [DEVELOPMENT_CHARTER.md](../../DEVELOPMENT_CHARTER.md)
- Target source path: [targets/codex/](.)
- Marketplace path: [`.agents/plugins/marketplace.json`](../../.agents/plugins/marketplace.json)
- Codex target distribution: [plugins/charter-kit/](../../plugins/charter-kit/)
- Official Codex docs: [Codex plugins](https://developers.openai.com/codex/plugins/) or the stable fallback [Codex docs](https://developers.openai.com/codex/)

## 中文

### 这是什么

`targets/codex/` 是 Codex 的目标封装源。它描述 Codex 如何进入、加载并分发 Charter Kit 核心，但它本身不是可安装包。真正可安装的产物是 `plugins/charter-kit/`。

### 可移植核心与目标封装

`portable/` 仍然是唯一的语义事实源。这个目录只负责 Codex 适配，所以它可以包含生成所需的本地镜像，但不能把镜像当成独立维护的第二份核心。

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

当前仓库只准备了 Codex 目标。后续新增目标也会是适配器源，而不是外部 harness 安装器。

### 验证

仓库级验证仍然是第一步：

```text
python scripts/validate_kit.py .
```

验证通过后，再在 Codex 里确认插件状态。

### 安全

- 不要手工编辑生成的发行包。
- 不要把未审阅的远程脚本直接管道进 shell。
- 不要让目标封装依赖仓库外的核心目录。
- 不要把目标封装当成宿主安装器或外部服务代理。

### 贡献

- 改核心时，优先改 `portable/` 和 `DEVELOPMENT_CHARTER.md`。
- 改 Codex 适配时，优先改这里。
- 分发前，重新生成 `plugins/charter-kit/` 并运行验证。
- 提交前确保中英文本、命令和链接都一致。

### 许可证

MIT License.

## English

### What It Is

`targets/codex/` is the Codex target source. It describes how Codex enters, loads, and distributes the Charter Kit core, but it is not the installable package itself. The installable artifact is generated at `plugins/charter-kit/`.

### Portable Core vs Target Packaging

`portable/` remains the single semantic source of truth. This directory only handles Codex adaptation, so it may include generated local mirrors for packaging, but those mirrors are not a separately maintained second core.

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

This repository currently prepares only the Codex target. Any future target will also be an adapter source, not a host installer or external harness package.

### Validation

Repository validation still comes first:

```text
python scripts/validate_kit.py .
```

After that passes, confirm the plugin state in Codex.

### Safety

- Do not hand-edit the generated distribution.
- Do not pipe unreviewed remote scripts into a shell.
- Do not let the target depend on a core directory outside the repository.
- Do not treat the target as a host installer or external service proxy.

### Contribution

- When changing the core, update `portable/` and `DEVELOPMENT_CHARTER.md` first.
- When changing the Codex adapter, work here first.
- Before distributing, regenerate `plugins/charter-kit/` and rerun validation.
- Before opening a change, make sure the Chinese and English text, commands, and links still match.

### License

MIT License.
