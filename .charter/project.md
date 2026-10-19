# Project Charter

## 1. Identity

- Project: `Charter Kit` —— 一个给 AI 编码用的治理套件（没有运行时，只有文件）
- Charter version: `0.3`
- Owner / approver: `YG`（唯一批准人）
- Date: `2026-10-19`
- Current status: `APPROVED`
- Current success level: `SYNTHETIC` 与 `INTEGRATED` 已达成；本版允许到 `INTEGRATED`，`RELEASE_AUTHORIZED` 需单独批准（见第 4 节）
- Reuse discovery gate: `COMPLETE`（2026-10-20 随章程批准转；证据见 `.charter/reuse-discovery.md` 的搜索日志与候选表）
- Reuse discovery record: `.charter/reuse-discovery.md`
- Reuse material-target / final-route projection: 见 `.charter/reuse-discovery.md` 的 `Material target test` 行与候选表的 `Disposition` 单元格 —— 本行不写取值（`REV-CHARTER-20` 的 NF-59：同一事实的六处取值副本里只有点过名的被断言）
- Intent interview evidence: 本版按 `references/design-interview.md` 的六簇清单，把本会话已确认的工程事实补齐；记录见 `.charter/handoff.md` 的 Capability notes。`grill-me` 探测为 `AVAILABLE` 但本会话未调用，按 `PORTABLE_FALLBACK` 记录，理由同处。
- Intent interview mode: `PORTABLE_FALLBACK`

## 2. Desired outcome

### Goal

Write one sentence describing the observable result a user or operator should receive:

> 当一次 AI 编码会话开始、或在中断后恢复时，agent 只读 `.charter/` 里已有的文件，就能说清「这一步被授权做什么、凭什么算做完、还有哪一层证据没人核过」，并把这个结论留成下一个会话能复核的记录——不依赖运行时，也不依赖向人追问。

### User and context

- Primary user: 用 AI 写代码、并且要为「它到底做对没有」负责的开发者：本仓维护者，以及把套件装进自己项目的人。
- Trigger or situation: 会话开始；会话 resume；或一个在叶执行中途到达的新要求。
- Existing pain: AI 愿意做、看起来很快，但会做过头（顺手改无关文件）、会用「我跑过了」代替证据、会把上一个会话的旧结论当成当前事实；反过来，很小的改动又会被同一套重流程拖住。
- Evidence that the pain is real: 2026-10-19 本仓一次独立上下文 Review A 判 BLOCK（findings 的分档与条数见 `docs/SELF-AUDIT.md` 第 9.9 节，本行不复制；那是历史观测，不是本行的现状断言）。当时的 blocker 全是「单个文件自洽、两个文件合起来矛盾」——决策记录落点仍指向被同一批改动判为非法的共享文件。这类缺陷只有跨文件重算才能发现。**注意这是套件级的另一条审阅线：审的是 `git diff 6c2a9bf d6eff20`，记录见 `docs/SELF-AUDIT.md` 第 9.9 节；它与本文件第 4 节 `INDEPENDENT_REVIEW` 行的章程级审阅链不是同一条链（轮次与判词以 `.charter/records/REV-CHARTER-*.md` 的文件集合为唯一权威；本文件只在第 4 节的 `INDEPENDENT_REVIEW` 行维护一次投影（按行标签定位，不按行号——行号会随任何一次插行漂移），其他任何位置不重复计数）**；`BLOCK` 不在 `portable/templates/review.md` 的 Verdict 枚举内，按枚举读作「带未闭合 blocker 的独立判词」。

### Non-goals for this charter version

- 不生成代码：不做 spec-as-source，不做「规范 1:1 映射成代码」的 MDD 路线。
- 不做并行：每个父节点 WIP=1。需要并行时先改这一条，而不是私下开第二条叶。
- 不做无记录的探索回合、不做目录式无审查安装、不做多工作集。
- 不替代人的判断：目标、授权边界、发布与放弃永远由人决定。
- 不追求「文档更全」。治理制品的体积是成本，唯一的成功判据是下一次判断更确定。

### Invariants

These remain true even when the implementation changes:

- 代码是主产物，`.charter/` 是治理事实源，其余治理制品是派生品。
- 没有运行时：每道门都由一个读文件的 agent 执行，所以规则必须写在下一会话会读到的文件里；写在读集之外的规则等于不存在。
- 授权是每一次状态转移的前提；「没有明确禁止」不是授权。
- 关闭由证据决定：执行者的自我报告在结构上不可信，所以检查必须真的能亮红灯。
- 手工源唯一：`portable/` 与根 `DEVELOPMENT_CHARTER.md` 是源，`targets/` 与 `plugins/` 是生成物；镜像字节一致，编号只增不改。
- 一条规则只有一个落点；同一事实出现在多处时只有一处权威，其余是投影，不一致是阻塞发现而不是观点分歧。
- **一个事实只有一个落点。** 计量数（文件数、测试数、字节数、条数、行数、耗时、退出码、由阈值换算出的字节数）只落在 `.charter/evidence/` 的证据文件里；会变的状态只在声明过的投影处写值（本文件第 1 节的 `Reuse discovery gate` 行、第 4 节的 `INDEPENDENT_REVIEW` 行、第 6.1 节的 `Gate result and reviewed on` / `Reuse discovery freshness` / `Reuse discovery ID` 三行、第 10 节的决策表、`roadmap.md` 的七态投影与它的 `Reuse discovery gate` / `Discovery freshness` / `Reuse discovery ID` 三行、`reuse-discovery.md` 的 `Gate status` / `Gate freshness for this leaf` / `Discovery ID` 三个字段；同一事实的每个投影点都必须同值。其中可机检的部分 —— 四个 gate 点、三处 freshness、三处 RD、以及本叶的三行复用取值 —— 由叶的 `AC3` 逐点断言，任何一点漂移都必须变红；第 4 节的 `INDEPENDENT_REVIEW` 行与第 10 节的决策表由 Review A 判，不由 `AC3` 断言（`REV-CHARTER-20` 的 NF-63：声明不许比断言宽）），别处写指针；`handoff.md` 不持有任何取值，只写指针。**计数器自属**：`lessons.md` 每条 entry 头部的 `Hits` 是该条目自身的命中计数，唯一落点就是该行、只增不改，`evidence/` 与别处都不复制它。**边界**：规则参数（阈值、预算、上限、枚举成员数）与结构常量不算计量副本。**这条不变量由 Review A 判，不由扫描器判**（检查项是 `CHK14`；叶的 `AC6` 机检决策表的列数自洽）：把判据机械化试过三轮（`REV-CHARTER-14` / `REV-CHARTER-16` / `REV-CHARTER-17`），每一版都被绕过——中文数词兼作冠词、聚合词跨行、数字躲进括号、同一段条文在两种忠实读法下判定相反；故已撤回扫描器路线，记成决定 `D-08`。读集里若读到与产物不一致的副本，以证据文件与投影处为准，并把该副本当缺陷记进 findings，不要就地改数字。**处置纪律**：任何处置行必须写明「如何在产物里验证」（命令 + 期望输出）；写不出的当场改判 `NOT_CLOSED`，不得用「已落地」结案。验证命令必须在属性为假时返回非 0 或空输出，并断言结构（格数、列位、计数）而不是子串——子串匹配一个状态词在一行多出一格、状态被截断时仍会命中，那样的命令不算验证。**命令里不许出现裸竖线**：表格单元格里的合法转义（`Y\|G`）会让 raw 源形态与渲染形态指向不同的断言，`REV-CHARTER-17` 处置表的两条命令就是这么坏的；要用 `chr(124)` 或 `startswith` 这类不含竖线字符的写法。出处见 `lessons.md` 的 `LS-001` 与 `LS-003`。


## 3. Product loop

Describe the shortest chain from input to outcome. Use the project's own domain terms; a useful neutral shape is `input → processing → verification → observable outcome → next action`.

```text
模糊请求 → Change Triage 判 route（CHARTER > ROADMAP > LEAF > IN_CONTRACT）→ 叶合同（结果句 + AC 与能移动退出码的检查 + 允许路径/效果 + 停止条件）→ 独立上下文审阅 + 四层证据 → 集成后验证 → PASS_CLOSED 与教训蒸馏 → 下一个候选（不是下一个授权）
```

The chain is the product. Gates, logs, branch names, and agent count are supporting controls, not the outcome.

## 4. Success levels and proof

Define project-specific success levels. Each level needs an entry condition, an observable result, required evidence, and an explicit unverified boundary. The following are optional neutral examples; rename or replace them as needed:

| Level | What must be true | Evidence required | Current result |
|---|---|---|---|
| `COMPONENT` | 单份模板或参考文件自身自洽，校验器断言的短语都在 | `validate_kit.py` 对应子检查 | PASS |
| `SYNTHETIC` | 套件自检全绿：镜像字节一致 + 跨文件一致性守卫 | `validate_kit.py .` 与全量 `pytest` | PASS；计数落点 `.charter/evidence/validate-2026-10-19.txt` 与 `.charter/evidence/pytest-2026-10-19.txt` |
| `INTEGRATED` | 三个宿主的手工源与生成物一致，且能从空目录建出可读工作集 | 三个 builder 的 `--check` + `init_project.py` 实跑 | PASS |
| `INDEPENDENT_REVIEW` | 章程级审阅链（轮次以 `.charter/records/REV-CHARTER-*.md` 的文件集合为唯一权威，本格是它在章程里的唯一投影，其他位置不重复枚举）：`REV-CHARTER-01` `REQUEST_CHANGES`（首轮：顺序错、投影不一致、指针指向不存在的东西、自述与实测不符、检查不动退出码） → `REV-CHARTER-02` `REQUEST_CHANGES`（修复动作自己制造了下一批缺陷） → `REV-CHARTER-03` `REQUEST_CHANGES`（原判词写作 `BLOCK`，按枚举读作带未闭合 blocker 的 `REQUEST_CHANGES`；存在性断言冒充相等断言） → `REV-CHARTER-04` `REQUEST_CHANGES`（投影停在一轮前） → `REV-CHARTER-05` `REQUEST_CHANGES`（同一病灶换了行号） → `REV-CHARTER-06` `REQUEST_CHANGES`（两个数并存） → `REV-CHARTER-07` `REQUEST_CHANGES`（处置表说「已落地」而产物里没有） → `REV-CHARTER-08` `REQUEST_CHANGES`（把轮数从散文里删掉，而不是再改一次数字） → `REV-CHARTER-09` `REQUEST_CHANGES`（删掉一个会变的数，不等于删掉所有会变的事实） → `REV-CHARTER-10` `REQUEST_CHANGES`（判据可检查，但被写在读不到它的地方） → `REV-CHARTER-11` `REQUEST_CHANGES`（修复自己制造的下游缺陷：行号也是会变的数） → `REV-CHARTER-12` `REQUEST_CHANGES`（修复按点名而不按形态） → `REV-CHARTER-13` `REQUEST_CHANGES`（散文持有计量数；行标签寻址的分水岭实验） → `REV-CHARTER-14` `REQUEST_CHANGES`（判准本身被判：过宽 / 过窄 / 过强 / 行级豁免漏洞） → `REV-CHARTER-15` `REQUEST_CHANGES`（判准由第三方实现后仍抓出一批残留；证据落点自身过期在门禁之外；子句级豁免仍可搭便车） → `REV-CHARTER-16` `REQUEST_CHANGES`（判准仍不可区分（「子句」与「紧跟」无边界、聚合词位次搬家即豁免）；「合并」只删标题而正文两份；读集仍复述退出码与决定清单） → `REV-CHARTER-17` `REQUEST_CHANGES`（判准 v4 自判失败：八个自造探针五漏两假阳，且同一段条文在两种忠实读法下判定相反 → 撤回扫描器路线并记 `D-08`；计量数以中文数词存活，且 6 与 8 已实漂移） → `REV-CHARTER-18` `REQUEST_CHANGES`（撤回只收敛了一半：承认不可机检，但「由 Review A 判」指不到任何检查项；`D-07` / `D-08` 两行多一格使 `OPEN` 被截断；`Hits` 计数器与不变量互斥；投影清单与实际投影不符） → `REV-CHARTER-19` `REQUEST_CHANGES`（两个新门判定不同：`AC6` 经五个突变验为真门，`CHK14` 只是半真门——第二子句的判据输入与实际投影集合不符、第三子句没有任何一步要求谁交出答案；声明投影不等于实际副本，只改第 6.1 节 gate 时六条 AC 全绿；只读锚点对未跟踪的读集全盲） → `REV-CHARTER-20` `REQUEST_CHANGES`（主判定：天平仍偏向「按点名修」——同形态六处取值副本、兄弟量具 `AC1` 裸切格、锚点只盖 `*.md`、`CHK14` 一行可删仍绿；本轮不再逐条修，改为「一条规则一个实现」：九条验收项载荷全部委托 `.charter/checks.py`，`AC8` 守抽取规则、`AC9` 守不许内联、`AC3` 并入本叶三行复用取值、锚点 ③ 覆盖全部文件） | 逐轮记录见 `.charter/records/`；**链在此封存**（`D-09`）：不再派 `REV-CHARTER-21`；人工门的检查项是 `CHK14`（定义在 `portable/templates/review.md`；本行只点名、不转述子句——上一版转述时漏了第二子句，而漏掉的正是会被证伪的那一条） | 尚无 `APPROVE`；YG 于 2026-10-20 按 `D-09` 裁决「接受带限度的封存」并批准章程 0.3（批准记录见第 11 节） |
| `RELEASE_AUTHORIZED` | 版本号统一，用户批准发布（含是否 push） | 批准引用 + 版本一致性检查 | 未批准 |

本版章程允许达到 `INTEGRATED`。`RELEASE_AUTHORIZED` 不在本版授权内：版本号变更与 push 各自需要一次单独决定。不要把低一级的结果描述成高一级。

## 5. Scope and effects

### Included

- 治理核心：`DEVELOPMENT_CHARTER.md`（循环 A/B、七态状态机、四层证据、失败停机、最小启动清单）。
- 会话入口与启动读集：`portable/commands/charter-workflow.md` 与各宿主 bootstrap prompt（份数见 `.charter/evidence/inventory-2026-10-19.txt`；各份必须同句同字节）。
- 模板：`project-charter` / `roadmap` / `leaf-task` / `reuse-discovery` / `handoff` / `decision` / `review` / `evidence-receipt` / `lessons` / `changelog`（份数见 inventory 证据）。
- 参考：`change-triage` / `contract-migrations` / `default-on-policy` / `design-interview` / `lessons`，加上模板内的复用门语义（份数见 inventory 证据）。
- 脚本与宿主目标：`init_project` / `check_dependencies` / `install_dependencies` / `validate_kit` / 三个 builder；`targets/{codex,zcode,dsh}` 与生成的 `plugins/*`（份数见 inventory 证据）。
- 测试：`tests/`（规模与分解见 `.charter/evidence/pytest-2026-10-19.txt`）。

### Allowed effects

Mark only what this charter authorizes; add project-specific effects when needed:

- [x] `read_only`
- [x] `sample_run`
- [x] `code_write`
- [x] `local_merge`
- [ ] `external_service`
- [ ] `sensitive_data`
- [ ] `release`
- [ ] `irreversible`

### Forbidden effects

- `push`、打 tag、发布到任何市场或目录：在 release 边界之外。
- 写全局目录、安装或卸载能力、修改宿主环境。
- 把仓库源码、密钥、私有文档放进外部查询或外部服务。
- 任何不可逆的外部效应。

Sensitive data, release changes, credential changes, and irreversible external actions require a separate decision record even if the project later needs them.

### Change Triage

- Use the bundled Change Triage reference to classify new requirements, defects, discovered constraints, and risks: `portable/references/change-triage.md` in the full kit or `references/change-triage.md` in the self-contained Skill.
- `CHARTER > ROADMAP > LEAF > IN_CONTRACT` is the precedence order when more than one route seems plausible.
- New requirement must not silently expand the current Leaf.

## 6. Current-state and asset audit

| Asset / capability | Evidence of current state | Classification (`KEEP / ADAPT / REPLACE / ARCHIVE / UNKNOWN`) | Why it serves the goal | Next action |
|---|---|---|---|---|
| `portable/` 模板与 references | `wc -c` + 校验器短语断言 | `KEEP` | 分发内容的唯一手工源 | 任何改动后镜像 + 三个 builder |
| `DEVELOPMENT_CHARTER.md`（体积见 `.charter/evidence/sizes-2026-10-19.txt`） | 镜像字节一致检查 | `KEEP` | 方法论本体：循环、状态机、证据等级 | 与镜像同一提交更新 |
| 各宿主 bootstrap prompt | sha256 全部一致（份数见 inventory 证据） | `KEEP` | 宿主入口，必须同句同字节 | 一处改动所有副本一起改 |
| `scripts/*.py` | 全量 `pytest` | `ADAPT` | 无运行时下的装机、诊断与自检 | 继续加跨文件守卫 |
| `targets/` 与 `plugins/` | builder `--check` | `KEEP`（生成物） | 三个宿主的可安装形态 | 只经 `--sync` 更新，绝不手改 |
| `docs/` 分析文档 | 阅读 | `KEEP` | 设计与取证历史（自审、机制审计、SDD 对照） | 不进分发包 |
| `.charter/` 本文件集 | 本次自举 | `KEEP` | 让套件本身受自己的治理 | 从本叶起纳管 |

Do not replace an asset merely because a new framework is attractive. Do not keep an asset merely because it exists.

### 6.1 Reuse discovery gate

After this charter's direction is approved, complete the single `.charter/reuse-discovery.md` record before approving or implementing the first leaf. A DRAFT leaf may be prepared during charter engineering, but it cannot move beyond DRAFT while the gate is `PENDING` or `BLOCKED` unless that specific Leaf has an explicit, separately approved bounded waiver recorded in the decision fields. The waiver must name the approved/omitted scope, limitation, approver, and expiry/recheck condition; it is not a fourth gate state or project-wide bypass. First record whether the requested capability is a material target; even `NO_MATERIAL_TARGET` receives a local sanity check. For a material target, choose `FAST`, `STANDARD`, or `DEEP` and search progressively: workspace/history → installed skills/plugins/cache/manifest and framework/SDK/dependencies → approved internal resources → official docs/upstream/registries and other explicitly authorized public sources. Scope meanings are fixed: `LOCAL_ONLY` = workspace/history; `LOCAL_ECOSYSTEM` = workspace/history + installed/cache + approved internal; `FULL_EXTERNAL` = LOCAL_ECOSYSTEM + official/upstream/registries + authorized public web. Record exact queries, coverage (`SEARCHED`, `NOT_SEARCHED`, `NOT_AUTHORIZED`, or `BLOCKED_TOOLING`), results (`MATCH`, `NO_MATCH`, or `UNKNOWN`), raw outputs under `.charter/evidence/`, fixed immutable candidate revisions, and the final route. Candidate disposition and final route are separate fields; `BUILD_NEW` is a capability-level final route justified in the hand-back, not a candidate-row decision.

- Discovery scope: `LOCAL_ONLY`
- External read authorization: `no`（本版不授权外网检索；需要时按叶单独批准）
- Privacy restrictions: 仓库源码、密钥、私有文档一律不得进入外部查询
- Search timebox / query budget: 每个叶不超过 20 分钟或 6 条具名查询，以先到者为准
- Stop condition: 声明 scope（`LOCAL_ONLY`）内的 tier 全部 `SEARCHED`，且 scope 外的 tier 明确记为 `NOT_SEARCHED` 或 `NOT_AUTHORIZED`
- Gate result and reviewed on: `COMPLETE` / `2026-10-20`（2026-10-19 采齐证据，2026-10-20 随章程批准转为 `COMPLETE`）
- Latest coverage / result: 见 `.charter/reuse-discovery.md` 第 3 节 Search log 的 `Coverage` / `Result` 两列 —— 本行不写取值
- Reuse discovery ID (mirrors the authoritative record): `RD-20261019-01`
- Reuse discovery freshness: `current`（2026-10-19 首检）。三处投影沿用各自模板的字段名 —— 本行 `Reuse discovery freshness`、`roadmap.md` 的 `Discovery freshness`、`reuse-discovery.md` 的 `Gate freshness for this leaf` —— 名字不同是模板本来的形状，**值必须相同**，并由叶的 `AC3` 与 gate 值、RD 编号一起断言。
- Limitation, waiver, approver, and recheck trigger: 无 waiver；触发条件与到期日见 `.charter/reuse-discovery.md` 第 1 节的 `Recheck trigger / date` 行 —— 本行不写日期

The gate status in this file and in `.charter/roadmap.md` is a projection of the authoritative `.charter/reuse-discovery.md` record. Update all projections in the same change; any disagreement or expired recheck keeps the project/leaf `BLOCKED` until reconciled. A limited or waived search is recorded in the decision/waiver reference with its Leaf, omitted scope, accepted limitation, approver, and recheck condition. A valid leaf-specific waiver may authorize only that Leaf to reach `READY`; it does not create another gate state or change the project-wide projection.

`COMPLETE` requires every material capability to cover its approved scope with raw evidence, explicit out-of-scope coverage, fixed immutable selected revisions, and no unresolved high-value `UNKNOWN` or deferred candidate. `NO_MATCH` is valid only after an exact query ran in the declared scope; `NOT_SEARCHED`, `NOT_AUTHORIZED`, and `BLOCKED_TOOLING` are never `NO_MATCH`. An uncertain item must become a `REUSE_SPIKE`, an explicitly approved bounded waiver for the named Leaf, or a blocking decision; a waiver must explicitly address any high-value `UNKNOWN`/`DEFER` and may not silently turn it into `BUILD_NEW`. A candidate is not permission to install, execute, copy, or change the approved goal; each such action gets its own contract and authorization.

## 7. Capability map

| Capability | Input | Output | Depends on | Required host ability | Observable acceptance | Missing-ability fallback |
|---|---|---|---|---|---|---|
| 治理记录（`.charter/` 工作集） | 章程、路线图、叶合同 | 下一次会话可读的事实源 | 文件系统 | 无 | `init_project.py` 建出整套工作集并可读（份数见 inventory 证据） | 手工复制模板并记录 |
| 会话恢复 | 启动读集（成员由入口命令点名） | 目标、活动叶、授权引用、下一动作 | 上一会话留下的记录 | 无 | 只读启动读集即可复述状态 | 手工摘要并记 `FALLBACK` |
| 变更分诊 | 新要求、缺陷、约束、风险 | 四条 route 之一 | `change-triage.md` | 无 | 每条 route 的判据可逐条对照 | 按优先序人工判 |
| 独立审阅（Review A/B） | 叶合同 + 规格 + 候选 diff | findings 表与 Verdict | 宿主的 fresh 上下文能力 | `subagent` 或 `charter_review` | 复现一次 BLOCK（本会话已发生；套件级审阅线，审 `git diff 6c2a9bf d6eff20`，记录见 `docs/SELF-AUDIT.md` 第 9.9 节，判词按枚举读作带未闭合 blocker） | 同上下文并记录 `FALLBACK`，命名丢失的独立性 |
| 宿主分发 | 手工源 | 三个宿主可安装包 | 三个 builder | `python` | 三个 `--check` 无差别 | 只发 `portable/` 并声明降级 |
| 自检与守卫 | 仓库树 | PASS 或具体失败断言 | `python` | `python` | `validate_kit.py` + `pytest` 全绿 | 手工核对清单并记录 |

For each required or recommended ability, link the latest dependency-check log and state whether it is `AVAILABLE`, `MISSING`, `UNVERIFIED`, or `FALLBACK`.

### 7.1 Review B policy

Review B triggers are kit-owned and cited by ID. The set is append-only: a retired trigger keeps its number and a new one takes the next, so an archived leaf record still means what it meant when it was written. Fill the judgment column once here instead of re-arguing it in every leaf.

| ID | Trigger | This project | Reason or narrowing |
|---|---|---|---|
| RVB1 | Security or authentication | `YES` | 套件里的「授权」就是安全语义：谁能批准哪次状态转移、什么算越界。窄化会把授权问题降级成风格问题。 |
| RVB2 | External dependency | `YES` | 声明零依赖是卖点之一；新增任何依赖都要按外部边界处理。 |
| RVB3 | Public API or public meaning | `YES` | 模板字段、编号语义、命令入口就是对外公共含义；改名会静默改变已归档记录的意思。 |
| RVB4 | High-risk or irreversible effect | `YES` | 版本号、push、发布到目录属于不可逆外部效应，不自动继续。 |
| RVB5 | Explicit user request | `YES` | 用户随时可以点名要求二审。 |

- Reviewer and freshness method: 独立上下文 fresh subagent（本会话已实际跑通：套件级一次判 BLOCK——审 `git diff 6c2a9bf d6eff20`，记录见 `docs/SELF-AUDIT.md` 第 9.9 节，`BLOCK` 不在 `portable/templates/review.md` 的 Verdict 枚举内，按枚举读作带未闭合 blocker；章程级审阅链的逐轮判词见本文件第 4 节的 `INDEPENDENT_REVIEW` 行枚举（按行标签定位，不按行号；轮次与判词以 `.charter/records/` 为唯一权威，本行不聚合判定））；审阅者的模型记在 `REVIEW_MODEL` 轴，不作为独立性结果。
- Decided on / by: `2026-10-19` / `YG`

A `YES` row ships enabled and says the trigger is in force, not that it has been hit. Narrowing a row to `NO`, or to a bounded `YES`, is a user decision recorded in `.charter/changelog.md`, and the narrowed value must state what it excludes; a narrowed row with no stated exclusion reads the same as an unfilled one. Leaving a row at `YES` costs a low-risk leaf nothing: that leaf records Review B `NOT_REQUIRED` and names the RVB ids it considered.

If `Reviewer and freshness method` is still `UNDECIDED` when a leaf first records Review B `REQUIRED`, stop and ask the user before implementing that leaf. The method is decided once, where the knowledge is, and then cited. A project that already holds independent-review evidence fills this line from that evidence instead of leaving it `UNDECIDED`.

Compare this table against the RVB list in the workflow Skill whenever either changes. An ID on either side that the other lacks is a recorded gap, not a silent pass: record it here and resolve it before the next leaf enters `READY`.

## 8. Task tree and route

```text
Epic: R1 —— 让 Charter Kit 本身受它自己的治理，并把治理证据变成可复核的默认
  └─ Capability: R1.1 治理自举（章程、路线图、复用门、第一个叶）
      └─ Vertical slice: R1.1-S1 从零建出可读工作集并批准
          └─ Leaf: R1.1-S1-L1 用本仓自己的模板填出章程与第一个叶合同
  └─ Capability: R1.2 修复轮复验与提交
      └─ Vertical slice: R1.2-S1 本轮审阅 findings 的复验
          └─ Leaf: R1.2-S1-L1 第二次独立 Review A 非 BLOCK 并提交
  └─ Capability: R1.3 模板体积上限的决定（阈值本身是规则参数，定义见 `portable/templates/leaf-task.md` 的 Bounded size 段与 `scripts/validate_kit.py` 的 `LEAF_CONTRACT_CEILING_KB`；「模板不超过其一半」的换算值与实测字节见 `.charter/evidence/template-budget-2026-10-19.txt`）
  └─ Capability: R1.4 下游项目级校验（今天只有套件自检）
```

Rules for leaves:

- one observable behavior per leaf;
- explicit predecessor and allowed scope;
- a test or inspection that can prove the result;
- a stop line and a repair budget;
- default `WIP = 1` for each parent.

## 9. Automatic development authorization

- Mode: `MANUAL`
- Authorized task IDs or range: 无（本版不授予自动连续执行）
- Allowed effects for automatic continuation: 无
- Maximum repair iterations per leaf: 不适用（MANUAL）
- Allowed B-class changes: 不适用
- Mandatory stop conditions: 命中任何一条即停并写 `decision.md`：改 Goal / Non-goals / Invariants、改授权或发布边界、触碰敏感数据、不可逆外部效应，以及 `references/change-triage.md` 判 `OUT_OF_SCOPE` 的请求。
- Expiry or review date: 下一次需要连续执行时重新决定；缺省不复用旧授权。

Automatic continuation never includes a change to the Goal, Non-goals, Invariants, release boundary, sensitive-data policy, public semantic contract, or irreversible external effect.

## 10. Risks and open decisions

This table is the single authority for a question the project has not settled: it
is where a `NEEDS_DECISION` block is discharged. A decision that needed a full record
lives at `.charter/records/<Decision ID>.md` - the format is `decision.md`, and each
decision is its own file, never an appended ledger - and the roadmap's "Decisions affecting
the route" table is a projection of the rows that changed a route. Neither of
those two decides whether a question is still open - read it here.

| ID | Question / risk | What would settle it | Owner | State |
|---|---|---|---|---|
| D-01 | 模板体积上限：`leaf-task.md` 体积对**模板体积阈值的一半**（阈值与换算值均见 `.charter/evidence/template-budget-2026-10-19.txt`），是否抬高该阈值或外移内容 | 一次同时改动所有同步位置的变更（清单见 `.charter/evidence/inventory-2026-10-19.txt` 的 update rule），或一次外移测量 | YG | `OPEN` |
| D-02 | 回溯性叶记录算不算证据：`d6eff20` 那批改动没有叶合同、没有收据 | 一次明确裁定并写进章程 | YG | `OPEN` |
| D-03 | 是否把执行纪律外拆进 `references/` 并加「执行前必读」钩子 | 一次对读集影响的评估 | YG | `OPEN` |
| D-04 | 模板「只增不减」：是否给它加 lessons 那样的准入与退休钩子 | 一次设计（准入钩子 + 退役规则） | YG | `OPEN` |
| D-05 | 下游项目级校验器要不要建（今天 `validate_kit.py` 只校验套件自身） | 一次对下游真实项目的成本收益评估 | YG | `OPEN` |
| D-06 | 依赖探测日志只记时间戳，不记 argv 与 `--optional`，日志无法自证是哪一次运行 | 一次 `check_dependencies.py` 的日志格式改动。召回触发：任何叶需要日志自证运行参数、或任何人改动该脚本的日志格式时，本行回到 `OPEN` | YG | `DEFERRED` |
| D-07 | 证据文件自身的自洽：`inventory` 的计数与真实 glob、`ac-liveness` 里的散文与它自己的表，都可能各自过期而门禁全绿（已采证据：`REV-CHARTER-17` 与本轮各重放一次 E1 / E4 探针，仍全绿，记录在 `.charter/evidence/probes-2026-10-19.txt`） | 一次下游校验器原型能对 `inventory` 的四条 glob 返回非 0；或 D-05 裁「不建」时本行转 `DECIDED`，接受限度是「证据文件的自洽由 Review A 逐次重算」，到期日为下一次证据文件被改动的叶 | YG | `OPEN` |
| D-08 | 读集数值副本没有机检：判据机械化三轮全被绕过（中文数词兼冠词、跨行聚合、括号内数字、两种忠实读法结论相反），已撤回扫描器路线；人工判定由 `CHK14` 接管，规则参数与结构常量不在此列 | 一次决定：承认这条不变量是人工门（写成 `DECIDED` 并接受限度「由 `CHK14` 逐叶检查，无机检」），或与 D-05 合并成一次校验器设计；D-05 裁「不建」时本行转 `DECIDED` 并带同样的接受限度 | YG | `OPEN` |
| D-09 | 章程级审阅链在无 `APPROVE` 的情况下封存：`REV-CHARTER-20` 判 `REQUEST_CHANGES`，六条 findings 已处置，但不再派下一轮（用户指示停止逐条迭代）；代价是失败模式清单停在经验集，不是闭集 | 已结算（2026-10-20）：YG 选「接受带限度的封存」。限度与仍开着的项见 `.charter/records/REV-CHARTER-20.md`；复核触发=任何一次新的章程级审阅，或 `D-08` 结算；到期 2027-01-20 | YG | `DECIDED` |
| D-10 | 读集无界增长：启动读集里 `project.md` / `roadmap.md` / `reuse-discovery.md` 三件没有体积触发条件（`P1-3` 曾以「实体型增长 + 扇出触发」落地，2026-10-19 用户裁决回滚，机制已删除） | 一次裁定：这个缺口是否真需要处理。是则选一个对超大项目也不失守的机制（绝对字节上限已被判不适用）；否则记为 `REJECTED` 并写明理由，使下一个人不必再提 | YG | `OPEN` |

`State` takes one of these five values and no others:

| State | Means | The row must also carry |
|---|---|---|
| `OPEN` | unsettled | who can settle it, and what evidence would |
| `DECIDED` | settled and current | the decision reference, any limitation accepted, and its expiry or recheck trigger |
| `DEFERRED` | settled as "not now" | the recheck trigger that brings it back |
| `REJECTED` | considered and refused | the reason, so it is not proposed again |
| `EXPIRED` | no longer answerable as written | what superseded it |

A `DECIDED`, `REJECTED`, or `EXPIRED` row that carries its field is what discharges
a `NEEDS_DECISION` block; a state with no carrying field reads as `OPEN` whatever the
cell says. Two review outcomes land here by name: a finding recorded
`ACCEPTED_WITH_LIMITATION` becomes `DECIDED` carrying its limitation and expiry, and
a finding recorded `DECIDED_BACKLOG` becomes `DEFERRED` carrying its recheck trigger.

`OPEN`, `DEFERRED`, and `REJECTED` are live rows and stay: a refusal an agent cannot
see is a refusal it will propose again. A `DECIDED` row leaves only after a decision
record carries the decision in full, and it leaves as a move, never as a deletion -
keep one line with the id, the one-line outcome, and the reference to the record.

## 11. Approval record

- Charter self-review evidence: `docs/SELF-AUDIT.md` 第 1 节的十二把尺子，加 `DEVELOPMENT_CHARTER.md` 第 2.8 节自审清单逐条
- Independent charter review evidence / applicability: `REQUIRED`（本版确立了套件自身的授权边界与不变式，属高风险章程）；审阅记录见 `.charter/records/REV-CHARTER-01.md`
- Approved goal and non-goals by: `YG`（2026-10-20，会话消息 m03483）
- Approved on: 2026-10-20
- Approved success level: `INTEGRATED`
- Approved effects: `read_only` / `sample_run` / `code_write` / `local_merge`（禁止项见第 5 节）
- Approval reference: 会话消息 m03483（YG：「那现在继续吧」）；章程级审阅证据 = `.charter/records/REV-CHARTER-01` 至 `REV-CHARTER-20`
- Conditions or expiry: 带限度批准 —— 章程级审阅链未取得 `APPROVE`，按 `D-09` 以「接受带限度的封存」批准；限度=语义类判据不由机检覆盖（`D-08`），由 Review A 判；到期 2027-01-20，届时必须复核或被新审阅取代

Project-charter approval does not approve the first leaf task. Record leaf approval or matching `AUTO_DEV` preauthorization separately in `.charter/current-task.md` before moving it from `DRAFT` to `APPROVED`.
Before setting `Current status` to `APPROVED`, the self-review field must contain evidence and the independent-review field must record either required review evidence, a bounded `NOT_REQUIRED` reason, or an explicit waiver. If a waiver is used, name the unavailable capability, the approving person, the limitation accepted, and its expiry or re-review condition.

## 12. Change log

The charter's version history lives in `.charter/changelog.md` and is not repeated here.
Only the current version is readable in this file: `Charter version` in section 1. A
resume reads the charter's current state, never its earlier states, so a table
holding both is how a superseded value gets read as the current one. Keep this section
a pointer.

A row is required by these changes, and nothing else: any narrowing of `RVB1`-`RVB5`
or of another risk trigger; any new mandatory contract field or checklist item; any
charter-level or record-level migration; any change to the Goal, Non-goals,
`Invariants`, effect boundary, or release boundary. `.charter/changelog.md` carries the
full rule and the row format; the list above is the part that decides whether a row
exists, and it lives here because this file is read on resume and that one is not.
