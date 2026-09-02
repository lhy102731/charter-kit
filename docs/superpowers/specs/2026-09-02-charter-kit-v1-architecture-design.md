# Charter Kit v1 轻量可移植架构

状态：已批准的设计基线；v1 候选已完成最终验证（Codex 已验证，其他 Harness 按实验性处理）
日期：2026-09-02  
范围：项目本地开发工作流、变化处理、轻量复用检查和 Harness 薄适配层

## 1. 定位

Charter Kit 是一个基于项目文件的开发工作流。它用 Charter 约束方向，用 Roadmap 和 Leaf 组织交付，用 Change Triage 控制范围和事实变化，用 Reuse Assessment / Reuse Check 减少不必要的重复建设，再用 Review、Verification 和 Git 证据关闭一个受授权的叶任务。

“可在任意 Harness 使用”表示 Codex、Claude、Gemini 或其他 Harness 可以独立读取并执行同一套 Portable Core。它不表示 Agent 之间有通信、Harness 之间有实时同步，也不要求中央调度服务或共享运行时。

项目领域、产品目标和专业数据由项目自己的 .charter/project.md 定义。通用核心不包含 KBase、AG2、回测、模型供应商或个人研究闭环。

## 2. 设计目标

必须实现：

1. 首次启动和继续执行最终进入同一条叶任务闭环。
2. 用户新需求、实现中新事实、Review 问题和 Verification 问题都进入同一个 Change Triage。
3. 新需求不能静默扩大当前 Leaf。
4. 每个 Leaf 在 READY 前至少经过一次轻量 Reuse Assessment 和本地 sanity check。
5. 只有必要时才升级到生态或外部搜索。
6. 复用发现、采用、安装、复制和执行彼此分离。
7. Review、Verification 和 Git 集成都留下可重查证据。
8. 缺失的可选能力使用明确 fallback，不得假装已经调用。
9. Portable Core 只维护一份，Harness 只提供薄适配层。
10. 默认保持 WIP = 1。

明确不做：

- Agent 间通信或任务调度；
- Harness 间实时同步或并发协调；
- 中央 Dispatcher、Recovery Service 或云端状态服务；
- Capability Registry、Candidate Board、数字评分系统或 Asset Memory 数据库；
- 强制每个 Leaf 做深度外部搜索；
- 自动安装第三方 Skill、插件、包、服务或 Harness；
- 自动把任意仓库转换为 Skill；
- 将个人领域研究流程写入通用核心。

## 3. 总体分层

~~~text
Charter Kit
├── Portable Core
│   ├── Charter / Roadmap / Leaf Contract
│   ├── Change Triage
│   ├── Reuse Assessment / Reuse Check
│   ├── Authorization
│   ├── Review / Verification
│   └── Evidence / Closure
├── Optional Providers
│   ├── grill-me / grilling
│   ├── j-space
│   ├── Superpowers
│   ├── reuse-first
│   ├── framework-first-coding
│   ├── reduce-reinvention
│   ├── find-skills
│   └── repo-to-skill
└── Thin Harness Adapters
    ├── entrypoint
    ├── plugin / skill mapping
    ├── capability detection
    ├── fallback mapping
    └── install and usage instructions
~~~

Portable Core 使用普通 Markdown、模板和可选的本地脚本表达规则。它定义流程、状态、门禁、证据格式和 fallback，不依赖某个 Harness API。

Harness Adapter 只负责启动入口、资源映射、能力检测、宿主特有 fallback 以及安装说明，不重新定义 Charter、Leaf、Reuse、授权或完成语义。

项目工作区是持久记录。它可以被用户在另一个 Harness 中再次读取，但不提供通信、锁、实时同步或并发协调。handoff.md 是恢复快照；j-space 是当前运行中的临时 ledger，重要事实必须落回项目文件。

## 4. 唯一主控制流

~~~mermaid
flowchart TD
    U([用户输入 / 继续执行]) --> R{Context Router}

    R -->|新项目| I["首启：补齐缺失的 .charter 文件"]
    R -->|已有项目| S["Resume：读取并校验工作集"]
    R -->|新需求 / 新事实 / 风险| READ["先读取当前项目状态"]

    I --> D["依赖与能力诊断"]
    D --> Q["目标访谈：grill-me 或 bundled fallback"]
    Q --> C["起草 Charter、Roadmap、首个 Leaf"]
    C --> CR["自审；高风险时做独立审阅"]
    CR --> CA{项目方向已批准？}
    CA -- 否 --> STOP["记录 decision，修改或暂停"]
    CA -- 是 --> L["Leaf Contract"]

    S --> SC["恢复 Goal、当前 Leaf、授权和唯一 Next"]
    SC --> L

    READ --> T["Change Triage"]
    T --> TR{最高影响层级}
    TR -->|CHARTER_CHANGE| C
    TR -->|ROADMAP_CHANGE| RM["更新 Roadmap，新增或拆分 Leaf"]
    RM --> L
    TR -->|LEAF_CHANGE| L
    TR -->|IN_CONTRACT| NEXT["回到当前 Leaf 的 Next"]
    TR -->|OUT_OF_SCOPE| STOP

    L --> RA["Reuse Assessment"]
    RA --> RC["Reuse Check"]
    RC --> READYQ{授权、依赖、证据和前置条件满足？}
    READYQ -- 否 --> STOP
    READYQ -- 是 --> READY["READY：WIP = 1"]

    READY --> LOOP["Design → Implement → Review → Verify"]
    LOOP --> INT["Git 集成与合并后验证"]
    INT --> CLOSE["更新 evidence、roadmap、handoff"]
    CLOSE --> DONE([PASS_CLOSED])

    LOOP -.发现新需求或新事实.-> T
    INT -.验证发现变化.-> T
~~~

主流程只有一条。首启和 Resume 在 Leaf Contract 处汇合，Reuse Check 是 READY 前的一道门，Change Triage 是所有变化的横向回入口。

Context Router 是工作流中的一个判断步骤，不是中央服务、Router Agent 或独立运行时。

## 5. 入口模式

### 5.1 首次启动

1. 检查 .charter/project.md 是否存在且可读。
2. 不完整时只补缺失文件，不覆盖已有内容。
3. 运行依赖和能力诊断，输出 AVAILABLE、MISSING、UNVERIFIED、FALLBACK。
4. 优先使用 grill-me；不可用时使用内置设计访谈。
5. 起草 Goal、Non-goals、Invariants、成功标准、效果边界、Roadmap 和首个 Leaf。
6. 完成自审；初始项目或高风险项目按需要进行独立审阅。
7. 等待项目方向批准。
8. 对首叶执行 Reuse Assessment / Reuse Check。
9. 获得首叶批准或匹配的 AUTO_DEV 预授权。
10. 将首叶推进到 READY，进入标准执行闭环。

### 5.2 继续执行

固定读取顺序：

~~~text
.charter/project.md
→ .charter/roadmap.md
→ .charter/reuse-discovery.md
→ .charter/current-task.md
→ .charter/handoff.md（如存在）
~~~

Resume 必须恢复 Goal、活动 Leaf 和状态、前置任务、Reuse Gate、授权范围、已验证事实、未解决事项和唯一下一步。

文件缺失、状态冲突、授权过期或证据不足时，只修复工作集并停止。

### 5.3 变化入口

用户新需求、实现中发现的新事实、Review 发现的问题、Verification 发现的问题、依赖或安全边界变化，统一进入 Change Triage。

## 6. Change Triage 协议

事件类型：

~~~text
NEW_REQUIREMENT
CLARIFICATION
DEFECT
DISCOVERED_CONSTRAINT
RISK
~~~

固定四问：

1. 它是否属于当前 Goal？
2. 它影响 Charter、Roadmap 还是当前 Leaf？
3. 它是否引入新的能力、依赖、版本、技术栈、风险或外部边界？
4. 当前授权是否覆盖？

路由优先级：

~~~text
CHARTER > ROADMAP > LEAF > IN_CONTRACT
~~~

| 路由 | 含义 | 动作 |
|---|---|---|
| IN_CONTRACT | 不改变合同语义的澄清、实现细节或合同内缺陷 | 记录后继续 |
| LEAF_CHANGE | 改变当前 Leaf 的结果、接口、验收或边界 | 暂停，修改并重新授权 |
| ROADMAP_CHANGE | 新增能力、Slice 或交付顺序 | 更新 Roadmap，创建或拆分 Leaf |
| CHARTER_CHANGE | 改变 Goal、Non-goals、Invariants、成功标准、公共语义或效果边界 | 修改 Charter，重新审阅和批准 |
| OUT_OF_SCOPE | 当前 Charter 不覆盖 | 拒绝、Backlog、新项目或请求决定 |

处置动作可以是 CONTINUE、REVISE_LEAF、CREATE_LEAF、REAPPROVE、BACKLOG、NEW_PROJECT、REJECT 或 NEEDS_DECISION。这些是动作结果，不是第二套状态机。

无法证明变化已经在当前合同内时，不得自行标记 IN_CONTRACT。

只有变化影响能力、依赖、版本、技术栈、安全、许可证、隐私或外部效果时，才重新触发 targeted Reuse Check。合同内的普通澄清和缺陷修复不必重复外部搜索。

## 7. Reuse Assessment / Reuse Check

### 7.1 Assessment

每个 Leaf 都执行一个轻量判断：

> 不进行复用检查，是否可能导致明显的重复建设、兼容性问题、安全问题、维护负担或未来重复劳动？

通常不构成 Material Target 的是局部几行字符串处理、一次性转换和明显项目专属的小逻辑。HTTP、认证、数据库、序列化、缓存、公共错误模型、核心算法、框架、SDK、依赖、Agent Skill、插件以及可能被多处复用的组件通常属于 Material Target。

没有 Material Target 时，仍做一次本地 sanity check，并记录 NO_MATERIAL_TARGET。

### 7.2 渐进式搜索

~~~mermaid
flowchart TD
    L["Leaf Contract + 所需能力"] --> M{Material Target？}
    M -- 否 --> N["本地 sanity check：NO_MATERIAL_TARGET"]
    M -- 是 --> D["选择 FAST / STANDARD / DEEP"]
    D --> L0["LOCAL：项目、历史、文档、测试、脚本"]
    L0 --> Q0{证据足够？}
    Q0 -- 是 --> O["形成决定"]
    Q0 -- 否 --> L1["ECOSYSTEM：manifest、framework、SDK、dependencies、已安装能力、获准内部资源"]
    L1 --> Q1{证据足够？}
    Q1 -- 是 --> O
    Q1 -- 否 --> X{允许外部只读搜索？}
    X -- 否 --> U["UNKNOWN / NOT_AUTHORIZED：决定或 REUSE_SPIKE"]
    X -- 是 --> L2["EXTERNAL：官方、上游、注册表、获准公开资料"]
    L2 --> O
    N --> O
~~~

搜索到足够证据就停止，不要求每个 Leaf 都进入 DEEP。

| 深度 | 范围 | 适用情况 |
|---|---|---|
| FAST | 项目和历史 | 小型、低风险、明显局部任务 |
| STANDARD | 项目和生态能力 | 新依赖、框架、SDK 或中等复用价值 |
| DEEP | 前两层和获准外部资料 | 安全、认证、数据库、公共 API 或高维护成本能力 |

复用记录保存在唯一事实源 .charter/reuse-discovery.md。不建立 Registry、Candidate Board 或数字评分系统。

每次记录至少包含 Discovery ID、目标 Leaf、搜索深度和范围、精确查询或路径、覆盖情况、搜索结果、候选来源和固定版本、观察和证据引用、候选处置、最终路线、未搜索或未授权范围、限制、复查触发条件和批准人。

字段语义分开：

~~~text
覆盖情况：SEARCHED / NOT_SEARCHED / NOT_AUTHORIZED / BLOCKED_TOOLING
搜索结果：MATCH / NO_MATCH / UNKNOWN
候选处置：ADOPT / ADAPT / REFERENCE_ONLY / REJECT / DEFER
最终路线：ADOPT / ADAPT / REFERENCE_ONLY / BUILD_NEW / REUSE_SPIKE / NEEDS_DECISION
~~~

规则：

- NO_MATCH 只能在声明范围内实际搜索后记录；
- NOT_SEARCHED、NOT_AUTHORIZED、BLOCKED_TOOLING 不能伪装成 NO_MATCH；
- UNKNOWN 不能自动变成 BUILD_NEW；
- BUILD_NEW 必须写简短理由；
- WAIVED 必须由用户或负责人批准；
- 复用记录因能力、版本、技术栈或边界变化失效时，门状态重新进入 PENDING；
- 发现候选不等于采用，采用候选不等于安装、复制或执行。

外部 Discovery 默认只读，不得上传私有代码、凭据、秘密或真实敏感数据。版本使用 Git commit/tag 或 package version，不使用内容 hash、digest 或 fingerprint。

Reuse Gate 只保留 PENDING、COMPLETE 和 BLOCKED 三种状态。叶任务只有在 Gate 为 COMPLETE，或该叶有明确、单独批准且记录完整的有界 waiver 时，才能进入 READY。waiver 必须写明叶 ID、批准/遗漏范围、限制、批准人和过期/复查条件；它不是第四种状态、不会改变项目级投影，也不授权其他叶。LIMITED 或 WAIVED 只是决定记录中的这些字段；没有当前叶 waiver 时，PENDING、BLOCKED 和 BLOCKED_TOOLING 仍阻塞 READY。waiver 必须显式处置相关高价值 UNKNOWN/DEFER，不能静默转成 BUILD_NEW。

### 7.3 五个 Reuse Skill

| Skill | 负责的问题 | 使用边界 |
|---|---|---|
| reuse-first | 项目内部是否已有 helper、utility、mapper 或模块 | 仅项目内复用 |
| framework-first-coding | 是否已有框架、SDK、依赖或共享组件 | 先查现有技术栈 |
| reduce-reinvention | 复用和自建的成本、风险和维护权衡 | 形成 Build vs Reuse 判断 |
| find-skills | 是否已有可用 Agent Skill | 只发现 Skill，不自动安装 |
| repo-to-skill | 已选定仓库是否值得转换为 Skill | 单独授权后的后续动作 |

这些 Skill 是按需插槽，不是固定串行流程，也不是核心硬依赖。

## 8. 叶任务执行闭环

~~~mermaid
flowchart TD
    R["READY"] --> J["J-space ledger：Goal / Core / Verified / Open / Next"]
    J --> G["设计拷问：grill-me 或 bundled checklist"]
    G --> P["Superpowers：规划、TDD、调试"]
    P --> I["按 Leaf Contract 实现"]
    I --> F{失败？}
    F -- 是 --> D["系统化调试，记录根因和实验"]
    D --> I
    F -- 否 --> A["Review A"]
    A --> B{高风险或需要独立审阅？}
    B -- 是 --> RB["Review B：不同上下文或审阅者"]
    B -- 否 --> V["Verification"]
    RB --> V
    V --> C{验收通过？}
    C -- 否 --> D
    C -- 是 --> GIT["提交、合并目标分支"]
    GIT --> PV["合并后重新验证"]
    PV --> PC["PASS_CLOSED"]
    I -.范围变化.-> T["Change Triage"]
    A -.合同外问题.-> T
    V -.新事实或风险.-> T
~~~

Leaf Contract 至少包含 Leaf ID、父级、唯一结果句、输入输出、前置任务、允许修改路径、允许效果、禁止副作用、正向和负向验收、停止条件、修复预算、授权引用、Reuse Discovery 引用、证据位置和集成策略。

正常状态：

~~~text
DRAFT → APPROVED → READY → IN_PROGRESS → REVIEW → VERIFIED → PASS_CLOSED
~~~

异常状态：

~~~text
BLOCKED
NEEDS_DECISION
SUPERSEDED
~~~

Review A 对每个 Leaf 必需。Review B 对安全、认证、外部依赖、公共 API、高风险或用户明确要求的任务必需；低风险任务可以记录有边界的省略理由。集成和合并后验证属于关闭证据，不必再增加独立状态。

AUTO_DEV 只覆盖预先列明的 Leaf、路径、效果、依赖、修复预算和停止条件，不能覆盖新需求或未列明的外部动作。

## 9. 文件事实源

~~~text
项目根目录/
├── AGENTS.md / CLAUDE.md / GEMINI.md
└── .charter/
    ├── project.md
    ├── roadmap.md
    ├── current-task.md
    ├── reuse-discovery.md
    ├── decision.md
    ├── handoff.md
    ├── review.md
    ├── evidence-receipt.md
    └── evidence/
~~~

四个 core Resume files 是 `project.md`、`roadmap.md`、`reuse-discovery.md` 和 `current-task.md`。`handoff.md` 是可选恢复快照；`decision.md`、`review.md`、`evidence-receipt.md` 与 `evidence/` 是按引用读取的 auxiliary receipts / evidence，不是每次 Resume 都要加载的第二状态层。

| 文件 | 唯一职责 |
|---|---|
| project.md | Goal、Non-goals、Invariants、成功标准和项目批准 |
| roadmap.md | 交付顺序、Leaf 索引和状态投影 |
| current-task.md | 当前 Leaf 合同、授权、状态和变化事件 |
| reuse-discovery.md | 复用搜索、候选、版本和决定 |
| decision.md | 需要人工决定的事项、waiver 和限制 |
| handoff.md | 恢复快照，不覆盖权威状态 |
| review.md | Review 收据和发现；不产生新的 Leaf 状态 |
| evidence-receipt.md | 单次验证、搜索或集成操作的收据模板 |
| evidence/ | 测试、Review、Verification、搜索和集成收据 |

current-task.md 是活动 Leaf 状态的权威来源，roadmap.md 是高层投影。如果两者冲突，Resume 必须停止并修复。

AGENTS.md、CLAUDE.md 和 GEMINI.md 只放静态项目或宿主规则，不复制动态状态。

## 10. Harness 发行结构

~~~text
charter-kit/
├── portable/
│   ├── rules/
│   ├── commands/
│   ├── prompts/
│   ├── templates/
│   └── references/
├── targets/
│   ├── codex/
│   ├── claude/
│   ├── gemini/
│   └── ...
└── plugins/              # 需要时的发行产物
~~~

portable/ 是唯一核心来源。目标包可以在构建时复制或装配核心，但不应手工维护多份不同语义。

某个 Harness 只有在真实安装和启动 smoke test 通过后才能标记为 supported；否则标记为 experimental。

## 11. 能力缺失和安全边界

启动或切换阶段报告 AVAILABLE、MISSING、UNVERIFIED、FALLBACK。

- 没有 grill-me：使用 bundled design interview；
- 没有 j-space：使用 handoff.md 和任务记录中的 ledger；
- 没有 Superpowers：执行同等的计划、RED/GREEN、调试、Review 和 Verification 清单；
- 没有外部搜索工具：不能写成 NO_MATCH，只能记录 NOT_SEARCHED、UNKNOWN 或请求决定。

项目批准、Leaf 批准、采用批准、安装批准、执行批准和发布批准彼此分离。默认只允许读项目文件、受控样例和明确批准的代码写入；外部服务、敏感数据、发布和不可逆动作需要单独批准。

用户明确批准优先于项目规则；项目 Charter 和 Leaf Contract 约束实现范围；Harness 默认行为和 Provider 建议不能悄悄提高权限。用户已有修改必须保留，失败和负面结果必须记录，Agent 自报不能替代独立证据。

## 12. 最小验证集合

实现后至少验证：

1. 空目录首启；
2. 部分 .charter 工作集补齐；
3. 已有项目 Resume；
4. 当前 Leaf 中出现新需求；
5. 合同内缺陷和合同外变化；
6. Reuse 的 NO_MATCH、UNKNOWN 和 BUILD_NEW；
7. 外部搜索未授权或工具缺失；
8. TDD 失败、系统化调试和 Review 回路；
9. 合并后 Verification；
10. 至少一个 Harness 的安装和启动 smoke test；
11. 未验证 Harness 不被标记为正式支持；
12. 通用核心不含个人领域内容。

## 13. v1 结束条件

- 规范、模板、Prompt、Skill 和 Adapter 使用同一套术语；
- 首启、Resume 和 Change Triage 能进入同一叶任务闭环；
- Reuse Check 能记录搜索范围、负结果、候选和最终路线；
- UNKNOWN、未授权和工具阻塞不会被误写成 NO_MATCH；
- 新需求不会静默扩大当前 Leaf；
- Review、Verification、Git 集成和合并后检查都有证据；
- 至少一个 Harness 有真实 smoke test；
- 没有新增中央服务、第二状态机或第二事实源。

## 14. 最终定义

> Charter Kit 是一个轻量、项目本地、可在任意 Harness 中独立执行的开发工作流：它用 Charter 约束目标，用 Roadmap 和 Leaf 组织交付，用 Change Triage 控制所有范围和事实变化，用 Reuse Assessment / Reuse Check 减少无谓重复建设，再通过设计、实现、Review、Verification 和 Git 证据关闭每一个受授权的 Leaf。
