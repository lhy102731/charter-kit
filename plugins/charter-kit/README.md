# Charter Kit

Charter Kit is a portable, host-neutral charter workflow. Its semantic core lives in `portable/` and `DEVELOPMENT_CHARTER.md`; target directories adapt that core for specific hosts, but they do not install an external harness or redefine the workflow.

Links:

- GitHub repository: [lhy102731/charter-kit](https://github.com/lhy102731/charter-kit)
- Core charter path: [DEVELOPMENT_CHARTER.md](DEVELOPMENT_CHARTER.md)
- Codex target source: [targets/codex/](targets/codex/)
- Codex marketplace path: [.agents/plugins/marketplace.json](.agents/plugins/marketplace.json)
- Official Codex docs: [Codex plugins](https://developers.openai.com/codex/plugins/) or, if you need the stable fallback, [Codex docs](https://developers.openai.com/codex/)

## 中文

### 这是什么

Charter Kit 是一个可移植、与宿主无关的章程工作流。它的语义核心放在 `portable/` 和 `DEVELOPMENT_CHARTER.md`，目标目录只负责把这份核心适配到不同宿主；目标目录不是外部 harness 安装器，也不会重新定义工作流本身。

### 可移植核心与目标封装

`portable/` 是唯一的语义事实源。`targets/codex/` 是 Codex 的目标封装源，只描述 Codex 如何进入和加载核心。可安装的 Codex 发行包是 `plugins/charter-kit/`，它是从目标源生成的自足包。

### 安装到 Codex

按照官方 Codex 插件文档，在支持的 Codex 界面中先添加 marketplace，再安装插件。

```text
codex plugin marketplace add lhy102731/charter-kit
codex plugin add charter-kit@charter-kit
```

### 更新与卸载

更新时，先刷新已配置的 marketplace，再重新执行安装命令：

```text
codex plugin marketplace upgrade charter-kit
codex plugin add charter-kit@charter-kit
```

卸载时，移除已安装的插件：

```text
codex plugin remove charter-kit@charter-kit
```

### 未来目标状态

当前只有 Codex 目标封装。未来新增的目标也会遵循同一原则：它们是适配器，不是第三方宿主或外部 harness 的安装器。

### 验证

推荐先做仓库级校验，再做 Codex 侧安装检查。

```text
python scripts/validate_kit.py .
```

安装后，可用 `codex plugin list --json` 检查是否已安装并启用。

### 安全

- 不要把未审阅的远程脚本直接管道进 shell。
- 不要手工编辑生成的 `plugins/charter-kit/`。
- 不要把 Codex 目标封装当成宿主安装器、代理层或外部服务协调器。
- 不要让目标封装依赖仓库外的核心路径。

### 贡献

- 改核心时，优先修改 `portable/` 和 `DEVELOPMENT_CHARTER.md`。
- 改 Codex 适配时，修改 `targets/codex/`。
- 需要分发时，重新生成 `plugins/charter-kit/`，再运行验证。
- 提交前请确认 README、目标源和发行包之间的语义是一致的。

### 许可证

MIT License.

## English

### What It Is

Charter Kit is a portable, host-neutral charter workflow. Its semantic core lives in `portable/` and `DEVELOPMENT_CHARTER.md`; target directories adapt that core to specific hosts, but they do not install an external harness or redefine the workflow itself.

### Portable Core vs Target Packaging

`portable/` is the single semantic source of truth. `targets/codex/` is the Codex target source and only describes how Codex enters and loads the core. The installable Codex distribution is `plugins/charter-kit/`, which is generated as a self-contained package from the target source.

### Install in Codex

Follow the official Codex plugin guidance in a supported Codex surface: add the marketplace first, then install the plugin.

```text
codex plugin marketplace add lhy102731/charter-kit
codex plugin add charter-kit@charter-kit
```

### Update and Uninstall

To update, refresh the configured marketplace and then rerun the install command:

```text
codex plugin marketplace upgrade charter-kit
codex plugin add charter-kit@charter-kit
```

To uninstall, remove the installed plugin:

```text
codex plugin remove charter-kit@charter-kit
```

### Future Target Status

Codex is the only target packaged today. Future targets will follow the same rule: they are adapters, not installers for third-party hosts or external harnesses.

### Validation

Run the repository validator first, then confirm the Codex installation state.

```text
python scripts/validate_kit.py .
```

After installation, use `codex plugin list --json` to confirm the plugin is installed and enabled.

### Safety

- Do not pipe unreviewed remote scripts into a shell.
- Do not hand-edit the generated `plugins/charter-kit/`.
- Do not treat the Codex target as a host installer, proxy layer, or external coordination service.
- Do not let the target depend on a core path outside the repository.

### Contribution

- When changing the core, update `portable/` and `DEVELOPMENT_CHARTER.md` first.
- When changing the Codex adapter, update `targets/codex/`.
- When publishing, regenerate `plugins/charter-kit/` and rerun validation.
- Before opening a change, confirm the README, target source, and distribution still say the same thing.

### License

MIT License.
