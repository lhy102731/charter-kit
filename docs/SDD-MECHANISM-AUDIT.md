# SDD 机制审计：spec-kit / OpenSpec 对照 Charter Kit

> 本文不重复 [SPEC-DRIVEN-DEVELOPMENT.md](SPEC-DRIVEN-DEVELOPMENT.md)。那份回答「SDD 是什么、生态走到哪了、我们该吸收什么」；本文回答更细的一层：**对方的每一个机制具体怎么写、我们的对应物在哪一行、差在哪里、补哪一行**。
>
> 审计日期 2026-10-19。审计基准：本工作树当前 HEAD，`DEVELOPMENT_CHARTER.md` 425 行 / 32656 字节。
> 阅读方式：每个机制一节，先引对方的原文（英文原句），再引我们自己的行号，然后给判定和补丁。跳过结论直接看 §8 补丁清单也可以。

## §0 方法与判定词表

### 0.1 读了多少原文

| 侧 | 对象 | 读法 | 规模 |
|---|---|---|---|
| 对方 | `github/spec-kit@main` | jsDelivr flat list + 逐文件取原文 | 67 个文件；5 份模板 22 KB；9 份命令协议约 90 KB |
| 对方 | `Fission-AI/OpenSpec@main` | jsDelivr flat list + 逐文档取原文 + 两份历史 change 原文 | 557 个 blob；docs 约 200 KB；样例 spec 8.4 KB |
| 我方 | 本章程与模板全套 | 全文读 + `wc -l -c` 实测 | 1164 行 / 136160 字节（见 0.3） |

判定只依据读到的一手原文。读不到的（例如 Kiro 的 GA 公告被 cookie 墙拦）不进入判定，也不用于支持结论。

### 0.2 判定符号

| 符号 | 含义 | 判据 |
|---|---|---|
| ≡ | 等价 | 意图相同，且约束力相同（都有可观测后果） |
| ⊃ | 我方更强 | 我方多出的约束能改变某次执行的结果，不是措辞差异 |
| ⊂ | 我方更弱 | 对方有量或形，我方只有意图 |
| ∅ | 对方有、我方无 | 我方全文找不到对应物 |
| ⊕ | 只有我方有 | 对方两套工具及其文档里都不存在 |
| ≠ | 同名不同物 | 字面相同，所指不同，不能比较强弱 |

### 0.3 我方实测尺寸（本文所有引用的基准）

    DEVELOPMENT_CHARTER.md              425 行  32656 字节
    templates/leaf-task.md              256 行  15708 字节
    templates/project-charter.md        217 行  12680 字节
    templates/roadmap.md                 82 行   7132 字节
    portable/commands/charter-workflow.md 54 行 13789 字节
    portable/references/change-triage.md          2145 字节
    portable/references/contract-migrations.md    6878 字节
    portable/references/default-on-policy.md      2607 字节
    portable/references/design-interview.md       3255 字节
    portable/references/lessons.md                4446 字节
    portable/prompts/*-bootstrap.md    5 份 × 13504 字节（字节级相同）

一处更正：早前口头说「叶合同模板约 10 KB、真实项目可达 35 KB」。模板自己在 `leaf-task.md:7` 里写的是 "This template is about 10 KB"，但实测当前模板已是 **15708 字节**——模板自己在描述一个更旧的自己。这条注释本身就该改，见 §8 P2-4。

---

## §1 十七个机制的总表

| # | 机制 | 对方版本 | 我方对应 | 判定 |
|---|---|---|---|---|
| M1 | 要求条目编号 | FR-001 / SC-001 / CHK001 / US1 / T012 | TASK-ID + RDY1–13 + E-01，验收项无编号 | ⊂ 验收项 |
| M2 | 验收表达形式 | Given / When / Then + Independent Test | 可观察检查 + Review focus | ≡／⊃ |
| M3 | 澄清的分类法 | clarify 九大类 × Clear/Partial/Missing | 无分类法，靠访谈 | ∅ |
| M4 | 澄清的量化上限 | 3 个 NEEDS CLARIFICATION、5 个问题、一次一个 | 无上限 | ∅ |
| M5 | 命名与目录约定 | 2–4 词 short name + `specs/NNN-name` + `feature.json` | roadmap 四级 ID | ⊂ |
| M6 | 拆解粒度与并行标注 | `[P] [Story]` + 精确文件路径 | 一叶一可观察行为 + 「两个 and 就拆」 | ⊃ 粒度／∅ 并行 |
| M7 | 依赖与阻塞 | Phase 2 Blocking Prerequisites + depends on | 前置须 PASS_CLOSED + WIP=1 | ⊃ |
| M8 | 阶段门 | Constitution Check 两处 GATE | 11 条启动门禁 + RDY1–13 | ⊃ |
| M9 | 违例的处置 | Complexity Tracking 四列表 | A/B/C × P0–P3 两轴 + waiver | ⊃ |
| M10 | 只读门 | checklist `[x]` 状态即门，implement 不得改标记 | Evidence + 「自报不能替代独立证据」 | ≡／⊃ |
| M11 | 只读分析命令 | analyze STRICTLY READ-ONLY + CRITICAL 冲突 | Review A/B 但无跨制品只读分析 | ⊂ |
| M12 | 状态的必要性与顺序 | "Actions, not phases" | 七态状态机 + 同步镜像 | ≠（取向相反） |
| M13 | 增量制品的表达 | ADDED/MODIFIED/REMOVED/RENAMED delta | 叶合同是完整快照，无 delta | ∅ |
| M14 | 归档与收尾 | `openspec archive`：未完成任务默认 No、目录已存在报错、主 spec 覆盖 | PASS_CLOSED + contract-archive 落证据 | ⊃ |
| M15 | 上下文注入通道 | context / rules / guidance 三通道 | project.md 单通道 + 模板 | ⊂ |
| M16 | 扩展点 | `hooks.before_<command>` + extensions.yml，带 enabled/condition/optional | §8 工具路由 + Provider 插槽 | ⊂ |
| M17 | 机读面 | 全部 `--json`，`validate --all --json` 批量 | validate_kit.py 只有人读输出 | ∅ |

---

## §2 A 组：需求侧怎么把话钉死

### M1 要求条目编号 —— ⊂ 只差验收项

**对方的写法。** `templates/spec-template.md` 三条编号线同时存在：功能需求 `**FR-001**: System MUST …` 起编，成功标准 `**SC-001**` 起编且要求「可量化、技术无关」，用户故事 `User Story N - [Title] (Priority: P1|P2|P3)`，故事内的验收场景再按 `1./2.` 编号。`templates/tasks-template.md` 的任务号 `T001` 起编，格式行写明 `**Format: `[ID] [P?] [Story] Description**`。`templates/checklist-template.md` 的条目 `CHK001` 顺序递增。

三条线全部互相回指：任务行写 `- [ ] T014 [US1] Implement [Service] in src/services/[service].py (depends on T012, T013)`，一个矩阵里同时含故事归属、文件路径、任务依赖；`plan-template.md` 的 Constitution Check 与 `tasks.md` 之间靠编号而不是复述对齐。

**我们的写法。** 我们已经有的：`roadmap.md:14` 的 Order + ID 四级层次编号（R1 / R1.1 / R1.1-S1 / R1.1-S1-L1）；`roadmap.md:50` 的 RDY 编号明文规定 **append-only**——"The numbering is append-only: retired items keep their number with a retirement date, new items take the next number — renumbering would silently change what archived leaf records mean"；`leaf-task.md:210` 引用方式规定为「RDY1-RDY13 PASS with the evidence source」，且非 PASS 项逐行写 `| RDY# | result | evidence |` 并明确 "cite items by number plus a short label, never by restating the checklist text"；`leaf-task.md:204` 证据表用 E-01 编号；`leaf-task.md:19` 合同带 Contract version 0.2 并有迁移文件。

我们缺的只有一处：**验收条件本身没有编号**。`leaf-task.md:84-90` 的 Positive behavior / Negative behavior 是两组可勾选项，形态是 `- [ ] <observable check 1>`，没有 AC-N。`leaf-task.md:98-102` 的 Review focus 也没有编号。

**判定与后果。** ⊃（RDY 的 append-only 纪律比 CHK 的「顺序递增」严格，因为它冻结了归档记录的含义）但验收项 ∅。后果是可观测的：Review A 的一条发现要说「第三组第三条负向检查未覆盖」，没法说「AC-7 未覆盖」；`roadmap.md` 的 Decisions 表、Change Triage、lessons 条目在引用同一检查时都只能重述原文，重述一次漂移一次。RDY 已经证明了编号加 append-only 的价值，验收项是这套纪律最后一块没编号的地方。

### M2 验收的表达形式 —— ≡／⊃

**对方的写法。** `spec-template.md` 每个用户故事强制三段，缺一段就不成故事：

- `**Why this priority**` —— 为什么是这个优先级，而不是「优先级高」；
- `**Independent Test**` —— 原文是 "Can be fully tested by [specific action] and delivers [specific value]"，并注明每个 story 必须可独立开发、测试、部署、演示；
- `**Acceptance Scenarios**` —— 编号枚举，句式为 **Given** … **When** … **Then** …。

**我们的写法。** `leaf-task.md:82-90` 的 Positive behavior 要求 `<observable check>`，Negative behavior 要求 `<invalid input or forbidden effect is rejected or remains unchanged>` 与 `<failure path is recorded>`；`leaf-task.md:94` 的 Suite verification 要求跑**整个套件**并明写 "a green run of this leaf's files alone is not a green suite"；`leaf-task.md:98-102` 的 Review focus 要求点名「规格暗示、但上面没有检查覆盖」的输入与失败模式，逐条给出钉住它的检查，或者写清为什么跑不了，没有就写 `none identified`。

**判定。** 形式 ≡（Given/When/Then 与「可观察检查」是同一件事的两种记法），约束力 ⊃：Independent Test 管的是 story 的独立性，而我们的 Review focus 管的是**规格与检查之间的缺口**——它强迫作者承认「规格暗示了但没检查」的条目，这是 spec-kit 模板里没有位置写的东西。Suite verification 的整表要求同样在对方只到 "Tests OPTIONAL — only if explicitly requested" 的地方多压了一层。

### M3 澄清的分类法 —— ∅

**对方的写法。** `templates/commands/clarify.md`（body 16843 字符）核心是一张固定的九类扫描表，每类标 Clear / Partial / Missing，产出一张内部覆盖图：

- Functional Scope & Behavior：核心用户目标与成功标准 / 显式 out-of-scope 声明 / 角色与 persona 区分
- Domain & Data Model：实体属性关系 / 身份与唯一性规则 / 生命周期与状态转移 / 数据量级假设
- Interaction & UX Flow：关键用户旅程 / 错误·空·加载三态 / 可达性或本地化
- Non-Functional Quality Attributes：性能 / 可扩展性 / 可靠性与可用性 / 可观测性 / 安全与隐私（authN/Z、数据保护、威胁假设）/ 合规监管
- Integration & External Dependencies：外部服务与 API 及失败模式 / 导入导出格式 / 协议与版本假设
- Edge Cases & Failure Handling：负向场景 / 限流节流 / 冲突解决
- Constraints & Tradeoffs：技术约束 / 显式取舍或被拒替代方案
- Terminology & Consistency：规范术语表 / 应避免的同义词与废弃术语
- Completion Signals：验收标准可测性 / 可量化的 DoD 指标
- Misc / Placeholders：TODO 未决项 / 缺量化的形容词（原文举例 "robust"、"intuitive"）

**我们的写法。** 需求考古六问（`DEVELOPMENT_CHARTER.md:63-76`）、首启访谈要点（`portable/commands/charter-workflow.md:31`：user/context、pain、observable goal、non-goals、invariants、product loop、assets、reuse scope、effects、success levels、risks、一个首个有界行为）、design-interview 便携回退（3255 字节）、以及 `leaf-task.md:246` 的 Design tree（frontier 只问当前可答的问题，每题附 Recommended / Reason / Alternative / Disclosed cost）。

**判定。** ∅。我们有点（六问、访谈清单、设计树），但没有**面**：没有一张固定分类表可以逐类打 Clear/Partial/Missing，因此无法证明「这张需求被系统性扫过一遍」。六问是一串开放问题，问完不知道自己漏了什么；九类表的价值在于**漏了什么看得见**——某一类标 Missing 就是一次显式承认。

**这是本次审计里最值得抄的一条**，因为它不带来新概念，只带来一张可勾的表。补丁见 §8 P0-2。

### M4 澄清的量化上限 —— ∅

**对方的写法。** 同一份 `clarify.md` 里三个硬数字：

- **最多 5 个问题**（"Maximum of 5 total questions across the whole session"），一次只问一个；
- 每个问题必须是 2–5 个互斥选项的多选，或明确限 ≤5 词的短答；
- 按 `(Impact × Uncertainty)` 排序，「超过 5 类未澄清时取前 5」。

`specify.md` 里另有一个数字：`[NEEDS CLARIFICATION]` 标记**上限 3 个**，且只有三种情况才允许标——显著影响功能范围或用户体验、存在多个合理解释且后果不同、无合理默认；优先级固定为 `scope > security/privacy > user experience > technical details`；其余一律「先做有依据的猜测」并把猜测写进 Assumptions。

另有一条写作硬约束值得单列：问题必须写成 `**Question:** <完整疑问句>?` 或 `**Question:** <疑问句>? (FR-023)`，**禁止**用话题标签、小节标题或需求 id 当问题本身。原文举的反例是 `Acceptance device/runtime matrix (FR-023)`，判为 INVALID，理由是 "it is a label, not a question"。id 只能放在问号后的括号里。

**我们的写法。** 没有上限。`DEVELOPMENT_CHARTER.md:230-232` 的首启访谈、§8 的 grill-me 路由、design-interview 都是「多轮问到清楚为止」。`leaf-task.md:246` 的 frontier 概念本身就是「只问当前可答的」，方向正确，但没有配数字，也没规定一次只问一个。

**判定。** ∅，而且这是**两条不同性质的缺口**：分类法缺的是覆盖证明，上限缺的是**停止条件**。无上限的追问在治理系统里是有代价的——它把澄清变成一个可以无限膨胀的阶段，而这正是 Fowler 批 SDD「大锤砸核桃」时的真实机制（不是 markdown 多，是**为了一个小 bug 也要走完整个澄清-规格-任务链**）。我们自己的 §11 流程健康检查（`:408-410`，每隔两三个叶看产品开发时间是否仍高于流程维护时间）是在**事后**发现这个膨胀；上限是在**事前**不让它发生。

### M5 命名与目录约定 —— ⊂

**对方的写法。** `specify.md` 步骤 1 直接从用户描述抽取 2–4 词 short name，action-noun 格式，原文举例：`"I want to add user authentication" → "user-auth"`、`"Fix payment processing timeout bug" → "fix-payment-timeout"`。步骤 3 定目录名 `<prefix>-<short-name>`：前缀按 `.specify/init-options.json` 的 `feature_numbering` 取 `timestamp`（`YYYYMMDD-HHMMSS`）或 `sequential`（扫 `specs/` 取下一个三位号），产出 `specs/003-user-auth` 这种名字。然后把解析结果持久化到 `.specify/feature.json` = `{"feature_directory": "specs/003-user-auth"}`，并明写目的是「让下游命令不依赖 git 分支名」。分支名与目录名解耦，一次调用只建一个 feature。

**我们的写法。** `roadmap.md:14-19` 的四级 ID 已经是稳定命名（R1.1-S1-L1），但叶**没有可读名字**字段——`leaf-task.md:14` 只有 `Title: <short verb + observable result>`，是自由文本，不是可寻址标识。目录上我们没有 `specs/` 之类的制品根，制品全在 `.charter/` 下平铺（project.md / roadmap.md / current-task.md / reuse-discovery.md / handoff.md / decision.md / review.md / evidence-receipt.md / lessons.md + evidence/，见 `charter-workflow.md:29`）。

**判定。** ⊂，但**不建议照抄**。ID 已经承担了寻址，再叠一层人类可读 slug 只会产生第二个命名源。真正值得拿的是两条小的：(a) 编号前缀的两种策略（顺序号 / 时间戳）对多分支并行有价值；(b) **把解析结果持久化成一份显式指针文件**，让下游不依赖分支名或目录推断——这一条我们有等价物（`.charter/current-task.md` 就是指针），但没写「为什么是指针而不是推断」，而 `roadmap.md:28` 那句 "this status is a synchronized projection and must match project.md" 已经在同一个坑上有了更强的表述。判定为「不需要补」。

---

## §3 B 组：任务侧怎么拆、怎么排

### M6 拆解粒度与并行标注 —— ⊃ 粒度，∅ 并行

**对方的写法。** `tasks-template.md` 的格式行 `[ID] [P?] [Story] Description`，其中 `[P]` 表示可并行（判据明写「不同文件、无依赖」），`[Story]` 是 US1/US2/US3 归属，描述必须含精确文件路径。结构是固定三段：Phase 1 Setup → Phase 2 Foundational（标 **Blocking Prerequisites**，⚠️ CRITICAL，任何 story 之前必须完成）→ Phase 3+ 每个 User Story 一节（Goal / Independent Test / Tests 可选且先写失败 / Implementation），每节末尾一句 Checkpoint。路径约定按项目类型分三套：single project 用 `src/`+`tests/`，web app 用 `backend/src/`+`frontend/src/`，mobile 用 `api/src/`+`ios/src/`。

**我们的写法。** 粒度判据比他们硬：`DEVELOPMENT_CHARTER.md:163-174` 一叶只交付一个可观察行为，WIP=1；`leaf-task.md:3` 写死 "If the result sentence contains **and** twice, split the task"——一条可机械判定的拆解规则，比「Phase 3+ 每 story 一节」更不容易被绕过。`leaf-task.md:59-63` 的 Allowed paths 要求工作区相对路径，比「描述里含文件路径」更可验证。`leaf-task.md:7` 还给了体积上限 36 KB 与超限时的搬运规则（把目标散文搬到 project.md、排序搬到 roadmap.md、候选证据与固定版本搬到 reuse-discovery.md、命令输出搬到 evidence/），并禁止用删验收来换体积。

我们**完全没有并行标注**：`DEVELOPMENT_CHARTER.md:5-18` 明文写「无锁、无租约、无并发合并、无 Agent 通信」，WIP 恒为 1。

**判定。** 粒度 ⊃（可机械判定的 and 规则 + 路径白名单 + 体积上限，三项都比对方硬），并行标注 ∅ 且**不应吸收**。`[P]` 标记的前提是并发合并在同一工作区里被假定安全；我们的模型是把并发排除在外，吸收 `[P]` 等于在一个串行模型上贴一个并行的标签，只会让人误以为可以同时开工。这一条归入 §9 不吸收。

### M7 依赖与阻塞 —— ⊃

**对方的写法。** 依赖靠两处表达：`tasks-template.md` 的 Phase 2 Foundational 作为全局阻塞段（⚠️ CRITICAL），以及任务行内的 `(depends on T012, T013)` 文本。/OpenSpec 侧则把它哲学化：`docs/workflows.md` 原文 "**Dependencies are enablers** — they show what's possible, not what's required next"，即依赖只说明「可以做什么」，不构成「必须先做什么」的强制序列。

**我们的写法。** `DEVELOPMENT_CHARTER.md:263-279` 十一条启动门禁里有两条直接管依赖：前置必须全部 `PASS_CLOSED`，且不得有另一个活动叶。`roadmap.md:53` RDY2 是 "predecessor is —, or every listed predecessor is actually `PASS_CLOSED`"，`roadmap.md:76` 收尾规则再压一次："Only `PASS_CLOSED` leaves may unblock a dependent leaf." 也就是说我们的依赖是**状态依赖**，不是任务号依赖；被依赖项必须已完成且已关闭，而不是「已排过号」。

**判定。** ⊃，且这是本质差异而非措辞差异。对方的 `depends on T012` 只表达「T014 在 T012 之后合理地做」，不检查 T012 是否真的通过；我们的前置检查是门禁第 5 条，过不了叶就不能进 `READY`。`roadmap.md:76` 那句 "A branch commit, a focused green test, or a proposed next candidate is not closure by itself" 正好封掉了对方模型里最容易漏的一格。

---

## §4 C 组：门禁与授权

### M8 阶段门 —— ⊃

**对方的写法。** `plan-template.md` 的 Constitution Check 只有一句原文式的门：*"GATE: Must pass before Phase 0 research. Re-check after Phase 1 design."* 两次检查，一次在设计前一次在设计后，判定依据是 `/memory/constitution.md`。另外 `plan-template.md` 的 Technical Context 有十项可填字段（Language/Version、Primary Dependencies、Storage、Testing、Target Platform、Project Type、Performance Goals、Constraints、Scale/Scope），每项都允许写 NEEDS CLARIFICATION。

**我们的写法。** `DEVELOPMENT_CHARTER.md:263-279` 十一条 + `roadmap.md:52-64` RDY1–RDY13 十三条。两者内容重叠但用途不同：十一条是章程侧的门禁清单，RDY 是叶侧可勾清单且带 append-only 编号。关键是这些条目全部**可观测**——章程原文要求「验收可观察或可测」「下一动作具体且唯一」，而不是「设计合理」。

**判定。** ⊃。两处 GATE 检查的是「设计是否符合原则」，十一条 + 十三条检查的是「这一叶现在能不能开工」——后者包含前者没有的：前置是否真的关闭、是否已有另一个活动叶、工作区与用户改动是否记录、依赖检查证据是否存在、复用门是否 COMPLETE 或有界 waiver、下一动作是否唯一。设计符合原则，仍可能因为没有审批而不能开工；反过来，有审批也不能让一个不合原则的设计通过。我们两轴都有，对方只有一轴。

### M9 违例的处置 —— ⊃

**对方的写法。** `plan-template.md` 有 Complexity Tracking 段，但触发条件写得很窄："**only when Constitution Check has violations that must be justified**"，表头三列 `Violation | Why Needed | Simpler Alternative Rejected Because`。/OpenSpec 侧的 analyze 命令把违例升级为强制事件：constitution 冲突**自动 CRITICAL**，要求调整 spec/plan/tasks，并明文规定「不得稀释、重解释或静默忽略」；若原则本身要改，必须在 analyze 之外单独显式更新 constitution。

**我们的写法。** `DEVELOPMENT_CHARTER.md:243-251` 把修复等级 A/B/C 与严重度 P0–P3 定为**两条独立轴**且不自动映射——A 合同内 / B 须预授权 / C 必须 NEEDS_DECISION，同时 P0/P1 不能因为标了 A 就降级。`:206` 规定「无法证明在合同内不得标 `IN_CONTRACT`」。waiver 在 `:224` 与 `roadmap.md:60` 都被要求写全五项（叶 ID、批准或遗漏范围、接受限制、批准人、过期或复查条件），并在两处明写「waiver 不是第四种门状态」。

**判定。** ⊃。对方的 Complexity Tracking 只是一张「请为你的复杂辩护」的表，没有处置路径、没有等级、没有过期；OpenSpec 的 CRITICAL 有强制力但只有一档。我们两轴四档加 waiver 五项，是可审计的处置链。

### M10 只读门 —— ≡／⊃

**对方的写法。** `checklist-template.md` 把 checklist 定义成 reviewer 所有的**需求质量**评审物，并在两处把语义钉死：

- "**Marker Semantics**: `[x]` means the criterion has been reviewed and satisfied for requirements quality. **It does not mean implementation work is complete.**"
- "`__SPECKIT_COMMAND_IMPLEMENT__` **reads checklist checkbox state as a gate and must not modify markers**"

`implement.md` 的 Step 2 落实这条：扫描所有 checklists/ 文件、统计 Total/Checked/Unchecked 出状态表、需要时**询问**再继续、**不得修改 checklist 文件或标记**。

**我们的写法。** `DEVELOPMENT_CHARTER.md:93` 通用不变量第四条「执行者自报不能替代独立证据」；`:329`「只在分支提交、只跑 focused 测试、只有 Agent 报告都不足以关闭」；`leaf-task.md:112-119` 的 receipt 纪律（记录的命令在提交 receipt 前要重跑；事实陈述要么在同一次提交里可核对，要么标为 aspirational；自验证必须从原始物重算，一个重读自己要认证的字段的检查最多证明文件没被改，被篡改的副本必须让它失败）；`leaf-task.md:121-138` 的 Check discipline（读被测对象 / 覆盖每一个实例 / 必须能移动退出码，打印但不影响退出码的违规只是日志行不是门）。

**判定。** 意图 ≡，约束力 ⊃。对方用「标记只读」这一条形式约束防止执行者自证；我们不靠单条规则，而是把「什么才叫证据」摊成 receipt + check discipline + 三条不变量。差别在覆盖面：他们的只读保护的是 checklist 这一个文件，我们的纪律覆盖任意检查。

### M11 只读分析命令 —— ⊂

**对方的写法。** `analyze.md`（11758 字符）是一个专门的跨制品只读分析命令：description 写 "Perform a non-destructive cross-artifact consistency and quality analysis across spec.md, plan.md, and tasks.md"，正文标 **STRICTLY READ-ONLY**——不改任何文件、只出结构化报告、可以给补救计划但必须用户显式批准后才走编辑命令；只能在该 `tasks.md` 已完整产出后运行；输出里出现 constitution 冲突即 CRITICAL。

**我们的写法。** Review A（每叶必需，查规格覆盖/实现正确性/范围漂移/测试质量，默认由不持有实现上下文的审阅者执行）与 Review B（另一个 fresh 审阅者，RVB1–RVB5 触发）都是**针对候选 diff** 的；`roadmap.md:70` 有「三份投影不一致即阻塞性发现」的对账规则，`leaf-task.md:220-227` 有「同一个声明在合同 §9、roadmap 状态列、handoff 活动叶块三处同时更正」的镜像纪律。

**判定。** ⊂，但缺的很小。我们有跨文件一致性纪律，但没有一个**独立的、可随时只读跑一次**的跨制品分析动作；它相当于在「Review A 之前」加一次零成本自检。价值在于时序：analyze 是**在任何候选存在之前**就能跑的，Review A 必须先有候选。补丁 P1-3。

---

## §5 D 组：状态、制品与收尾

### M12 状态的必要性与顺序 —— ≠ 取向相反

**对方的写法。** OpenSpec `docs/workflows.md` 的标题就是 "Actions, not phases"，并把依赖定义为 enabler。默认 core profile 只有六个命令（propose / explore / apply / update / sync / archive），扩展命令（new / continue / ff / verify / bulk-archive / onboard）要手动启用 profile 才有。`/opsx:update` 可以在 apply 之后回头改规划制品，链路是环形的：propose → review →（refine → update 回环）→ apply →（plan changed → update）→ verify → sync → archive。它的自陈旧版四宗罪里第一条就是「指令硬编码在 TypeScript 里不可改」，解法是把 schema.yaml 与 templates 摊成可编辑文件——同一种「少约束、多可改」的取向。

**我们的写法。** `DEVELOPMENT_CHARTER.md:331-345` 七态强制序列 `DRAFT → APPROVED → READY → IN_PROGRESS → REVIEW → VERIFIED → PASS_CLOSED`，每个叶必须在任务文件与 roadmap **同步**经历七态；异常态五个；项目级 `PAUSED/CLOSED` 明文不是通过状态；`leaf-task.md:218` 再钉一次顺序 "Required order: Review → Verification → target-branch integration → post-integration verification"，并禁止「从 Review 直接集成」「把集成前验证当集成后证明」。

**判定。** ≠。这不是同一条曲线上的强弱，是两个目标函数：对方优化的是**改动的自由**（少状态、可回环、依赖不强制），我们优化的是**关闭的可信**（每步有证据、状态转移即授权事件、不可跳过）。这个差异不该被消解——但要承认它有一个代价，而对方的 explore 命令正好是对代价的补偿。

对方 `/opsx:explore` 的定位是 "a no-stakes thinking partner"：读代码库、比选项、画图，**任何结构都不要求**，想清楚了再决定是否落成一个 change。我们最接近的是 `:230-232` 首启访谈与 §8 的 grill-me 路由，但二者都发生在 `INIT` 阶段，且都以「产出章程」为目的；**在一个已经跑起来的项目里，我们没有「不产出任何记录的思考回合」这个动作**——任何进入 §2.8.1 Change Triage 的东西都立刻被分类、走路由、留痕。有些想法不值得留痕。这一条见 §9。

### M13 增量制品的表达 —— ∅

**对方的写法。** OpenSpec 的核心制品是 **delta**，规则在真实 spec 里（`archive/2025-08-19-adopt-delta-based-changes/specs/openspec-conventions/spec.md`，4049 字符）：

- Requirement 的 `### Requirement: <header>` 头**就是唯一标识符**；规范化只有 `normalize(header) = trim(header)`，规范化后**大小写敏感**比较；
- 重命名必须走 `## RENAMED Requirements`，写 `- FROM:` / `- TO:` 两行；若内容同时变，则放进 MODIFIED 并使用**新** header；
- 同一 spec 内 header 不得重复，校验工具**必须**报错；
- 变更只存增量不存完整未来态：ADDED 每条含完整内容；MODIFIED 用与当前 spec 相同的规范化 header 加**完整修改后需求（不是 diff）**，可选行内注释 `← (was X)`；REMOVED 用规范化 header 加删除原因与迁移路径；
- CLI 符号规范：`+` ADDED 绿 / `~` MODIFIED 黄 / `-` REMOVED 红 / `→` RENAMED。

配套的 proposal 三段式（`archive/2025-08-19-add-zod-validation/proposal.md`）：`## Why` / `## What Changes`（bullet 列表）/ `## Impact`，Impact 下再分 `**Affected specs**` 与 `**Affected code**`，每条带文件路径。

**我们的写法。** 叶合同是**完整快照**：`leaf-task.md:5` 允许对已在必读集里的来源用「引用 + 本叶增量」写（例如 `project.md section 5 baseline, plus: <leaf-specific item>`），但明文规定「Never replace a leaf-specific field with a reference」——结果句、允许路径、验收检查、修复预算、任何非标准停止条件必须写全。也就是说我们**有** delta 的概念，但它只存在于「合同 vs 必读集」之间，不存在于「本次变更 vs 上一次制品」之间，而且没有 ADDED/MODIFIED/REMOVED 三分，也没有「header 即身份」的唯一性规则。

**判定。** ∅，且**部分是设计选择**。叶合同是快照而不是 delta，是因为关闭后它要被归档并在后续任意时刻被重新读通——一个只有 delta 的制品，读它必须先有完整上下文。这是对的。真正缺的是 `## Impact` 那一层：`leaf-task.md` 有 Allowed paths（正向白名单）与 Forbidden effects（负向清单），但没有「**这次变更会影响哪些既有制品/公共含义**」的枚举。`roadmap.md:80-82` 的 Decisions 表有 `Affected IDs` 一列，说明这个想法在我们体系里已经存在，只是没有进叶合同。补丁 P1-2。

### M14 归档与收尾 —— ⊃

**对方的写法。** 真实 spec（`archive/2025-08-13-add-archive-command/specs/cli-archive/spec.md`，4373 字符）把收尾行为逐条写成 WHEN/THEN：未完成任务（`- [ ]`）→ 列出全部未完成项 → 提示确认 → **默认 "No"（for safety）**；目标 archive 目录已存在 → 报错，**不覆盖**；spec 更新是**覆盖**，理由原文是 "specs represent current reality, change specs are the new reality"；确认提示必须显式列出 NEW specs to be created 与 EXISTING specs to be updated 及各自源路径。CLI 侧 `openspec archive --yes` 跳过确认，但**仍会 validate 再应用 delta 并归档**。

另有一条架构纪律值得记：`openspec instructions archive --change X --json` 本身**只读**——不检查也不合并 delta、不写主 spec、不移目录、不跑静态归档流程。

**我们的写法。** `leaf-task.md:229-242` 五选一的关闭决定（PASS_CLOSED / PARTIAL / BLOCKED / BLOCKED_TOOLING / NEEDS_DECISION），`:211` 要求「既无对账又无 `NOT_ENABLED` 留痕不得 PASS_CLOSED」——无对账就关成 `PARTIAL` 并写原因；`:174-178` 出向合同归档到 `.charter/evidence/<date>-<leaf>-contract-archive.md` 并在同一次会话内、在 `current-task.md` 被覆写之前提交，且要求**增量编辑，绝不整文件重写**，理由是「留在叶工作树里未提交的记录会随工作树一起死掉」；`roadmap.md:72` 要求关闭时清 `Active leaf` 并同步 `Next authorization`。

**判定。** ⊃。「默认 No」「不覆盖」「归档前必须 validate」三条纪律我们有等价物或更严的版本（关闭五态、对账证据、增量编辑、同会话提交）。他们那条「主 spec 覆盖，因为 spec 代表当前现实」在我们这里没有对应物，但那是因为我们的制品结构不同（`.charter/` 是治理事实源而非当前现实），不构成缺口。

---

## §6 E 组：上下文与扩展

### M15 上下文注入通道 —— ⊂

**对方的写法。** `docs/customization.md` + `docs/opsx.md` 把注入拆成**三条独立的通道**，语义严格分离：

| 通道 | 位置 | 作用域 | 约束力 |
|---|---|---|---|
| `context` | `openspec/config.yaml` 的 `context` | **注入全部 artifact** | 必需的提示词级输入 |
| `rules` | 同上 `rules`，按 artifact 分（proposal / specs / design …） | **只注入匹配的 artifact** | 强制 |
| `guidance` | `operations.apply.guidance` / `operations.archive.guidance` | 只对某个 operation | **顾问性**，不约束 artifact 内容 |

三条边界各有一句明文守住：operation guidance 是顾问性的、不约束 artifact 内容；**artifact rules 永远不会被重标成 operation guidance**；工作流会**报告 context 冲突但保留控制值**，不跟随不适用或冲突的 guidance。另外 `openspec instructions <op> --change X --json` 在**运行时**返回当前 context 与 operationGuidance 的 fresh snapshot（每次调用重读解析根），`--store <id>` 时三者都取自那个 store。

三级定制（`customization.md`）：Project Config（最省事）/ Custom Schemas（自定义 artifact 序列）/ Global Overrides（跨项目共享 schema）。

**我们的写法。** `.charter/project.md` 是主通道（目标、非目标、不变量、约束），模板只提供形状，`portable/references/*.md` 与 `portable/prompts/*-bootstrap.md` 是固定文本。`DEVELOPMENT_CHARTER.md:388-390` §9 有一条重要的反向纪律：领域细节**不得**回写通用章程、模板与宿主入口；运行时业务 Prompt 与开发治理 Prompt 分开。

**判定。** ⊂ 在结构，⊃ 在纪律。他们把上下文分成三档约束力（必需 / 强制 / 顾问）是可执行的——一个写了 guidance 的人知道它不会被当规则执行；我们的全部上下文都是同一档，靠 §9 的一条禁令防止污染。缺的是「按制品分别加规则」这个粒度：我们的 `references/design-interview.md`、`change-triage.md`、`lessons.md` 都是全局可读，没有「这条只对叶合同生效、那条只对 roadmap 生效」的表达方式。

### M16 扩展点 —— ⊂

**对方的写法。** 所有 `templates/commands/*.md` 共有一段 **Pre-Execution Checks**，读 `.specify/extensions.yml` 的 `hooks.before_<command>`，规则有四层：

1. 过滤 `enabled: false`（缺省视为启用）；
2. `condition` 非空则跳过，交给 HookExecutor 求值；
3. `optional: true` 只输出提示块；`optional: false` 输出 `EXECUTE_COMMAND` 并**必须真的调用并等待完成**——原文明确 "光输出块不算执行"；
4. YAML 解析失败**不得静默跳过**，须报告 parser error 并说明未检查任何 hooks。

另一处更锋利的授权机制在 `constitution.md` 的 **Scope Guard**：把用户输入分类为「constitution 内容」或「独立的非治理意图」；若是 feature 实现/代码生成/重构/构建/部署请求，**MUST NOT 执行**，提取为 deferred intents；完成后在 `Next Actions` 段落列出原始意图并**建议**后续命令，但**不调用**。

**我们的写法。** `DEVELOPMENT_CHARTER.md:369-386` §8 工具路由是 11 行职责表（需求澄清→brainstorming、多步计划→writing-plans、TDD、根因→systematic-debugging、独立审阅、完成验证→verification-before-completion、方案拷问→grill-me、长任务状态→J-space、复用发现、隔离集成），`:228` 的五个 Reuse Provider 明文是「插槽非固定串行」。缺省行为也已写死：provider 失败允许重试一次，随后必须**当场明示** FALLBACK，静默降级视为违规。

**判定。** ⊂ 在形式，⊃ 在诚实度。我们的 Provider 模型比 hooks 更有原则（失败必须留痕、插槽不串行、只发现不安装），但全部是**散文规定**，没有一份机器可读的注册表，因此无法在出错时判断「这个 provider 到底注册过没有、它的 before/after 是什么」。他们那份 `extensions.yml` 的价值不在扩展性，在于**错误可判**：`optional: false` 没真执行就是违规，YAML 解析失败必须报错而不是当没有 hooks。

最值得单独拿的是 Scope Guard 那条纪律。我们 `charter-workflow.md:12` 的 Context Router 已经分 `INIT/RESUME/CHANGE` 三支（这是形式上的类似物），但**没有「当用户在一个非写入动作里夹带了实现请求，必须拒绝执行并只建议下一步」这条显式规则**。我们在这一格上靠 `:253-255` 的 `NEXT_CANDIDATE ≠ NEXT_AUTHORIZATION` 兜底——方向对，但不是同一件事：那是防「候选被当授权」，这是防「顺手把活干了」。

### M17 机读面 —— ∅

**对方的写法。** OpenSpec CLI 的命令面被明确切成 **Human-Only** 与 **Agent-Compatible（`--json`）** 两组。Agent-Compatible 组包含 `list / show / validate / status / instructions / templates / schemas / store * / new change / workset *`；其中 `validate` 支持 `--all --json` 批量。/spec-kit 侧的每个命令 frontmatter 都声明三份等价脚本（`sh` / `ps` / `py`），并用 `handoffs:` 声明下一步能交给哪个 agent 与什么 prompt。

**我们的写法。** `scripts/validate_kit.py` 只出人读文本，唯一判据是退出码与一行 `PASS (N files checked)`；`check_dependencies.py` 有 `--json --log-file`（`charter-workflow.md:49` 用到了），但那是依赖探测，不是制品校验。

**判定。** ∅。这一条直接落在我们自己的 §10.2「中期可吸收」清单里，本文只是把它对应到了具体的对方命令面上。补丁 P2-1。

---

## §7 三条结构性差异的机制级论证

前文第 2 轮已给出三条分野；这里只补它们的**机制证据**，即「为什么这不是措辞差异」。

**差异一：代码是主产物，还是 spec 是主产物。** 判据在关闭动作上。`leaf-task.md:229-242` 的关闭决定里，`PASS_CLOSED` 的定义是"acceptance, Review, pre-integration Verification, target-branch integration, and post-integration verification are all evidenced"——主语全是**验证动作**；`openspec archive` 的定义是「validate 之后把 delta 应用到主 spec 并移目录」——主语是**制品**。前者即使 spec 写坏了，只要验收与集成证据齐也能关；后者即使代码没跑过，只要 delta 应用成功也能归档。机制上这是两个不同的完整性判据，不能互相替代。

**差异二：授权是不是建模对象。** 对方两套工具里，最接近授权的构造只有两处：`constitution.md` 的 Scope Guard（拒绝执行非治理请求、只建议下一步）与 hooks 的 `optional: false`（必须真跑并等待）。前者限制的是**命令能做什么**，后者限制的是**一个 hook 有没有被执行**，两者都不改变任何制品的状态；**没有任何状态转移以「获得授权」为条件**。/Charter Kit 侧，`:253-255` 的 `NEXT_CANDIDATE ≠ NEXT_AUTHORIZATION`、`:345`「项目批准只批方向不批任何叶」、`:263` 门禁第 3 条「单独批准或匹配 AUTO_DEV 且同步 APPROVED」、`leaf-task.md:241-242` 的 `Next authorization: NOT_GRANTED` 默认值——四处独立构造指向同一件事：**每个状态转移都是一个授权事件**，且默认值是否定的。

**差异三：规模控制靠什么。** 对方的规模控制是**制品类型数 × 每个制品的模板自由度**——`propose` 一次生成 proposal / specs / design / tasks 四份（`core` profile 的快速路径），自由度靠 schema.yaml 与 templates 放开。我们的规模控制是**叶边界 + 体积上限 + 时间指标**：一叶一可观察行为、结果句两次 and 就拆、合同 ≤ 36 KB、lessons ≤ 64 KB、§11 每两三个叶检查产品开发时间是否仍高于流程维护时间。Fowler 批的「大锤砸核桃」在我们的模型里**没有被前置阻止**——这一点在 §8 P0-1 处理。

---

## §8 补丁清单

排序原则：先补「不改变模型、只加形式」的（低风险高收益），再补「加结构」的，最后补「加机制」的。

### P0 —— 立刻可做，纯加法，不动既有语义

**P0-1 TRIVIAL 路由（对应 §7 差异三）**

在 `DEVELOPMENT_CHARTER.md` §2.8.1 Change Triage 之后插入一小节，给「不值得走完整叶循环」的改动一条有界的路。草案：

    ### 2.8.2 TRIVIAL 路由

    一次改动只有同时满足以下五条才可判 TRIVIAL：
    1. 不改任何已批准的行为、公共含义、不变量或效果授权；
    2. 不新增依赖、版本、栈、外部边界；
    3. 允许路径不超过一个文件，或纯文档；
    4. 不触及 BLOCKED 的判断或复用门的结论；
    5. 可由一次整表验证完整覆盖。

    TRIVIAL 不是新状态，也不是跳过门禁：叶仍走 DRAFT → APPROVED → READY，
    但 §4.3 设计外置、§4.5 Review B、§4.2 门禁的第 9、10、11 条按有界省略处理，
    省略理由写进 Events 表。任何一条不满足，立即降级回标准叶循环。
    一个会话内连续三个 TRIVIAL 叶，第四个必须走标准循环。

需要同时改的三处：`roadmap.md` 的 Level 列加一个取值；`leaf-task.md:16` 的 Mode 行加 `TRIVIAL`（或另设一行）；`validate_kit.py` 若校验 Mode 取值则同步放开。

**P0-2 澄清的分类法与上限（M3 + M4）**

新建 `portable/references/clarification.md`，装那张十类扫描表（Clear/Partial/Missing）与三个数字：`[NEEDS CLARIFICATION]` 全叶上限 3、访谈问题上限 5、一次一个、(Impact × Uncertainty) 排序。然后在两处引用它：`DEVELOPMENT_CHARTER.md:230-232` 首启访谈、`leaf-task.md:246` Design tree。原文里的写作约束（问题必须是完整疑问句，id 只放问号后括号里）照抄，因为那是可直接校验的形式。

**P0-3 验收条目编号 AC-N（M1）**

`leaf-task.md` §5 的三组检查各加编号，规则与 RDY 完全一致（append-only，退休保号记日期）：

    ### Positive behavior
    - [ ] AC1 — <observable check>
    - [ ] AC2 — <observable check>

    引用方式：Review A / Change Triage / lessons 一律写 AC# 加短标签，
    不重述检查文本；改检查即改号，旧号退休不重用。

同时把 `leaf-task.md:210` 的 RDY 引用句扩成「RDY# 与 AC# 均按编号引用」。

**P0-4 不变量违例扫描进门禁（M8 的补）**

`DEVELOPMENT_CHARTER.md:263-279` 十一条后加第十二条：逐条比对 `:93` 五条通用不变量，任何一条可能被本叶触及即必须显式写「不触及」或「如何保持」，空着不算通过。`leaf-task.md:43-55` 的 Preconditions 同步加一节。

### P1 —— 加结构，需要一次设计

**P1-1 扩展点注册表（M16）**

新建 `.charter/hooks.yaml`，最小字段照 `extensions.yml` 的四层规则：`command` / `optional` / `enabled` / `condition`，并继承两条硬纪律——`optional: false` 必须真执行并等待，解析失败必须报错不得静默。把 `:369-386` §8 的 11 行路由表与 `:228` 的五个 Reuse Provider 注册进去。

**P1-2 Impact 段（M13）**

`leaf-task.md` §4 加一小节，照 OpenSpec proposal 的 `## Impact`：

    ### Impact
    - Affected specs: <project.md 的节号或 roadmap 的行 ID>
    - Affected code: <路径 + 该路径当前的公共含义>
    - Affected governance: <哪些既存记录会因此失真>

第三条是我们自己的扩展——对方没有治理层，所以没有这一行。

**P1-3 只读分析动作（M11）**

把 `leaf-task.md` §9 之前的某个位置加一个可显式调用的「合同-规格-候选三方扫描」，语义照 `analyze.md`：STRICTLY READ-ONLY、不改文件、只出报告、可与 Review A 分离执行、任何不变量冲突自动升级为阻塞。

**P1-4 Schema Guard（M16 的 Scope Guard）**

`portable/commands/charter-workflow.md:12` 的 Context Router 加一条：当一次非写入动作（RESUME / CHANGE 的读取步骤）里出现实现请求，MUST NOT 执行，提取为 deferred intent，在末尾以建议形式列出，不调用。草案可直接改写那句话。

### P2 —— 加机制，收益确认后再做

**P2-1 `validate_kit.py --json`（M17）**：输出机读结构，支持批量。
**P2-2 制品级校验（M17 的延伸）**：现在只校验套件自身，不校验下游 `.charter/`；补一个 `--project` 模式，检查 RDY 编号连续性、AC 编号唯一性、三处状态镜像一致。
**P2-3 上下文三通道（M15）**：若将来 `project.md` 膨胀，再考虑按制品分流 rules；现在不建议。
**P2-4 修正 `leaf-task.md:7` 的自述尺寸**：模板写着 "about 10 KB"，实测 15708 字节。改成实测值或改成区间，否则这句话本身就是一条失真的证据。

---

## §9 不吸收，以及为什么

| 候选 | 不吸收的理由 |
|---|---|
| `[P]` 并行标注（M6） | 我们的模型把并发排除在外（`:5-18` 无锁无租约无并发合并），贴并行标签会制造「可以同时开工」的错觉 |
| spec-as-source 的生成式映射 | 代码是主产物，没有 spec→code 生成，抄来只会引入 MDD 的老坑（抽象层级尴尬、非确定性 + 不可解析双输） |
| 完全 fluid 的 "Actions, not phases"（M12） | 关闭的可信依赖状态序列；去掉序列就失去「每个状态转移是授权事件」 |
| `/opsx:explore` 的「不产出记录的思考回合」 | **这一条我改变过主意**：原本想照抄，但它与 `:392-406` 九条停机条件、`:253-255` 授权纪律冲突——一个不留痕的回合在事后无法被审。折中见下 |
| 多仓 stores / workset（OpenSpec CLI） | 单项目单工作集是 `:5-18` 的前提；多根会让「唯一事实源」变成「哪一根」 |
| Catalog 式无审查安装 | 与 `:228` 的「find-skills 只发现不安装、repo-to-skill 选定后单独授权」直接矛盾 |

关于 explore 那一格的折中：不引入无记录回合，但可以在 `handoff.md` 里加一段显式的「未定想法（advisory）」——不入 Change Triage、不产生状态、不构成授权，只在恢复时被读到。它保留了 explore 的用途，又不破坏留痕纪律。这一条列为待定，不写入补丁清单。

---

## §10 怎么复核本文

本文所有对方事实都可复现，取原文的命令形态是：

    https://cdn.jsdelivr.net/gh/github/spec-kit@main/templates/spec-template.md
    https://cdn.jsdelivr.net/gh/github/spec-kit@main/templates/tasks-template.md
    https://cdn.jsdelivr.net/gh/github/spec-kit@main/templates/checklist-template.md
    https://cdn.jsdelivr.net/gh/github/spec-kit@main/templates/plan-template.md
    https://cdn.jsdelivr.net/gh/github/spec-kit@main/templates/commands/{specify,clarify,analyze,implement,constitution}.md

    https://cdn.jsdelivr.net/gh/Fission-AI/OpenSpec@main/docs/{workflows,opsx,commands,customization,cli}.md
    https://cdn.jsdelivr.net/gh/Fission-AI/OpenSpec@main/openspec/changes/archive/2025-08-19-adopt-delta-based-changes/specs/openspec-conventions/spec.md
    https://cdn.jsdelivr.net/gh/Fission-AI/OpenSpec@main/openspec/changes/archive/2025-08-13-add-archive-command/specs/cli-archive/spec.md
    https://cdn.jsdelivr.net/gh/Fission-AI/OpenSpec@main/openspec/changes/archive/2025-08-19-add-zod-validation/proposal.md

注意两条取文限制，它们会影响复现的结论：

1. OpenSpec 仓库里**未归档**的 `openspec/changes/<name>/*` 在 main 上取不到（404），只有 `archive/YYYY-MM-DD-<change>/*` 可取。本文的样例全部来自 archive，因此是一手但非当前进行中的工作。
2. spec-kit 的 `/memory/constitution.md` 在该 CDN 路径取不到（404），本文关于 constitution 的判定只依据 `templates/commands/constitution.md`、`analyze.md`、`implement.md` 里对它的引用，未读该文件本身。

我方事实的复现：

    wc -l -c DEVELOPMENT_CHARTER.md skills/charter-workflow/templates/*.md portable/commands/charter-workflow.md portable/references/*.md
    python scripts/validate_kit.py .
