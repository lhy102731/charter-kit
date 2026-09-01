# Charter Kit 多目标封装与 Codex 指令安装设计

## 背景

Charter Kit 的语义核心已经可以脱离具体宿主运行，但当前 Codex 插件目录位于仓库根部。随着 Claude、Gemini、DeepSeek 等目标封装增加，根目录会同时承担核心协议、目标适配和可安装发行包三种职责，导致入口、版本和镜像边界不清楚。

本设计把“目标封装”定义为同一 Charter Kit 面向不同宿主的发行适配，不包含也不安装任何第三方宿主本身。

## 目标

- 保留一份跨宿主的 Charter Kit 核心语义源。
- 把 Codex 相关封装放到独立目标目录。
- 生成一个无需构建、可由 Codex marketplace 直接安装的自足包。
- 让用户可以用 GitHub 仓库和两条 Codex 指令完成安装。
- 为后续目标封装提供统一目录和适配契约。
- 让 README 提供中英双语说明、可点击链接和可复制命令。

## 非目标

- 不安装、下载或管理 Codex、Claude、Gemini、DeepSeek 等宿主。
- 不改变 `charter/v1` 的核心协议语义。
- 不把核心逻辑分别重写成多套目标版本。
- 不引入服务器、中央协调服务、凭据或自动依赖安装。

## 目录与职责

```text
charter-kit/
├─ portable/                         # 跨宿主核心：模板、提示词、命令和引用资料
├─ DEVELOPMENT_CHARTER.md            # 核心章程的 canonical 文档
├─ targets/
│  └─ codex/                         # Codex 目标封装源
│     ├─ .codex-plugin/plugin.json   # Codex manifest 源
│     └─ skills/charter-workflow/    # 自足 Skill 源及受控核心镜像
├─ plugins/
│  └─ charter-kit/                   # 已生成并提交的 Codex 安装包
│     ├─ .codex-plugin/plugin.json
│     └─ skills/charter-workflow/
├─ .agents/plugins/marketplace.json # GitHub marketplace 清单
├─ scripts/
│  ├─ build_codex_plugin.py          # 从目标封装源生成发行包
│  └─ validate_kit.py                # 核心、目标源、发行包一致性检查
└─ README.md                         # 中英双语用户入口
```

`portable/` 是唯一的语义事实源。`targets/codex/` 只描述 Codex 如何进入和加载核心；它可以包含为安装自足而生成的核心镜像，但镜像不得手工独立维护。`plugins/charter-kit/` 是提交到 GitHub 的发行快照，用户不需要先运行构建器。

为兼容当前已安装的本地插件，现有根目录 `.codex-plugin/` 与 `skills/` 在迁移期保留为旧快照，并标记为 deprecated；构建器和验证器负责同步它们，维护者不直接编辑两套内容。待新 marketplace 路径稳定后再删除旧快照。

## Codex 安装契约

仓库根的 `.agents/plugins/marketplace.json` 注册名为 `charter-kit` 的条目，条目源路径固定为 `./plugins/charter-kit`。该目录必须包含 `.codex-plugin/plugin.json`，manifest 的 `skills` 必须指向自身目录下的 `./skills/`，且不依赖仓库外或插件目录外的相对路径。

首次安装的命令为：

```text
codex plugin marketplace add lhy102731/charter-kit
codex plugin add charter-kit@charter-kit
```

第一条命令登记 GitHub marketplace；第二条命令从已登记的 marketplace snapshot 安装插件。后续更新沿用同一插件选择器，在刷新 marketplace 后重新执行安装命令。README 同时提供 PowerShell、macOS/Linux shell 和手动 UI 说明（若宿主版本提供该入口），但不使用未经审计的远程脚本管道。

## 生成与一致性

`scripts/build_codex_plugin.py` 只接受仓库内的 canonical 核心和 `targets/codex/` 作为输入，生成 `plugins/charter-kit/`，并在迁移期同步根目录旧快照。生成过程不访问网络、不安装依赖、不写全局目录。

`scripts/validate_kit.py` 必须检查：

- marketplace 清单的名称、路径和插件条目；
- 发行包的 manifest、Skill 自足性和路径安全；
- `portable/` 与 `targets/codex/` 中所有核心镜像的字节一致性；
- `targets/codex/` 与 `plugins/charter-kit/` 的发行一致性；
- 旧根快照（存在时）与正式发行包的一致性；
- 目标封装允许宿主特有文本差异，但共享语义字段、协议版本和安全限制必须一致。

所有镜像检查使用字节比较，避免换行转换造成未发现的漂移。未来新增目标时，目标特有文件只需通过同一适配契约检查，不要求与 generic prompt 逐字相同。

## 版本与兼容

核心协议版本继续保持 `charter/v1`，当前包版本保持 `0.2.0`，本次目录变化属于发行布局调整。Codex marketplace 的正式安装路径是 `plugins/charter-kit`；根目录旧插件仅作为迁移兼容，不在 README 中作为新安装路径推荐。

## README 验收内容

README 必须包含中英文对应章节：项目简介、核心/目标封装关系、Codex 安装命令、更新与卸载、其他目标的状态、验证方式、安全边界、贡献方式和许可证。链接至少覆盖 GitHub 仓库、Codex 插件/marketplace 相关官方说明（可用时）以及本仓库的核心章程和目标封装目录。

## 验收标准

1. `python -B -m unittest -v tests.test_charter_kit` 全部通过。
2. `python scripts/validate_kit.py .` 通过，并报告 marketplace、目标源和发行包均已检查。
3. Codex 官方插件校验器对 `plugins/charter-kit/` 通过。
4. 从干净临时目录运行构建器后，生成包与仓库中的发行包逐字节一致。
5. `codex plugin marketplace add lhy102731/charter-kit` 能读取 marketplace，`codex plugin add charter-kit@charter-kit` 能安装并显示 `installed, enabled`；若网络或认证不可用，记录实际阻塞，不伪造成功。
6. README 中英双语章节、命令和链接可读、可复制且没有未完成占位符。

