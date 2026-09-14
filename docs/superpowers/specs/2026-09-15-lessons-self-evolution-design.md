# Charter Kit 自进化 Lessons 层设计

## 背景

Charter Kit 是一个轻量、项目本地、跨宿主（Claude Code / Codex / ZCode / DSH）的开发工作流，把目标、边界、叶任务、复用证据、评审结果和验证收据记录在 `.charter/` 的普通文件里。它已经能保证"如实记录"——叶任务 Events 表里的 FALLBACK、返工、Review 发现、超预算修复都是现有工作流的常规产出——但这些记录在叶关闭和 handoff 归档后就沉没在文件里，**没有机制把它们提炼成可复用的经验，在下次会话里生效**。

用户的原始诉求："我希望 charter-kit 越用越强：实战里踩了坑，它自己能学会，下次不再踩。"本仓库自己的 git 历史就是这个需求的证据：最近 20 个提交里有一整串 review-timeout 相关的连环修复（超时预算按整次调用算而不是单次尝试、teardown 和 dispatch 也要竞速、超时字段要可编辑）——每一个坑都是"修完就沉没"，如果有 lessons 机制，同类坑第二次出现时就会在册防御。

本设计遵循 kit 的既有哲学：文件 + 规则文本，无新脚本、无中央服务、无自动安装。全部机制复刻 `handoff.md` 已验证的模式（可选但存在即读、有界、归档、提升扫掠），零新机制。

## 用户已确认的四个决策

| 决策点 | 选择 |
| --- | --- |
| 进化范围 | 两层：项目 `.charter/lessons.md` + 经人工确认提升到 kit 本体（`portable/`） |
| 坑的捕获 | 从现有记录自动提炼（叶 Events 表 FALLBACK/返工/Review 发现、handoff 归档扫掠、Change Triage 缺陷事件），不新增流程步骤 |
| 经验消费 | 读 + 引用：lessons 进必读集合（有界），在关键决策点引用，建议性质，不做硬门控 |
| 本体进化治理 | 人工确认提升：agent 只能提炼并暂存候选，提升到 kit 本体必须用户显式确认，走现有 git 贡献路径 |
| 可见性（第 2 节修订新增） | 汇报而非轮询：lessons 状态挂到既有汇报时刻（Resume 状态行、叶关闭汇报行），用户无需刷新磁盘 |

## 目标

- 踩过的坑在叶关闭时被自动提炼为带 ID 的教训条目，存入 `.charter/lessons.md`，成为 Resume 必读集合"存在即读"的第 6 个核心文件。
- 下次会话在 Design、Reuse Check、Change Triage 三个决策点引用相关 lesson，主动防御已知的坑。
- 同一坑只维护一条：重踏已有坑时更新条目（计数+1、证据追加），不新增重复条目。
- 用户在每次会话开始时通过 Resume 汇报行看到 lessons 积累状态和待审批的 GENERALIZE 候选，无需轮询磁盘。
- 超限时按命中计数淘汰最弱条目到 `lessons-archive.md`（非必读），主文件保留单行指针；淘汰前做提升扫掠，被引用为防御依据或已标 GENERALIZE 候选的条目不得淘汰。
- 通用坑经用户显式确认后进入 kit 本体（`portable/references/lessons.md` 规则、命令文件、模板），随插件构建分发到所有项目、所有宿主。

## 非目标

- 不改叶状态机（`DRAFT → APPROVED → READY → … → PASS_CLOSED`）、门语义（Reuse Gate 三态、RVB1–RVB5）、WIP=1、`.charter/` 治理权威源。
- 不做硬门控：lessons 是建议性知识层，不是第四种门状态，不阻塞 READY，不改变任何授权。
- 不做全局/跨项目自动经验库（用户主目录聚合、老化统计、跨项目去重）——违背项目本地哲学，且与"人工确认提升"决策冲突。
- 不做命令式查询、看板、主动通知、web UI——可见性通过既有汇报时刻解决。
- 不加新脚本、不改三个构建器的拷贝逻辑（它们按 `PACKAGE_ROOT_ITEMS` 整体拷贝 `portable/`，新文件自动进入发行包）、不改 DSH/ZCode/Codex 适配器行为。
- 不自动修改 kit 本体：agents 只能提议（暂存候选），提升永远是用户显式动作。

## 整体形状与数据流

一个坑的完整旅程：

```text
踩坑（叶任务实施中：FALLBACK / 返工 / Review 发现 / 超预算修复）
  → 叶 PASS_CLOSED 时：distill（提炼）扫掠该叶 Events 表
     把「事件」转成「教训」：坑是什么、证据指针、下次怎么防
     → 写入 .charter/lessons.md（新条目，或同坑重踏 → 计数+1，不新增重复）
  → 项目内下次 Resume：lessons.md 在必读集合（存在即读），agent 已知坑
  → Design / Reuse Check / Change Triage：引用 LS-ID 并说明相关性
     引用即命中计数+1
  → 超限（>8 KB）：按命中排序淘汰最弱条目 → 归档 lessons-archive.md（非必读）
     淘汰前提升扫掠：被引用为防御依据、或已标 GENERALIZE 候选的条目不得淘汰
  → 通用坑（用户标 GENERALIZE）→ 暂存候选 → 用户显式确认
     → 编辑 portable/ 对应文件 + 跑构建器 --sync + 现有 git 提交流程
     → 项目内条目标 GENERALIZED，保留指针行防止重提
```

不改变的东西：lessons.md 是建议性知识层，与 Reuse Gate 的"门"模式平行存在，不越权。零新机制——每个环节都复刻 kit 里已验证的 handoff.md 模式。

## 文件格式与模板

### `.charter/lessons.md`（项目层）

init 时随标准工作集创建（模板来自 `portable/templates/lessons.md`）：

```markdown
# Lessons

> 本文件记录本项目实战中踩过的坑与下次的防御措施。它是有界的项目知识层：
> ≤ 8 KB，超出时按命中计数淘汰最弱条目到 lessons-archive.md。
> 它是建议性知识：引用它来避免重蹈；它不是门状态，不改变任何授权。

## 条目

- LS-001 | 状态: ACTIVE | 命中: 3 | 来源: TASK-004 Events/Review B | 日期: 2026-09-15
  - 坑: <什么情况导致了什么代价>  — 一句话，可被快速扫读
  - 证据: `.charter/evidence/<file>` / `<commit>`  — 指针，不复制内容
  - 下次防御: <在哪个决策点、检查什么、怎么处理>
  - 通用候选: NO
```

字段语义：

- **ID（`LS-NNN`）**：不可复用、不重排。淘汰/归档后 ID 冻结，主文件保留单行指针，归档保留完整内容——不会出现"LS-003 在两处指不同坑"的歧义。
- **状态**：`ACTIVE`（在册） / `GENERALIZED`（已提升为 kit 规则，项目内保留指针行，防止重提） / `RETIRED`（已失效，如被新版本修掉的坑）。
- **命中计数**：agent 在决策点引用即 +1。被动重踏（事后发现踩了在册的坑）计为缺陷信号：计数照加，事件写回来源叶记录，供下次提炼扫掠。
- **坑与防御分离**：“坑是什么”与“下次怎么防”强制分开，防止浓缩成无法执行的“经验总结”。
- **证据是指针**：指向 `.charter/evidence/` 或 commit，不复制内容，保证条目轻量且可溯源。
- **通用候选**：默认 `NO`；用户标 `GENERALIZE` 后进入提升流程（见提升规则）。

### `portable/references/lessons.md`（kit 层参考）

五条规则集，全部是给 agent 的指令文本（进镜像拓扑，宿主无感知）：

1. **提炼规则（distill）**：触发时机为叶 `PASS_CLOSED` 时、handoff 归档前扫掠时、Change Triage 缺陷路由时；扫叶 Events 表的 FALLBACK/返工/超预算修复、Review A/B 发现、超期 waiver；产出新条目或对已有条目计数+1 并追加证据。**同一坑只一条**：先查现有条目，特征匹配则合并，不新增重复。**零提炼产出合法**——没有坑就是没有教训，不凑数（防止"每叶必产出"的垃圾膨胀）。
2. **引用规则（cite）**：在 Design、Reuse Check、Change Triage 三个决策点检查 lessons.md 相关条目并引用 ID 说明相关性。被动重踏是在册防御失效的信号：记入叶 Events 表并再次提炼。
3. **汇报规则（report）**：三个既有汇报时刻强制挂载 lessons 状态——
   - Resume 汇报行：`lessons: 3 active / 1 archived ｜ 最新: LS-012（TASK-007，09-14）｜ 1 条 GENERALIZE 候选待你决定: LS-009`
   - 叶关闭汇报行：`提炼: 新增 1 条 (LS-012)，更新 2 条（重踏 LS-004），本叶引用 3 条`
   - 候选不积压：存在 GENERALIZE 候选的会话，Resume 汇报行必须列出候选 ID；用户对每条做出提升/保持/丢弃决定后记入条目。
4. **淘汰规则（decay）**：主文件 ≤ 8 KB；超出时按「命中计数最低 + 最早」排序淘汰，完整内容 append 到 `lessons-archive.md`（不在必读集合），主文件留单行指针。**淘汰前提升扫掠**（镜像 handoff 归档 promotion sweep）：被引用为某叶防御依据、或已标 GENERALIZE 候选的条目不得淘汰——只淘汰真正不再被引用的弱条目。
5. **提升规则（generalize）**：用户在条目上标 `GENERALIZE` → 暂存候选 → **用户显式确认后**，编辑 `portable/` 对应文件（规则、模板、参考）并跑构建器 `--sync` 与 `validate_kit.py` → 走现有 git 提交流程。提升后的条目在项目内标 `GENERALIZED`，保留指针行防止重提。防御失效处理：在册防御被证伪（防御写了但没防住）→ 计数+1 且必须重提炼，算新事件不算失败借口。

## 改动面（手工源）与镜像传播

| # | 文件 | 改动 |
| --- | --- | --- |
| 1 | `portable/templates/lessons.md` | **新增**：条目格式模板 + 头部规则提示（有界、建议性、非门状态） |
| 2 | `portable/references/lessons.md` | **新增**：五条规则集（提炼/引用/汇报/淘汰/提升） |
| 3 | `portable/commands/charter-workflow.md` | Resume 必读集合加"存在即读"的 lessons.md；Bootstrap 第 1 步随 init 创建；叶关闭接提炼扫掠；Resume 汇报加 lessons 状态行 |
| 4 | `scripts/init_project.py` | 模板映射加 `lessons.md` 条目 |
| 5 | `scripts/validate_kit.py` | 三处注册：`PORTABLE_TEMPLATES` 加 `portable/templates/lessons.md`（段落头断言 + 自动进 MIRRORS 生成元组与 `check_domain_neutrality` 扫描）；`REQUIRED_FILES`（line 287 起的存在性清单）加 `portable/references/lessons.md`；若仿照 change-triage 的四联常量模式（`CHANGE_TRIAGE_REFERENCE` / `SKILL_` / `TARGET_` / `DISTRIBUTION_`），还需加 targets 与 distribution 的 lessons 参考路径常量并纳入 `check_command` 或新 `check_lessons_reference` 的断言 |
| 6 | `tests/test_workflow_contract.py` | 必读集合断言加 `.charter/lessons.md`（存在即读）+ 汇报行断言 |
| 7 | `tests/test_documentation_contract.py` | lessons 模板/参考在镜像树中的存在与一致性断言 |
| 8 | `docs/MIRROR-TOPOLOGY.md` + `README.md` | 镜像表加新文件行；README 主流程/Resume 段落提及 lessons 层 |

镜像传播链（已验证，`docs/MIRROR-TOPOLOGY.md`）：

- `portable/templates/lessons.md`、`portable/references/lessons.md` 是手工源。
- **`targets/codex/skills/charter-workflow/` 与 `targets/zcode/skills/charter-workflow/` 是手工源的多份拷贝**——`SKILL.md`、`dependencies.json`、`check_dependencies.py`、`init_project.py`、`DEVELOPMENT_CHARTER.md` 都各有 3–4 份手工拷贝。新模板和参考文件必须同样复制到这两棵 target 树（templates/ 与 references/ 子目录），保持 byte-identical。参考文件（lessons 规则）仿照 change-triage 的常量模式注册进验证器（portable / skill / target / distribution 四联路径）。
- 三个构建器（`build_codex_plugin.py`、`build_zcode_plugin.py`、`build_dsh_plugin.py`）按 `PACKAGE_ROOT_ITEMS` 整体拷贝 `portable/` 目录——新文件自动进入三个发行包，**无需改构建器脚本**。
- 根 `skills/charter-workflow/` 是 Codex 构建器回写的生成物（DSH 消费它）——不要手工编辑，靠 `--sync` 刷新。
- 维护顺序：改手工源 → `python scripts/validate_kit.py .` → `build_codex_plugin.py --sync` → `build_zcode_plugin.py --sync` → `build_dsh_plugin.py --sync`（DSH 读根 `skills/`，必须最后跑）→ 三者 `--check` 全绿。

## 测试策略

纯文本契约断言，沿用 kit 现有 pytest 套件风格：

- **模板契约**：lessons.md 模板含必需结构（条目字段、状态语义）；头部提示含"≤ 8 KB""建议性""非门状态"关键词；通过禁用词扫描（命名用 lesson 不用 learning——`FORBIDDEN_CORE_TERMS` 禁用 `Learning`）。
- **工作流契约**：命令文件含"lessons.md 在必读集合（存在即读）""叶关闭时提炼扫掠""Resume 汇报行"三处规则文本；`PROMPT_REQUIREMENTS` 四件套断言保留（lessons 是加法不是替换）。
- **文档契约**：README 主流程/Resume 段落、MIRROR-TOPOLOGY 镜像表提及 lessons。
- **init 行为**：`init_project.py` 在空目录产出 lessons.md 且与模板字节一致。
- **既有断言不受影响**：已验证 `test_workflow_contract.py` 的 read-set 断言（`required_block` 循环）是加法式扩展点。

## 风险与缓解

| 风险 | 缓解 |
| --- | --- |
| lessons.md 膨胀失控 | 8 KB 硬上限 + 命中排序淘汰 + 归档非必读，与 handoff 同族机制，已被该仓库验证 |
| agent 汇报流于形式（状态行走过场） | 契约测试断言规则文本存在；与 handoff 状态行同为"必须出现"的汇报项 |
| 自动提炼质量低（凑数条目） | 规则集明文"零提炼产出合法"；同坑只一条；防御失效强制重提炼；首版接受噪声，靠淘汰和 GENERALIZE 审批过滤 |
| 镜像漂移 | 三构建器 `--check` 全目的地比对 + 发布前 `validate_kit.py`，既有机制无新增 |
| 用户看不到积累状态 | 第 2 节修订的三条可见性规则：Resume 汇报行、叶关闭汇报行、候选不积压——用户在既有汇报时刻被动获知，不轮询磁盘 |

## 已验证事实（设计前探针）

| 验证项 | 结果 |
| --- | --- |
| 构建器按目录整体拷贝 `portable/`（`PACKAGE_ROOT_ITEMS`），新文件自动进发行包 | ✅ 三个构建器均在 |
| `validate_kit.py` 的 MIRRORS 通过 `PORTABLE_TEMPLATES` 生成元组展开，模板注册后自动进镜像比对 | ✅ |
| `init_project.py` 的 `find_template_dir` 已通用（`portable/templates` 与 `templates` 双路径查找），加映射条目即可 | ✅ |
| 禁用词 `Learning` 的扫描范围（`check_domain_neutrality`）覆盖全部 `PORTABLE_TEMPLATES`、命令文件与注册的参考文件；新 lessons 模板/参考自动进扫描。命名与行文用 lesson/教训，不出现 "Learning"（中文"学习"不匹配） | ✅ `FORBIDDEN_CORE_TERMS` + `check_domain_neutrality` |
| `test_workflow_contract.py` read-set 断言（`required_block` 循环）为加法式扩展点 | ✅ |
| `targets/codex` 与 `targets/zcode` 的 skill 树为手工源多份拷贝，需同步编辑 | ✅ `docs/MIRROR-TOPOLOGY.md` 手工源表 |

## 与两份未落地遗留计划的关系（吸收与分歧）

仓库 `docs/superpowers/plans/` 里有两份今天日期、未跟踪的实施计划，均无对应 spec 落地，推断为前期探索（很可能即用户与 qwen 的讨论）遗留：

- `2026-09-15-lesson-ledger.md`：跨项目全局账本（`{home}/.charter/lessons/`，一坑一文件 + `INDEX.md`），纯 stdlib Python 脚本随技能分发，阈值触发自动提议晋升。
- `2026-09-15-gate-immunity.md`：守卫破坏测试——`gates.json` 注册表 + scratch 树变异重放历史缺陷，守卫对重放缺陷必须变红，否则报 `VACUOUS`。

**本设计与其分歧**（用户四个已确认决策为据）：

| 分歧点 | 遗留计划 | 本设计 |
| --- | --- | --- |
| 作用范围 | 跨项目全局账本 | 项目本地单文件 + 人工确认提升到 kit 本体（用户决策 1） |
| 机制形态 | 新增 Python 脚本随技能分发到宿主 | 零新脚本，纯规则文本 + 既有汇报时刻（kit 哲学：文件 + 规则） |
| 记录粒度 | 一坑一文件，append-only 目录 | 单文件有界（≤8 KB）条目制，命中计数合并同坑 |

**从遗留计划吸收的三个点**（它们是被验证过的教训，本身就是 lessons）：

1. **晋升门槛："无可检测失败，不晋升"**（lesson-ledger 全局约束：晋升候选必须同时给出 detectable failure 和能抓住它的 gate，缺一即拒绝）。本设计的 GENERALIZE 提升规则采纳此条：候选必须指明"该坑对应哪个可检测的失败模式 + kit 里哪个决策点/门能拦住它"，否则用户应拒绝提升。
2. **反模式警告："未挂钩的账本会死"**（证据：`PA_Agent/experience/` 是五个只剩 `.gitkeep` 的空目录）。本设计靠叶关闭提炼扫掠 + Resume 必读 + 汇报行三处强制挂钩，与该教训一致——但把它明文写进 references/lessons.md 作为反模式警示。
3. **规则数上限**（lesson-ledger："每个被接受的晋升必须指明它替换哪条子句，否则账本变成 prompt 膨胀"）。本设计采纳：GENERALIZE 候选除指明可检测失败外，还应指明它替换或强化 kit 里哪条现有规则；纯增量规则膨胀应被用户拒绝。

**明确不做**（本设计非目标已覆盖，此处记录原因）：gate-immunity 的破坏测试运行器（`sabotage_check.py`）是有价值的独立维护工具，但它是**仓库维护命令**而非工作流层，且遗留计划自己也否决了把它接入叶关闭（"per-leaf tax was one of the costs this plan explicitly rejected"）。若未来要做，应作为独立 feature 走自己的 spec，不与 lessons 层捆绑。

## 验收标准

1. `python scripts/validate_kit.py .` 通过（含新模板注册与镜像比对）。
2. `python scripts/build_codex_plugin.py --check`、`build_zcode_plugin.py --check`、`build_dsh_plugin.py --check` 全绿。
3. `pytest` 全绿：新增断言覆盖模板契约、工作流契约（必读集合+汇报行）、文档契约、init 行为。
4. 空目录 `init_project.py` 产出含 lessons.md 的标准工作集。
5. README 中英文段落、MIRROR-TOPOLOGY 镜像表反映 lessons 层。
