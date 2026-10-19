# SDD（规范驱动开发）对照：对齐点、分野与风险

> 目的：把 Charter Kit 与 2025 年流行的 SDD（Spec-Driven Development，规范驱动开发）放在同一张桌上比对——哪些是同构、哪些是刻意不同、哪些是 SDD 的批评正好落在本套件身上。
> 本文是分析文档，不是章程、不是门、不改变任何授权。所有"本套件"的引用都指向当前仓库文件与行号。
> §1–§8 是 2025-10 的基线；§9–§12 是 2026-10 的生态复盘与吸收清单，两者冲突时以 §9 之后为准。
> 机制级对照（逐条原文、行号、判定、补丁草案）另见 [SDD-MECHANISM-AUDIT.md](SDD-MECHANISM-AUDIT.md)——本文给结论，那份给证据。

---

## 0. 一句话结论

SDD 与 Charter Kit 在 **spec-first 层高度同构**：Kiro 的 `Requirements → Design → Tasks`、spec-kit 的 `Constitution → Specify → Plan → Tasks`，在本套件里都有明确对应物。真正的分野有三条，而且都是刻意的：

1. **规范的定位不同**——SDD 让 spec 成为"人和 AI 的事实源"、Tessl 更进一步让 spec 成为主产物（spec-as-source）；本套件让 `.charter/` 成为**治理**的事实源，**代码/产品仍是主产物**，没有任何一步"由 spec 生成代码"。
2. **SDD 不建模授权**——三款工具回答的是"下一步该写哪个文档"；本套件每个状态转移回答的是"谁允许做、允许到什么程度"（`DRAFT→APPROVED→READY`、`MANUAL/AUTO_DEV`、A/B/C 修复等级、带批准人与过期条件的 waiver）。
3. **规模控制机制不同**——SDD 用固定三段流水线，本套件用 Change Triage 四问 + `WIP = 1` + 叶边界（结果句出现两次"and"就拆）。但见 §5.1：本套件同样缺 fast lane，Fowler 那条"大锤砸核桃"的批评对 INIT 路径**依然成立**。

---

## 1. SDD 的现状（外部事实，先校准认知）

术语定义仍在漂移。目前最可用的分级来自 Thoughtworks 的 Birgitta Böckeler（martinfowler.com，2025-10-15）：

| 级别 | 含义 | 代表 |
| --- | --- | --- |
| **spec-first** | 先写一份想清楚的 spec，再进入 AI 辅助开发流程 | 三款工具都满足 |
| **spec-anchored** | 任务完成后 spec 保留下来，继续用于该功能的演进与维护 | Tessl 明确追求；spec-kit 名义上靠拢但按变更请求建分支，实际停在 spec-first |
| **spec-as-source** | spec 长期就是主源文件，人只编辑 spec、不碰代码 | Tessl 在 beta 里试水，1:1 映射，代码顶部标 `// GENERATED FROM SPEC - DO NOT EDIT` |

三款工具的实现形态：

- **Kiro**：VS Code 分发内引导三段 `Requirements → Design → Tasks`；Requirements 用 "As a…" + "GIVEN/WHEN/THEN" 验收条件；Tasks 回指需求编号并逐条可执行；memory bank 叫 *steering*，默认产出 `product.md / structure.md / tech.md`。
- **spec-kit**（GitHub）：CLI 生成工作区 + 斜杠命令驱动；**Constitution 是前置的"不可变原则"**（一个极强的 rules file）；`𝄆Specify → Plan → Tasks𝄇` 循环；每个 spec 建一个分支；用文件内 checklist 追踪澄清项、constitution 违例、研究任务。
- **Tessl Framework**（当时 private beta）：CLI 兼 MCP server；唯一明确追求 spec-anchored 并试探 spec-as-source 的工具；spec 里用 `@generate`/`@test` 之类标签告诉它生成什么，`tessl build` 产出代码。

同一篇文里的四条实测批评（后文 §5 会逐条对回本套件）：

1. **过度前置**：一个小 bug 被 Kiro 写成 4 个 user story、16 条验收条件，"像用大锤砸核桃"；spec-kit 一个 3–5 点故事产出大量 markdown，作者认为用普通 AI 编码早就做完了，而且更可控。
2. **review 负担错位**：markdown 多、互相重复、还和已有代码重复，有些里面已经含代码；"我更愿意 review 代码"。
3. **虚假掌控感**：模板/checklist 齐全，agent 仍然不遵守——spec-kit 的研究步骤正确识别了"这些是已有类的描述"，agent 却当成新 spec 重新生成了一遍，造成重复。
4. **功能/技术 spec 边界混乱**：什么时候停在功能层、什么时候加技术细节，教程自己都不一致；作者由此联想到 MDD 的老坑——抽象层级尴尬、非确定性 + 不可解析双输。

---

## 2. 逐项对照表

| SDD 概念 | 本套件对应物 | 位置 | 关系 |
| --- | --- | --- | --- |
| Kiro Requirements + 验收条件 | 叶合同的「One result sentence」+「Positive / Negative behavior」+「Review focus」 | `skills/charter-workflow/templates/leaf-task.md` §2、§5 | **同构且更严**：强制"一个叶只交付一个可观察行为"，不写 user story 集合 |
| Kiro Design | §4.3 设计外置与最小计划（写进任务目录/handoff，不单独建 `design.md` 主产物） | `DEVELOPMENT_CHARTER.md:281` | **弱化**：设计是叶内产物，不升级为独立事实源 |
| Kiro Tasks | roadmap 的 `EPIC / CAPABILITY / SLICE / LEAF` 四级 + 叶合同 | `DEVELOPMENT_CHARTER.md:163`；`templates/roadmap.md` | **增强**：任务不只是执行清单，而是**可授权单位** |
| spec-kit Constitution | `project.md` 的 Goal / Non-goals / Invariants + 规则优先级（用户指令 > 章程 > 叶合同 > 宿主默认） | `DEVELOPMENT_CHARTER.md:5-18`、`:78` | **同构且更强**：带批准、版本与门状态 |
| spec-kit checklist（每步的 definition of done） | `RDY1…` 编号就绪清单（只增不改，退役保留号） | `templates/roadmap.md` 的 Leaf readiness check | **同构**：都用稳定编号做可引用检查点 |
| spec-kit memory bank | 核心 Resume 文件：`project.md / roadmap.md / reuse-discovery.md / current-task.md / handoff.md / lessons.md` | `README.md`「会话恢复文件」 | **同构**，但显式区分"权威源"与"投影" |
| spec-kit 的 research 步骤 | §2.9 复用发现门（五层搜索、固定版本、`NO_MATCH` 需证据） | `DEVELOPMENT_CHARTER.md:208` | **增强**：搜索本身受授权约束，发现≠安装≠执行 |
| Tessl spec-as-source | **无对应，且明确不做** | — | **分野**（见 §3.1） |
| spec 的生命周期 | spec-anchored 只发生在治理侧：章程/roadmap 长期演进；叶合同关闭后归档保留 | `DEVELOPMENT_CHARTER.md:331` 状态机 | **半对齐**：叶合同锚定的是"这次变更"，不是"这个功能" |
| —（SDD 未建模） | 授权、门状态、waiver、证据收据、Review A/B、修复等级、失败停机 | `DEVELOPMENT_CHARTER.md:234-330`、`:392` | **本套件重心** |
| —（SDD 未建模） | 多宿主可移植、能力缺失记账（`AVAILABLE/MISSING/UNVERIFIED/FALLBACK`、`BLOCKED_TOOLING`） | `DEVELOPMENT_CHARTER.md:138`、`:369` | **本套件重心** |

---

## 3. 三条实质差异

### 3.1 规范是治理文件，不是生成源

SDD 的核心承诺是"spec 成为事实源，代码是最后一公里"。本套件只取前半句的**治理侧**：`.charter/` 是治理的事实源（`portable/commands/charter-workflow.md:46` 明确写 `.charter/ remains the governance source of truth`），但**没有任何机制从叶合同生成代码**。可检验的差别：

- Tessl 的 spec 与代码 1:1 映射、代码标"勿手改"；本套件里没有这种产物关系，叶合同只约束**边界、验收、证据与停止条件**。
- 因此本套件不会踩 MDD 的坑（非确定性 + 失去可解析结构带来的工具支持），代价是也不享受"改 spec 即改代码"的收益——这是有意为之的取舍，不是能力缺口。

### 3.2 授权模型是 SDD 的空白

三款工具里，流程步骤是"文档进度"；本套件里每个转移都是授权事件：

- `DRAFT → APPROVED → READY` 需要**单独批准**或匹配的 `AUTO_DEV` 预授权，项目批准**不隐含**批准任何叶（`DEVELOPMENT_CHARTER.md:331`）。
- 修复按 A/B/C 变更等级授权，与 P0–P3 严重度**两轴分离**（`:243`）。
- 复用门只有 `PENDING/COMPLETE/BLOCKED` 三态，waiver 必须写叶 ID、范围、限制、批准人、过期/复查条件，且不是第四态（`:208`）。

这正好回应 Fowler 那条"虚假掌控感"：控制点放在**授权与证据**上，而不是文档数量上。

### 3.3 规模控制：叶边界 + Change Triage

SDD 的固定流水线对 bug 级任务过重。本套件的抑制手段是：结果句含两次 "and" 就拆（`templates/leaf-task.md` 开篇）、`WIP = 1`、新需求不得静默扩大当前叶（`DEVELOPMENT_CHARTER.md:193`）、`NEXT_CANDIDATE ≠ NEXT_AUTHORIZATION`（`:253`）。

但注意：**INIT 路径仍然重**（见 §5.1），所以"同一组洞见"不等于"同样克制"。

---

## 4. 你们独立收敛到的同一组洞见

这些是 SDD 与本套件各自得出、但结论一致的东西——可以当作互相验证：

| 洞见 | SDD 侧 | 本套件侧 |
| --- | --- | --- |
| 先对齐意图再动手 | Kiro Requirements、spec-kit Specify | §2.10 首启访谈，`grill-me` 优先 / `design-interview` fallback（`:230`） |
| 事实源必须落在文件里，不能靠会话记忆 | memory bank / constitution | 六个核心 Resume 文件，恢复顺序固定（`:361`） |
| 别让 agent 自报成功 | （普遍缺失） | §6.1 证据记录、Review A fresh 上下文、合并后重新验证（`:309`、`:317`） |
| 失败要留痕 | （普遍缺失，正是"agent 忽略指令"无人记录） | `MISSING/UNVERIFIED/FALLBACK` 两层记账、`BLOCKED_TOOLING`（`:138`） |
| 检查点要可引用 | 需求编号回指 | `RDY`/`RVB` 编号只增不改（`:309`、`templates/roadmap.md`） |

---

## 5. 差距与风险：Fowler 的批评逐条对回本套件

### 5.1 过度前置 / 大锤砸核桃 —— **成立**

§12 最小启动清单是 8 步（`DEVELOPMENT_CHARTER.md:412`），加上章程自审、独立审阅触发判定、复用发现门；即使改一行 typo 也要走 INIT 语义。仓库里**没有** fast lane / trivial 路由（已 grep 确认：`portable/` 与 `skills/` 中不存在 `fast lane`、`trivial`、`轻量路径` 之类概念）。

建议（择一，属 B 类合同调整）：
- 增加 `TRIVIAL` 路由：单文件、无新能力、无外部效果 → 只记一条 Change Triage `IN_CONTRACT` + 证据，不重写章程、不走复用门；
- 或在 §11 流程健康检查里加一条硬上限："流程维护时间 > 产品开发时间"连续两次即暂停增机制。

### 5.2 review 负担 —— **部分成立**

叶合同模板自述约 10 KB、真实项目可达 35 KB，且**每次 resume 都要重读**（模板开篇已自认这笔成本）。目前只有"单个合同 ≤ 36 KB"的上限，没有"spec 总量 / 代码量"的比例约束，也没有"设计段必须迁出"的硬规则。

建议：把 Design 段迁往 `.charter/evidence/` 或 handoff，叶合同只留引用；或在 §11 加"markdown 增量 vs 代码增量"的观察项。

### 5.3 agent 不遵守 —— **部分成立，但已有兜底**

本套件的门是"AI 解释的 checklist"，执行者自报仍是主要信息来源（`:138`、`:263`）。真正的机械化兜底只有两处：Review A 的 fresh 上下文（`:309`）与套件级验证（`templates/leaf-task.md` 的 Suite verification）。`scripts/validate_kit.py` 校验的是**套件自身**的一致性（镜像、模板、契约字段），不校验任何下游项目的叶执行质量。

这正是 SDD 踩坑的地方：spec-kit 的研究步骤读对了、agent 却照旧重新生成。本套件对此的答案不是"写更多模板"，而是"让另一个人/进程看 diff"——方向是对的，但覆盖不到没有触发 Review B 的低风险叶。

### 5.4 功能 / 技术 spec 分离 —— **本套件更清楚，但没被命名**

`project.md` 承载 Goal / Non-goals / Invariants（功能与方向层），叶合同承载 Allowed paths / effects / 验收（边界与技术层），分离是**按文件切的**，比三款 SDD 工具都干净。但 `:78` 的"目标纠偏"没有把这条原则写成一句可引用的话。建议在 §2.2 补一行："功能层只写在 project.md，技术细节只写在叶合同；跨层插入视为 Change Triage 事件。"

### 5.5 spec-as-source 的诱惑 —— **建议写成不变量**

若未来想"让叶合同生成代码"，会直接进入 MDD 的老坑。建议把"代码/产品是主产物，规范不生成代码"作为 Invariants 的示例条目写进 `:93`，防止路线漂移。

---

## 6. 值得从 SDD 偷的三样

1. **需求/验收的稳定编号与追溯**：Kiro 的 requirement → task 回指很实用。本套件 `RDY`/`RVB` 有编号，但叶内的**验收条目**没有稳定 ID，跨叶追溯只能靠文字描述。
2. **一 spec 一分支**：spec-kit 每个 spec 建分支。本套件 §4.4 要求隔离分支（`:297`）但未规定"一叶一分支"，可对齐成默认。
3. **constitution violation 检查点**：spec-kit 在每步做一次"是否违反 constitution"的显式扫描。本套件的 Invariants 是静态清单，`:263` 的启动门禁**没有**这一条——加一条"本叶是否触碰任一 Invariant"的低成本自检，收益大于成本。

---

## 7. 对外一句话话术

> Charter Kit ≈ 给 SDD 补上治理层：把 spec-first 的产物从"给 agent 的提示材料"升级为"带授权、门、证据与关闭条件的合同"，并刻意停在 spec-anchored 的**治理侧**，不进入 spec-as-source——因为代码仍然是主产物。

反过来说也成立：**SDD 补上了 Charter Kit 缺的东西**——需求级编号、按变更切分支、以及"小改动也要有 spec"的直觉；本套件在 `TRIVIAL` 路由与验收编号上是短板。

---

## 8. 事实来源

- Birgitta Böckeler, *Understanding Spec-Driven-Development: Kiro, spec-kit, and Tessl*, martinfowler.com, 2025-10-15 — <https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html>
- Thoughtworks Technology Radar, *Spec-driven development* — <https://www.thoughtworks.com/cn/radar/techniques/spec-driven-development>
- 本仓库：`DEVELOPMENT_CHARTER.md`、`skills/charter-workflow/templates/leaf-task.md`、`skills/charter-workflow/templates/roadmap.md`、`docs/MIRROR-TOPOLOGY.md`、`README.md`「会话恢复文件」

---

## 9. 2026-10 生态快照（§1 之后一年的实际走向）

§1 记的是 2025-10 的三款原型。一年后再看，**三款原型没有一个还在原路线上**，而战场整体换了位置。

### 9.1 三款原型的走向

| 原型 | 2026-10 状态 | 关键变化 |
| --- | --- | --- |
| **spec-kit** | 活跃且高速演进：v1.2.1（2026-10-16），2,220 commits、235 tags | 从"一套模板"变成**分发平台**；且把"固定流水线"拆成三个**独立入口** |
| **Tessl** | 仍在运营，但对外主张已换 | 首页改成 *Build your software factory, one skill at a time — From skills to loops to factory*；博客主线是 Tessl Code Review 与 Tessl verifiers（2026-09/10）。**spec-as-source 不再是它的对外主张** |
| **Kiro** | 站点被 cookie 墙挡住，未取到一手公告 | 中文二手源称已 GA 并有 Windows 上手教程——**存疑，未一手核实** |

spec-kit 这一年的演进最值得看，因为它直接印证了 §5.1 的批评：

- **三个独立入口，不是强制阶段**：README 明说 *These are independent entry points, not mandatory phases*。
  - **SDD**（core）：`/speckit-constitution → specify → plan → tasks → implement → converge`，`implement → converge` 反复直到 *Converged*。
  - **Bug fixing**（`specify extension add bug`）：`assess → fix → test`，产出落在 `.specify/bugs/<slug>/`，最终判定 `verified | partial | failed`，并写明 *Missing verification is not a successful fix*。
  - **Idea assessment**（`specify extension add assess`）：`intake → research → define → shape → decide`，产出 `go / needs-clarification / kill`，**在没有任何源代码的项目里也能用**。
- **也就是说：连 GitHub 自己都承认固定流水线对 bug 级任务过重**，解法不是"把 spec 写短一点"，而是**给不同任务不同的入口 + 可选扩展**。这正是本套件 §5.1 缺的那一层结构。
- Thoughtworks Radar Vol 34（2026-04）：`Spec-driven development` 这个**技术**条目发布于 2025-11、评 `Assess`，并标注 **NOT ON THE CURRENT EDITION**；取而代之的是**工具级**条目——GitHub Spec Kit（`Assess`）、OpenSpec（`Assess`）、Superpowers（`Assess`）。SDD 作为"技术"没有升级，作为"工具"被逐个评估。

### 9.2 新玩家 OpenSpec：值得单独对标

Thoughtworks Radar 2026-04 `Assess`，理由写得很直白：多数 SDD 框架（含 Spec Kit、Superpowers）**更适合 greenfield**，而 OpenSpec 的 **spec delta** 更适合 brownfield。

它的结构（`docs/concepts.md`）：

```text
openspec/
├── specs/<domain>/spec.md      # 当前系统如何工作 —— 事实源
└── changes/<change>/           # 一次变更 = 一个文件夹，独立、可并行、可归档
    ├── proposal.md             # 为什么 / 范围 / 方法
    ├── design.md               # 技术方案与架构决策
    ├── tasks.md                # 实现清单（带勾选框）
    ├── specs/<domain>/spec.md  # **delta**：只写"变什么"
    └── .openspec.yaml          # 元数据：schema / skip_specs / retire_capabilities / 自定义 x-*
```

**delta 语法**（这是它真正的发明，直接可借）：

| 段 | 含义 | 归档时 |
| --- | --- | --- |
| `## ADDED Requirements` | 新行为 | 追加进主 spec |
| `## MODIFIED Requirements` | 变更的行为 | 替换原 requirement |
| `## REMOVED Requirements` | 废弃的行为 | 从主 spec 删除；声明 `retire_capabilities: true` 时删掉最后一条即退役整个能力 |
| `## Purpose` | 新能力的用途 | 用于播种新建 spec 的 Purpose |

需求格式：`### Requirement:` + RFC 2119 的 SHALL/MUST/SHOULD；`#### Scenario:` + GIVEN/WHEN/THEN。

四条设计哲学（原文）：**fluid not rigid**（无阶段门，按需创建工件）/ **iterative not waterfall** / **easy not complex**（秒级初始化）/ **brownfield-first**（delta 优先，不是描述新系统）。

还有一条概念值得抄：**schema 依赖是"使能"不是"门"**——`proposal → {specs, design} → tasks`，可以跳过 design，可以并行；自定义 schema 用 `openspec schema init/fork`。

### 9.3 2026 年真正的战场：不是 spec，是上下文工程

Radar Vol 34 的相关条目连起来看，信号很清楚：

| 条目 | 环 | 要点 |
| --- | --- | --- |
| Context engineering | **Adopt** | 已经是默认实践 |
| Agent Skills | **Trial** | 开放标准，按描述按需加载，缓解上下文耗尽与指令膨胀 |
| **Agent instruction bloat** | **Caution** | `AGENTS.md` / `CLAUDE.md` 越长越互相冲突；模型对中段内容注意力更弱；AI 生成的 `AGENTS.md` 往往不如手写（引 arXiv 2601.20404）；建议渐进披露 |
| Progressive context disclosure | Trial | 只呈现当前任务需要的指令 |
| MCP by default | Caution | 很多场景用本地 CLI/脚本更划算 |

Spec Kit 团队的实测解法也印证了这一点：把可复用指导抽成 **skills**、让 agent 指令保持精简、把重复上下文搬进 `.github/prompts/speckit.<command>.prompt.md` 让提示更短更稳定；代价侧他们自认还有"多余的防御性检查"和"过长的 markdown 输出增加认知负担"，需要靠改模板/限制生成文件数来压。

**对本套件的直接含义**：叶合同自述约 10 KB、真实项目可达 35 KB，且每次 resume 都要重读——正好落在 instruction bloat 的射程内。§5.2 的"部分成立"应当升级为**高优先级**。

### 9.4 spec-kit 的平台化清单（可逐项对标）

| spec-kit 机制 | 作用 | 本套件对应 |
| --- | --- | --- |
| Integration | 接入/切换不同编码 agent | 多宿主 bootstrap prompt（`portable/prompts/*`）≈ 同构 |
| **Extension** | 加命令、质量门、完整流程（可装/可停/可卸） | **无** |
| **Preset** | 覆盖模板/命令/术语，可多层按 priority 叠加 | **无**（宿主差异硬编码在 prompt 里） |
| Workflow + overlay + step | 把 prompt/命令/门/脚本编排成流程，且可不 fork 地改 | 部分（§12 启动清单是散文，不是可执行流程） |
| **Bundle** | 面向角色/团队的打包 | **无** |
| **Catalog**（含私有、认证、air-gapped） | 发现与分发，带策略 | **无** |
| **Artifact inventory** | 回答"这条命令/模板由哪一层供给、谁赢、谁被遮蔽" | `docs/MIRROR-TOPOLOGY.md` 只描述**构建期**，缺**运行时**视角 |

---

### 9.5 中文圈其实早就出圈了（与"国内外隔阂"的直觉相反）

一个必须纠正的前提：**SDD 在中文社区不是空白，而是已经在 2026 年上半年被"常识化"了。** 按社区舆情盘点的时间线：

| 时间 | 事件 |
| --- | --- |
| 2025-10 | 掘金《让 AI 编程 100% 可控》——早期布道文，OpenSpec 还是小圈子工具 |
| 2025-12 | CSDN《OpenSpec 详解》，11,292 次阅读、37 收藏——概念体系开始被系统梳理 |
| 2026-02-12 | 掘金《AI 编程三剑客：Spec-Kit、OpenSpec、Superpowers 深度对比与实战指南》，36,005 次阅读、216 赞、41 评论 |
| 2026-03-11 | 掘金《OpenSpec 完整使用流程笔记（SDD）》，39,830 次阅读 |
| 2026-03-23 | 掘金《SDD 实践：OpenSpec + Superpowers 整合创建自定义工作流》 |
| 2026-03-24 | 得物技术团队《Claude Code + OpenSpec 正在加速 AICoding 落地》——进入企业技术团队视角 |
| 2026-04~05 | 企业实战密集：OPENSPEC 企业级 API 开发（电商平台重构）、基于 Trae-CN 的 Java 工作流、Claude + DeepSeek + OpenSpec 自动生成 |
| 2026-10 | CSDN/掘金被收录的 OpenSpec 教程 30+ 篇；GitHub 一周净增 1,538 星（约日均 220） |

内容形态也走完了三代：**概念科普期**（是什么/为什么）→ **工具组合期**（双引擎/三剑客/整合，Claude Code + OpenSpec、OpenSpec + Superpowers、OpenSpec + CodeGraph）→ **工程落地期**（实战、案例、企业级）。

OpenSpec 之所以在中文圈跑得最快，是因为它本身就是**胶水层**设计：在 AI 助手里以斜杠命令存在，与模型解耦。`supported-tools.md` 给出的适配矩阵——Claude Code 用 `.claude/commands/opsx/<id>.md`、Cursor 用 `/opsx-<id>`、Codex 走 skills-only 路径用 `$openspec-<skill>`、Amazon Q 用 `@opsx-<id>`——使"OpenSpec + 任意国产模型 + 任意 IDE"的组合教学成立。

**因此结论要改写**：不是"国内外隔阂让你没听说"，而是——**英文圈在讨论方法论（martinfowler / Thoughtworks Radar），中文圈在讨论工具组合（OpenSpec + Claude Code / Trae / DeepSeek）**。同一个词，两个市场的重心不同。你恰好是从方法论这一侧独立走到同一个位置的。

---

## 10. 能吸收什么（按吸收成本分三档）

### 10.1 立刻可吸收（不动授权模型，只加字段与路由）

1. **`TRIVIAL` fast lane**——借 spec-kit 的"独立入口"与 OpenSpec 的 fluid。做法：Change Triage 加第五问"是否单文件、无新能力、无外部效果"，命中则记 `IN_CONTRACT` + 一条证据，跳过复用门与章程重写；**但叶合同三个必填项必须保留**（结果句、允许路径、一条验证）。这是把 §5.1 补上，同时不破坏 WIP=1。
2. **验收条目稳定编号 `AC-1…`**——学 OpenSpec 的 `Requirement / Scenario` 与 Kiro 的 requirement→task 回指。规则与 `RDY`/`RVB` 同规：只增不改、退役保留号。现在叶内验收条目只能靠文字描述，跨叶无法引用。
3. **增量合同（delta contract）**——叶合同的修订不重写全文，用 `## ADDED / MODIFIED / REMOVED` 三段记录，关闭时合并进归档版。直接借 OpenSpec 的 delta 语法，挂到 Change Triage 的 route 字段上。这同时缓解 §5.2 的 review 负担：reviewer 只看增量。
4. **一叶一分支**（学 spec-kit）——`:297` 要求隔离，但没规定"一叶一分支"，可定为默认。
5. **Invariant 违例扫描进 `:412` 启动清单**——一行"本叶是否触碰任一 Invariant？否 / 是 + 引用"。这是 spec-kit constitution 检查点的最小可用形态。
6. **需求强度词（RFC 2119）**——叶合同 Positive/Negative behavior 用 MUST / SHOULD 区分硬性与期望，减少"验收条件全靠形容词"。

### 10.2 中期（需 B 类合同 + 契约版本迁移）

7. **三层分层**：core（状态机/门/授权，任何 preset 不可覆盖）+ preset（模板/术语/宿主差异）+ project-local override。本套件现在是"单一套件 + 字节镜像"，宿主差异靠 bootstrap prompt 硬编码。
8. **Extension 机制**：把 Review A/B、复用发现门、证据收据做成可开关扩展；核心只留最小 SDD。这是 §5.1 与 §5.2 的**结构性**解法，比加 fast lane 更彻底——但代价是引入版本兼容矩阵，需要独立叶。
9. **运行时 artifact inventory**：`charter artifact` 能回答"这个命令/模板由哪一层供给、谁赢、谁被遮蔽"。`MIRROR-TOPOLOGY` 是构建期视角，缺运行时视角。

### 10.3 明确不吸收（且要写清理由）

- **spec-as-source**：Tessl 自己都转走了，且会直通 MDD 老坑（§3.1、§5.5）。
- **Catalog 式无审查安装**：spec-kit 自己写明 *Catalog listings are not audits or endorsements*，`preset update` 更是"无预检、无版本比较、无回滚、无恢复事务"，失败后旧 preset 已被删除。本套件"发现 ≠ 安装 ≠ 执行"（`:208`、`portable/prompts/*-bootstrap.md:29`）必须原样保留——这是资产，不是负担。
- **完全 fluid 的流水线**：OpenSpec 的 fluid 是有代价的——它会削弱 `WIP = 1` 与授权边界。本套件只借它的 delta 语法，不借它的"无阶段门"。

---

## 11. 定位重估（2026-10）

一句话：**SDD 在 2026 年已经从"方法论"退化成"工具品类"，真正的公共战场是上下文工程 + 验证。**

本套件的稀缺性不在 spec。到 2026-10，下列四件事仍**没有任何一款 SDD 工具建模**：

1. 授权（谁允许做、允许到什么程度、批准不隐含下一步）；
2. 证据（收据、`MISSING/UNVERIFIED/FALLBACK` 记账、`BLOCKED_TOOLING`）；
3. 关闭条件（`PASS_CLOSED` 需要验收 + Review + 集成前验证 + 集成 + 集成后验证全有证据）；
4. 多宿主可移植（同一套字节同时供 Codex / Claude / DeepSeek）。

因此对外表述建议从「spec-driven 的一个变体」改为 **「agentic engineering 的治理层（governance layer）」**——spec 只是它的输入格式之一，而不是它的定义。

---

## 12. 事实来源（2026-10 增补）

- `github/spec-kit` README（main）：三个独立入口、Capabilities 表、catalog 免责声明 — <https://github.com/github/spec-kit>
- `github/spec-kit` `docs/reference/overview.md`：Integration / Extension / Preset / Workflow / Bundle / Catalog / Artifact 的定义 — <https://github.com/github/spec-kit/blob/main/docs/reference/overview.md>
- `github/spec-kit` CHANGELOG：v1.2.1（2026-10-16）、v1.2.0（2026-10-13） — <https://github.com/github/spec-kit/blob/main/CHANGELOG.md>
- `Fission-AI/OpenSpec` `docs/concepts.md`：Philosophy / Changes / Delta Specs / Schemas — <https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md>
- Thoughtworks Technology Radar Vol 34（2026-04）：GitHub Spec Kit、OpenSpec、Superpowers（均 `Assess`）；Agent Skills（`Trial`）；Agent instruction bloat（`Caution`）；Progressive context disclosure（`Trial`）；Context engineering（`Adopt`）；MCP by default（`Caution`） — <https://www.thoughtworks.com/radar>
- Thoughtworks Technology Radar：Spec-driven development（2025-11，`Assess`，已不在当期） — <https://www.thoughtworks.com/cn/radar/techniques/spec-driven-development>
- `tessl.io` 首页与博客（2026-09/10）：software factory / skills / verifiers / Tessl Code Review — <https://tessl.io/>
- Kiro 状态：官方站点被 cookie 墙拦截，未取得一手公告；中文二手源称已 GA，本文按**未核实**处理。
- 中文圈舆情盘点（§9.5 时间线来源）：《一周 +1538 星背后：中文社区 OpenSpec 教程三个月刷出 30+ 篇，SDD 概念彻底出圈》，CSDN，2026-10-16 — <https://blog.csdn.net/gitblog_00020/article/details/168119225>
- 中文侧 SDD 词条与教程样本（§9.5 佐证）：百度百科「规范驱动开发」、百度百科「SDD实战：规范驱动开发之道」、CSDN《规范驱动开发（Spec-Driven Development）：一个批判性审视》、uml.org.cn《Spec-Driven Development 完整指南：6 要素 + 3 模式 + 多智能体》。
