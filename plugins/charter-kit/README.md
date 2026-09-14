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
3. 在叶任务进入 `READY` 前，Reuse Gate 必须为 `COMPLETE`，或该叶带有上面所述、单独批准的有界 waiver；然后单独取得叶任务批准或匹配的 `AUTO_DEV` 预授权。Change Triage 可触发的定向 Reuse Check 是范围更窄的另一件事：它只在变更涉及能力、依赖、版本、技术栈、安全、许可、隐私或外部影响时启动，不能代替这个门。
4. 按一个叶任务一个闭环执行；遇到范围、能力或安全边界变化，回到 `Change Triage`。

运行时的核心恢复文件（core Resume files）只有 `.charter/project.md`、`roadmap.md`、`reuse-discovery.md` 和 `current-task.md`；`handoff.md` 可选，但只要存在就是必读的第五项：它承载跨会话交接（活动叶加最近关闭的那一个叶，更早的块移入 `handoff-archive.md`），在没有账本控制器时也是手动五行账本的落点。初始化器还会准备 `decision.md`、`review.md`、`evidence-receipt.md` 和 `evidence/` 作为辅助收据（auxiliary receipts）及证据容器；它们只在被当前记录引用时读取，不构成第二套状态源。`current-task.md` 是活动叶状态的权威来源，`roadmap.md` 只是投影。

### 安装到 Claude Code

```bash
claude plugin marketplace add lhy102731/charter-kit
claude plugin install charter-kit@charter-kit
```

重启 Claude Code 后用 `/charter-kit:charter-workflow` 调用。

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

### 安装到 Codex

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

### 安装到 ZCode

ZCode 插件发行包位于 `plugins/zcode-charter-kit/`。在 ZCode 的 **Settings → Plugin Management → Discover** 中点 `+`，添加本仓库（`lhy102731/charter-kit`）或本地目录（仓库根的 `.agents/plugins/marketplace.json` 已注册 `zcode-charter-kit` 条目），然后安装即可。安装后：

- `/charter-workflow` 出现在命令菜单（`commands/charter-workflow.md`，自动挂载技能）；
- `charter-workflow` 技能进入 Skills 分组（触发式发现）；
- 同名资源的优先级：用户级 `~/.zcode/skills` / `~/.agents/skills` 高于插件根——若此前手动复制过副本，请删除旧副本以免遮蔽插件版本。

不想用市场时，可手动复制：`skills/charter-workflow` → `~/.agents/skills/`、`commands/charter-workflow.md` → `~/.agents/commands/`；但市场安装是主路径，二者不要同时使用。

### 安装到 DSH

DSH 插件发行包位于 `plugins/dsh-charter-kit/`，可通过 DSH 插件工具链安装：

```text
dev_inject_plugin <repo>/plugins/dsh-charter-kit
# 或正式装配到 profile（重启后保留）
dev_install_package <repo>/plugins/dsh-charter-kit
```

该插件还注册宿主设置命名空间 `charter-kit-review` 与 `charter_review` 工具。该命名空间是「插件配置」页上那张卡片的 key：Review A 与 Review B 各自选择一个本部署已配置的模型，留空则跟随当前会话模型；卡片上还有一个「单次评审超时（秒）」数字输入，默认 240，工具会把它限制在 30–270 秒之间——这个上限是按**整次调用**算的：配置的尝试加上改用会话模型的重跑，最多 2×270+30=570 秒，仍低于宿主约 600 秒的外部上限，好让工具在外部上限之前返回自己的结果。工具用配置的模型执行一次无上下文评审，并报告它实际使用的路由，跟随会话模型时则为 `inherited`；一次尝试超过该预算时，工具中止那个子代理。配置的路由只要没产出评审——子代理失败、空结果，或上述超时——处理方式都相同：用同一份简报在一个新的无上下文子代理里改用会话模型重跑，返回 `outcome: "fallback"`，并在 `routeFallbackReason` 中写明是哪条路由、发生了什么、花了多久；这次回退本身仍然在会话模型上产出一份评审，所以配置的路由交付不了并不会让该叶失去评审。工作流不会中断，调用也不会超出预算——派发、子代理结果与子代理释放各自都与该预算竞速，因此一个永远不发布 run、或永远不释放 run 的 provider 也无法把调用拖住。空评审不会作为成功形态返回：它只会以显式的 `outcome: "unavailable"` 返回，并带上原因——完全起不了评审者时（没有调用方 agent，或没有唯一明确的子代理 provider）、会话模型这次尝试本身失败时，或配置的路由失败且重跑也失败时，这三种情况下确实没有评审可报。可选参数 `route: "session"` 直接跳过配置的路由、在会话模型上执行，供同一会话内某个 `(kind, route)` 已经失败后的后续评审避免重付超时；在卡片里改模型就是换了一条路由，会重新尝试。缺少 `charter_review` 工具、或某条路由没被用上，都不等于失去评审独立性：评审独立性与模型路由是两条分开记录的轴。

### 目标状态

Claude Code 和 Codex 是当前仓库经过安装与启动 smoke test 验证的目标。DSH 和其他 Harness 目录在完成真实宿主验证前仍标记为 `experimental` / `unverified`，本仓库不会为未验证目标提供正式安装承诺。

### 可选依赖安装（显式）

superpowers、j-space、grill-me 以及 Reuse Skills 不是自动安装项。安装 Charter Kit 后，如希望补齐可选依赖，可运行：

```text
python scripts/install_dependencies.py --list
python scripts/install_dependencies.py --yes
# 或只安装某几个
python scripts/install_dependencies.py --only j-space grill-me
```

该命令会从 `dependencies.install.json` 记录的 GitHub 仓库安装到 `~/.agents/skills`，需要 Git；不会在插件加载时自动执行。

### 依赖与安全

- `superpowers`、`j-space`、`grill-me`、便携 `design-interview` 以及五个可选 Reuse Skill 是增强插槽，不是核心硬依赖。
- 叶任务状态从 `DRAFT` → `APPROVED` → `READY` 开始，经过实现、Review 和 Verify 后才可 `PASS_CLOSED`。
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

以下维护命令只在源码仓库 checkout 中运行：修改核心时先编辑 `portable/` 和 `DEVELOPMENT_CHARTER.md`；修改 Codex 入口时编辑 `targets/codex/`，修改 ZCode 入口时编辑 `targets/zcode/`，修改 DSH 入口时编辑 `targets/dsh/`。同一份内容在仓库中存在多份拷贝，且根目录 `skills/` 由 Codex 构建器生成并回写，动手前先读 `docs/MIRROR-TOPOLOGY.md`。发布前运行 `python scripts/validate_kit.py .`，并按顺序运行 `python scripts/build_codex_plugin.py --check`、`python scripts/build_zcode_plugin.py --check` 与 `python scripts/build_dsh_plugin.py --check`；DSH 构建器读取根目录 `skills/`，所以它必须最后运行。`--check` 比对每个构建器声明的**全部**生成目的地（Codex 构建器的声明包含它回写的根目录 `skills/` 与 `.codex-plugin/plugin.json`）；某一项变红时，改那棵树 `GENERATED.md` 指名的手工源，再跑同一个构建器的 `--sync`——它只刷新这些声明过的目的地，不写别处。MIT License.

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
3. Before a leaf becomes `READY`, the Reuse Gate must be `COMPLETE`, or that leaf must carry the separately approved bounded waiver described above; then obtain separate leaf approval or matching `AUTO_DEV` preauthorization. The targeted Reuse Check that Change Triage can trigger is a narrower, separate event — it runs only when a change touches capability, dependency, version, technology stack, security, license, privacy, or external effects — and it does not stand in for this gate.
4. Close one leaf at a time. If scope, capability, or safety boundaries change, return to `Change Triage`.

The four core Resume files are `.charter/project.md`, `roadmap.md`, `reuse-discovery.md`, and `current-task.md`; `handoff.md` is optional, but it is read as the fifth item whenever it exists: it carries the cross-session handoff — the active leaf plus the most recently closed one, with older blocks appended to `handoff-archive.md` — and it is where the manual five-line ledger lives when no ledger controller is available. The initializer also prepares `decision.md`, `review.md`, `evidence-receipt.md`, and `evidence/` as auxiliary receipts and an evidence container. Read those when the active records reference them; they are not another state authority. `current-task.md` is authoritative for the active leaf state, while `roadmap.md` is a projection.

### Install in Claude Code

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

### Install in Codex

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

### Install in ZCode

The ZCode plugin distribution lives in `plugins/zcode-charter-kit/`. In ZCode, open **Settings → Plugin Management → Discover**, press `+`, and add this repository (`lhy102731/charter-kit`) or a local checkout directory (the repository root `.agents/plugins/marketplace.json` already registers the `zcode-charter-kit` entry), then install. After installation:

- `/charter-workflow` appears in the command menu (`commands/charter-workflow.md`, with the skill auto-mounted);
- the `charter-workflow` skill is listed under Skills (trigger-based discovery);
- same-name resource precedence: user-level `~/.zcode/skills` / `~/.agents/skills` outrank the plugin root — if you previously copied a manual snapshot, delete it so it cannot shadow the plugin copy.

Without the marketplace, copy manually: `skills/charter-workflow` → `~/.agents/skills/` and `commands/charter-workflow.md` → `~/.agents/commands/`; the marketplace is the primary path, so do not use both.

### Install in DSH

The DSH plugin distribution lives in `plugins/dsh-charter-kit/`. Use the DSH plugin toolchain:

```text
dev_inject_plugin <repo>/plugins/dsh-charter-kit
# Or install permanently into the profile (survives restart)
dev_install_package <repo>/plugins/dsh-charter-kit
```

The plugin also registers the host settings namespace `charter-kit-review` and the `charter_review` tool. That namespace is the key of the card on the plugin-configuration page: Review A and Review B each pick one of the models this deployment has configured, an unset pick follows the current session model, and a numeric field sets the per-review timeout in seconds — default 240, clamped by the tool to 30–270 s. That range is dimensioned against the whole call rather than one attempt: a configured attempt plus a session-model rerun is at most 2 × 270 + 30 = 570 s, still under the host's ~600 s external ceiling, so the tool returns its own result before that ceiling instead of being preempted by it. The tool runs one context-free review with the configured model and reports the route it used, or `inherited` when it followed the session model; when an attempt outruns that budget the tool aborts that child. Every way the configured route fails to produce a review — a failed child, an empty result, or that timeout — gets the same treatment: rerun the same brief on the session model in a fresh, context-free child and return `outcome: "fallback"`, with `routeFallbackReason` naming the route, what happened, and how long it took. That fallback still produces a review on the session model, so a configured route that cannot deliver does not cost the leaf its review. The workflow is never interrupted, and the call never waits past its budget: dispatch, the child's result, and teardown are each raced against it, so a provider that never publishes a run or never releases one cannot hold the call open. An empty `review` is never returned as a success shape — it comes back only as an explicit `outcome: "unavailable"` carrying a reason. That is what happens when no reviewer could be started at all (no calling agent, or no unambiguous subagent provider), when the session-model attempt itself failed, or when the configured route failed and the rerun failed too; there is genuinely no review to report in each of those cases. An optional `route: "session"` argument skips the configured route entirely and runs the session model, so later reviews of a `(kind, route)` that already failed in this session do not re-pay the timeout; changing the model in the card makes it a different route, which is tried again. A missing `charter_review` tool, or a route that went unused, is not a loss of review independence: independence and model routing are recorded on two separate axes.

### Target status

Claude Code and Codex are the targets in this repository with verified installation and startup smoke-test evidence. DSH and any future Gemini or other Harness adapter remain `experimental` / `unverified` until tested in the real host; this repository makes no supported-install claim for an unverified target.

### Optional dependency installation (explicit)

superpowers, j-space, grill-me, and the Reuse Skills are not auto-installed. After installing Charter Kit, run this command to install missing optional providers:

```text
python scripts/install_dependencies.py --list
python scripts/install_dependencies.py --yes
# or install only selected providers
python scripts/install_dependencies.py --only j-space grill-me
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

In a source repository checkout, update `portable/` and `DEVELOPMENT_CHARTER.md` first when changing the core, and update `targets/codex/`, `targets/zcode/`, or `targets/dsh/` when changing a host entry. Several trees hold copies of the same files, and the root `skills/` tree is generated by the Codex builder, so read `docs/MIRROR-TOPOLOGY.md` before editing. Before publishing, run `python scripts/validate_kit.py .`, `python scripts/build_codex_plugin.py --check`, `python scripts/build_zcode_plugin.py --check`, and `python scripts/build_dsh_plugin.py --check` — the DSH builder reads root `skills/`, so it runs last — then confirm the installation state in each host. `--check` covers **every** destination its builder declares, including the root `skills/` tree and `.codex-plugin/plugin.json` that the Codex builder writes back; when one of them is red, edit the hand-edited source named in that tree's `GENERATED.md` and run the same builder with `--sync`, which refreshes those declared destinations and refuses to write anywhere else. These maintainer paths and commands are not expected inside an installed plugin package. MIT License.
