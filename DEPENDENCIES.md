# Charter Kit 依赖需求与能力诊断

Charter Kit 的核心协议是普通 Markdown；项目不需要安装某个特定模型、Agent 或供应商。依赖分为“核心可运行条件”“推荐的工程能力”“可选 provider”和“项目自定义运行时”。本包不会自动安装任何依赖；加载插件、Skill 或命令也不会改写宿主全局目录。

## 1. 分级要求

### 核心可运行条件

| 能力 ID | 用途 | 缺失时的影响 | 便携 fallback |
|---|---|---|---|
| `readable-markdown` | 读取章程、模板和证据 | 无法建立共同事实源 | 人工读取并记录限制 |
| `project-directory-access` | 在项目内创建/更新 `.charter/` | 无法保存合同和证据 | 由用户准备目录后再继续 |
| `design-interview` | 首次启动澄清意图 | 不能可靠形成完整章程 | 使用包内设计访谈清单 |
| `python`（仅运行本包脚本时） | 初始化、依赖诊断和结构校验 | 自动检查不可用 | 手工复制模板并记录检查 |

### 推荐能力

| 能力 ID | 用途 | 缺失时的影响 | 处理 |
|---|---|---|---|
| `git` | 分支、提交、祖先关系和合并后验证 | 版本证据较弱 | 使用宿主版本系统或人工不可变标识 |
| `isolated-workspace` | 保护主工作树 | 隔离保证较弱 | 临时目录并在交接中声明 |
| `executable-tests` | 自动验收和负向测试 | 只能做人工/静态检查 | 降低完成等级并保留覆盖限制 |
| `independent-review` | 风险或用户触发的新鲜 Review B / CHARTER_INDEPENDENT | 不能声称已完成被触发的独立审阅 | 未触发时记录省略理由；触发但不可用时记录 `BLOCKED_TOOLING` 或取得明确 waiver |

### 可选 provider

| Provider | 提供能力 | 缺失时必须报告 | 便携 fallback |
|---|---|---|---|
| Superpowers | brainstorming、writing-plans、TDD、系统调试、Review、完成验证 | `MISSING` 或 `UNVERIFIED`，说明影响 | Charter Kit 便携清单 |
| J-space | 长任务 ledger、seam、resume 和状态自检 | `MISSING` 或 `UNVERIFIED`，说明影响 | `.charter/handoff.md` 与任务 ledger |
| grill-me / grilling | 逐轮意图访谈和设计树拷问 | `MISSING` 或 `UNVERIFIED`，说明影响 | `references/design-interview.md` |
| reuse-first | 项目内 helper、utility、mapper 和模块发现 | `MISSING` 或 `UNVERIFIED`，说明影响 | 便携的本地复用检查 |
| framework-first-coding | 现有 framework、SDK、dependency 和 shared component 发现 | `MISSING` 或 `UNVERIFIED`，说明影响 | 便携的生态能力检查 |
| reduce-reinvention | Build-vs-Reuse 的成本、风险和维护权衡 | `MISSING` 或 `UNVERIFIED`，说明影响 | 便携的候选决策清单 |
| find-skills | 发现已有 Agent Skill（只发现，不安装） | `MISSING` 或 `UNVERIFIED`，说明影响 | 便携的 Skill inventory |
| repo-to-skill | 对已选仓库进行转换为 Skill 的后续评估 | `MISSING` 或 `UNVERIFIED`，说明影响 | 不转换；先创建单独授权的后续任务 |

检查器会识别常见的 provider 安装形态（例如独立 Skill 目录或宿主的插件缓存），但只读取目录元数据，不递归加载其中的指令。若你的宿主使用其他位置，可用 `--provider-dir id=path` 明确提供只读探测位置。

项目还可以在自己的 `.charter/project.md` 中声明语言运行时、数据库、浏览器、外部 API 或其他工具。它们不是 Charter Kit 的默认依赖，必须由项目单独授权和验证。

## 2. 机器可读声明

`dependencies.json` 是本包的轻量声明，使用 Python 标准库即可读取。它描述能力、可选 provider 的角色、探测位置、是否必需、影响和 fallback；它不是安装清单，也不授予网络或生产权限。独立 Skill 包含自己的同名副本，便于没有包根路径的宿主从零启动。

## 3. 运行依赖检查器

在包根或已安装 Skill 目录运行：

```text
python scripts/check_dependencies.py --project <project-dir> --log-file <project-dir>/.charter/evidence/dependency-check.log
```

常用选项：

- `--require <id>`：本次把某能力视为必需（可重复）；
- `--optional <id>`：本次把某能力视为可选（可重复）；
- `--provider-dir <id>=<path>`：提供一个只读探测位置（可重复）；
- `--require-git`：把 Git 提升为必需；
- `--config <path>`：使用项目自己的 JSON 声明；
- `--json`：输出机器可读记录。

检查器只做本地元数据探测：查找可执行文件、读取目录可访问性和检查已声明的文件。它不会执行发现的程序，不会 import provider，不会联网、clone、build、install、copy 或写全局目录。日志会过滤控制字符、URL 用户信息和常见 secret/token 赋值；不要把凭据放进配置或命令行。

每项检查输出四种彼此独立的状态之一：

```text
AVAILABLE   已检测到并可使用
MISSING     明确不存在或不在声明位置
UNVERIFIED  无法可靠判断（例如宿主能力或环境变量未提供）
FALLBACK    原能力不可用时可使用的便携替代记录
```

输出和日志都必须包含 capability、reason、impact、fallback 和用户 action。必需能力为 `MISSING` 或 `UNVERIFIED` 时退出码非零，并把相关项目/叶任务保持为 `BLOCKED_TOOLING`；推荐/可选能力缺失时退出码仍可为零，但不得把 fallback 写成原 provider 已运行。

依赖诊断状态与 Reuse Check 字段不要混用：`AVAILABLE`、`MISSING`、`UNVERIFIED`、`FALLBACK` 只描述本地能力探测；Reuse 记录另行使用 `SEARCHED`、`NOT_SEARCHED`、`NOT_AUTHORIZED`、`BLOCKED_TOOLING`（覆盖情况）以及 `MATCH`、`NO_MATCH`、`UNKNOWN`（搜索结果）。未授权、未搜索或工具阻塞都不能写成 `NO_MATCH`。

若没有 Python 或脚本不可执行，宿主必须手工按同一字段写一条日志，例如：

```text
[MISSING] grill-me (optional, provider) — provider not detected; impact: interactive intent interview unavailable; fallback: references/design-interview.md; action: continue with fallback or install it explicitly later
[FALLBACK] grill-me (optional, provider) — portable design interview is available
```

## 4. 首次启动时机

当没有 `.charter/project.md` 时，启动顺序是：创建工作集 → 运行依赖检查并写日志 → `grill-me` 优先访谈 → 缺失时内置访谈 fallback → 起草章程/路线/首叶 → 自审和独立审阅 → 用户批准 → 复用发现 → 单独批准首叶。依赖诊断和访谈结果属于证据，不会替代用户批准。

已有项目恢复时仍先读取 `.charter/project.md`、`.charter/roadmap.md`、`.charter/reuse-discovery.md`、`.charter/current-task.md`，再读取可选 handoff；缺文件只补缺失模板，不覆盖已填写内容。

## 5. 复用发现工具的边界

复用发现按工作区/历史 → 已安装 skills/plugins、缓存和 manifest → 获准内部资源 → 官方文档/上游/注册表 → 获准公开 Web 的顺序只读搜索。每个层级受 `LOCAL_ONLY`、`LOCAL_ECOSYSTEM` 或 `FULL_EXTERNAL` 范围和 `External read authorization` 约束。候选查找阶段不安装、不执行、不复制候选，版本必须固定为 immutable commit/tag/package version；结果和原始输出写入 `.charter/reuse-discovery.md` 与 `.charter/evidence/`。

## 6. 安装与授权原则

依赖安装是独立的、明确的用户动作。用户决定安装后，应使用目标宿主的官方机制，记录安装版本和授权范围，再重新运行检查器；Charter Kit 不替用户执行安装，不自动更新，也不修改 `~/.agents`、`$CODEX_HOME` 或其他全局目录。没有某个 provider 时，直接使用便携 fallback 并记录限制即可开始章程访谈和文档审计。
