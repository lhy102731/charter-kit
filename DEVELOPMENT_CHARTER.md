# AI 项目开发章程（通用版）

这是一份项目本地的开发治理协议。它把“要改变什么”“当前允许做什么”“什么证据才算完成”写进项目文件，而不是依赖某个运行会话的隐藏记忆。任何能够读写项目文件的 Harness 都可以独立遵循同一份协议；协议不提供 Agent 间通信、Harness 间同步或中央服务。具体领域、产品闭环、技术栈和工具由项目自己的 `.charter/project.md` 定义；本章程只规定方法和边界。

## 0. 使用边界

本章程适用于个人、团队、开源仓库、企业项目、研究项目和自动化流水线。它不是中央调度服务，也不要求所有 Harness 安装相同的 Agent、模型或插件。核心文件使用普通 Markdown 和可选的 JSON；不同 Harness 只需独立读取项目工作集即可遵循它。

规则优先级如下：

1. 用户或负责人的明确指令和批准；
2. 当前项目章程；
3. 当前叶任务合同；
4. 宿主默认行为、工具建议和 Agent 的个人判断。

低层规则不能悄悄推翻高层目标。工具能力不足时要报告限制，不把无法完成的动作写成完成。加载本包不会自动安装插件、Skill、包、模型、服务或全局配置；依赖检查只读并把缺失项写成可审计日志。

## 1. 总体模型：一个主控制流

Charter Kit 只有一条主控制流：`Charter → Roadmap → Leaf → Reuse Check → Design → Implement → Review → Verify → Integrate → Close`。下面的两个循环是便于阅读的阶段分组，不是互相独立的状态机，也不要求跨 Agent 或跨 Harness 协调。

### 循环 A：章程工程

```text
需求考古
→ 目标纠偏
→ 现状与资产审计
→ 复用发现计划
→ 成功等级与效果边界
→ 能力地图与任务树
→ 章程草案
→ 设计访谈（grill-me 优先）
→ 自审
→ 独立审阅
→ 人工批准方向
→ 复用发现门
→ 路线与任务树校准
→ 首叶授权
```

### 循环 B：章程驱动开发

```text
叶任务合同
→ 启动门禁与依赖检查
→ 设计拷问与最小计划
→ 隔离实现
→ 测试与根因调试
→ Review A / Review B
→ 新鲜验证
→ 合并目标分支
→ 合并后验证
→ 关闭任务
→ 产生下一候选
```

首启和 Resume 在 Leaf Contract 处汇合；实现、Review 或 Verification 中出现的新需求、新事实、缺陷或风险，都回到同一个 Change Triage 入口。循环 A 决定方向，循环 B 交付一个可观察结果。不能用循环 B 的局部绿灯替代方向批准，也不能让流程维护取代真实产品工作。

## 2. 章程工程：从需求到可执行方向

### 2.1 需求考古

先收集原始需求、痛点、用户访谈、历史反馈、现有计划、失败记录和真正想改变的结果。把事实、推测、偏好和待验证假设分开写。

至少回答：

- 谁会使用结果，在哪个场景使用？
- 当前最痛的可观察问题是什么？
- 结果必须改变什么行为、决策或体验？
- 哪些内容只是实现手段，而不是产品目标？
- 已经有哪些代码、数据、文档、流程、Skill 或服务可以复用？
- 哪些信息不能进入外部查询或日志？

不要在这一步急着决定目录、框架、模型或插件。先确认要改变的世界。

### 2.2 目标纠偏

把目标写成结果句，而不是工程动作。例如：

```text
结果目标：给定一份有效输入，用户能得到可验证、可追溯的结果并知道下一步。
不是目标：增加更多 Gate、日志、状态字段或 Agent 数量。
```

明确三类内容：

- `Goal`：完成后用户能观察到的结果；
- `Non-goals`：本章程版本明确不做的事；
- `Invariants`：无论路线如何调整都不能破坏的约束。

通用不变量示例是：用户已有改动不被覆盖；失败和负面结果保留；未经授权不触碰敏感数据、发布系统或不可逆外部效果；执行者的自报不能替代独立证据；项目领域的关键事实必须能追溯到来源。项目应在自己的章程中删改示例并写出真正适用的版本。

### 2.3 现状与资产审计

对已有能力逐项分类：

| 分类 | 判断 | 处理 |
|---|---|---|
| `KEEP` | 已满足目标且证据足够 | 原样复用并记录边界 |
| `ADAPT` | 方向正确但接口或边界不合适 | 最小改造 |
| `REPLACE` | 阻塞目标或无法验证 | 设计替代并说明原因 |
| `ARCHIVE` | 与当前目标无关但有历史价值 | 保留引用，不进入主线 |
| `UNKNOWN` | 没有足够证据判断 | 小型审计或 Spike |

资产存在不等于能力完成。要区分“文件在”“局部检查通过”“离线闭环通过”“用户场景通过”和“已获发布授权”。本地资产审计盘点项目已经拥有的东西；章程批准后的复用/先例发现另按第 2.9 节记录。

### 2.4 成功等级与证明

成功等级是项目可配置的证明阶梯，不是本包固定的产品分类。项目应在 `.charter/project.md` 里声明名称、进入条件和退出证据。若没有更合适的命名，可采用以下中性示例：

1. `COMPONENT`：一个组件能按合同被调用；
2. `SYNTHETIC`：离线或受控样例的端到端路径通过；
3. `INTEGRATED`：真实项目边界内的多个部分协同通过；
4. `USER_VALIDATED`：目标用户在约定场景确认结果有用；
5. `RELEASE_AUTHORIZED`：负责人批准发布，并完成发布后检查。

项目可以重命名、合并或增加等级，但每一级都必须写清输入、证据和未覆盖边界。没有真实数据、外部服务或发布授权时，明确写“未验证”，不能补一段乐观说明。

### 2.5 作用域与副作用

把动作按效果分类，并在章程中明确允许范围。下面是可按项目增删的中性标签：

```text
read_only          只读检查和审计
sample_run         受控样例或离线运行
code_write         修改代码或文档
local_merge        合并到本地目标分支
external_service   调用外部服务或网络
sensitive_data     读取或处理受限数据
release            修改或发布对外/生产系统
irreversible       不可逆的外部动作
```

默认只允许 `read_only`、`sample_run` 和明确批准的 `code_write`。外部服务、敏感数据、发布和不可逆动作需要单独批准；日志不得包含凭据、秘密或不必要的个人信息。

### 2.6 能力地图与依赖状态

能力地图描述“要完成目标必须具备什么”，而不是列出所有想用的工具。对每项记录：

- 输入和输出；
- 上游/下游依赖；
- 所需宿主能力；
- 可观察验收；
- 缺失时的降级等级和停止条件。

启动时运行本包的依赖检查器（若宿主可执行）：

```text
AVAILABLE   能力已检测到
MISSING     能力明确不存在
UNVERIFIED  无法可靠检测
FALLBACK    使用便携替代，并记录限制
```

每一项检查都要输出能力名、原因、影响、fallback 和用户行动建议，并写入 `.charter/evidence/dependency-check.log` 或项目指定日志。必需能力为 `MISSING`/`UNVERIFIED` 时保持 `BLOCKED_TOOLING`；推荐或可选能力缺失时可以继续，但不能声称使用了该能力。独立 Review 需要新的上下文或进程；同一会话自审不能冒充独立 Review B。

### 2.7 任务树与叶任务

按以下层次拆解：

```text
Epic
  └─ Capability
      └─ Vertical Slice
          └─ Leaf Task
```

一个叶任务只交付一个可观察行为。叶任务必须有独立输入、输出、前置依赖、验收和停止线。默认保持 `WIP = 1`：同一父任务同时只有一个活动叶任务。好的叶任务是“输入经过一条可验证路径后产生一个结果”，不是“把所有服务接上”。

### 2.8 章程自审、独立审阅与批准

章程草案完成后逐项检查：

- 有没有把控制面、工具或实现动作写成产品目标？
- Goal、Non-goals、Invariants 是否互相矛盾？
- 成功等级是否与实际证据匹配？
- 资产审计是否说明了复用、改造或替换的理由？
- 任务树是否存在跨越多个行为的“大叶子”？
- 敏感数据、外部网络、发布和不可逆效果是否有明确边界？
- 自动继续的范围、修复次数和停止条件是否清楚？
- 复用发现范围、查询预算、许可证/安全筛选和无结果证据是否明确？

在自审前进行结构化设计访谈：由 `grill-me`（或宿主提供的 `grilling` 能力）逐轮追问目标、用户、接口、负向路径、失败模式和边界；事实由执行者调查，取舍交还用户。没有该 provider 时使用内置 `references/design-interview.md`，并记录 `FALLBACK`/限制。访谈结束后作者完成逐项自审并保留证据；随后由不负责起草的审阅上下文或独立进程，在新鲜上下文中执行 `CHARTER_INDEPENDENT` 审阅。换名字、在同一上下文重读或由作者代写，都不算独立审阅。

所有发现必须解决、降级为有明确限制的开放决定，或在批准记录中说明 waiver；未处置的发现保持项目 `BLOCKED`，不能请求项目批准。人工批准的是目标、非目标、关键不变量、高风险效果、成功等级和审阅限制；实现细节可在合同范围内演化。

### 2.8.1 Change Triage：所有变化的统一入口

用户提出的新需求、需求澄清、实现中发现的事实或约束、缺陷、Review 发现和风险，都先记录为一个 Change Triage 事件。新需求不能静默扩大当前 Leaf（New requirement must not silently expand the current Leaf）。

固定回答四个问题：

1. 它是否属于当前 Goal？
2. 它影响 Charter、Roadmap 还是当前 Leaf？
3. 它是否引入新的能力、依赖、版本、技术栈、风险或外部效果？
4. 当前授权是否覆盖？

事件类型为 `NEW_REQUIREMENT`、`CLARIFICATION`、`DEFECT`、`DISCOVERED_CONSTRAINT` 和 `RISK`；路由优先级为 `CHARTER > ROADMAP > LEAF > IN_CONTRACT`，可用路由是 `IN_CONTRACT`、`LEAF_CHANGE`、`ROADMAP_CHANGE`、`CHARTER_CHANGE` 和 `OUT_OF_SCOPE`。这些是路由和动作，不是第二套状态机。

无法证明变化已经在当前合同内时，不得标记为 `IN_CONTRACT`。改变 Goal、Non-goals、Invariants、公共语义或效果边界的事件回到 Charter 决策；新增能力、依赖、版本、技术栈、安全、许可证、隐私或外部效果的事件，在重新授权前触发 targeted Reuse Check。处置动作可以是 `CONTINUE`、`REVISE_LEAF`、`CREATE_LEAF`、`REAPPROVE`、`BACKLOG`、`NEW_PROJECT`、`REJECT` 或 `NEEDS_DECISION`。

### 2.9 复用发现门（Reuse Discovery Gate）

方向获批后、每个 Leaf 从 `DRAFT` 推进到 `APPROVED`/`READY` 前，必须完成一次轻量 Reuse Assessment / Reuse Check。目标是减少重复造轮子，不让搜索结果替项目决定目标，也不把发现当作安装或执行授权。没有 Material Target 时，做一次本地 sanity check 并记录 `NO_MATERIAL_TARGET`。

复用发现使用已批准的 Goal、Non-goals、Invariants 和能力地图，主动检索：当前工作区/历史 → 已安装 skills/plugins、缓存和 manifest → 获准的内部资源 → 官方文档、上游项目和包注册表 → 获准的公开 Web。所有结果写入唯一事实源 `.charter/reuse-discovery.md`，原始输出放在 `.charter/evidence/`。记录 discovery ID、章程版本、目标能力、负责人、宿主和工具版本、搜索层级、精确查询、时间/查询预算、停止条件、候选路径或 URL、固定版本、许可证/安全/维护/可移植性、集成成本和决定。

候选行决定只能是 `ADOPT`、`ADAPT`、`REFERENCE_ONLY`、`REJECT`、`DEFER` 或 `UNKNOWN`；`BUILD_NEW`、`REUSE_SPIKE` 和 `NEEDS_DECISION` 是完成检查后对能力的最终路线。没有合适候选也是有效结果，但必须保留查询、覆盖范围、时间和 `NO_MATCH` 证据。

范围含义固定：

- `LOCAL_ONLY` = 工作区/历史；
- `LOCAL_ECOSYSTEM` = 工作区/历史 + 已安装/缓存 + 获准内部；
- `FULL_EXTERNAL` = 前述范围 + 官方/上游/注册表 + 获准公开 Web。

非本地层级需要选定 discovery scope 和 `External read authorization`；范围外写 `NOT_SEARCHED` 或 `NOT_AUTHORIZED`，不能写成 `NO_MATCH`。发现阶段只读，禁止 clone、build、run、import、install、copy、加载候选指令、写全局目录或上传私有源代码/秘密/敏感数据。候选版本必须固定为 immutable commit/tag/package version；浮动分支和 `latest` 不算证据。

门状态只保留 `PENDING | COMPLETE | BLOCKED`。记录字段分开：Coverage 为 `SEARCHED | NOT_SEARCHED | NOT_AUTHORIZED | BLOCKED_TOOLING`；Result 为 `MATCH | NO_MATCH | UNKNOWN`；Final route 为 `ADOPT | ADAPT | REFERENCE_ONLY | BUILD_NEW | REUSE_SPIKE | NEEDS_DECISION`。有限搜索或 waiver 写入决定、遗漏范围、限制和复查条件，不扩展门状态。`COMPLETE` 要求每个 Material Target 覆盖获准范围、每个已搜索层有证据、范围外层级有明确状态，并处理高价值 `UNKNOWN`。项目和 roadmap 中的门状态只是记录的投影；三处不一致、工具阻塞或记录过期时保持 `BLOCKED`。

搜索深度按成本和风险选择：`FAST` 只查项目与历史，`STANDARD` 再查已安装能力、manifest、框架和依赖，`DEEP` 才查获准的官方、上游、注册表或公开资料。搜索到足够证据就停止，不要求每个 Leaf 做深度外部搜索。

五个可选 Reuse Provider 按需使用：`reuse-first` 查项目内 helper/utility/module；`framework-first-coding` 查框架、SDK、依赖和共享组件；`reduce-reinvention` 评估 Build vs Reuse；`find-skills` 只发现 Skill，不安装；`repo-to-skill` 只在选定仓库后、得到单独授权时执行。Provider 是插槽而非固定串行流程，缺失时记录 `MISSING`/`FALLBACK` 或 `BLOCKED_TOOLING`。

### 2.10 首次启动访谈

当没有 `.charter/project.md` 时，不能把“缺少工作集”当成开发阻塞。先创建工作集和空的 evidence 目录，运行依赖检查，再用 `grill-me` 优先进行多轮意图访谈；若不可用，明确显示 `MISSING`/`FALLBACK` 并使用内置设计访谈。访谈至少覆盖：目标用户、痛点、可观察结果、非目标、不变量、产品闭环、已有资产、候选复用范围、风险效果、成功等级和首个叶任务。访谈记录写进项目章程的访谈证据字段及任务设计区，不把用户的一句话直接当成完整规格。

## 3. 自动开发授权

### 3.1 两种模式

- `MANUAL`：每个叶任务开始前由用户确认；
- `AUTO_DEV`：用户预先批准一小批连续叶任务，Agent 仍按叶任务逐个关闭。

`AUTO_DEV` 不是无限自主权。预授权必须写明任务范围、允许效果、最大修复轮次、失败处理、依赖缺失处理和必须停下的决策类型。

### 3.2 修复变更等级（与缺陷严重度独立）

A/B/C 描述拟议修复需要的授权，不是影响大小。Review 另填缺陷严重度 `P0 / P1 / P2 / P3`；两轴不自动映射。

- **A 类**：实现细节、测试补充、命名和局部重构，仍在合同内；
- **B 类**：合同列明的接口调整、兼容性修复或低风险范围扩展，须有预授权；
- **C 类**：改变目标、非目标、不变量、公共语义、敏感数据/发布边界或不可逆效果，必须进入 `NEEDS_DECISION`。

任何严重度的 C 类修复都需要决定；P0/P1 不能因为标成 A 类而降低响应级别。

### 3.3 下一步候选与授权分离

`NEXT_CANDIDATE` 只是可能的下一叶，不等于 `NEXT_AUTHORIZATION`。只有当前任务达到关闭条件且授权存在，才能启动下一叶。

## 4. 叶任务开发流程

### 4.1 叶任务合同

叶任务至少包含任务 ID、父任务、目标引用、单一结果句、前置任务、基线、允许路径/效果、禁止副作用、正负验收、停止条件、修复预算、模式、集成策略、证据位置和下一候选。没有合同、前置任务未关闭或范围不清时保持 `BLOCKED`/`NEEDS_DECISION`。

### 4.2 启动门禁

启动时确认：

1. 项目章程已批准；
2. roadmap 与当前任务的 ID、状态、依赖和复用门一致；
3. 当前叶已取得单独批准或匹配的 `AUTO_DEV` 预授权，并在任务与 roadmap 中同步为 `APPROVED`；
4. readiness 检查通过，二者都是 `READY`；
5. 前置任务已 `PASS_CLOSED`；
6. 没有另一个活动叶任务；
7. 工作区、分支和用户已有改动已记录；
8. 依赖检查结果、宿主能力和效果授权存在；
9. 验收能被实际观察或测试；
10. 复用门为 `COMPLETE`，或有明确批准、遗漏范围、限制和复查条件的有界 waiver；
11. 下一动作具体且唯一。

必需文件、依赖、授权或能力缺失时保持 `BLOCKED` 或 `BLOCKED_TOOLING`，不得以实现代替补齐门禁。

### 4.3 设计外置与最小计划

首次代码改动前，把关键设计、接口假设、测试意图和计划写入任务目录或交接文件。使用 `grill-me`/`grilling` 做分支树访谈；没有时使用内置设计访谈并记录 fallback。长任务维护一个简短 ledger：

```text
Goal:      当前任务要交付的结果
Core:      最重要的约束/接口
Verified:  已验证事实（追加）
Open:      尚未解决的问题及解决条件
Next:      唯一的下一动作
```

不要维护第二套互相独立的事实源；计划、状态和证据应互相引用。

### 4.4 隔离实现与 TDD

代码任务优先使用独立分支或临时工作区，保护主工作树和用户已有改动。对新行为、Bug 修复和重构执行：

```text
RED      写一个能证明缺失行为的检查，并亲眼看到它失败
GREEN    写最小实现使检查通过
REFACTOR 保持绿色，清理重复和命名
```

失败先查根因；不要降低验收、删除负向检查或把检查改成实现回声。文档、审计和 Spike 可用相应的可观察检查替代代码 TDD，但必须记录验证方式。

### 4.5 Review A 与 Review B

候选版本冻结后再审阅：Review A 检查规格覆盖、实现正确性、范围漂移和测试质量；Review B 由不同于实现者的审阅者在新鲜上下文或独立进程中做行为探针，尤其检查负向路径、越界输入和错误处理。没有 fresh 能力只能如实记为 `BLOCKED_TOOLING`，不能改名冒充独立审阅。

### 4.6 修复与决策循环

每条发现同时记录 `P0–P3` 严重度和 A/B/C 变更等级。A 类在合同和预算内可修复；B 类须有授权；C 类或预算耗尽必须写 `decision.md` 并等待决定。每次代码变化产生新候选，旧候选证据不能覆盖新候选。

### 4.7 集成与关闭

```text
候选提交
→ 合并目标分支
→ 在目标分支重新验证
→ 写完成/证据记录
→ PASS_CLOSED
```

只在分支上提交、只跑 focused 测试或只得到 Agent 报告，都不足以关闭任务。无关历史失败要单独列出。

## 5. 状态机

```text
DRAFT
→ APPROVED
→ READY
→ IN_PROGRESS
→ REVIEW
→ INTEGRATION_PENDING
→ POST_MERGE_VERIFIED
→ PASS_CLOSED
```

异常状态：`BLOCKED`、`BLOCKED_TOOLING`、`NEEDS_DECISION`、`PARTIAL`、`SUPERSEDED`。项目管理状态还可用 `PAUSED` 和 `CLOSED`；它们不是通过状态。

`BLOCKED_TOOLING` 表示所需宿主能力、依赖、独立上下文或进程暂不可用；两种阻塞都不能改写成 `READY` 或 `PASS_CLOSED`。项目批准只批准方向，不批准任何叶任务。每个叶必须在任务文件和 roadmap 中同步经历 `DRAFT → APPROVED → READY`，后续状态也要同步；`PASS_CLOSED` 必须绑定最终候选、验收、审阅、集成和合并后验证。

## 6. 证据、版本和完成等级

### 6.1 证据记录

每条证据说明谁在什么宿主/运行中、针对哪个任务和候选、做了什么、实际观察、退出结果、覆盖/未覆盖边界、是否 fresh/独立以及原始输出位置。依赖证据还要写能力状态、原因、影响和 fallback；日志不记录凭据或秘密。

### 6.2 版本事实

代码项目优先使用 Git 的分支、提交、父链、状态和差异作为版本事实。没有 Git 的宿主可引用自己的不可变版本标识，但要标注保障等级较低。不要另建由时间戳、内容摘要或临时指纹组成的版本门禁。

### 6.3 完成声明前的检查

在说“完成”前重新阅读目标，逐条标记已满足、部分满足、未满足和未检查边界，并给出验证命令/观察、候选版本、审阅结果、集成和合并后状态。证据先于结论。

## 7. 项目本地恢复快照

`.charter/handoff.md` 是可选的项目本地恢复快照，不是跨 Agent 通道、消息队列或同步服务。需要暂停、压缩上下文或在另一 Harness 独立继续时，可以更新它；重要状态仍以 `project.md`、`roadmap.md`、`current-task.md` 和 `reuse-discovery.md` 为准，不能只依赖快照或口头承诺。

快照应让下一次运行快速回答：目标、当前叶、已验证事实、未解决问题、唯一下一动作、禁止动作、依赖状态、复用 discovery ID、证据和授权引用。恢复时重新按 `project.md → roadmap.md → reuse-discovery.md → current-task.md → handoff.md（如存在）` 检查；文件缺失或互相冲突时保持 `BLOCKED`，先修复工作集。

## 8. 工具路由

工具按职责使用，不按品牌绑定：

| 工作 | 有原生工具时 | 没有原生工具时 |
|---|---|---|
| 需求澄清/设计 | Superpowers brainstorming | `grill-me` 之外使用内置 design-interview |
| 多步计划 | Superpowers writing-plans | 叶任务合同 + 手写计划 |
| 新功能/Bug | Superpowers TDD | 普通 RED/GREEN 记录 |
| 根因调查 | Superpowers systematic-debugging | 复现、假设、实验和结论记录 |
| 独立审阅 | 新鲜上下文中的 Review 工具 | 新鲜进程/上下文，或明确 `BLOCKED_TOOLING` |
| 完成验证 | Superpowers verification-before-completion | 证据清单逐条复核 |
| 方案拷问 | grill-me（grilling 原语） | `references/design-interview.md` |
| 长任务状态 | J-space ledger/seam/resume | handoff + ledger 区块 |
| 复用发现 | 按固定顺序只读搜索 | 查询矩阵 + evidence receipt |
| 隔离/集成 | worktree/Git 工具 | 临时目录或明确未集成 |

Superpowers、J-space、grill-me 是增强 provider，不是核心硬依赖。缺失时必须输出 `MISSING` 或 `UNVERIFIED`、说明影响并使用便携 fallback；不能静默模拟。

## 9. 项目领域扩展

领域项目可以在自己的 `.charter/project.md`、附录或独立 Skill 中定义产品闭环、术语、数据源、实验方法和专业验收。例如可以把通用的“输入 → 处理 → 验证 → 可观察结果 → 下一步”替换成该领域真正的链路。领域细节不得回写到本包的通用章程、通用模板或宿主入口；领域扩展不能绕过 Goal、Non-goals、Invariants、授权和证据门禁。运行时业务 Prompt 也应与开发治理 Prompt 分开。

## 10. 失败与停机规则

遇到以下情况立即停在当前状态并记录：

- 目标、非目标、不变量或公共语义发生变化；
- 前置任务并未真正关闭；
- 需要未授权的网络、敏感数据、发布或不可逆动作；
- 任务合同与现实实现冲突，继续修补会改变语义；
- 修复预算耗尽或同类失败重复出现；
- 关键依赖/工具不可用，无法提供承诺的独立证据；
- 复用发现工具不可用、记录仍为 `PENDING` 或已过期；
- 候选的来源、版本、许可证或安全影响无法确认；
- 发现用户已有改动可能被覆盖。

停止记录要写已完成部分、阻塞原因、可选决定和恢复所需的第一步。没有依赖时不能把 fallback 的局部检查写成原能力已提供。

## 11. 流程健康检查

每隔两三个叶任务检查：产品开发时间是否仍高于流程维护时间；是否连续修改章程却没有推进产品；关闭时间和重开次数是否上升；是否有越来越多流程证据而没有真实行为证据。若流程连续两次成为主要工作，暂停增加机制，回到产品 backlog。

## 12. 最小启动清单

新项目从零开始时：

1. 判断 `.charter/project.md` 是否存在。不存在就创建完整工作集和空的 `.charter/evidence/`；部分存在只补缺失文件，绝不覆盖已有内容；
2. 运行 `scripts/check_dependencies.py`（或宿主等价检查），把 `AVAILABLE`、`MISSING`、`UNVERIFIED`、`FALLBACK` 和影响写入日志；
3. 用 `grill-me` 优先访谈用户意图；不可用时明确记录缺失并使用内置 `design-interview`；
4. 起草 Goal、Non-goals、Invariants、产品闭环、成功等级、效果边界、资产审计、能力地图、任务树和开放决定；
5. 起草 roadmap 与首个 `DRAFT` 叶任务，完成自审和 `CHARTER_INDEPENDENT` 审阅（或有边界 waiver），取得项目批准；
6. 按 `.charter/reuse-discovery.md` 完成轻量 Reuse Assessment / Reuse Check 并校准路线；覆盖为 `NOT_AUTHORIZED` 或 `BLOCKED_TOOLING` 时先停下，不得写成 `NO_MATCH`；
7. 单独批准首叶或引用匹配的 `AUTO_DEV` 预授权，把任务和 roadmap 同步推进到 `APPROVED`、`READY`；
8. 按叶任务逐一执行 RED/GREEN、审阅、合并、fresh verification 和关闭，并为下一叶重新检查授权。

当模板已支撑几个真实项目后，再考虑增加脚本或宿主集成；治理系统不应比产品本身更复杂。
