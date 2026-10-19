# 自审：用本套件自己的判据审本套件

> 主体是 Charter Kit 本身。缺口不是从别人的功能表抄来的，是从本套件自己立下的判据推出来的。
> 外部项目（Spec-Driven Development 工具链、BMAD、Agent OS、Shape Up、ADR 实践）在这里只作对照，不作出题人。
> 方法、判据来源、行号引用、复核命令全部可复现。

---

## 0. 为什么重做一次

前两稿有一处共同的错：**问题清单是按「别人有什么」逐条扫出来的，不是按「本套件自己判什么为缺陷」扫出来的。**

后果有两个。第一，方向反了——套件自己装着 `reuse-first`、`reduce-reinvention` 两个 provider 和一道复用发现门，而我在给建议时没有对自己的项目跑一遍，把「已经有了而且更强」的机制判成了空白（澄清机制、默认值盘点、negative control 三处判错）。第二，冲突看不见——空白只是没做，冲突是两个 agent 拿着两条相反的指令各按最省力的一边执行，而且不留记录。冲突比空白危险，但按别人的功能表扫，只能扫出空白。

这一稿换方向：**先问本套件自己拿什么当缺陷判据，再用那些判据量本套件自己的制品。**

---

## 1. 十二把尺子（全部原文级，出自本套件自身）

这些不是我发明的标准，是套件自己写下来的。审计的唯一合法性来自：**它们对下游项目成立，就对本套件自己成立。**

| # | 判据 | 出处（原文） | 审计问句 |
|---|---|---|---|
| A1 | 可见性 | `portable/references/default-on-policy.md:10-15`："There is no runtime. Every gate is enforced by an agent reading the file that records whether the gate passed. A rule that ships off is therefore not neutral — it is invisible, and the next agent has no way to tell 'considered and declined' from 'never noticed'." | 这条规定落在 agent 本来就会读的哪个文件里？只存在于一份没人保证会读的文档 = 等于 shipped off。 |
| A2 | 钩子 | `portable/references/lessons.md:69-71`："An unhooked ledger dies — records that no workflow step reads or reports become an empty directory of .gitkeep files; the distill, cite, and report hooks above are what keep this one alive." | 哪一步读它？哪一步**报**它？ |
| A3 | 门禁 | `portable/templates/leaf-task.md:121-138` Check discipline：读被测对象 / 覆盖每一个实例 / **必须能移动退出码**（打印但不影响退出码的违规只是日志行，不是门）。 | 这条规定能不能让某次运行变红？ |
| A4 | 证据 | `portable/templates/evidence-receipt.md:42-46`："a self-verification recomputes asserted values from the originals — a check that re-reads the field it certifies is not a gate, and a tampered copy must fail it." | 这个数字是从原始物重算的，还是抄自己的？ |
| A5 | 冻结 | `portable/templates/roadmap.md:50`："Every checklist item carries a stable number (`RDY1`…); leaf contracts reference results by number plus a short label … never by restating the item text. The numbering is append-only: retired items keep their number with a retirement date, new items take the next number — renumbering would silently change what archived leaf records mean." 同款纪律：`LS-NNN` 冻结（`lessons.md` 模板）、RVB 集合 append-only（`project-charter.md:143`）、`contract-migrations.md:79-81`「新增块必须是 `### 7.1`，绝不能作为新的编号章节」。 | 这条规定/这份记录有没有稳定编号？加一条时旧记录的含义会不会静默改变？ |
| A6 | 不折叠 | `reuse-discovery.md:65` "Coverage and result are separate fields; do not collapse them into one combined status."；`:77` "BUILD_NEW is a capability-level route, never a candidate disposition."；`:16` waiver "is not a fourth Gate state or a project-wide bypass"；`leaf-task.md:5` "Never replace a leaf-specific field with a reference." | 有没有把两个不同的东西塞进一个格子里？ |
| A7 | 有界 | `handoff.md:7`："This file is in the required-start read set, so every actor pays for it on every resume and it must not grow with the project."；`lessons.md:8-9` ≤64 KB 同理由；`charter-workflow.md:47` "Both bounds exist because every resume re-reads the required set." | 这份文件在启动读集里吗？在的话，它的上限是多少？ |
| A8 | 成本 | `DEVELOPMENT_CHARTER.md:410`（若流程连续两次成为主要工作，暂停增加机制）、`:425`（治理系统不应比产品本身更复杂）；`default-on-policy.md:29-32` 第 4 要素 "Zero cost for the case that does not need it. … If holding the default on is expensive for the ordinary case, it will be narrowed for the wrong reason." | 普通场合付多少？有没有按后果省略的路径？ |
| A9 | 留痕 | `leaf-task.md:151-157` "Deviating without a recorded Ruling is a decision made in secret"；`decision.md:14` "Do not hide a scope change inside an implementation note." | 这个决定留在哪儿？谁签的字？什么时候失效？ |
| A10 | 自报不算 | `:93` 不变量「执行者自报不能替代独立证据」；`:161`「同一会话自审不能冒充独立 Review」；`:329` 分支提交 / focused 测试 / agent 报告，三者都不足以关闭。 | 这条结论的证据是谁产的？与产出者独立吗？ |
| A11 | 报告 | `portable/references/lessons.md:32-39`：Report 在 resume 状态行与关闭报告里出，「用户从不轮询磁盘」；GENERALIZE 候选是「决定」不是「搁置」。 | 它出现在任何一份**会被念出来**的报告里吗？ |
| A12 | 唯一权威 | `:22` 只有一条主控制流；`change-triage.md:33` "Keep the current task contract as the active Leaf state authority; use the roadmap only as a projection."；`project-charter.md:128` 投影必须同一次改动同步，"any disagreement or expired recheck keeps the project/leaf `BLOCKED` until reconciled"。 | 同一个事实有几个载体？谁是权威？不一致时谁输？ |

---

## 2. 把十二条压成一个模型：三个钩子

A1、A2、A11 说的是同一件事的三层。合起来就是本套件对「记录为什么活不下来」的完整解释，而 `lessons.md:69-71` 那句话只把它用在了 ledger 一件事上。

我把这三层叫**三钩**：

- **编号钩**（A5）：这份记录/规定有稳定编号，能被别处按编号引用。
- **读取钩**（A1）：有一个流程步骤**必然**打开它。
- **报告钩**（A11）：它出现在 resume 状态行或关闭报告里。

判据：**三钩缺一，规定退化为建议；三钩全缺，规定等于不存在。** 而 `default-on-policy.md:10-15` 讲的「shipped off = invisible」正是「读取钩缺失」的正式表述。

### 2.1 本套件自己的制品逐个过三钩

这一张表就是本次审计的结论摘要。判定只有三种：**活**（三钩齐）/ **半活**（缺一钩：能被引用但没人报，或有人读但引不了）/ **死**（缺两钩以上）。

| 制品 / 规定 | 编号钩 | 读取钩 | 报告钩 | 判定 |
|---|---|---|---|---|
| RDY1–RDY13 就绪清单 | 有，append-only | 有（`:263-277` 启动门禁逐条核） | 有（leaf-task `Readiness record` 按编号引用） | **活** |
| RVB1–RVB5 审阅触发 | 有，append-only | 有（`:311`、`project-charter.md:141-160`） | 有（`Review B / fresh behavior check` 记 id） | **活** |
| LS-NNN 教训 | 有，冻结 | 有（Design / Reuse Check / Change Triage 三处查询并引用） | 有（resume 状态行 + 关闭报告） | **活** |
| E-ID 证据收据 | 有 | 有（每次验证） | 有（Evidence 表 / F 行 Evidence reference） | **活**（但落盘结构性矛盾，见 §3.5） |
| 叶 Events 表 | **无编号** | 有（本叶内） | 部分（关闭时对账） | 半活 |
| `review.md` Checks performed 11 条 | **无编号** | 有（每次审阅） | 有（`:54` "No findings is a valid result only after every applicable check above has an observation"） | **半活** |
| `project-charter.md` §10 开放决定 State | 有（D-01） | 有（草拟与批准时填） | **无** | **半活** |
| `project-charter.md` §12 change log | 有（Version） | 部分（`:156` 规定 narrowing 记这里） | **无** | **半活** |
| 关闭条件（`:329` / `:345` / `:367` / `:224`） | **无** | 部分（散在四处，无一处汇总） | 有（关闭报告） | **半活** |
| `default-on-policy.md` 四要素 | 文件名 | **无** | **无** | **死** |

最后一行是本次审计的起点，也是最讽刺的一行：**本套件对「规定为什么会隐形」写得最清楚的那份文档，自己就是隐形的。**

---

## 3. 十五条缺口，逐条裁定

每条给四样：现象（可指认）→ 违反哪把尺子（原文+行号）→ 按本套件自己的逻辑为什么算缺陷 → 最小修法与冲突检查。

### 3.1 P0-1：`default-on-policy.md` 是唯一三钩全缺的判据文件

**现象。** 全仓 authoring 源里，这份文件只被提到过一次——`DEVELOPMENT_CHARTER.md:311` 的一句括注：「这是 default-on 策略的又一实例（见 `references/default-on-policy.md`）」。没有任何步骤要求作者去读它的四要素清单，它不出现在 resume 状态行，不出现在关闭报告，不出现在 `:263-277` 门禁。

**违反。** A1 + A2。按它自己的话："A rule that ships off is therefore not neutral — it is invisible"；按 `lessons.md:69-71`："records that no workflow step reads or reports become an empty directory of .gitkeep files"。

**为什么这是缺陷而不是风格问题。** 它不是一份参考资料，它是**本套件唯一一份关于「怎么定默认值」的元规则**：保守默认值 / 收窄须具名并说出排除了什么 / 在拥有该策略的文件里记批准人和日期 / 用不到的场合零成本。凡是新增门禁、新增必填字段、新增清单项的场合都要用它。而它的位置决定了下游项目加第 12 条门禁时不会想到问「这条对普通场合是否零成本」。§3.2 的缺口之所以能存在，直接原因就是这份元规则没有钩子。

**最小修法。**
1. `DEVELOPMENT_CHARTER.md` §1 循环A 的「起草门禁/清单」那一步，加一句必读指令：任何新增或修改门禁、必填字段、清单项的改动，先按 `portable/references/default-on-policy.md` 四要素逐条写出答复，答复进 §12 change log。
2. `contract-migrations.md` 的迁移步骤里加一条前置检查——新增必填字段属于「需要过四要素」的改动类别。
3. `review.md` 的 checks 加第 12 条（配合 §3.4 的编号改造）：本轮是否新增了门禁/必填字段/清单项；若是，四要素答复在哪儿。

**冲突检查。** 与 `project-charter.md:3` "Keep it short enough to reread" 不冲突——加的是三处指针句，不是正文。

### 3.2 P0-2：主循环没有按后果省略的出口，而本套件自己立了成本判据

**现象。** `:26-41` 循环A 十五步、`:45-57` 循环B 十步、`:263-277` 十一条启动门禁，全套件找不到任何「按后果降低流程成本」的路由。唯一像档位的东西是 `project-charter.md:180-190` §9 自动开发授权（Mode `MANUAL | AUTO_DEV`），但它管的是**效果边界**（允许写哪些路径、允许哪些 B 类改动、最大修复轮次、强制停止条件），不是**流程档位**——一个 AUTO_DEV 的叶仍然要跑完整个设计树、全套门禁、Review A、四层证据。

**违反。** A8 三处同时命中：`:410`「若流程连续两次成为主要工作，暂停增加机制」、`:425`「治理系统不应比产品本身更复杂」、`default-on-policy.md:29-32` 第 4 要素「用不到的场合零成本」。

**为什么按本套件的逻辑这是缺陷。** 本套件已经在**一个**地方做到了零成本：`project-charter.md:156`——RVB 行出厂为 `YES`，低风险叶「records Review B `NOT_REQUIRED` and names the RVB ids it considered」，代价接近零。也就是说套件自己证明了「默认全开 + 按后果声明不适用」这个形状是可行的，而且已经用在了它最贵的那道门（独立审阅）上。而主循环——比 Review B 贵得多的那部分——没有采用自己已经验证过的形状。这不是缺一个外部功能，这是**同一份判据在套件内部适用范围不一致**。

**最小修法（三档 + 三条元规则）。**
- **轻量档**：五条件同时满足才可用 ——（a）单个结果句、不新增公共语义；（b）只改一个叶已允许路径内的文件，不动不变量、授权、敏感数据、发布边界、不可逆效果；（c）不新增依赖、不改构建配置；（d）验收能被一条命令观察；（e）复用门为 `NO_MATERIAL_TARGET` 或候选已钉版本。满足则省设计树、省 Review B、就绪清单只核 RDY1/RDY2/RDY5/RDY7 四条（其余逐条写不适用理由，不是留空）。
- **标准档**：默认。当前全流程。
- **结构档**：命中 `project-charter.md:190` 排除清单任一项，或改 Goal / Non-goals / Invariants / 公共语义 / 发布边界 / 敏感数据 / 不可逆效果 → 加方案评审与反对者角色。
- 三条元规则：档位由**后果**定，不由工作量定（工作量小但碰不变量的是结构档）；升级免费、降级有价（降级必须写明省了什么、为什么这些省的代价可接受）；**没写档位的叶按标准档处理**。

**冲突检查（重要）。** 这条必须与 §9 自动开发授权**合并**实现，不能并列。§9 已经定义了「允许效果」与「强制停止条件」，档位只是把同一组边界显式化成后果分级。两处并列会让 agent 面对两张都叫「授权」的表。

**与既有缺口的耦合。** 连续三个轻量档叶之后，第四个强制回到标准档；轻量档叶不得关闭父节点。没有这两条，轻量档会自我强化到流程消失——这正是 `:410` 那句「连续两次成为主要工作就暂停增加机制」的反向风险。

### 3.3 P0-3：开启是十一条编号门禁，关闭是散在四处的散文

**现象。** 开叶有 `:263-277` 十一条编号门禁，逐条可核、可引用。关叶的条件却散在至少六处：`:329`（分支提交 / focused 测试 / agent 报告都不足以关闭）、`:345`（账本对账 + Git 集成与合并后验证同为关闭证据）、`:367` 与 `portable/references/lessons.md:11-18`（handoff 归档前的提升扫掠、distill 时机）、`:224` 与 `roadmap.md:74-76`（门状态与依赖解锁）、`roadmap.md:72`（七态镜像、清 Active leaf、同步 Next authorization）、`leaf-task.md:229-242`（关闭五选一）。

**违反。** A3 + A10。对照 `review.md:28-54`：审阅有 11 条 checkbox，且 `:54` 立了铁律 "No findings is a valid result only after every applicable check above has an observation"。关闭这个动作比审阅更贵、更不可逆，却没有对应的形状。

**为什么这是缺陷。** 按 A3，一条规定只有在能让运行变红时才是门。关闭侧的这些条件没有一个统一载体，所以「哪一条没做」只能靠执行者自己想起来——而 A10 刚说完：执行者自报不能替代独立证据。开启侧的门禁是给**别人**核的（审阅者、下一个 agent）；关闭侧没有清单，等于关闭只能由**执行者自己**核，正好落在 A10 的禁区里。

**最小修法。** 新建 `CLS1–CLS9` 关闭清单，放进 `leaf-task.md` §9，编号 append-only（理由与 RDY 完全相同，见 A5）：
- CLS1 目标重读并逐条标记（`:359`）
- CLS2 四层证据齐：退出码 / 原始物重算 / 独立上下文审阅 / 集成后验证（`:351`）
- CLS3 审阅 findings 全部处置：修复 / 有界 waiver / 明确 decided backlog（`:191`、`review.md:50-56`）
- CLS4 会话账本已对账，或有命名 `NOT_ENABLED` 豁免（`:345`）
- CLS5 Git 集成与合并后验证已记录（`:345`、`roadmap.md:76`）
- CLS6 handoff 归档前提升扫掠已跑（`handoff.md:9`）
- CLS7 lessons distill 已跑或已声明零产出（`lessons.md:11-18`，零产出是合法结果）
- CLS8 三处投影一致（leaf / roadmap / project），Active leaf 与 Next authorization 同步（`roadmap.md:70-72`）
- CLS9 关闭五选一已选并写理由（`leaf-task.md:229-242`）

任一 CLS 项非 PASS 则不得 `PASS_CLOSED`，只能停在 `PARTIAL` 或对应异常态。`:345` 的「无对账无豁免不得 PASS_CLOSED」是 CLS4 的特例，原文保留，清单引用它而不是复述它（A6 的 "Never replace a leaf-specific field with a reference" 说的是字段值，编号引用是 A5 明确要求的形态）。

**冲突检查。** 与 `:425`「模板撑过几个真实项目再加脚本」不冲突——这是模板，不是脚本。与 `project-charter.md:3` 不冲突——清单进 leaf-task.md，不进章程。

### 3.4 P0-4：审阅清单 11 条没有编号，而本套件冻结编号的理由对它完全成立

**现象。** `review.md:30-40` 的 11 条 checkbox 无编号。而结构完全同构的 RDY 清单有编号，且 `roadmap.md:50` 给出了冻结理由："renumbering would silently change what archived leaf records mean"。

**违反。** A5。

**为什么这是缺陷，且为什么它比看起来严重。** 三条连带后果，全部由套件自身逻辑推出：

1. **无法引用。** RDY 的引用纪律是「by number plus a short label」（`roadmap.md:50`、`leaf-task.md:210`）。审阅结论要跨记录引用某一条 check 时没有编号可用，只能复述原文——而 A6 的 "Never replace a leaf-specific field with a reference" 与 A5 的 "never by restating the item text" 恰好说明复述是不允许的形态。
2. **无法 append-only。** 加第 12 条 check 时，已归档的 review 记录无法区分自己当时跑了 11 条还是 12 条。这正是 `contract-migrations.md:3-7` 描述的那个失败："the field is simply absent, which looks the same as a field that was considered and left empty"——只不过这里缺的是**一条 check**，不是**一个字段**。
3. **迁移机制盖不住它。** `contract-migrations.md` 的 Fields added after `0.1` 表（`:36-44`）与 Charter-level 迁移表（`:75-77`）都只处理「新增必填**字段**」，全篇没有「新增一条 check」「新增一个枚举值」这两个迁移类别。后者只提了一个先例（`:46` 的 `control.py controller` 是 "an enum extension, not a migration"），没给规则。

**最小修法。**
1. `review.md:30-40` 的 11 条改为 `CHK1–CHK11`，声明 append-only，引用方式与 RDY 同款（编号 + 短标签）。归档记录不迁移；在 review 模板顶部记一次读法边界注记（同 `contract-migrations.md:94-99` 处理 `WAIVED`/`NOT_REQUIRED` 的范式）。
2. `contract-migrations.md` 增加两类迁移：**check 级**（新增一条 check → 记 CLARIFICATION 命名 CHK 编号，已关闭记录不迁移，在模板顶部记读法注记）与**枚举级**（新增一个合法值 → 不迁移，旧值继续有效，写明何时旧值失效）。

**冲突检查。** `validate_kit.py` 覆盖 review.md 的必填字段集，改编号需同步校验脚本与 `skills/charter-workflow/templates/review.md` 生成物——注意生成物由 `scripts/` 从 `portable/` 重建，不能直接改。

### 3.5 P1-1：三份 per-event 记录被固定成单一文件名，其中一份的模板自己要求「每项一条」

**现象。** `charter-workflow.md:29`（以及五份 bootstrap prompt 的 `:24`，字节相同）把 `.charter/` 固定为九件 + `evidence/` 目录，其中 `decision.md`、`review.md`、`evidence-receipt.md` 各是**一个固定文件名**。同时：

- `decision.md:5` 有 `Decision ID: <DEC-ID>`——一个文件装一个决定。
- `review.md:5` 有 `Review ID: <REV-ID>`；Review A 每叶必需（`review.md:26` "Review A is required for every Leaf"），Review B 可能同叶再跑一次，且 `:311` 要求 Review B 必须是**另一个** fresh 审阅者 → 每叶至少一份、常有两份。
- `evidence-receipt.md:3` 开头第一句就是 "Use one receipt per meaningful test, inspection, review, or integration check." → 每叶多份。

**违反。** A7 + A5。按 A7 的理由（在启动读集里、每次 resume 都付体积、不得随项目增长——`handoff.md:7`、`charter-workflow.md:47`），这三份文件按 per-event 语义写下去必然单调增长，而它们属于每次都要付的集合。

**为什么这是缺陷。** 本套件对同一个形状已经给出过两次解：`lessons.md:10-12` 的 `.charter/lessons-archive.md` + 指针行，`handoff.md:7` 的 `.charter/handoff-archive.md` + 指针行。三份 per-event 记录**一个都没有**。而且 `leaf-task.md:175` 给叶合同归档定了 per-leaf 文件名规则（`.charter/evidence/<date>-<leaf>-contract-archive.md`），说明套件知道 per-ID 落盘该怎么做，只是没用在这三份上。最尖锐的是 `evidence-receipt.md:3`：模板的**第一句话**要求多条，bootstrap 的**第一件事**只给一个格。

按 A1，这个矛盾的后果可预测：下游 agent 面对「一个文件装多条」时，最省力的做法有两种——每次整文件覆盖（丢历史），或者无限追加（丢有界）。`leaf-task.md:174-178` 对叶合同归档明文禁止了第一种（增量编辑绝不整文件重写），对这三份没有说。

**最小修法。**
1. 落盘规则改为 per-ID 文件名：`.charter/records/<TYPE>-<NNN>[-<slug>].md`（review / receipt / decision 三类），配 `.charter/records/index.md` 单行索引（ID | 类型 | 叶 | 日期 | 结论 | 指针）；索引保留最近 N 条，其余追加到对应 archive 文件并留一行指针（与 lessons / handoff 同款）。
   或者更保守的等价做法：保留单文件名，但把它明确定义为**索引**，正文一律落 `.charter/records/`。两种都行，必须选一种并写死，不能留空——留空正是 `default-on-policy.md:10-15` 说的 invisible。
2. bootstrap 与 `charter-workflow.md:29` 的工作集清单同步：九件变成九件 + `records/` + `records/index.md`。五份 prompt 字节必须一致（`validate_kit.py` 会核）。
3. `evidence-receipt.md:3` 加一句：本条与落盘规则的关系。

**冲突检查。** 这是本次审计里唯一会改动 bootstrap 工作集与五份 prompt 的一条，波及面最大。`validate_kit.py` 会核镜像字节与模板字段，改完必须重跑。

### 3.6 P1-2：同一个事实有三个载体，没有权威规则

**现象。** 记录「一个未决/已决决定」的地方有三张表、三种 ID、三套字段，互不声明关系：

| 载体 | 字段 | 状态枚举 |
|---|---|---|
| `project-charter.md` §10 Risks and open decisions（`:192-197`） | ID / Question or risk / What would settle it / Owner / State | 示例只有 `OPEN` |
| `.charter/decision.md`（`decision.md:5-10`） | Decision ID / Required authority（`OWNER / PRODUCT / SECURITY / PRODUCTION_OPERATOR`）/ Status | `OPEN / APPROVED / REJECTED / EXPIRED` |
| `roadmap.md` Decisions affecting the route（`:78-82`） | Decision ID / Affected IDs / What changed / Approval or evidence | 无状态列 |

**违反。** A12（唯一权威 + 投影同步）+ A6（不折叠）。

**为什么这是缺陷。** 本套件对复用门立了一条极严的投影纪律：`roadmap.md:28` 声明 gate "is a synchronized projection and must match `project.md`"，`:70` "Any mismatch is a blocking finding, not permission to choose the most optimistic copy"，`project-charter.md:128` "any disagreement or expired recheck keeps the project/leaf `BLOCKED` until reconciled"。同一套纪律对**决定**这个事实类别不存在：一个决定可以只在 §10 是 `OPEN`、只在 decision.md 是 `APPROVED`、而 roadmap 那条表里根本没有它，没有任何步骤会因此变红。

更具体的两处断裂：（a）`decision.md` 的 Status 有 `EXPIRED`，而 `roadmap.md:78-82` 那张表没有状态列，所以一个过期决定在路线投影里和有效决定长得一样；（b）§10 的 `Owner` 与 decision.md 的 `Required authority` 是两个不同概念（一个填写者，一个批准权限），同名列不同义。

**最小修法。**
1. 声明权威：`.charter/records/decision-<DEC-ID>.md` 为唯一权威（状态 + 权限 + 选项 + 失效条件）；`project-charter.md` §10 降为决定清单投影，只留 `ID | 一句话 | Owner | State`，项目级决定用 `DEC-` 前缀而不是 `D-01`；`roadmap.md:78-82` 降为路由投影，补一列 `Status`。
2. 三处不一致 = blocking finding（照抄 `roadmap.md:70` 的措辞），并进 CLS3。
3. §10 的 `State` 补齐枚举：`OPEN / DECIDED / DEFERRED / REJECTED / EXPIRED`，并规定 `DEFERRED` 必须带复查点。理由直接写进表头：`design-interview.md:50` 说未闭合分支是实现开始的停止条件（"An unresolved branch at implementation start is a stop condition, not a footnote"），而一张只有 `OPEN` 一个示例值的表无法承载「已闭合」。

**冲突检查。** 与 `contract-migrations.md:66-73`「charter 级迁移是 records-only，改 Goal/Non-goals/Invariants/授权/公共语义才算 scope change」一致：§10 补枚举与补投影列属于 records-only，走 charter-level 迁移，版本落 §12 change log。

### 3.7 P1-3：启动读集六件，只有三件有上限

**现象。** `:365` 恢复读序 = `project.md` → `roadmap.md` → `reuse-discovery.md` → `current-task.md` → `handoff.md` → `lessons.md`。有上限的三件：`current-task.md` 36 KB（`charter-workflow.md:47`）、`handoff.md` 结构性有界（`handoff.md:7`，只留活动叶 + 最近一个已关闭叶）、`lessons.md` 64 KB（`:367`）。**无上限的三件**：`project.md`（唯一相关句 `project-charter.md:3` "Keep it short enough to reread" 是形容词，无数字无结构规则）、`roadmap.md`（Delivery order 表随叶单调增长，`:14-19`）、`reuse-discovery.md`（按叶 append；`:46` 明确「不要建注册表」但没说怎么归档）。

**违反。** A7，而且违反的是**它自己给出的理由**：`handoff.md:7` "This file is in the required-start read set, so every actor pays for it on every resume"、`charter-workflow.md:47` "Both bounds exist because every resume re-reads the required set"。这个理由对六件同等成立，只对三件执行了。

**为什么这是缺陷。** 按 A8 第 4 要素，一个没有上限的启动读集成员，其成本随项目线性增长而无人察觉——它不会报错，只会让每次 resume 更慢、更贵、更容易在中段丢关键信息。三种上限存在的事实说明套件认为这件事值得管；三种缺失说明规则的添加是**按踩过的痛逐个加的**，不是按判据统一推的。§3.5 与 §3.7 是同一个病因。

**最小修法。**
1. `project.md` 给结构上限：例如「§1–§6 合计 ≤12 KB；§7 能力地图只留当前能力，历史归档到 `.charter/project-archive.md`」。数字由作者定，但必须是一个**可判定**的数字，且给出超限动作（像 `handoff.md:7` 的第三块规则）。
2. `roadmap.md` 给滚动窗口：已完成叶移入 `.charter/roadmap-archive.md`，Delivery order 表保留未关闭 + 最近 N 个已关闭，指针行保留计数。注意这条与 `:50` 的 append-only 编号纪律**不冲突**——编号冻结管的是编号含义，归档管的是体积，两者正交。这一点必须写进文档，否则下一个 agent 会以为归档违反 append-only。
3. `reuse-discovery.md` 给「每叶一个 section、已关闭叶的 section 在关闭时压缩成三行摘要（覆盖范围 / 结论 / 最终路线）+ 指针」，正文移 archive。
4. 在 `default-on-policy.md` 四要素里补第 5 条：**凡进入启动读集的制品必须带可判定上限**。这条让 A7 对**新**制品自动生效，而不是等下一次踩痛。

### 3.8 P1-4：全局发现没有编号，`:191` 的「所有发现必须解决」无法核对

**现象。** `:191` 要求「所有发现必须解决、降级为有明确限制的开放决定、或在批准记录中说明 waiver；未处置的发现保持项目 BLOCKED」。而发现编号 `F-01` 只在**单份 review 内**唯一（`review.md:50-52`）。跨 review 的唯一载体是 `handoff.md:44-46` 的 `Open findings:`——两行自由文本。

**违反。** A5 + A11。

**为什么这是缺陷。** 这是「规定已经立了，但判据无法被履行」的典型：要核「所有发现都处置了」，必须先能**列举**所有发现；发现没有全局编号，列举只能靠通读所有归档 review 记录——而 §3.5 刚说明这些记录连 per-ID 落盘都没有。同时 A6 禁止把自由文本当结构化字段用：`Open findings:` 两行自由文本正是「折叠」的形态。

**最小修法。** 发现编号升为项目级：`FND-001`，在 `records/index.md` 登记（ID | 叶 | 严重度 | 变更类 | 状态 | 处置 evidence）。`review.md` 的 F 行改为引用全局 ID（保留本 review 内的局部序号作辅助列）。`handoff.md:44-46` 的 `Open findings:` 改为引用全局 ID 列表，自由文本降为注释。CLS3 核这张表：无 `CLOSED / ACCEPTED_WITH_LIMITATION / DECIDED_BACKLOG` 状态的发现即阻塞关闭。

**冲突检查。** 与 `review.md` 的 P0–P3 × A/B/C 双轴不冲突——两轴是属性，不是状态；新增的是一个**处置状态**列。

### 3.9 P2-1：§12 change log 被两处引用为落点，却没有写入规则

**现象。** `project-charter.md:156` 规定 narrowing 一行 RVB 必须「recorded in the section 12 change log」；`contract-migrations.md:69` 规定 charter 级迁移「the version lands in its section 12 change log」。而 §12（`:213-217`）只有表头 `Version | Date | Change | Reason | Approved by` 和一行示例 `0.1 Initial charter`。**没有任何一句说何时必须加行、加行必须写什么、谁批准。**

**违反。** A1 + A9。

**为什么这是缺陷。** 一个被别处指定为权威落点、自己却没有写入规则的表，等于一个没有触发条件的日志。下游 agent 遇到 narrowing 时会看到「要记到 §12」然后自己发明格式——而 A9 的 `decision.md:14` 刚说过 "Do not hide a scope change inside an implementation note"，此处的等价风险是「把 narrowing 的理由塞进 Change 列一句话」。

**最小修法。** §12 增三行规则：（a）必须加行的四种情形（任何 RVB narrowing / 任何必填字段或清单项新增 / 任何 charter 级迁移 / 任何 Invariants 或 Effect boundary 修改）；（b）`Reason` 列必须写出**排除了什么**（与 `:156` 的 narrowing 纪律同款，引用不复述）；（c）`Approved by` 不得为空，无批准人则记 `UNDECIDED — <为什么可以等>`（照 `:154` 的范式）。

### 3.10 P2-2：§12 最小启动清单 8 步与循环A 15 步是同一事实的两份载体，未声明投影

**现象。** `:412-425` 的「最小启动清单」8 步与 `:26-41` 的循环A 15 步描述同一件事，粒度不同，未说明对应关系，未声明谁是权威、谁是投影。

**违反。** A12 + A9。套件自己在 `change-triage.md:33` 与 `project-charter.md:128` 立了投影纪律，对这两份清单没有执行。

**最小修法。** 二选一，写死：要么 §12 声明为「循环A 的操作投影，权威是 §1 循环A，两者不一致时以循环A为准」；要么把 §12 的八步改成引用循环A 的步骤编号。选后者更符合 A5。

### 3.11 P2-3：`:359` 的四态与关闭的两态不对齐，「未检查边界」没有承载字段

**现象。** `:359` 要求「说完成前重读目标，逐条标记**已满足 / 部分满足 / 未满足 / 未检查边界**」。关闭只认 `PASS_CLOSED` / `PARTIAL` 两个通过性状态（`:343`）。四态里「部分满足」和「未检查边界」都无法在关闭记录里表达——没有字段，没有枚举，没有模板位置。

**违反。** A6。

**最小修法。** `leaf-task.md` 的关闭段加一张目标对账表（目标条目 ID | 四态 | 证据 | 若是部分满足/未检查边界，写出边界与复查点），并在 `review.md` 加一条 check 引用它。绑定规则：出现「未检查边界」时不得选 `PASS_CLOSED`，只能 `PARTIAL` 或对应异常态——这一条把 `:359` 从描写变成门（A3）。

### 3.12 P2-4：`leaf-task.md:7` 的体积自述与实测不符

**现象。** `leaf-task.md:7` 写 "Bounded size ≤36 KB … This template is about 10 KB"。实测 15708 字节（15.3 KB）。

**违反。** A4 的 receipt discipline："a self-verification recomputes asserted values from the originals — a check that re-reads the field it certifies is not a gate"。这条自述描述了一个更旧的自己，属于 A4 明令禁止的「re-reads the field it certifies」形态。

**最小修法。** 改成不依赖具体数字的表述（如「本模板约占 36 KB 上限的 40%」）或改成 15 KB；并在 `validate_kit.py` 里加一条自述与实测的偏差检查——这是唯一一条可以机核的自述值。

### 3.13 P2-5：`:355` 禁止自建版本门禁，与 receipt 的 timestamp 并存但未区分

**现象。** `:355`「Git 是版本事实，不要另建由时间戳、内容摘要或临时指纹组成的版本门禁」。而 `evidence-receipt.md:12` 有 `Recorded at: <YYYY-MM-DDThh:mm:ssZ>`，`:16` 有 `Candidate / revision: <branch, commit, or provider revision>`。

**裁定：不构成冲突**，但缺一句说明。版本事实确实由 Git 承载——`:16` 正是 commit；`:12` 是**记录时间**不是版本标识；`:44` 的 receipt discipline 已经把版本归给 commit（"this receipt names the commit its proof describes"）。问题在于文档没有把这个区别写出来，而按 A1 的判据，不写出来的区分对下一个 agent 是不存在的。

**最小修法。** `:355` 加一句括注：timestamp 是记录时间与观测顺序，不是版本标识；版本标识只在 `Candidate / revision`。

### 3.14 P2-6：迁移机制缺两个类别（check 级与枚举级）

见 §3.4 的最小修法 2。独立列出是因为它即使不改 review.md 编号也该有——只要套件继续增加清单项与枚举值（它一直在加：RDY 到 13、RVB 到 5、CLS 若采纳到 9、CHK 若采纳到 12），迁移类别就会持续缺位。

### 3.15 P3-1：`handoff.md` 无数字上限

`handoff.md:7` 的有界规则是**结构性**的（只留活动叶 + 最近一个已关闭叶），不是数字的。结构有界优于数字有界，所以这不算缺陷；但 `charter-workflow.md:47` 把三件上限并列说成「都有数字」的语境下，读者容易以为 handoff 也有一个数字。加半句澄清即可。**此项登记，不建议改。**

---

## 4. 根因：四条，不是十五条

十五条里没有一条是「忘了写」，全部是同一个形状的重复。收敛成四条：

### 4.1 「示例即规范」

凡是一个**取值集合**只以示例行的形式出现，它的实际取值集合就是「示例值 + 作者能想到的一切」。
- §10 的 `State` 只有示例 `OPEN` → 闭合值不存在（§3.6）
- §12 的 `Version` 只有示例 `0.1` → 何时加行不存在（§3.9）
- `decision.md` 的 `Required authority` 有四个值（好），`review.md` 的 `Review type` 有三个值（好）—— 这两份做对了，恰好都是**同类文件里带枚举的**。差别不在能力，在是否把枚举写成了枚举。

对 AI 读者这一点是致命的：它照示例枚举。示例只有一个值，它就只认一个值，并且**不会报告自己发现了缺口**——因为对一个只见过 `OPEN` 的读者，`CLOSED` 不是缺失，是不存在。

### 4.2 开启面向未知，关闭面向已发生——但 A10 说关闭才是不能自报的那一侧

开启侧要穷举「未来可能缺什么」，所以做成了清单；关闭侧要核对「已经发生了什么」，所以写成了散文。这个分层直觉没错，落点反了：开启由**别人**核（审阅者、下一个 agent），关闭在现状下只能由**执行者**自己核——正好落在 `:93` 与 `:329` 明令禁止的自报区。§3.3 的 CLS 清单修的就是这个倒置。

### 4.3 上限是按踩过的痛逐个加的，不是按判据统一推的

有上限的三件都曾被点过名（`current-task.md` 36 KB、handoff 有界、lessons 64 KB），无上限的三件还没有人踩过。A7 给的理由（在启动读集里、每次 resume 都付）对六件同等成立。§3.7 的修法 4（给四要素补第 5 条「凡进启动读集必须带上限」）就是把它从逐个踩痛改成自动生效。

### 4.4 最锋利的判据文件自己没有钩子

`default-on-policy.md` 是全套件唯一一份关于「怎么定默认值」的元规则，也是唯一一份三钩全缺的制品。它缺席的直接后果就是 §3.2：主循环向所有叶收同一个价，而没人问过「普通场合是否零成本」。

---

## 5. 一句总结论

**这个套件的问题不在它规定的强度，而在它把纪律写成了「内容」而不是「结构」。**

编号、append-only、投影权威、启动读集上限——这四件事套件全想清楚了，并且用在了它最在意的四处（RDY、RVB、LS、决定与路线投影）。凡是被做成结构的地方，规矩活着；凡是还停在散文与示例的地方，规矩会漂——不是因为有人不遵守，而是因为按 A1 的原文，「没被写进会被读的那份文件」，就等于「没有被注意到」。

三个钩子缺一个，规定降级为建议。这条判据对下游项目成立，对本套件自己同样成立。

---

## 6. 修补批次

顺序按「修完之后能让后续修补不再依赖人的记性」排。

### 第一批（让判据本身有钩子，先做）
1. **P0-1** `default-on-policy.md` 三处补钩（§3.1）
2. **P0-4** `review.md` 11 条改 `CHK1–CHK11` + append-only 声明（§3.4）
3. **P2-6** 迁移机制补 check 级与枚举级两个类别（§3.14）——与 2 同批，没有它 2 落地后第一批新 check 就无迁移路径

### 第二批（关闭与开启对称）
4. **P0-3** `CLS1–CLS9` 关闭清单（§3.3）
5. **P1-4** 全局发现编号 `FND-NNN` + 处置状态（§3.8）——CLS3 的前置

### 第三批（成本与体积）
6. **P0-2** 三档路由，且必须与 `project-charter.md` §9 合并实现（§3.2）
7. **P1-3** 三件补上限 + 四要素补第 5 条（§3.7）

### 第四批（记录落盘与权威）
8. **P1-1** per-event 记录落盘规则 + 工作集清单（§3.5）——波及 bootstrap 与五份 prompt，单独一批，改完必须重跑校验器
9. **P1-2** 三套决策登记册的权威与投影（§3.6）

### 第五批（补齐小口）
10. **P2-1 / P2-2 / P2-3 / P2-4 / P2-5**（§3.9–§3.13）
11. **P3-1** 登记不改（§3.15）

### 每批的共同验收
- `python scripts/validate_kit.py .` → `PASS (235 files checked)`，12 项子检查全绿；
- 改动落在 `portable/` 与 `DEVELOPMENT_CHARTER.md`（手工源），**不直接改 `skills/charter-workflow/`**（生成物，会被重建覆盖）；
- 五份 bootstrap prompt 保持字节一致；
- 每批改动同时给 §12 change log 加行（P2-1 落地后即适用）。

---

## 7. 这次自审能查出什么，查不出什么

**能查出的：** 结构性的东西——三钩的有无、取值集合是否被写成枚举、编号是否冻结、上限是否存在、同一事实有几个载体、规定与记录是否对称。这些都能从原文逐条核，且结论不依赖我读了多少外部项目。

**查不出的三类：**

1. **读起来顺不顺。** 三钩模型对此没有意见。一份组织混乱但三钩齐备的文档在本次审计里是「活」的——对 AI 读者这个判定成立，对人读者未必。本项目已经明确「是给 AI 用的，不是给人类用的」，所以这里按可判定性优先。
2. **要不要这么多机制。** 十五条全修完，套件比现在更重。`:410`「连续两次成为主要工作就暂停加机制」与 `:425`「治理系统不应比产品本身更复杂」随时可以叫停这批修补——而且按 A8，**叫停是合法的**，不叫停才需要论证。这不是免责声明，这是第 4 把尺子对本次审计本身的要求：本审计的产出也是一批新增机制，它必须先过自己那一关。
3. **真实项目里的效用。** `validate_kit.py` 只校验套件自身一致性（镜像字节、模板、契约字段、manifest），不校验下游叶执行质量。这一层只能靠真实项目，套件自己已经说过了（`:425`）。

---

## 8. 复核方式

```bash
# 在本仓库根（含 scripts/ 与 portable/ 的那一层）执行
python scripts/validate_kit.py .          # 无 --check 参数，期望 PASS (235 files checked)
```

原文核对（本文所有行号指向的都是这些文件）：

| 文件 | 行数 / 字节 |
|---|---|
| `DEVELOPMENT_CHARTER.md` | 425 行 |
| `portable/commands/charter-workflow.md` | 54 行 / 13789 字节 |
| `portable/references/contract-migrations.md` | 112 行 |
| `portable/references/change-triage.md` | 36 行 |
| `portable/references/default-on-policy.md` | 46 行 |
| `portable/references/design-interview.md` | 50 行 |
| `portable/references/lessons.md` | 71 行 |
| `portable/templates/leaf-task.md` | 256 行 / 15708 字节 |
| `portable/templates/project-charter.md` | 217 行 |
| `portable/templates/roadmap.md` | 82 行 |
| `portable/templates/review.md` | 82 行 |
| `portable/templates/evidence-receipt.md` | 63 行 |
| `portable/templates/decision.md` | 53 行 |
| `portable/templates/handoff.md` | 99 行 |
| `portable/templates/reuse-discovery.md` | 92 行 |
| `portable/prompts/*-bootstrap.md` | 五份，各 13504 字节 |

本文档本身不在 `validate_kit.py` 的扫描范围（`docs/` 不被 `check_tests_and_docs()` 与 `check_domain_neutrality` 覆盖），因此新增它不影响校验结果；但它一旦被引用为下游行为依据，就自动受第 1 把尺子约束——**必须落在某个步骤会读的地方，否则它就是下一份 `default-on-policy.md`。**

---

## 9. 执行日志（按批追加，只增不改）

用户 m00600 在 18 条面板上逐条裁决：做 14、不做 2（P1-3、P3-1）、待定 2（P0-2、P1-1）。
每一批改完必须在这里留一行，并附 `validate_kit.py` 的结果。

### 批 1 —— 完成（2026-10-19）

范围：P0-1 钩子缺失、P0-4 编号未冻结、P2-6 迁移补 check/enum 级。

| 改动 | 文件 | 内容 |
| --- | --- | --- |
| P0-1 | `portable/references/default-on-policy.md` | 新增 `## Hooks`，把策略自己的三个钩子写成 `DOP1` 起草读、`DOP2` 迁移前置、`DOP3` 审阅检查；声明只增不改 |
| P0-1 | `DEVELOPMENT_CHARTER.md` §2.8 | 自审清单加第九条「默认值是否可见」，指名 `default-on-policy.md` |
| P0-4 | `portable/templates/review.md` | 十一条检查加 `CHK1`-`CHK11`，声明编号只增不改、不适用记 `N/A` 不删除 |
| P0-1 | `portable/templates/review.md` | 新增 `CHK12`，引 `DOP3` |
| P2-6 | `portable/references/contract-migrations.md` | `## Steps` 前加两条前置（成员类别、默认值落地）；新增 `## Check-level and enum-level additions`，含 `CHK12` 与 `control.py controller` 两行，并说明枚举扩展不等于改名 |

镜像：上述四个文件同步到 `targets/codex/skills/charter-workflow/` 与 `targets/zcode/skills/charter-workflow/`；再跑 codex → zcode → dsh 三个构建器 `--sync`，根 `skills/charter-workflow/` 与三个 `plugins/` 由生成器刷新，未手改生成物。

校验：`python scripts/validate_kit.py .` → PASS (235 files checked)，11 项子检查全绿，exit 0。

### 批 2 —— 完成（2026-10-19）

范围：P0-3 关闭清单、P1-4 发现处置。判据自 m00737 起改为 **稳定性优先**：任何减少治理覆盖的改动不入批，因此 P1-4 从「新建全局 `FND-NNN` 编号空间」改判为「复合句柄 + 处置列」。

| 改动 | 文件 | 内容 |
| --- | --- | --- |
| P0-3 | `portable/templates/leaf-task.md` | §9 新增 `### Closure checklist`：`CLS1`-`CLS9` 九行，每行必须作答，不适用记 `N/A` 加理由，空行等于未关闭；声明 `CLS` 编号只增不改、id 永不移位也永不消失；并写明 `CLS3` 不等于「没有发现」、`CLS9` 最后答，上方空行使关闭动作「过早」而非「可选」 |
| P0-3 | `portable/templates/leaf-task.md` | `Contract version` 由 `0.2` 升 `0.3` |
| P1-4 | `portable/templates/review.md` | `## Findings` 表加 `Disposition` 列（`CLOSED` / `ACCEPTED_WITH_LIMITATION` / `DECIDED_BACKLOG` / `OPEN`）；写明空白不算处置、`OPEN` 只能与 `REQUEST_CHANGES` / `BLOCKED_TOOLING` / `NEEDS_DECISION` 同时出现、非 `CLOSED` 必须在同一提交写进 `project.md` §10 或 `decision.md` |
| P1-4 | `portable/templates/review.md` | 新增 `CHK13`：每个发现都有处置，非 `CLOSED` 的必须写明限制、到期或复查触发、以及承载它的条目 |
| P1-4 | `portable/references/contract-migrations.md` | `## Fields added after 0.1` 加 `Closure checklist` 行并注明随 `0.3` 模板；`### Checks` 加 `CHK13` 行；补一句 `0.2` 合同迁移时九行一次性补齐 |

为什么 P1-4 不建 `FND-NNN`：本套件没有运行时（`default-on-policy.md`：「There is no runtime」），而全局顺序号必须有中央分配器才不撞号——本套件恰好没有分配器。改用一个发现的天然复合句柄 `<REV-ID>/F-NN`：两半都不复用，结构上不可能撞，也不需要谁来发号。

镜像与构建：三个文件同步到 `targets/codex/skills/charter-workflow/` 与 `targets/zcode/skills/charter-workflow/`；再跑 codex → zcode → dsh 三个构建器 `--sync`。

校验：`python scripts/validate_kit.py .` → PASS (235 files checked)，11 项子检查全绿，exit 0；`python -m pytest tests -q` → 271 passed, 511 subtests passed。

`portable/templates/leaf-task.md` 现为 17,512 字节；`validate_kit.py` 的模板上限断言是「不超过 36 KB 的一半」即 18,432 字节，余量约 920 字节——后续再往该模板加内容前必须先腾位置。

### 批 2b —— 完成（2026-10-19）

范围：P2-3、P2-4、P2-5 —— 用户已批准、且全部属于纯增或纯修正的条目，稳定性判据下无冲突，因此在等待 P0-2 / P1-1 裁决期间先落地。

| 改动 | 文件 | 内容 |
| --- | --- | --- |
| P2-3 | `DEVELOPMENT_CHARTER.md` §5 状态机 | 异常状态段后加：每个异常状态是记录事件不是标签，进入时必须在 Events 表写承载记录（谁判定、卡在什么、解封条件、复查时间或授权引用），`PARTIAL` 还要点名哪条要求开着；只有状态名没有承载记录，读取时等同于该状态没有发生 |
| P2-3 | `DEVELOPMENT_CHARTER.md` §6.3 | 「未检查」的边界不计入已满足，也不能由 `PASS_CLOSED` 收尾；关闭前要么转成已检查，要么写进 `project.md` §10 并带复查触发 |
| P2-5 | `DEVELOPMENT_CHARTER.md` §6.2 | 追加：时间戳不是版本标识，它记录事件何时发生（Events 的 `Time` 列），不能判定两个候选是否同一版本；摘要只能证明两个对象相同，不能证明哪一个是当时被审阅的那个 |
| P2-4 | `portable/templates/leaf-task.md` §0 | 删掉自述里会漂的实测值「This template is about 10 KB」，改成判据「stays under half that ceiling」 |
| P2-4 | `scripts/validate_kit.py` | 同步把 :124 注释里的同一个实测值改成判据，避免判据的注释本身开始漂 |

镜像与构建：`leaf-task.md` 同步到两个 target 树，`DEVELOPMENT_CHARTER.md` 同步到根 `skills/` 与两个 target 树的 `references/`；再跑 codex → zcode → dsh `--sync`。

校验：`python scripts/validate_kit.py .` → PASS (235 files checked)，11 项全绿，exit 0；`python -m pytest tests -q` → 271 passed, 511 subtests passed。

余量：`portable/templates/leaf-task.md` 现为 17,538 字节，模板上限 18,432，余量 894 字节。后续往该模板加任何内容（例如 AC 编号机制）之前必须先腾位置：把 `Closure checklist` 的问题文字外移到 `portable/references/`，模板里只留 id 与列结构。

### 批 3 —— 完成（2026-10-19）

范围：P1-2（决策登记册定权威）、P1-6（与 P1-2 合并）、P1-3（按 m00843 改判为「成长形态 + 扇出触发」）、P0-2（正式撤回，不落地）。

P1-3 原判「三件无上限」被用户驳回：绝对字节上限对超大项目必然失守，失守之后内容被砍就是丢信息。改判后的判据不设字节，设成长形态与扇出触发——读集只允许**实体型**增长（一行一个活实体），**历史型**增长（一行一次事件）一律进档案；实体型不设上限，但单文件超过 60 个实体行、或单父节点超过 12 行时必须拆成索引 + 分支文件。读集体积因此约等于「索引 + 当前活跃分支」，与项目总规模无关。

| 改动 | 文件 | 内容 |
| --- | --- | --- |
| P1-2 | `portable/templates/project-charter.md` §10 | 声明该表是「问题是否仍未决」的唯一权威，`decision.md` 只存需要完整记录的那次决定的正文，roadmap 的 route 表是投影，两者都不判定开放与否 |
| P1-2 | `portable/templates/project-charter.md` §10 | `State` 由只出现一个示例值 `OPEN` 改成五态枚举表（`OPEN` / `DECIDED` / `DEFERRED` / `REJECTED` / `EXPIRED`），每态写明「这一行还必须携带什么」；没有承载字段的状态按 `OPEN` 读 |
| P1-2 | `portable/templates/project-charter.md` §10 | 把批 2 的 `CHK13` 接到本表：`ACCEPTED_WITH_LIMITATION` → `DECIDED`（带限制与到期/复查），`DECIDED_BACKLOG` → `DEFERRED`（带复查触发） |
| P1-6 | `portable/templates/project-charter.md` §10 | 读集止血：`OPEN` / `DEFERRED` / `REJECTED` 是活行必须留在表里（「一个 agent 看不见的否决，就是它会重新提一遍的否决」）；`DECIDED` 行只有在 `decision.md` 完整承载该决定之后才移出，且只能移不能删，留一行 id + 一句结论 + 记录引用 |
| P1-6 | `portable/templates/decision.md` | `Status` 由 `OPEN | APPROVED | REJECTED | EXPIRED` 改为 `OPEN | DECIDED | REJECTED | EXPIRED`，并写明 `DEFERRED` 只在 §10 存在（停在 §10 的问题还没有资格成为决定记录） |
| P1-3 | `DEVELOPMENT_CHARTER.md` §7 | 新增读集增长规则：实体型 vs 历史型、历史型不进读集、扇出触发（60 / 12）、判据用行数不用字节、拆分不是删除 |
| P1-3 | `portable/templates/roadmap.md` | 首段加 `Growth` 说明，指向 §7 的扇出触发——roadmap 是读集里最大的实体表，也是第一个会撞触发的文件 |
| P1-3 | `portable/references/contract-migrations.md` | 新增 `### Renamed members` 表并记录 `APPROVED → DECIDED` 这次改名（旧名对归档记录仍有意义，永不复用），理由写明「一个状态两个词是 agent 会静默解决的漂移」 |

> 更正（2026-10-19，用户裁决「把 P1-3 回滚回去」）：上表前两行已回滚——`DEVELOPMENT_CHARTER.md` §7 的读集增长规则与 `roadmap.md` 的 `Growth` 引线均已删除，`project-charter.md` §10 末尾那句指向 §7 活实体规则的话也一并删掉（它随规则一起失去所指）。第三行保留：`### Renamed members` 记录的是 `P1-2` 的 `APPROVED → DECIDED` 改名，它服务迁移可读性，不是 `P1-3` 的产物。详见 §9.11。

为什么 `DECIDED` 而不是继续用 `APPROVED`：`project.md` §10 是「问题是否仍未决」的唯一权威，而 `decision.md` 写 `APPROVED`、§10 写 `OPEN`，等于同一个状态在启动读集的两个位置有两个词。批 1 的教训是「示例即规范」——只以示例行出现的取值集合，对没见过别的取值的读者不是缺失而是不存在；这次把两份文档收成一套词。

镜像与构建：`project-charter.md`、`roadmap.md`、`decision.md` 同步到两个 target 树的 `templates/`；`DEVELOPMENT_CHARTER.md` 同步到两份 target 的 `references/`；`contract-migrations.md` 同步到两个 target 树的 `references/`；再跑 codex → zcode → dsh 三个构建器 `--sync`。

校验：`python scripts/validate_kit.py .` → PASS (235 files checked)，11 项全绿，exit 0；`python -m pytest tests -q` → 271 passed, 511 subtests passed。

### 批 4 —— 完成（2026-10-19）

范围：P1-5 —— 章程变更史移出启动读集。

病灶是字幕第三段那条：文档里同时写着「原来是 A，某个时间点改成了 B」，AI 上下文一长就只捡到 A，于是把 B 改回 A。`project.md` 里的 §12 change log 正是这个形状，而 `project.md` 是启动读集第一件——当前值与废弃值在同一文件、同一次 resume 一起进上下文。

| 改动 | 文件 | 内容 |
| --- | --- | --- |
| P1-5 | `portable/templates/changelog.md` | 新建。版本史独立成文件，明写「不在 resume 读集里」「不得在 `project.md` 复述」，四类规则：一行一个版本、行不改只追加、`Change` 说动了什么 `Reason` 说为什么、取代某决定的行必须记该决定 id；`## Growth` 说明这是 `.charter/` 里唯一预期无界增长的文件，过大时按大版本拆 `changelog-v<N>.md` 且只许移动不许删除 |
| P1-5 | `portable/templates/project-charter.md` §12 | 表格换成指针段落：历史在 `.charter/changelog.md`，本文件只保留当前版本（§1 的 `Charter version`），并写明理由——resume 读的是当前状态，把两者放在一起正是让废弃值被读成当前值的方式 |
| P1-5 | `portable/commands/charter-workflow.md` 与五份 bootstrap prompt | 引导清单加入 `changelog.md`，并明写它是历史、不进 resume 读集，其余每一件都要读 |
| P1-5 | `targets/zcode/commands/charter-workflow.md` | 同一句同步（该文件是 LF 的宿主变体，比 portable 版多一行 `skills: charter-workflow`） |
| P1-5 | `scripts/init_project.py` | `FILES` 加 `changelog.md`，新项目建集时一并生成 |
| P1-5 | `scripts/validate_kit.py` | `PORTABLE_TEMPLATES` 加新模板条目，让新文件也进标题断言，而不是只进镜像比对 |
| P1-5 | `portable/references/contract-migrations.md` | 章程级迁移表加一行（把 §12 表原样搬到 `.charter/changelog.md` 再留指针）；并把「章程没有 Contract version 可 bump，版本落在 §12」改指向新文件 |

五份 bootstrap prompt 改后仍是同一条规范句、字节完全一致（sha256 前 16 位同为 `cccb916fc4199245`），这是套件对 prompt 一致性的既有断言。

校验：`python scripts/validate_kit.py .` → PASS (240 files checked)，11 项全绿，exit 0。文件数由 235 升到 240 是新增模板在 portable、两个 target 树和三个分发目录各自的副本。

### 批 5 —— 完成（AC 编号部分，2026-10-19）

范围：AC 编号（稳定性判据下新增的 P0）。P1-1 未做，移入批 6。

病灶：§5 的验收项是无编号散文，`leaf-task.md` 后面那套「检查必须能移动退出码」的纪律与它没有任何强制对应——五条验收只做两条，流程里没有任何东西会发现。

| 改动 | 文件 | 内容 |
| --- | --- | --- |
| AC 编号 | `portable/templates/leaf-task.md` §5 | 新增 `### Acceptance items`：每项编号 `AC1`/`AC2`…，id 只创建一次、永不重编号/重划范围/复用，撤回的项保留 id 并写撤回理由（与 `RDY`、`CLS` 同一套冻结规则） |
| AC 编号 | `portable/templates/leaf-task.md` §5 | 每个 `AC` 必须写明「这一项为假时能移动退出码的检查」——命令、测试 id 或断言——否则记 `N/A` 加不能检查的理由；两样都没有的项是愿望不是验收项。§9 关闭时逐项对着那个检查确认 |
| AC 编号 | `portable/templates/leaf-task.md` §1 | `Contract version` 由 `0.3` 升 `0.4` |
| AC 编号 | `portable/references/contract-migrations.md` | `## Fields added after 0.1` 加一行；正文补一句：旧合同在原地给既有条目编号，某项的检查跑不了就记 `N/A` 加理由，不是把这一项删掉 |

校验：`python scripts/validate_kit.py .` → PASS (240 files checked)，11 项全绿，exit 0；`python -m pytest tests -q` → 271 passed, 519 subtests passed（较批 3 多 8 个 subtest，来自新模板的标题断言）。

余量：`portable/templates/leaf-task.md` 现为 18,095 字节，模板上限 18,432，余量 337 字节。该模板再加内容前必须先外移一段文字，否则超限。

### 批次重排（自 m00737 稳定性判据起生效）

| 批 | 内容 | 状态 |
| --- | --- | --- |
| 1 | P0-1、P0-4、P2-6 | 完成 |
| 2 | P0-3、P1-4 | 完成 |
| 2b | P2-3、P2-4、P2-5 | 完成 |
| 3 | P1-2、P1-6、P1-3（改判）、P0-2（撤回） | 完成 |

> 更正：批 3 的 `P1-3`（改判）已于 2026-10-19 按用户裁决回滚，见 §9.11；批 3 其余两项（`P1-2`、`P1-6`）不受影响，`P0-2` 仍是撤回状态。
| 4 | P1-5（§12 change log 移出 `project.md` 读集） | 完成 |
| 5 | AC 编号（验收项 → 可移动退出码的检查） | 完成 |
| 6 | P1-1 作用域 ID、P2-1、P2-2、P2-7 | 待做 |
| — | P3-1 | 不做（handoff 结构性有界已是最好形态） |

P1-1 在稳定性判据下只剩两件事：叶合同 §8 的 `E-01` 与项目级证据 ID 撞号（`leaf-task.md` 明写 ids are single-use），以及单文件证据在第二片叶出现时只能覆盖或无限追加。作用域 ID（`E-<task>-<nn>`）解前者，per-ID 落盘解后者；索引与成本动机全部去掉。

未落地的两条 P0 仍开着，是最接近「AI 跑偏」的口子：① 验收项 `AC1`-`ACn` 编号且每项必须指向一个能移动退出码的检查（现状 §5 是无编号散文，与 §6 的检查纪律没有强制对应，五条验收只做两条也没有任何东西会发现）；② 套件本体不受自己的治理管——仓库根没有 `.charter/`，批 1 到批 3 的改动都没走叶合同、Review A 或收据。

## 9.5 批 5b —— 合同上限的理由修正（完成）

起因：作者问「这个 leaf-task 的上限是什么东西，哪来的」。核查结果——`scripts/validate_kit.py:133` 的 `LEAF_CONTRACT_CEILING_KB = 36` 无外部来源，是套件自定值；机器执行的只有一条：模板不得超上限的一半（18,432 字节，`:1657-1668`）。真实项目的 `.charter/current-task.md` 有没有超限，没有任何东西核。

由此暴露一个前提错误：原文字把上限的理由写成成本论证（「Every resume re-reads this contract, so its length is paid by every later actor」）。按 m00843 的判据，字节数不能当判据用——超大项目必失守。合同之所以仍可设上限，理由不是成本而是**设计**：合同大小不随项目规模增长，它由「一片叶能做多少」定；装不下通常意味着这已经不是一片叶，或者吸收了本该属于读集里别的文件的材料。

| 改动 | 位置 | 内容 |
| --- | --- | --- |
| 理由改写 | `portable/templates/leaf-task.md` §0 | 保留成本事实作为次要说明，把判定权交给设计读法：「a contract that needs more than this has almost always absorbed material that belongs to a file already in the read set, or it is more than one leaf」；并把外移方向与「若别处都放不下，该切的是结果句」写成同一段的两个分支 |
| 超限出口 | 同上 | 补「Past the bound, record a Ruling that says why this leaf needs it and what you gave up」——超限不再是静默违规，而是一个必须留痕并被定价的决定；抬数字须点名改到每一份声明它的文档 |
| 入口文档理由对齐 | `portable/commands/charter-workflow.md`、五份 bootstrap prompt、`targets/zcode/commands/charter-workflow.md`、三份 `SKILL.md` | 同一句末尾补「and for the contract the bound also carries a design reading: a contract that needs more than it is usually more than one leaf」，消除「读集上限讲成长形态、合同上限讲字节成本」的双口径 |

校验：`python scripts/validate_kit.py .` → PASS (240 files checked)，11 项全绿，exit 0；`python -m pytest tests -q` → 271 passed, 519 subtests passed。

余量更新：`portable/templates/leaf-task.md` 现 18,250 字节，上限 18,432，余量 182 字节（批 5 一节记的 337 已不成立）。

更正上文：批 5 一节末尾所列「未落地的两条 P0」中，第 ① 条（验收项 `AC1`-`ACn` 编号且每项指向能移动退出码的检查）已在批 5 落地。未落地的只剩第 ② 条：套件本体不受自己的治理管。

未决：抬不抬 36 KB 这个数字本身。抬需协调十处声明（模板、入口命令、五份 prompt、zcode 变体、三份 `SKILL.md`、校验器常量、测试常量）；不抬则批 6 的 P1-1 必须先外移现有一段文字。当前选择不抬，先靠外移腾空间。

## 9.6 批 6 —— 完成（P1-1、P2-1、P2-2、P2-7）

> 追认（2026-10-20）：本批的 ¬P1-1¬ 在 YG 的 18 条裁决里是「待定」，由我判做并落地，属偏离裁决。YG 于 m03465 追认：『留着吧，就按照这15条来』。口径与记账缺口见 §9.12。


四项全部落地。判据仍是 m00737 的稳定性：作用域 ID 解撞号与覆盖销毁，不加索引、不谈成本。

### 改了哪些文件、每一处解决什么

| 项 | 文件 | 改动 |
| --- | --- | --- |
| P1-1 | `portable/templates/evidence-receipt.md` | `Evidence ID` 由 `<E-ID>` 改为 `E-<TASK-ID>-<nn>`；引句后补一段：每份收据是 `.charter/records/<Evidence ID>.md` 一个文件，永不追加进共享文件、永不覆盖，并写明 id 按产生它的任务定作用域，因此不需要中央分配器 |
| P1-1 | `portable/templates/review.md` | `Review ID` 改为 `REV-<TASK-ID>-<nn>`；身份段后补一段：id 按被审任务定作用域，同一片叶的第二次审阅是新文件而不是覆盖上一份 |
| P1-1 | `portable/templates/decision.md` | `Decision ID` 改为 `DEC-<YYYYMMDD>-<slug>`；并写明这是**项目作用域而非叶作用域**——两个叶可能在同一会话里各开一个决定，按叶编号必撞，日期加 slug 不需要分配器；每份决定一个文件 |
| P1-1 | `portable/templates/leaf-task.md` §8 | 示例 ID 改 `E-<TASK-ID>-01`；表后补一句规则：id 按本合同的 Task ID 定作用域（裸 `E-01` 跨叶必撞），每份收据是 `.charter/records/<ID>.md` 一个文件，本表只是索引 |
| P1-1 | `portable/commands/charter-workflow.md` 第 1 步、`targets/zcode/commands/charter-workflow.md`、五份 `portable/prompts/*-bootstrap.md` | 引导清单在 `evidence/` 之外补 `records/`，并说明它装的是「一份收据/审阅/决定一个文件、按 id 命名」 |
| P1-1 | 三份 `SKILL.md` | 初始化段由「copy the nine files」改为「copy the ten files」，并写明初始化要建 `.charter/evidence/` 与 `.charter/records/` |
| P1-1 | `scripts/init_project.py` | 建 `.charter/records/`；`validate_destinations` 对 links 与非目录同 `evidence/` 一样拒绝；模块 docstring 写明为什么要这个目录（写进共享文件的记录不是覆盖上一份，就是长成没人读的文件） |
| P1-1 | `portable/references/contract-migrations.md` | 新增 `## Record-level migrations` 一节：三份记录的新形状表，加两条合法收尾（同一提交改名并更新每一处引用，或历史记录原样保留、新记录起用新形状），并点名唯一不合法的是「继续往共享文件追加」 |
| P2-1 | `portable/templates/changelog.md` | 新增 `## When a row is required`：四种必须加行的情形（收窄 `RVB1`-`RVB5` 或任何风险触发、新增必填合同字段或清单项、charter 级迁移、改动 `Invariants` 或效果边界）；`Reason` 必须写出排除了什么；`Approved by` 不得为空，未批准记 `UNDECIDED - <为什么等不了>` |
| P2-2 | `DEVELOPMENT_CHARTER.md` 循环 A | 十四步加冻结编号 `LA1`-`LA14`，并写明只增不改、id 永不移位改指；引用写编号加短标签 |
| P2-2 | `DEVELOPMENT_CHARTER.md` §12 | 声明本节是循环 A 的操作投影、不进第二套流程、不一致时以循环 A 为准；八步各自前缀对应 `LA` 编号（第 8 步标为循环 B，不在循环 A 内） |
| P2-7 | `DEVELOPMENT_CHARTER.md` §7 | 读集增长规则后补人可读下限：需要人授权才能继续的记录必须用一句话说明要决定什么，不得只用代码块/枚举/缩写；未定义技术名词首次出现须给定义或指向定义处；只约束新增文字 |

### 校验器新增的钩子（P1-1 的规则不能只写在模板里）

`scripts/validate_kit.py` 新增三组断言：`review.md` 必须含 `` `REV-<TASK-ID>-<nn>` `` 与 `` `.charter/records/<Review ID>.md` ``；`evidence-receipt.md` 必须含 `` `E-<TASK-ID>-<nn>` `` 与 `` `.charter/records/<Evidence ID>.md` ``；`decision.md` 必须含 `` `DEC-<YYYYMMDD>-<slug>` `` 与 `` `.charter/records/<Decision ID>.md` ``。另加一条入口断言：`portable/commands/charter-workflow.md` 与五份 prompt 必须含 `records/`——引导路径不建这个目录，规则就无处落地。

### 顺手改正的一处自述失真（A4 类）

`tests/test_workflow_contract.py::test_entry_documents_wire_the_lessons_layer` 原本硬编码断言 `SKILL.md` 里有「nine templates / nine files」。批 4 增加 `changelog.md` 后工作集已是十件，`SKILL.md` 的自述却还写 nine，测试两个月来一直在保护那个过期句子。改法不是把数字改一遍，而是把数字变成推导出来的：模板数用 `portable/templates/*.md` 计数，工作集件数用 `ast` 读 `scripts/init_project.py` 的 `FILES` 键数，文档里的英文数词由 `WORD_NUMBERS` 表给出。下次工作集再变，测试会在文档还写旧数时失败并点名，而不是替它继续背书。

### 校验

`python scripts/validate_kit.py .` → PASS (246 files checked)，11 项子检查全绿，exit 0。
`python -m pytest tests -q` → 271 passed, 519 subtests passed（134.28s）。

文件数由 240 涨到 246 的原因：`changelog.md` 是批 4 新增的模板，它在本轮 `--sync` 后才第一次出现在三个分发包里（每个包两份），校验器按分发树计数，所以是数字反映了新增文件而不是新增了规则。

### 尺寸（均为字节，镜像已同步）

| 文件 | 现尺寸 | 备注 |
| --- | --- | --- |
| `portable/templates/leaf-task.md` | 18,366 | 上限 18,432，余量 66。为容纳 §8 新规则，就地压缩了三处：`CLS` 前言段、`CLS` 收尾段、§0 的 Bounded size 段 |
> **更正（`REV-CHARTER-13`，点名被更正行）**：上一行记的 `18,366` 是当时工作树的读数，不是现在的值；叶模板体积的权威落点是 `.charter/evidence/template-budget-2026-10-19.txt`。本文件是历史审计日志，按 A 类惯例原行不改、更正行在此。
| `portable/templates/review.md` | 6,908 | |
| `portable/templates/evidence-receipt.md` | 3,213 | |
| `portable/templates/decision.md` | 2,337 | |
| `portable/templates/changelog.md` | 2,668 | |
| `portable/references/contract-migrations.md` | 12,935 | |
| `DEVELOPMENT_CHARTER.md` | 36,165 | |
| `portable/commands/charter-workflow.md` | 14,149 | |
| `targets/zcode/commands/charter-workflow.md` | 14,175 | |
| 五份 `portable/prompts/*-bootstrap.md` | 13,753 各 | 五份仍字节一致 |
| 三份 `SKILL.md` | 18,755 各 | |
| `scripts/validate_kit.py` | 140,272 | |
| `scripts/init_project.py` | 16,347 | |

### 批 6 之后的余账

m00600 裁决的 14 条**全部完成**（批 1、2、2b、3、4、5、5b、6）。判不做的两条（P1-3 已改判为做、P3-1 仍不做）与撤回的一条（P0-2）见上文。仍然开着的只有一条，且它不在这次裁决里：**套件本体不受自己的治理管**——仓库根没有 `.charter/`，批 1 到批 6 的改动都没有走叶合同、Review A 或收据。这不是缺一条规则，而是这套东西能不能对自己用一次的证明；要做，最小形态是拿批 6 本身当第一片叶，补一份叶合同与一份收据，不重做已完成的改动。

另一个未决仍是 36 KB 那个数字：本轮选择不抬，靠就地压缩腾出 66 字节。下一次再往 `leaf-task.md` 加内容就必须先外移，或者正式抬高上限（需同时改模板、入口命令、五份 prompt、zcode 变体、三份 `SKILL.md`、校验器常量与测试常量）。

## 9.7 发布整理（提交前）

两件事在提交前做了，都属于「记录不能自述失真」这一条。

**版本号统一到 `0.6.0`。** 提交前五个载体停在两个不同的数上：`.claude-plugin/marketplace.json`、`.claude-plugin/plugin.json`、`targets/codex/.codex-plugin/plugin.json`、`targets/zcode/.zcode-plugin/plugin.json` 是 `0.3.0`，`targets/dsh/package.json` 是 `0.5.0`。同一次改动在两个宿主上自称不同版本，正是这套东西一直在治的那类漂移。全部改为 `0.6.0`，`tests/test_dsh_target.py` 的方法名与断言同步改为 `0_6_0`，生成的 `plugins/*` 与根 `.codex-plugin/plugin.json` 由 `--sync` 刷新。选主版本号而不是小节号：叶合同 `Contract version` 由 `0.2` 走到 `0.4`，记录 ID 形状与 `records/` 目录对下游都是破坏性变更。

**三个审阅面板删除。** `docs/.panel.html`、`docs/.panel.data.json`、`docs/.panel.input.html` 是这次审阅时生成的一次性界面与它的数据副本；判定结果在 §2、§3、§9 里已有正式版本，留着只会变成要维护的第二份投影。`.gitignore` 增加 `docs/.panel*`，让下一次审阅的同类产物默认不进版本库。

校验：`python scripts/validate_kit.py .` → PASS (246 files checked)，11 项全绿，exit 0；`python -m pytest tests -q` → 271 passed, 519 subtests passed。

提交形状：两个提交——先是 `docs/` 下五份分析文档（本套件自身不是受治理项目，这些文档就是这批改动的叶记录），再是源码、模板、镜像与三个分发包。逐批历史没有保留，原因见 §9.6 末尾：六个批次都动过 `leaf-task.md`，事后按 hunk 拆出来的只是像历史的东西；可信的分批账在本节之上。

## 9.8 批 7 —— 独立审阅与跨文件一致性测试

### 为什么补

§9 之前的每一批都跑过校验器和全量 pytest，但**14 条新规则没有换来一个用例**。提交里唯一的测试改动是把硬编码工作集件数的旧断言改成从源推导（见 §9.6）。机器侧实际只有 `validate_kit.py` 的短语存在性断言：它能挡住「这句话被删掉了」，挡不住「同一个规则的两处说法不一致」。举证很容易——`CHK1`–`CHK13` 只活在 `portable/templates/review.md`，`portable/references/contract-migrations.md` 的检查级迁移表只列了 `CHK12`、`CHK13`，而没有任何断言保证两处对齐；编号在一边被重排、记录形状在迁移表里承诺而模板不带，全都能一直绿着。

审阅侧同样没有发生过：本套件自己要求 Review A 使用独立上下文，而批 1 到批 6 全是同一上下文的自我复检。证据是批 5 压缩时删掉过三个**唯一落点**（章程已批准的前置勾选、收据纪律指针的落点、ledger 事件名），`validate_kit.py` 与全量 pytest 全绿，是逐 hunk 复查才发现的。

### 新增 `tests/test_absorption_contract.py`

16 个用例、6 个测试类，判据是**每一条都从仓库另一侧重算**，不重述字面量，所以内容合法变化时不误报。

| 类 | 守的是什么 | 重算自 |
| --- | --- | --- |
| `ReviewCheckIds` | `CHK` 编号连续、无重号；任何文件引用的 `CHK` 都必须在 `review.md` 里被声明；迁移表点名的 `CHK` 也必须是已声明的 | `review.md` 的检查行 + 全 `portable/` 与 `DEVELOPMENT_CHARTER.md` 的引用 |
| `ClosureChecklist` | `CLS1`–`CLS9` 连续；每行都必须是未作答模板（`<answer>` 与 `<raw ref>` 两个槽）；跨文件引用的 `CLS` 必须已声明 | `leaf-task.md` 的 `CLS` 行 |
| `AcceptanceItems` | `AC` 编号连续；每个验收项必须带 `check:` 槽 | `leaf-task.md` 的 `AC` 行 |
| `RecordScoping` | 迁移表承诺的记录 ID 形状必须真的出现在对应模板里，且模板必须写明记录落到 `.charter/records/`；把未加作用域的 `E-01`／`REV-01` 当指令用会红（只允许作为反例出现在含 `bare` 的行里） | `contract-migrations.md` 的记录级迁移表 |
| `ReadSetAndHistory` | `changelog.md` 必须被创建且不得进 resume 读集；读集必须是工作集的子集；`init_project.py` 必须创建工作集里的每一件；`project-charter.md` §12 只许是指针，出现版本行即红 | `charter-workflow.md` 的两行 + `init_project.py` 的 `FILES` |
| `DefaultOnHooks` | 每个 `DOP` 钩子点名的落点文件必须存在、点名的锚点（`## Steps`、`CHK12`）必须真的在该文件里；任何文件引用的 `DOP` 必须已被声明 | `default-on-policy.md` 的钩子表 |

### 十一条反向对照（证明这些门真的能移动退出码）

拿判据改一处再跑，逐个确认会红。全部 11 条都被抓住，改完即还原：

| 篡改 | 结果 |
| --- | --- |
| `review.md` 把 `CHK13` 改成 `CHK14` | 3 failed |
| 迁移表把 `CHK13` 改成 `CHK17` | 2 failed |
| `leaf-task.md` 把 `CLS9` 改成 `CLS11` | 2 failed |
| 给 `CLS2` 预先填好答案 | 1 failed |
| 删掉 `AC2` 的 `check:` 槽 | 1 failed |
| 迁移表把 `REV-<TASK-ID>-<nn>` 改成 `REV-<NN>` | 1 failed |
| 把 `changelog.md` 塞进 resume 读集那一行 | 1 failed |
| 在 §12 恢复一张版本表 | 1 failed |
| 钩子落点从 `CHK12` 改成 `CHK99` | 2 failed |
| `review.md` 把 `DOP3` 改成 `DOP9` | 1 failed |
| `init_project.py` 的 `FILES` 删掉 `changelog.md` | 1 failed |

### 反向对照抓出的两个真实缺陷

**一个是我自己写的测试里的。** 第一轮反向对照里「把 `changelog.md` 塞进读集」这条**没被抓到**。原因是 `names()` 用了 `.+` 式的贪心边界：正则写成反引号 + 文件名 + 反引号，而读集那一行里的路径形如 `.charter/handoff.md`——反引号后紧跟的是 `.`，不是文件名首字符，于是那次解析返回空集合，`assertNotIn` 在空集合上永远通过，另外一条「读集是工作集子集」也在空集合上空转。改成匹配任意位置的 `.md` 文件名，并给两条用例加上**非空断言**（读集必须解析出 `project.md`、`lessons.md` 且至少 4 件；工作集至少 8 件）之后，同一条篡改才被抓到。这条正好复现了 `leaf-task.md:121-138` 那句话的镜像版本：一个跑不出失败的门只是日志行。

**另一个是工具链的。** 为还原篡改，我先用了 `git restore --source=HEAD --worktree -- .`。它把四个文件按 `.gitattributes` 的 `* text=auto eol=lf` 重写成了 LF，而这四个文件在工作区本来是 CRLF——镜像比对的是**字节**，于是 `validate_kit.py` 从 PASS 掉到 12 条 mismatch，全量 pytest 掉到 27 failed（`test_zcode_target`、`test_dsh_target` 的分布树一致性全红）。修复不是重跑构建，而是把镜像的字节原样拷回源文件（镜像与源在 HEAD 上本就字节相同）；`git hash-object --path` 逐件证明工作区内容与 `HEAD` 的 blob 一致，剩下的 ` M` 只是 stat 缓存过期，`git add` 同一份内容即清。

记两条给下一次：反向对照的还原必须**先快照原始字节再原样写回**，不能借 `git checkout`／`git restore`；镜像比对是字节比对，任何 EOL 归一化都会把它变成另一个文件。

### 校验

`python scripts/validate_kit.py .` → PASS (246 files checked)，11 项子检查全绿，exit 0。
`python -m pytest tests -q` → 287 passed, 519 subtests passed（149.08s）。用例数由 271 涨到 287，增量全部来自本轮新增的 16 条。

### 仍然开着的

独立上下文 Review A 已派发（干净上下文的 subagent，brief 限定只看 `portable/`、`DEVELOPMENT_CHARTER.md`、`scripts/`、`tests/`、`.claude-plugin/`、`targets/` 的 diff，不看生成镜像正文），要求按五个角度给 findings：自相矛盾、悬空引用、编号自洽、迁移充分性、唯一落点完整性。结果落地后作为 §9.9 追加，发现的缺陷逐条处置。**在此之前，`d6eff20` 的诚实状态仍然是：一致性验过、跨文件一致性现在也验过了，独立正确性还没验过。**

## 9.9 Review A 回来了：十六条 findings 的逐条处置

独立上下文审阅（fresh subagent，只读、不看生成镜像正文）给出 **BLOCK**：2 blocker + 7 major + 7 minor。下面按 id 记处置，全部落在手工源（`portable/` 与 `DEVELOPMENT_CHARTER.md`），再经镜像与三个 builder 的 `--sync` 分发。

### 处置表

| F-NN | 严重度 | 缺陷 | 处置 |
|---|---|---|---|
| F-01 | blocker | 三个权威入口仍把决策记录指向旧共享文件 `.charter/decision.md`（章程 §10、审阅模板 findings 段、入口命令第 53 行），而同一提交的迁移文档已判这种写法非法 | 三处改指 `.charter/records/<Decision ID>.md`，并各自说明 `decision.md` 是格式不是账本 |
| F-02 | blocker | 入口命令第 29 行说「every other file in the set is read on resume」，与第 39 行的六件读集互斥（工作集 10 件） | 改写该句：三份记录文件是「写入时才读的格式」，`changelog.md` 是历史且永不进读集，**读集就是 Resume 模式点名的那六件**。zcode 宿主变体同步同一句 |
| F-03 | major | 迁移表末句「The last three rows ship with the `0.2` template」在表尾追加两行后指向错位 | 改成按行点名的分档陈述：表头七行属 `0.2`，`Closure checklist` 与 `Acceptance items` 随当前 `0.4` 到达 |
| F-04 | major | 步骤 2 只写「bump `Contract version`」不写目标版本；文档按从未发行过的 `0.3` 分档叙述 | 步骤 2 写明目标版本 `0.4`，并说明版本记录的是批准而不是步骤数；正文补「No `0.3` template was ever released」，`0.2` 一次跳到 `0.4` |
| F-05 | major | `## Record-level migrations` 只有散文和三行表，没有步骤：不建 `records/`、不处理存量共享文件里的记录、不给序号起点与 slug 口径 | 新增 `### Steps` 六步：建目录 → 按原顺序拆 `01` 起 → 无法还原 id 的记迁移日期并声明 → 共享文件降级为格式并留一行索引 → 同一提交更新全部活引用 → 迁移本身记进 `changelog.md` |
| F-06 | major | 循环 A 的 `LA13`（路线与任务树校准）在八步投影里没有任何位置，而投影自称每步标注覆盖阶段 | 第 6 步补 `LA13` |
| F-07 | major | 关闭清单 `CLS2` 要求「四层证据」，而四层的定义只存在于 `docs/`（不进分发物），分发镜像里无法判定 | 章程 §6.1 写入四层定义（退出码／原始物重算／独立上下文审阅／集成后验证），`CLS2` 点名「charter 6.1」 |
| F-08 | major | 「未检查边界不得 `PASS_CLOSED`」只活在章程正文，关闭清单与五种关闭结论都没有落点 | 关闭清单追加 `CLS10`（append-only，不重编号）：每条边界要么检查过，要么带复查触发写进 `project.md` §10 |
| F-09 | major | 决定「何时必须加一行版本」的四类触发只写在 `changelog.md`，而该文件被明确排除在读集外——触发因此无法被读到 | 四类触发摘要写进 `project.md` §12 指针段（读集内），`changelog.md` 保留完整规则并反指该处 |
| F-10 | minor | §7.1 仍写「recorded in the section 12 change log」，同文件 §12 已改成指针 | 改为 `.charter/changelog.md` |
| F-11 | minor | 占位符没跟上新命名：`<REV-ID>`、`<DEC-ID>` | 改成 `REV-<TASK-ID>-<nn>/F-NN` 与 `DEC-<YYYYMMDD>-<slug>` |
| F-12 | minor | 同一 kit 文件三种路径写法（`references/…`、`portable/references/…`、裸文件名） | 章程内统一为自包含 Skill 的 `references/…` 形，与同文件其余六处一致 |
| F-13 | minor | 叶模板写「Section 9 confirms each `AC` against its check」，而关闭清单没有一行做 AC 对账 | `CLS9` 的判定文字补「every `AC` confirmed against its check」，叶模板该句改指 `CLS9` |
| F-14 | minor | §9 自述第 12 项写「BINDING/SETTLED」，全仓零命中——自述与实现不一致 | 本表按实际落地记（五态表 + `DECIDED` 只以移出离场 + 改名双记录），不再使用未存在的术语 |
| F-15 | minor | `init_project.py` 仍生成三份共享记录脚手架，等于鼓励继续追加 | 保留三份文件（它们承载字段 schema），但在第 29 行把性质写死：格式，不是账本；每条记录是 `records/` 下的独立文件 |
| F-16 | minor（工具链） | `core.autocrlf=true` 的宿主上，工作树镜像比对会变红（提交本体自洽，`git archive HEAD` 解包后 PASS） | 记为已知工具链事实：镜像比对是字节比对，复现校验须在 LF 归一化的树上或 `git archive HEAD` 后执行。不改比对语义 |

### 顺带修掉的空白

- `contract-migrations.md` 里 `## Record-level migrations` 与上一段之间缺一个空行（格式缺陷，一并补上）。
- `contract-migrations.md` 从 HEAD 起就是**混行尾**（202 行里 179 行 CRLF、23 行 LF）。本轮补丁把它归一成 CRLF：内容未变，字节变了，镜像同步重建。

### 新增的跨文件守卫（11 条，全部重算型）

| 类 | 守的规则 |
|---|---|
| `DecisionRecordLanding` | 决策不得再被送进旧共享文件；写决策的三个入口都必须点名迁移表承诺的 `records/` 路径（路径本身从迁移表解析，不写死） |
| `WorkingSetVersusReadSet` | 工作集里不在读集的文件，必须在同一句里被声明为什么不在读集；禁止「every other file … read on resume」这种全称断言 |
| `MigrationVersionArithmetic` | 迁移步骤点名的目标版本必须等于叶模板当前的 `Contract version`；任何被承诺的模板版本都不许比它新 |
| `PhaseCoverage` | 循环 A 定义过的每个 `LA` 阶段，必须在八步里被点名或被一个范围覆盖 |
| `EvidenceLayers` | 关闭清单引用的定义必须真的在分发物里：它点名的章程小节要存在，且四层标记齐 |
| `ClosureChecklistCoverage` | 「`CLS9` 确认每个 AC」这句承诺必须对应一行真提 AC 的行；章程里的未检查边界规则必须在关闭清单里有行 |
| `ChangeLogTriggers` | 「何时必须加一行」的规则不许只活在读集之外 |

新增 11 条后，本轮自己的反向对照只剩一条经验要记：**新写的断言必须先看它能不能红**。第一版六条里有五条因为正则被转义两次而空转（例如 `\d` 写成 `\\d` 后进正则成了字面反斜杠），全部「通过」；是它们各自的**非空断言**（解析到空集合就 fail）把它们暴露出来的。

### 校验

`python scripts/validate_kit.py .` → PASS (246 files checked)，11 项子检查全绿，exit 0。
`python -m pytest tests -q` → 298 passed, 519 subtests passed（137.58s）。用例数 287 → 298。

### `d6eff20` 的状态更新

此前写的是「一致性验过、跨文件一致性验过、独立正确性没验过」。现在独立正确性**验过了第一遍**，代价是审阅给出 BLOCK；十六条 findings 里十四条是**真缺陷**（两条 blocker、七条 major 中的六条会让下游写出违规记录或让规则读不到），已逐条修完并加了守卫。剩下的诚实表述是：这套改动现在的强度是「有独立审阅 + 有跨文件守卫 + 有反向对照证明守卫会红」，仍然**没有**走它自己的叶合同与收据——仓库根没有 `.charter/`。

## 9.10 让套件受自己治理：章程自举与独立审阅链（轮次见 `.charter/records/`，本节不计数）

这一节补的是 §9.9 里一直挂着的那笔账：d6eff20 与十六条 findings 的修复都没走本套件自己的叶合同、没有收据、没有独立审阅者之外的记录。用户在本轮发出一份 charter-workflow 命令，Context Router 判定 INIT（仓库根无 `.charter/project.md`），于是按套件自己的模板在仓库根自举治理工作集。

### 9.10.1 做了什么

| 步骤 | 动作 | 产出 |
|---|---|---|
| 1 | `python scripts/init_project.py .` | `.charter/` 十件 + `evidence/` + `records/` |
| 2 | 按模板逐份填写，锚点替换 + 命中数断言 | `project.md`（目标/六条不变量/五个成功等级/§9 授权/§10 决策五态）、`roadmap.md`（R1.1–R1.4 四级树）、`reuse-discovery.md`（RD-20261019-01）、`current-task.md`（叶 R1.1-S1-L1）、`handoff.md`、五份格式与教训文件 |
| 3 | 依赖探测两段 | `dependency-check.log`（12:43:28Z 全仓 / 12:54:05Z 复用阶段）+ `reuse-probe-2026-10-19.txt` |
| 4 | 独立章程审阅 | `.charter/records/REV-CHARTER-01.md` |
| 5 | 实跑证据 | `.charter/evidence/validate-2026-10-19.txt` |

### 9.10.2 REV-CHARTER-01 的结论与处置

独立上下文子代理（只读、无实现上下文）判 **REQUEST_CHANGES**：5 条 P1、7 条 P2、3 条 P3。它同时核对了三件事实并全部属实——`validate_kit.py .` PASS (246 files)、`pytest -q` 298 passed / 519 subtests、`leaf-task.md` 18,349 字节对阈值 18,432（余量 83）。

值得记的不是条数，而是**它抓到的错属于哪一类**：

| 类型 | 例子 | 说明 |
|---|---|---|
| 顺序错 | 复用门的 gate 先写成 `COMPLETE` 并签了 `Approved by YG`，而章程还是 `DRAFT` | 门禁比它守护的批准动作先完成，正是 §5 状态机要防的那件事，发生在写状态机的那份文件自己身上 |
| 投影不一致 | `project.md` 的 recheck trigger 写「无」，复用记录写 2027-01-19 到期；`project.md` 根本没有 `freshness` 字段 | 同一个事实在三处有三种写法，正是 §7「事实源唯一、投影必须同步」的活靶子 |
| 证据指针指向不存在的东西 | 两处引用 `records/REV-CHARTER-01.md` 与 `records/E-R1.1-S1-L1-01.md`，而 `records/` 当时是空的 | 收据纪律的反面：引用了还没发生的证据 |
| 自述与实测不符 | 「21+ 个 M」实测 77 M + 2 未跟踪；「六份参考」实测 5 个；「约 35 KB」实测 36,731 字节 | 与 P2-4 同一类病：文档里写着会漂的实测值 |
| 检查不动退出码 | `AC3` 用 `grep -c ... >= 1` | 与 leaf-task.md:121-138 的「必须能移动退出码」直接冲突，写在叶合同的验收段里 |

十五条已逐条处置并写进 `REV-CHARTER-01.md` 的 Findings 表（十三条 `CLOSED`、一条 `DECIDED_BACKLOG` 即 D-06 日志不记 argv）。两条 AC 换成 `python -c` 断言并实测 exit 0；还故意把 gate 改坏验证它们会退出非零。

### 9.10.3 这一轮的诚实状态

- 章程仍未批准（`Status: DRAFT`）。`REV-CHARTER-01` 不自我批准，修复后需要 `REV-CHARTER-02` 复验。
- `.charter/` 目前是未跟踪目录；批准动作包含把它单独提交。工作区其余 77 个改动不属于这次批准。
- 本轮没有改 `portable/`、`targets/`、`scripts/`、`tests/`、生成物或根 `DEVELOPMENT_CHARTER.md`，所以 `validate_kit.py .` 仍是 PASS (246 files) —— 这个数字不变本身就是证据：自举没有污染套件。
- 遗留：D-01（模板体积阈值 36 KB 与其一半的换算关系；数字落 `.charter/evidence/template-budget-2026-10-19.txt`）、D-02（回溯性叶记录算不算证据）、D-03（执行纪律外拆）、D-04（模板准入与退役钩子）、D-05（下游项目校验器）、D-06（日志记 argv）。

### 9.10.4 REV-CHARTER-02 与十条处置

`REV-CHARTER-02`（fresh subagent `383cfdb5-e460-44f6-8c64-8a250da804fd`，只读）判 `REQUEST_CHANGES`：`REV-CHARTER-01` 的十五条里 12 条真关闭、3 条半关闭（F-05 / F-06 / F-08），同时新增十条。这一轮最值得记的不是那十条，而是它们的类型：**修复动作自己制造了下一批缺陷**。

| 类型 | 实例 | 为什么值得记 |
|---|---|---|---|---|
| 修复时删掉了整节 | N-01：叶的 `### Negative behavior / boundaries` 与 `AC2` 一起消失，且无撤回记录 | 与上一轮压缩 `portable/templates/leaf-task.md` 时踩的是同一个坑：把「第二个投影」与「唯一落点」混为一谈。区别是这次落在叶合同的编号上，而编号只增不改是套件最硬的规则之一 |
| 用存在性断言冒充检查 | N-02：`AC1` 只查「状态词是否出现在 roadmap 全文」 | 这正是 `leaf-task.md`:121-138 明令禁止的：打印但不影响退出码的违规只是日志行，不是门。改成按 `|` 切行、取 Status 单元比对之后才能被打红 |
| 数字自述与实测脱钩 | N-03 / N-06：`21+ 个 M`、`十六条` 与 `十五条` 四处打架 | 与 P2-4 同型：会漂的实测值被写进文档正文。可接受的写法是指向基线清单文件，而不是复述数字 |
| 两处投影互相矛盾 | N-04：`handoff.md` 写 `local_merge`，叶 §4/§7 写 `Merge allowed: no` | 章程 §7「事实源唯一、投影必须同步」的活靶子，而投影不一致在 `roadmap.md` 被定义为阻塞性发现 |
| 枚举值写错 | N-05：`DECIDED_BACKLOG` 的 finding 落成 `OPEN` | 五态枚举是批 3 刚定下的规则，第一次使用就写错一格 —— 枚举成员必须逐个出现在编辑者视野里，靠记忆会漏 |
| 占位符未替换 | N-07：`Mode:` 后仍是 `MANUAL | AUTO_DEV` 选择器 | 模板里的选择器形状被原样复制进实例；这一条只能靠审阅发现，校验器不认 |
| 字段名三处不同 | N-09：`Reuse discovery freshness` / `Discovery freshness` / `Gate freshness for this leaf` | 模板原名不同是套件既有形状，改名会与模板分叉；正确做法是把**值**纳入一条跨文件断言，而不是把字段名统一 |
| 只声称不记录 | N-10：`用户已有改动已记录与保护` 未勾选 | 隔离是声称而不是事实。修法是先落基线清单文件，再让 AC2 拿它逐行比对 —— 「记录」必须先成为一个可读的制品 |

处置与证据：N-01 … N-10 全部 `CLOSED`，逐条写在 `.charter/records/REV-CHARTER-02.md` 的 Findings 表里。修完后叶合同现 22,916 字节；五条 AC 全部原样 exit 0，并且各自被一条真实突变打红（`.charter/evidence/ac-liveness-2026-10-19.txt`）：

- AC1：`Status` 改 `PASS_CLOSED` → exit 1
- AC2：基线清单新增一条 `portable/templates/zzz-probe.md` → exit 1
- AC3：roadmap gate 改 `COMPLETE` → exit 1；freshness 改 `stale` → exit 1
- AC5：期望基线提交改成 `deadbeef` → exit 1
- AC4 直接调用 `validate_kit.py .`，失败模式继承自校验器（镜像字节不一致时变红，本仓历史上出现过 17 条 mismatch），不在证据文件里另做突变

这一轮的教训可以压成一句：**审阅发现的每条缺陷，修完之后都要再问一次「我删掉的东西有没有第二个落点」**。上一轮压缩模板时犯规三次，这一轮修 findings 时又犯规一次，两次都发生在校验器与 pytest 全绿的情况下。

仍然开着的：`REV-CHARTER-03`（窄范围复验 N-01…N-10 与五条 AC 的活性）未回；章程仍 `Status: DRAFT`，批准动作包含把 `.charter/` 单独提交；D-01 … D-06 未决。

### 9.10.5 REV-CHARTER-03：判 BLOCK，九条 findings 与证据重造

`REV-CHARTER-03`（fresh subagent `63dd44b4-83da-48b0-8246-0fdc5f04ab0b`，只读，窄范围只核 N-01…N-10 与五条 AC 的活性）判 **BLOCK**：N-03 / N-04 / N-05 / N-06 / N-07 / N-08 / N-09 与隔离项判 CLOSED，N-01 / N-10 PARTIAL、N-02 NOT_CLOSED、活性证据 PARTIAL，另给九条 findings。

这一轮最值得记的一件事：**上一轮我"修好"的两条 AC，其实只是把断言换了个写法，仍然动不了退出码。**

| ID | 我上一轮写的 | 审阅者实际做的 | 为什么没红 |
|---|---|---|---|
| F-01（P1） | `AC2` 拿 `git status --porcelain` 逐行 `l[3:]` 与基线比对 | 删除基线里已列出的 `portable/commands/charter-workflow.md`、给 `DEVELOPMENT_CHARTER.md` 追加一行、新建 `plugins/evil.md`、新建 `docs/other.md` | 只取 `portable/`/`targets/`/`scripts/`/`tests/` 四个前缀比对，79 行基线里 **56 行从未参与比对**；删除与新增在同前缀下可能互相抵消 |
| F-02（P2） | `AC1` 取 roadmap 里含该叶 ID 的行，判断状态词是否在其中 | 把叶 `Status` 改成 `LEAF`（roadmap 的 Level 单元本来就有这个值） | `s in cells` 是对**整行所有单元**做成员测试，`DRAFT` 换成任何已存在于同一行的词都通过 |
| F-03（P2） | `AC3` 判断 RD 编号是否出现在三处文件的全文里 | 把字段值改成 `-99`，旧 id 留在注释行 | 全文 `in` 测试管不到"这个字段的值是什么"，只管"这个字符串在不在文件里" |

三条是同一个病：**把"存在"当成"相等"**。存在性断言有一个共同特征——它永远不会因为对象被改坏而变红，只会因为对象被删光而变红。这也是 9.10.4 里 N-02 那一行记过的同一件事，我改了一轮仍然只改到表面。

处置（九条全部 CLOSED，逐条写在 `.charter/records/REV-CHARTER-03.md` 的 Findings 表里）：

| 改法 | 内容 |
|---|---|
| `AC1` 改为定位单元格 | 按表头找到 `Status` 列的 index，用第 3 列（ID 单元）唯一定位 `R1.1-S1-L1` 那一行，取该单元格与叶的 `^- Status: (.+)$` 比；命中数必须为 1，所以 decoy 行会让它变红 |
| `AC2` 改为全量集合 + 摘要 | 两侧都取「(状态码, 路径)」全量集合做对称差；允许路径白名单是 `.charter/**` 与 `docs/SELF-AUDIT.md`；另加一条 `git diff` 摘要比对，覆盖「本来就脏的文件被继续改写」这类 porcelain 看不出的变化（摘要写在基线文件首部） |
| `AC3` 改为取值 | 按字段标签取出**值**再比，三处 freshness 值必须相同，RD 值必须相等且以 `RD-` 开头 |
| 投影失同步（F-04） | `reuse-discovery.md` 的章程版本从 `0.1` 改到 `0.2` —— 这是 0.2 bump 自己制造的失同步 |
| 状态行与事实对齐（F-05 / F-06） | 审阅状态行改成三轮全记并写明「未拿到 APPROVE 前不得写 PASS」；`handoff` 的 Open findings 从「无」改成「REV-03 判 BLOCK，九条已处置，REV-04 未回」 |
| 引用与召回（F-08 / F-09） | 效果来源改指章程第 5 节（第 9 节只给 `MANUAL` 任务授权）；D-06 补召回触发 |

活性证据重造的要点：不再只写结果行，而是**先抄录合同里的 check 原文**，再对**对象侧**做突变（改叶 Status、改 roadmap 单元格、插 decoy 行、改 gate / freshness / RD 字段、加删文件、改已脏文件、破坏镜像），每次突变后按字节还原，最后 clean 复跑。其中两条特别值得记：

- 一条**对照实验**：新建 `.charter/probe-allowed.md` 必须保持 exit 0。只证明「会红」而不证明「该绿的时候绿」等于把检查改成永远失败。
- 一条**骗过成员测试的突变**：叶 `Status` 改成 `LEAF`。它不是随意挑的字符串，而是取 roadmap 同一行里已经存在的 Level 单元值 —— 这类突变才能暴露存在性断言。

校验：`python scripts/validate_kit.py .` → PASS (246 files checked)，11 项子检查全绿，exit 0；`python -m pytest tests -q` → 298 passed, 519 subtests（138.86s）。仓库状态与实验前一致：`git status --porcelain` 仍 79 行，HEAD 仍 `d6eff20`。

教训（第三次出现同一类）：审阅者说的「这条检查动不了退出码」不是语法问题，是**语义问题**——要问的是「把对象改坏，它会不会红」，而不是「它有没有 return 非零」。写检查时先写突变，再写检查。

### 9.10.6 REV-CHARTER-04：九条全 CLOSED，但投影又停在一轮前

第四轮审阅（fresh subagent，只读，窄范围只核 F-01…F-09 与活性证据）判 `REQUEST_CHANGES`。结论是分两半的：**F-01…F-09 九条全部 CLOSED**，审阅者独立跑了 23 个自己的突变场景（与证据表 22 行不是同一套，两者不必相等）、把五段检查文本与合同逐字节比对 5/5 相同、用 `cp -a` 副本（含 `.git`）做实验并 `diff -q` 自证没动真实仓库；**但**同一份文件里另有两行写着「待 REV-CHARTER-03」，与它自己上面那行、`.charter/project.md:70`、以及 REV-03 记录三处冲突。

这一条比前几轮更像一个结构性问题而不是笔误：`.charter/handoff.md` 是六件启动必读件之一，下一会话若照它的 Exact next action 执行，会重派一个已经做完的审阅。**投影失同步的代价不是难读，是照着错的做。**

| ID | 严重度 | 处置 |
|---|---|---|---|---|---|
| F-10 | P2 | `.charter/handoff.md` 第 43 行改成四轮全记（01 → 02 → 03 → 04 都是 `REQUEST_CHANGES`）、第 59 行改成派 `REV-CHARTER-05` 并写明范围 |
| F-11 | P3 | REV-03 记录的起止时刻改标为「批次写入标签，取自文件 mtime」，不再声称是实测审阅时间 |
| F-12 | P3 | REV-03 判词由 `BLOCK` 改为枚举词 `REQUEST_CHANGES`，并在记录里留一行映射说明 |
| O-01 | P3 | AC5 的检查由前缀匹配改成完整 SHA 全等，说明与检查一致 |
| O-02 | P3 | AC1 增加「叶内 `^- Status:` 必须恰好出现一次」 |

活性证据随之重生成：五条 check 原文照抄、21 条对象侧突变（18 条打红、3 条控制组保持绿）、突变后按字节还原、clean 复跑全 0。两条新突变专为关闭上面两个 O 而设——「追加第二条 Status 行」与「把完整 SHA 缩成 7 位前缀」，都必须 exit 1。

重生成过程踩到两个坑，都记在这里：

- **突变必须改在检查体上**。AC5 的完整 SHA 在叶文件里出现两次（一句说明、一段检查），`replace(..., 1)` 命中的是说明那次，于是「突变后仍然 exit 0」，看上去像检查不灵敏，实际是突变没落到被测对象上。
- **允许路径内的改动不是漏洞，是控制组**。`.charter/` 全在 AC2 白名单里，所以「在 `.charter/` 内改名」必须 exit 0。把它写成打红项就是把正确行为记成缺陷。

校验：`python scripts/validate_kit.py .` → PASS (246 files checked)，11 项子检查全绿，exit 0；`python -m pytest tests -q` → 298 passed, 519 subtests（138.89s）。仓库状态未变：`git status --porcelain` 79 行，HEAD `d6eff20`。

下一步：派 `REV-CHARTER-05` 只核这五条与两条新突变能否复现；不重做 CHK 全表，不重验已 CLOSED 的 F-01…F-09。拿到 `APPROVE` 之前，章程与叶都停在 DRAFT。

### 9.10.7 REV-CHARTER-05：同一个病灶第三次出现，只是换了行号

第五轮审阅（fresh subagent，只读，只核 F-10 / F-11 / F-12 / O-01 / O-02）判 `REQUEST_CHANGES`：四条 `CLOSED`，**F-10 未关闭**。原因是 `.charter/handoff.md:43` 仍把 `REV-CHARTER-03` 记成 `BLOCK` —— 而 `REV-CHARTER-03.md:24` 与 `.charter/project.md:70` 上一轮已经改成 `REQUEST_CHANGES` 了。上一轮我改的是同一行的另外半句（Exact next action 与第 42 行），把状态行的判词漏在 `BLOCK`。

这一轮值得记的不是这五条，而是它暴露的模式：**同一个「投影停在一轮前」的病灶，连续三轮分别出现在 handoff:42、handoff:59、handoff:43 三个不同位置。**每次我都只改被点名的那一处，而没有把 handoff 的整条审阅状态链当作一个投影一次性重算。改一处被审一次，说明缺的不是细心，是「一处改动要重算所有指名同一事实的行」这条规则没有落到动作上。

| ID | 严重度 | 处置 |
|---|---|---|---|
| F-13 | P2 | handoff:43 的 `BLOCK` 改为 `REQUEST_CHANGES`，保留「原判词写作 `BLOCK`」并说明按枚举读作带未闭合 blocker 的 `REQUEST_CHANGES`；三处投影自此一致 |
| F-14 | P3 | handoff:43 与 project.md:70 的「三条 P3」改为「四条 P3」（与同文件 :42 和 REV-04 表一致） |
| F-15 | P3 | project.md:70 的「章程级已跑三轮」改为「五轮」（连同本轮的 04 / 05 一起记） |
| F-16 | P3 | 正文与记录里的「21 条突变（18 红 / 3 绿）、AC2 八种」改为「22 条（19 打红、3 控制组绿）、AC2 九种（六红三控制）」，并显式计入 AC4 一条。审阅者已按证据表逐行复现 22/22 与 exit 列一致 —— 错的是正文计数，不是证据 |
| F-17 | P3 | 证据文件的小节标题由「each applied to the working tree」改为「applied to the working tree, except the AC5 rows which mutate the check text itself」。审阅者第一版复现时按标题字面在对象侧做，得到 exit 0，误判成 MISMATCH —— 标题与行内措辞不一致会直接制造假缺陷 |

顺带把这一轮自己的投影也一次性重算：handoff:42 / :43 / :59 与 project.md:70 全部改到「05 已回、待 06」，并在证据文件末尾追加一段「REV-05 处置后无突变复跑」，五条 AC 全部 exit 0。

校验：`python scripts/validate_kit.py .` → PASS (246 files checked)，11 项子检查全绿，exit 0；`python -m pytest tests -q` → 298 passed, 519 subtests（138.47s）；`git status --porcelain` 79 行，HEAD `d6eff20`。五条 AC 复跑全部 exit 0。

审阅者这一轮还披露了一个工具坑，值得抄进教训：它第一版突变驱动用了裸 `bash`，PATH 命中 WSL 桩 `C:\Windows\System32\bash.exe`，每条命令都返回 rc=1（stderr `execvpe(/bin/bash) failed`），于是 3 条控制组被误判成 MISMATCH、19 条红被误判成通过。它把那一整轮结果作废、改用 dsh-ops 自带的 bash 重跑，并加逐条树哈希完整性断言。**一个坏掉的执行器会让所有检查同时说假话**——这与本项目「检查必须能移动退出码」是同一条判据的另一面。

### 9.10.8 REV-CHARTER-06：四条关闭，第三种「两个数并存」

第六轮审阅（fresh subagent，只读，窄范围 F-13…F-17 + 自查别的行是否停在旧轮次）判 `REQUEST_CHANGES`：F-13 / F-14 / F-15 / F-17 四条 `CLOSED`，F-16 的四个计分项（22 条 / 19 红 / 3 控制绿 / AC2 九种六红三控制）与证据表逐项相符，但**同一个病灶又留下三处**：

| ID | 严重度 | 处置 |
|---|---|---|---|
| F-18 | P3 | 「审阅者独立跑了 23 个突变场景」与证据表 22 行并存（handoff:42、project.md:70、REV-04:25）。三处都改成「23 个**自己的**突变场景（与证据表 22 行不是同一套，两者不必相等）」。**没有简单改成 22** —— 23 是审阅者自跑的集合，22 是证据表的行数，两者本来就不是同一个量；改成 22 是为了让文本自洽而伪造一次等式 |
| F-19 | P3 | handoff:72 的 Session ledger 仍写「最近 seam = REV-CHARTER-02 的 N-01…N-10 处置完成」。改为本轮，并注明 `.jspace` 自 12:45Z 起未再更新、本节是它的权威投影 |
| F-20 | P3 | project.md:30 / :154 / :172 三处把 `BLOCK` 当判词且无记录指针，与「六轮全 `REQUEST_CHANGES`」并置时像同一条线自相矛盾。三处都补 `docs/SELF-AUDIT.md` 第 9.9 节的指针，并写明那是**套件级**的另一条审阅线（审 `git diff 6c2a9bf d6eff20`），与章程级六轮不是同一条链 |

三条与前面几轮同源，但 F-18 是新的一种：**不是停在旧轮次，而是两个都「对」的数被并列**。修法不能二选一，得说明它们各自量的是什么。这与 F-17（标题与行内措辞不一致）是同一类的两个变体：读者按字面执行时得到的结果与作者意图不同。

审阅者这轮给的两个动作值得复用：① 把 findings 表**机械计数**（每轮的行数写在该轮自己的记录里，本文不汇总）；② 给真实仓库算一个**零改动锚点**，开工与收尾相同才声明「零改动」——这比 `git status` 有力，后者只看被跟踪路径。注意 ② 的做法后来被 `REV-CHARTER-10` 的 NF-13 判为不可复现：自建遍历的文件数与聚合哈希没有记口径，第三方重放不出同一个数。可复现的锚点配方写在 `.charter/handoff.md` 的 Capability notes 里（`git ls-files -s | sha256sum` 与 `git status --porcelain | sha256sum` 成对记录）。

校验：`python scripts/validate_kit.py .` → PASS (246 files checked)，11 项子检查全绿，exit 0；`python -m pytest tests -q` → 298 passed, 519 subtests（136.14s）；`git status --porcelain` 79 行，HEAD `d6eff20`；五条 AC 复跑 AC1=0 AC2=0 AC3=0 AC4=0 AC5=0。

### 9.10.9 REV-CHARTER-07：处置表说「已落地」是最难被抓的一种失实

第七轮审阅（fresh subagent，只读，窄范围只核 F-18 / F-19 / F-20）判 `REQUEST_CHANGES`：前两条 `CLOSED`，F-20 只到 `PARTIAL` —— 三处记录指针确实到位，但被处置表声称「已落地」的两项内容（`git diff 6c2a9bf d6eff20` 区间与 `:172` 的枚举括注）在 `project.md` 里零命中。另新开四条 P3：

| ID | 严重度 | 是什么 | 处置 |
|---|---|---|---|
| F-21 | P3 | `project.md:30` 与 `:172` 仍写「章程级五轮」，而 `records/` 已有六份；`:30` 的「本文件第 6 项」也不指向章程级投影（在 §4 的 `:70`） | 两处改六轮，`:30` 的指针改为 §4 `INDEPENDENT_REVIEW` 行 |
| F-22 | P3 | 三处都没有 `git diff 6c2a9bf d6eff20`，`:172` 缺 `BLOCK` 的枚举括注，而 REV-06 记录与本节都以「本轮已落地」写下这两项 | 三处补齐，并在 REV-06 记录**另起一行更正、点名被更正行** |
| F-23 | P3 | `handoff.md:84` / `:89` 停在「五轮 / 五次 `REV-CHARTER-01…05`」——第六轮已回，而 handoff 是六件启动读集之一 | 改六轮 / 六次 `01…06`，并写明 REV-03 原判词写作 `BLOCK` |
| F-24 | P3 | `handoff.md:72` 把 `.jspace` 的 init 标签 `12:45Z` 当成「未再更新」的边界，而 `control.json` 的 mtime 是 `12:48:01Z` | 两个时刻都写出：记录标签 12:45Z、最后写入 12:48:01Z |
| F-25 | P3 | `docs/SELF-AUDIT.md:825` 的「审阅者独立跑了 23 个突变场景」缺限定，是 F-18 同一句的第四处；而该文件正是 F-20 三处指针的落点 | 补同一限定语 |

这一轮值得单独记的是**第四种缺陷类型**。前三种是顺序错（复用门先签 COMPLETE）、投影不一致（三处字段名与值打架）、证据指针指向不存在的东西（records/ 空）；F-22 是**处置表说做了、产物里没有**。它比前三种更难抓，因为读者本来就在用处置表替自己省掉重读——一张被信任的假记录比没有记录更危险。修法只有两条且必须选一条：要么真做，要么把描述降级为「未落」。本轮选前者，并在 `REV-CHARTER-06` 记录里另起一行更正、点名被更正的行、原行不改。这条写法与 `changelog` 的「更正另起一行并指名被更正行」是同一条规则——现在可以说它不只约束版本史，也约束审阅记录。

还留了一条**计数摩擦**的档：`handoff.md:54` 的括注写「两条允许路径控制」，而证据表里该控制组实为 3 行（`.charter/` 内新建、允许路径内追加 `docs/SELF-AUDIT.md`、`.charter/` 内改名）。两个数各自都对得上不同的量，只是并置会误导下一轮读者；写法应改成能被数出来的那个量（3 行），而不是描述性的那个数（2 条允许路径）。

还有一条**假红**的坑值得记：我从叶合同里抽 AC 命令时，最后一条 AC 的截断条件写成了「下一条 AC 或文件结尾」，于是 `### Suite verification` 之后小节的 backtick 被并进 payload，`AC5` 报 exit 1 —— 而手工跑同一条命令是 exit 0。抽取器要在下一个 `###` 标题处截断。它与 §9.10.7 那条「坏掉的执行器让所有检查同时说假话」是同一枚硬币的两面：**坏掉的检查器也会说假话**，两个方向都会伪造结论。

另外，`REV-CHARTER-07` 提供了两个可直接复用的核对手法：findings 表**机械计数**（每轮的行数写在该轮自己的记录里，本节不再汇总裁数）与**非 `.git` 树逐字节聚合哈希**。它也披露了一次执行器失误：把辅助脚本误写进仓根，导致 `AC2` 因白名单外多出一条未跟踪文件而红，删除后即恢复 `exit 0`——这条恰好是 `AC2` 在替我们干活的正面证据。

校验：`python scripts/validate_kit.py .` → PASS (246 files checked)，11 项子检查全绿，exit 0；`python -m pytest tests -q` → 298 passed, 519 subtests；`git status --porcelain` 79 行，HEAD `d6eff20`；五条 AC 复跑 AC1=0 AC2=0 AC3=0 AC4=0 AC5=0。

### 9.10.10 REV-CHARTER-08：把轮数从散文里删掉，而不是再改一次数字

第八轮审阅（fresh subagent，只读，窄范围 F-20 收尾 + F-21…F-25）判 `REQUEST_CHANGES`：F-22 / F-24 / F-25 与 F-20 收尾四项 `CLOSED`，F-21 与 F-23 判 `PARTIAL` —— 指针与字面落点都到位了，但同一批编辑把 `project.md:70` 改成「已跑七轮」的同时，`:30`、`:172`、`handoff.md:84`、`:89` 仍写「六轮 / 六次 `01…06`」，而 `records/` 已有七份。记 NF-01。

| ID | 严重度 | 是什么 | 处置 |
|---|---|---|---|
| NF-01 | P2 | 散文里的轮数落后一轮（四处） | **不改成七轮，而是把轮数从散文里整体删掉**：四处改为「轮次与判词以 `.charter/records/REV-CHARTER-*.md` 的文件集合为唯一权威，其他位置不重复计数」，`project.md:70` 留作唯一投影 |
| NF-02 | P3 | `handoff.md:72` 的 seam 停在第七轮之前，且用会随轮次滚动的「本轮」 | seam 改为 `REV-CHARTER-08` 的 NF-01…NF-03，并写明该行的「本轮」随每轮重算 |
| NF-03 | P3 | `SELF-AUDIT` 把 `REV-05` 的计数写成 10 行 | 改为「findings 表 5 行 + 复验判定表 5 行」 |

**为什么不按审阅者的建议改数字。** F-15 → F-18 → F-21 → NF-01 连续四轮是同一个病灶，只是每次落点不同：`handoff:42` → `:59` → `:43` → 这四处的轮数。机制很清楚——**一个会随事件变化的数被复制到多处，而只有一处会被想起来更新**。把「七」写对一次，下一轮加一份记录，四处又全落后一轮。所以这一轮改的是生成机制本身：删掉所有散文里的轮数，让**轮数**只有一个可写错的地方。这句的更强版本（「这一类会变的事实都只剩一处」）被 `REV-CHARTER-09` 证否——`project.md:172` 的逐轮聚合判词与 `handoff.md:89` 的判词复述是残留的两处，见本节末的 NF-05 / NF-06。

同一处置也用到了 `handoff.md` 的两条状态行：`:42` 的 Open findings 与 `:43` 的 Review status 原本各自复述整条七环审阅链，现在改为指向 `project.md:70` 与 `.charter/records/`，不再复述整条链，只留着「尚无 `APPROVE`、待 `REV-CHARTER-09`」这类会变的事实——注意它们是**若干个**，不是一个；`REV-CHARTER-09` 的 NF-07 抓的正是上一稿把这个数说成「一个」。**删掉一处重复的枚举，等于关掉这一类枚举带来的 finding**，但不会关掉所有会变的事实。

更正：§9.10.9 的 F-21 处置行把轮数写成「六轮」，那一行在写入当时（六份记录）成立，但同一批编辑已把 `project.md:70` 改成七轮，两处因此打架——即本节的 NF-01。原行不改，此行为更正并点名被更正的那一行。

审阅者这轮还纠正了我一个口径错误，值得记：它指出 `SELF-AUDIT` 上一条的「533 文件 / `3fe761862ed9…`」是 `REV-CHARTER-06` 时点、不同 skip 集下的数，不能与本轮的 490 / 535 直接相减。**任何跨轮比较的计量都必须连口径一起记**，否则下一轮会把两个不可比的数当成一次变化。

校验：`python scripts/validate_kit.py .` → PASS (246 files checked)，11 项子检查全绿，exit 0；`python -m pytest tests -q` → 298 passed, 519 subtests；`git status --porcelain` 79 行，HEAD `d6eff20`；五条 AC 复跑 AC1=0 AC2=0 AC3=0 AC4=0 AC5=0。

### 9.10.11 REV-CHARTER-09：删掉一个会变的数，不等于删掉所有会变的事实

第九轮（fresh subagent `62cf97e1-6161-43e5-b681-7ce990e38768`，只读，窄范围 NF-01 / NF-02 / NF-03 + 一条一致性）仍判 `REQUEST_CHANGES`。三条里 NF-02 `CLOSED`、NF-03 在其点名位置 `CLOSED`、NF-01 判**字面 `CLOSED` / 目的 `NOT CLOSED`**：四处轮数断言确已清零，但它自跑全仓 grep 后仍找到两处「会随每轮变化却写在散文里」的现状断言。

| ID | 严重度 | 位置 | 是什么 | 处置 |
|---|---|---|---|---|
| NF-04 | P3 | `SELF-AUDIT.md:902` | 「机械计数（… 05 10 …）」与同文件 `:880` 的「5 行 + 5 行」冲突：同一现行文件对同一次测量给出两个值 | 就地把跨节汇总的计数列表整段删掉，改为指向各轮自己的记录 |
| NF-05 | P2 | `.charter/project.md:172` | 「章程级审阅链的每一轮都判 `REQUEST_CHANGES`」是 `project.md:70` 之外的第二个写值处；下一轮判 `APPROVE` 即与 `:70` 相撞 | 删掉该聚合分句，只留「逐轮判词见 `project.md:70` 的枚举，本行不聚合判定」 |
| NF-06 | P3 | `.charter/handoff.md:89` | 「截至最近一轮判词全是 `REQUEST_CHANGES`…尚无一份记 `APPROVE`」与 `:43` 重复同一会变事实 | `:89` 只留 fresh-subagent 的方法断言，状态交给 `:43` |
| NF-07 | P3 | `records/REV-CHARTER-08.md:51`、`:53`；本节 `:916`、`:918` | 「这个缺陷类型在结构上不再可能发生」「handoff 只保留…这一个会变的事实」与产物不符 | 四处声称收窄为「删掉了**轮数**这一项」，并点名残余的 `:172` 与 `:89` |

**这一轮的教训。** 上一轮我把轮数从散文里删掉，并在记录里写「这个缺陷类型在结构上不再可能发生」。审阅者证否了这句话：我删掉的是**轮数**这一维，而**判词聚合**是同一类的另一维——「每一轮都判 X」是一个永远会过期的全称断言，它不在轮数上，却和轮数一样会随每轮失效。推广成一条判据：

> **每一处现状断言都要能回答一个问题：它下一次会因为什么而变。**
> 答不出来的，可以留在散文里；答得出来的，要么删掉、只留唯一投影，要么写明它随什么重算。

**顺带立一条更正惯例的分界。** NF-04 指出同一条文档里并存两套更正写法：`:920` 规定「原行不改、更正另起一行并点名被更正行」，而 NF-03 的处置是对 `:880` 就地改写。两者的适用范围不同，现在写死：

- **历史判词、轮次判定、记录正文** → 「原行不改 + 更正行点名被更正行」。理由是它们记录的是「当时发生了什么」，改写它等于伪造历史。
- **跨节复制的计量数**（行数、文件数、字节数、突变条数）→ **一律就地删除，不允许两个值并存**。理由是计量数没有「当时成立」的语义，它只是同一次测量的第二份副本；给它留一条更正行，等于承认两个值都有资格留在文档里。

校验：`python scripts/validate_kit.py .` → PASS (246 files checked)，11 项子检查全绿，exit 0；`python -m pytest tests -q` → 298 passed, 519 subtests；`git status --porcelain` 79 行，HEAD `d6eff20`；五条 AC 复跑 AC1=0 AC2=0 AC3=0 AC4=0 AC5=0。

### 9.10.12 REV-CHARTER-10：判据可检查，但被写在读不到它的地方

第十轮（fresh subagent `acdff5d7-26e6-425e-b30d-504b073211c1`，只读，窄范围 NF-04…NF-07 + 判据是否落地）仍判 `REQUEST_CHANGES`。四条里三条 `CLOSED`，NF-04 判 `PARTIAL`；但它真正指出的问题不在那四条里：

> 判据**可检查**（它按判据自己扫，就机械地扫出了结果），但**没落地**。判据写下的同一轮，读集里仍有 4 类、合计 16 处以上它自己判为非法的现状断言。

更根本的一层：这条判据只写在本文件里，`.charter/` 零命中。而 `.charter/project.md:45` 的不变量自己写着「规则必须写在下一会话会读到的文件里；写在读集之外的规则等于不存在」。**我立了一条规则，然后把它放在了它自己判为不存在的位置。**

| ID | 严重度 | 位置 | 是什么 | 处置 |
|---|---|---|---|---|
| NF-08 | P2 | 判据只在 `docs/SELF-AUDIT.md`；`lessons.md` 空 | 规则没有读集落点 | 规则本体进 `project.md` 不变量「会变的事实只有一个落点」；`lessons.md` 立 `LS-001` 只记代价与指针，不复制规则正文 |
| NF-09 | P2 | 读集 9 + 4 + 2 + 3 处计量数副本；`SELF-AUDIT:880` | B 类分界在它被写下的同一轮被违反 | 全部改指针，数值收进 `.charter/evidence/`（新增 pytest 与 template-budget 两份证据） |
| NF-10 | P2 | `handoff.md:23` | 把「PASS (246 files)」写成不变量 | 去掉数字，只留「exit 0 且无 side-effect 警告」 |
| NF-11 | P2 | `handoff.md:42`/`:43`/`:59` | 会变状态有 4 份副本，3 份没写重算子句 | 改指针 + 写明「本行随每一轮审阅回件重算」 |
| NF-12 | P3 | `handoff.md:35`、`current-task.md` Q1 | 现在时写工作区计数，下一步动作一动即过期 | 改基线指针 + 以 `git status --porcelain` 为准 |
| NF-13 | P3 | 本文件两轮记录里的聚合哈希 | 零改动锚点口径未记、不可复现（审阅者实测四种口径：537/500/491/356，无一等于记录的 354） | 可复现配方写进 `handoff` Capability notes；旧哈希标为不可复现 |
| NF-14 | P3 | `handoff.md:89` | 悬空指针「本文件 `.charter/records/` 指针」 | 改指 `:43` 与 `project.md:70` |

**这一轮学到的两件事。** 第一，**判据的可检查性不等于它的落地**：能机械扫出结果，只证明这条判据是个好工具；工具放在读集之外，下一会话根本不会拿它出来用。第二，**判据先要能判自己**：一条说「会变的事只能有一个落点」的规则，如果它的正文本身有两个副本（`SELF-AUDIT` 与 `lessons.md`），它就已经违反了自己。所以规则本体只留在 `project.md` 不变量，`LS-001` 只认领代价，并明确写「不重复规则正文」。

顺带解决一个 A/B 分界没答的格子（「记录正文里引用别轮计数算哪类」）：某一轮记录或日志里**自己那一次**的校验行，记的是那一次的观测，可以保留；**跨节汇总别轮**的数是复制，必须删。判例写在不变量里，今后不必再推。

校验：`python scripts/validate_kit.py .` → PASS (246 files checked)，11 项子检查全绿，exit 0；`python -m pytest tests -q` → 全绿（输出落点 `.charter/evidence/pytest-2026-10-19.txt`）；五条 AC 复跑全部 exit 0。

### 9.10.13 REV-CHARTER-11：修复自己制造的下游缺陷（行号也是一种会变的数）

第十一轮（fresh subagent `f645e7c3-94f9-4180-96a1-77ec6a5df994`，只读）判 `REQUEST_CHANGES`。七条里六条真关闭、NF-09 判 `PARTIAL`，AC 抽取规则的修复被判 `CLOSED` 并有反向对照作证；但它抓出四条新 finding，其中一条是 **P1，而且是我上一轮修复自己造成的**。

| ID | 严重度 | 是什么 | 处置 |
|---|---|---|---|
| NF-15 | P1 | 读集里 6 处「`project.md:70`」全部指向漂移后的另一行——`:70` 现在是 `SYNTHETIC` 格，真正的逐轮投影在 `:72`。成因：为写「会变的事实只有一个落点」这条不变量，我在 `project.md` 插了两行，把所有下游指针推歪 | 6 处改成**行标签寻址**（「第 4 节的 `INDEPENDENT_REVIEW` 行」+ 明写「按行标签定位，不按行号」） |
| NF-16 | P2 | `handoff` 的 Lessons 状态写成 `active 1 / LS-001（Hits 5）`，而本轮刚立了 `LS-002` | 改成「以 `.charter/lessons.md` 的 Entries 段为准」 |
| NF-17 | P2 | 基线计数「79 行 = 77 `M` + 2 未跟踪」在散文有两份副本 | 两处改成「见该文件首行注释，此处不复制」 |
| NF-18 | P3 | 证据文件里同一小节出现两次、逐行相同 | 合并，并留下「两次独立运行、输出相同」这一事实 |

**这一轮的模式是新的。** 前十轮是「投影停在一轮前」——某处状态没跟着更新。这一轮是：**修复自己制造了下游缺陷**。那些指针在写下的那一刻都是对的，坏掉不是因为有人写错，而是因为另一个文件多了一行。

所以处置不能是把 `:70` 改成 `:72`（那只是把这一次写对），而要把**寻址方式**换掉。行号也是一种「会随事件变化的数」：它复制到六处，就必然在某一处先漂。这与 `LS-001` 是同一个病灶，所以 `LS-001` 命中 +1（5 → 6），而不是新开一条——`lessons.md` 的「One pitfall, one entry」要求如此。

审阅者还给了一个可复用的动作：**反向对照证明修复非空转**。它把抽取规则改回旧写法（取最后一个反引号），在同一份未突变副本上 AC4 立刻变红（载荷 94 字节、exit 1），其余四条仍 0 —— 只有红没有绿不算跑过，只有绿没有红也不算。这与 `LS-002` 是同一条纪律的另一面。

校验（本轮终态）：`validate_kit.py .` → PASS (246 files checked)、11 项全绿、exit 0；AC1–AC5 按文档化规则全部 exit 0；`git status --porcelain` 79 行；HEAD `d6eff20`。新增 `.charter/records/REV-CHARTER-11.md`。已派 `REV-CHARTER-12`（窄范围：NF-09 残留 + NF-15…NF-18）。

## 9.10.14 第十二轮：行标签寻址的分水岭实验与「散文持有计量数」

`REV-CHARTER-12`（fresh 只读）判 `REQUEST_CHANGES`：`NF-16` / `NF-17` / `NF-18` 关闭，`NF-15` 与 `NF-09` 判 `PARTIAL`，另开 `NF-19` … `NF-22`。四条已全部处置。

### 这一轮最有价值的一步：把「行号 vs 行标签」变成可观测的分水岭

审阅者在副本里给首页文件顶部插一行空行，然后同时用两种寻址读同一个事实：

| 寻址方式 | 控制组（未突变） | 突变组（插一行） | 结果 |
|---|---|---|---|
| 行标签「第 4 节的 `INDEPENDENT_REVIEW` 行」 | 第 72 行，文本哈希 `aa2f8e43…` | 第 73 行，文本哈希 `aa2f8e43…` | 同一行、同一文本 → 绿 |
| 行号 `project.md:70` | `d258c24b…`（`SYNTHETIC` 行） | `ca7ab19d…`（`COMPONENT` 行） | 指向了别的事实 → 红 |

这不是「风格偏好」的论证，是一次对照实验：行号在插行后必然指向另一个事实，行标签不会。结论直接吃到 `LS-002` 的 Next defense（指针按行标签定位，不按行号）。

### 四处处置

| Finding | 问题形态 | 处置 |
|---|---|---|
| `NF-19` | 复用记录 `SR-01` 的指针格错到 Review B 行，且它自述的 `Exact query` 实跑 0 命中 —— 该 `MATCH` 用自身命令复现不出来 | 命令换成可复现形式（双引号包 Review A 的 grep）、指针换成行标签寻址、表下加更正行点名原值 |
| `NF-20` | 同一「子检查条数」两份散文副本，其中一处还自称「本行即全套计量数的唯一落点」 | 两处都改指针，删掉那句自称 |
| `NF-21` | 两处「散文持有计量数、证据零落点」（测试规模分解、章程文件体积） | 数字落进证据文件（pytest 证据加分解段、新建 `sizes-…txt`），散文只留指针 |
| `NF-22` | 突变计数与 per-AC 分项是跨节汇总别轮观测的散文复制 | 只留指针到证据文件的 `## Mutations` 段 |

### 这一轮暴露的新病灶：修复按「点名」而非按「形态」

审阅者在六件读集里只剩一处 file:line 指针，而那一处恰好是最早写下、从未被任何一轮点名过的地方。前十轮的处置都是「把被指出的行号改成标签」，没有一轮做过「扫一遍还有没有行号」。所以这一轮我把机械扫描写进复核动作：用一条 grep 同时扫六件读集，判读规则是「命中项只允许是更正行里记录的原值」。

实测（本轮处置后）：六件读集里 file:line 命中 1 处，即 `reuse-discovery.md` 的更正行 —— 它按 A 类惯例点名被更正的原值，属允许项；其余五件命中 0。计量数（子检查条数 / 测试条数 / 章程字节数 / 收集总数）在读集散文里命中 0，全部只在 `.charter/evidence/` 下。

### 结论

这一轮没有新规则，只有两个动作模式的修正：指针一律按行标签寻址（已有实验作证）、复核一律先机械扫全量再抽查。`docs/SELF-AUDIT.md` 正文自身的 file:line 指针未被本轮裁定覆盖（审阅者明确列为未验），它是下一个候选面。

## 9.10.15 REV-CHARTER-13：把「会随一次普通改动而变的数」当一整类清掉

`REV-CHARTER-13`（fresh 只读 `f2ead4b5…`）判 `REQUEST_CHANGES`：`NF-19` / `NF-20` / `NF-21` / `NF-22` 四条全部 `CLOSED`、上一轮的 `NF-15` 转 `CLOSED`；`NF-09` 仍 `PARTIAL`，新开 `NF-23` / `NF-24` 两条 P3。

它这一轮最有价值的两件事：

1. **把「行标签 vs 行号」做成可判定的实验**：在仓库副本顶部插一行空行，行标签仍解析到同一段文本（哈希不变），而行号 `project.md:70` 从 `SYNTHETIC` 漂到 `COMPONENT`、`:72` 从 `INDEPENDENT_REVIEW` 漂到 `INTEGRATED`。上一轮的修法因此从「一个说法」变成「一个已验证的机制」。
2. **把缺陷类从「被点名的行」提回「类」**：它没有停在「上一轮那四处都修了」，而是顺着判据继续扫，扫出两个同类未修项 —— 体积阈值行持有 `18,432` 而无指针（`NF-23`），读集散文里以现在时持有可变文件数（`NF-24`）。

**处置**：`NF-23` 删掉字面量只留指针（数字落 `template-budget-2026-10-19.txt`）；`NF-24` 新建 `.charter/evidence/inventory-2026-10-19.txt` 承载四个计数 + update rule，读集里删数字只留指针。顺带把同一形态的中文计数一次清掉：`一处改动五份一起改`、`六件启动读集`、`十件工作集`、`十件模板` 全部改成不带数的表述。

**这一轮写下的判准**（这是 `NF-09` 第三次被判 `PARTIAL` 才逼出来的）：**计数若会随一次普通改动而变，就不能以现在时留在读集散文里。** 它只有两个合法形态 —— 指向 `.charter/evidence/` 的指针，或历史叙述（记录某一次运行、某一轮判定）。判准的关键在于「会随什么变」这个问题：答得出来的一律搬走，答不出来的（如某轮自己的判定条数）允许留在原地。

**为什么这一轮不是改数字而是建证据文件**：这些数字写在枚举前面，读者会以为枚举与数字互相印证；但枚举变了数字不会跟着变 —— 它们是两份事实，只有一份会被想起来更新。把数字搬进证据文件后，「谁该在什么时候重算它」第一次被写下来。继续把数字改准，只把它写对一次，改不了它下次会错。

**本轮实测**：`AC1`–`AC5` 全 `exit 0`；`python scripts/validate_kit.py .` → `PASS (246 files checked)`、`exit 0`；锚点成对哈希与上一轮逐字节相同（`git ls-files -s` `d534ad515ce454d1…` 34,241 B、`git status --porcelain` `483cea696dfdb171…` 4,816 B）；`inventory` 四个计数实测 `10 / 5 / 7 / 10` 与证据文件一致。

**仍开着的**：`NF-09` 待 `REV-CHARTER-14` 判定能否转 `CLOSED`；`docs/SELF-AUDIT.md` 正文自身的约 94 处 `file:line` 指针与其中的计量数，审阅者明确列为未验 —— 它是下一个候选面，但要先决定一件事：这份报告算「读集」还是「历史档案」。

## 9.10.16 REV-CHARTER-14：判准本身被判，行级豁免的漏洞

`REV-CHARTER-14`（fresh 只读 `dedec5d6…`）判 `REQUEST_CHANGES`：`NF-23` `CLOSED`；`NF-24` 判 `NOT_CLOSED` 并上调 P2（读集仍有三处现在时可变数）；`NF-09` 保持 `PARTIAL`；**判准本身被判不合格**，新开 `NF-25` / `NF-26` / `NF-27` / `NF-28`。

它做的一件我自己没做的事：把上一轮写下的判准当成被测对象，逐字实现了一遍，发现它过宽（72 个候选，多为「一个 / 一次」这类指称）、过窄（标题与派单把它收窄成「可变文件数」，条数 / 行数 / 个数 / 字节数 / 测试数全在判准外）、过强（与 `portable/templates/lessons.md` 的 `Hits` 字段冲突）、同类不同处置。

**它揭出的真正机制**（本轮最重要的一条）：我的豁免是**行级**的 —— 一行里只要出现 `REV-` id，整行的裸数字都被放过，而 `project.md` 的投影格正是一行装下整条审阅链。它用 C4 / C5 两个控制组把这条区分出来：同句带 id 不报、同句无 id 报。处置是把豁免从行级收到**子句级**。

**处置**：判准从一句散文改写成三问（数得出来的量 / 会变的状态 / 某一次运行的观测）+ 两条豁免（E1 计数器自属、E2 结构常量）+ 投影例外 + 适用范围；三处残留改指针或去量化；`docs/SELF-AUDIT.md` 的第二落点改指针。

**这一轮的教训可以压成一句**：一条判准如果只能由写它的人来执行，它就是一条自述。判准必须写成第三人能机械执行、并且能判自己的形式 —— 而判自己的第一步，是有人拿它去扫一遍写它的人没扫过的地方。

**本轮实测**：`AC1`–`AC5` 全 `exit 0`；`validate_kit.py .` → `PASS (246 files checked)`、`exit 0`；四计数实测 `10 / 5 / 7 / 10` 与 `inventory` 一致。
## 9.10.17 REV-CHARTER-15：判准第三次被测，门禁盲区被记成决定

`REV-CHARTER-15`（fresh 只读 `b911224f…`）判 `REQUEST_CHANGES`：`NF-23` `CLOSED`；`NF-24` 仍 `NOT_CLOSED`（P2）；`NF-09` 仍 `PARTIAL`（P1）；`NF-25` / `NF-26` 仍 `PARTIAL`；新开 `NF-29`（口径未定义）、`NF-30`（派单行把已修项当现存缺陷 + 反引号奇偶错导致小标题被吞）、`NF-31`（子句级豁免仍可搭便车）、`NF-32`（证据落点自身过期在门禁外）、`NF-33`（证据小节重复追加未合并）。

**它做到的、我没有做到的事**：上一轮我把判准写成了三问 + 两条豁免，并用散文描述自己扫过的结果。它把那条不变量**逐字实现成一个扫描器**（Stage 0 程序跨度掩码 → Stage 1 日期 / 时间 / id / sha / 版本 / 文件名 / 行引用 / 节引用 / 比值掩码 → Stage 2 数字 + 量词候选 → Stage 3 ③ 问豁免算两遍：paren-aware 与 flat 从句 → Stage 4 E1 / E2 不自动豁免），跑出 `TOTAL=69 LIVE_paren=41 LIVE_flat=47`，按文件分布 `project.md` 18 / `current-task.md` 7 / `lessons.md` 5 / `reuse-discovery.md` 4 / `handoff.md` 4 / `roadmap.md` 3，其中真违规 13、`E2` 豁免 17、误报 11。

**它的结论比命中数更重要**：判准**可判定**了（第三人能执行），但**不合格**（执行出来的绝大多数不是真缺陷）。而唯一真正会误导的两项是 `handoff.md` 的实测耗时与外层预算毫秒数 —— 恰是 ① 问类目当时漏掉的「实测值」这一类。

**处置（全部落盘）**

| finding | 处置 |
|---|---|
| `NF-09` P1 | D-01 行改纯指针；Subprocess 行只留指针；另把 `project.md` 的 R1.3 投影行与 `handoff.md` 的 D-01 待决行改成「阈值是规则参数 + 定义在哪 + 换算值在哪」。至此 36 KB 只出现在 `current-task.md` 的 Bounded size 条款里 —— 那是规则自己的定义处，不是副本 |
| `NF-24` P2 | 不追被点名的短语，改整格重写投影格、D-01 改纯指针、inventory 重写口径 |
| `NF-25` P2 | 投影格整格改为逐轮枚举（每轮一句判词 + 一句该轮病灶），不出现任何汇总量与聚合词 |
| `NF-26` P2 | 判准 v3：① 问补入实测耗时 / 实测退出码 / 实测比值 / 阈值换算出的字节数；③ 问豁免只覆盖紧跟其 id 或时间戳的那一个观测；新增聚合词规则（合计 / 共 / 另有 / 其余 / 累计 / 加上 / 总计 一经出现即取消豁免）与多 id 规则（两个以上 id 同句只覆盖各自那一次观测，跨轮相加的数不豁免）；`E2` 扩为「结构常量与规则参数」并加前置条件——同一行或同一格必须能指出定义位置 |
| `NF-29` P3 | inventory 重写：count basis 定义为「该行写的 glob，非递归，排除隐藏文件」，并写明它刻意不是「the working set」（那个说法没有定义），另注明 `evidence/`、`records/` 与日志不匹配任何 glob |
| `NF-30` P2 | 派单行重写；六个读集文件反引号奇偶自检，现全部为偶数（`project.md` 656 / `handoff.md` 288 / `current-task.md` 450 / `roadmap.md` 212 / `reuse-discovery.md` 258 / `lessons.md` 42） |
| `NF-31` P2 | 用聚合词规则与多 id 规则正面处理，并重写投影格本身。**不声称这一类已关闭**，`REV-CHARTER-16` 被要求重跑 C5b / C5c |
| `NF-32` P2 | 不静默保留：记成决定 `D-07`（`OPEN`），问题本身（校验落在套件自检还是 D-05 的下游校验器）待裁，E1 / E4 两个探针写成实证 |
| `NF-33` P3 | 两段重复小节合并为一份并加注；`The 22-row table above` 改为 `The table above` |

**这一轮浮出的三条模式**

1. **豁免的范围只能和它计量的单位一样窄**。行级 → 子句级是上一轮的修法，本轮证明仍然可以搭便车（同句带 id 让相邻的跨轮汇总量借到豁免；整句聚合直接过）。继续收窄「子句到哪里结束」不会收敛；聚合词本身就是豁免不应覆盖的信号，把它列成清单才可判。
2. **只写参数名、不写定义位置的指针，仍然是复述**。`36 KB` 在 D-01 行出现两次却无法被读者核对 —— 它在散文里既像参数又像结论。改成「参数名 + 定义在哪个文件哪一处 + 换算值在哪个证据文件」，同一句话才既能被判准检查也能被第三人复算。
3. **门禁的盲区只能被记成决定，不能被宣布修好**。证据文件自己过期（E1）、glob 型计数变化（E4）都不会让 `validate` 变红；本轮能做的是把它写成 `D-07` 并附实证。写「已修复」是这一条链上被抓过四轮的缺陷类型（处置表说已落地、产物里没有）。

**本轮实测**：`AC1`–`AC5` 全 `exit 0`；`python scripts/validate_kit.py .` → `PASS (246 files checked)`、`exit 0`；锚点成对哈希与上一轮逐字节相同（`git ls-files -s` `d534ad515ce454d1…` 34,241 B、`git status --porcelain` `483cea696dfdb171…` 4,816 B）；porcelain 79；HEAD `d6eff20`。

**仍开着的**：`NF-09` 能否转 `CLOSED` 待 `REV-CHARTER-16` 判；判准的命中精度（41 项里只有 1 项真误导）没有处置，它对应的是 `D-07` 那条待裁；`docs/SELF-AUDIT.md` 正文自身的 `file:line` 指针与其中的计量数仍未裁定归属（读集还是历史档案）。

## 9.10.18 REV-CHARTER-16：判准不可区分，与「修复动作在 A，损坏落在 B」

`REV-CHARTER-16`（fresh 只读，仓外副本自证 547 文件 sha256 前后 diff 0 行、porcelain 79 行同哈希、HEAD 未变）判 `REQUEST_CHANGES`：`NF-25` / `NF-29` / `NF-30` / `NF-32` `CLOSED`；`NF-09` / `NF-24` / `NF-26` `PARTIAL`；`NF-31` / `NF-33` `NOT_CLOSED`。六条新 findings：

| id | 一句话 |
|---|---|
| `NF-34` | `ac-liveness` 的 REV-14 段落只删了第二个标题，正文仍是两份（并注着「Merged into one copy」） |
| `NF-35` | `handoff` 的 Open 行仍枚举 `D-01…D-05`，缺 `D-06` / `D-07` —— 今天就是错的 |
| `NF-36` | 四处证据行逐字复述实测退出码，同行注却写「本行不计数」 |
| `NF-37` | `LS-002` 的数字靠一串非相邻 id 借豁免 |
| `NF-38` | 判准 v3 的聚合词规则是子句局部；聚合词搬进无数字子句即全句豁免（C5b 1/2、C5c 1/1、C5e 0/2） |
| `NF-39` | 「20 分钟 / 6 条具名查询」在两份读集各写一次、互不指向 |

**处置**：`NF-34` 正文真合并（注写明两次独立运行除时间戳外逐行相同）；`NF-35` 改指针不枚举；`NF-36` 四处删掉 exit 数字；`NF-37` 只留因果；`NF-39` 第二个落点改指针。`NF-38` 把判准升到 v4，给自己认定的三处模糊各写一条硬边界：

1. **紧跟** = id / 时间戳与数字间不超过 24 个字符，且不跨越句号、分号、问号、叹号。
2. **子句** = 同一行内以句号、分号、问号、叹号、逗号、破折号切开的片段，**括号不外切**。
3. **聚合词同线即取消** = 合计 / 共 / 另有 / 其余 / 累计 / 加上 / 总计，或「两类」「三条」这类计数名词，只要出现在同一行任何位置，该行全部 ③ 问豁免作废。

第 3 条是这轮唯一有理论含量的改动：前两轮都在收窄「豁免覆盖到哪里」（行级 → 子句级 → 24 字符），而审阅者每轮都能把聚合词搬到规则没看的那一侧。结论是**聚合词不是位置问题而是信号问题**——它一出现，这一行就不该享受「单次观测」的豁免，因为它把多次观测合成了一个没有人能核对的新数。判准里能写的只有「同线即取消」，写不出「哪个子句之外的聚合词不算」。

**本轮自己抓到的自伤（审阅者未指出）**：第 15 轮重写 `project.md` 第 4 节成功等级表的 `INDEPENDENT_REVIEW` 行时，把整行改成了表外段落，并丢掉轴名，把一张表切成两半。`validate_kit.py` 与五条 AC 全绿，因为两者都不读章程的表格结构。

这类与 `NF-15`（行号漂移）同族而方向相反：`NF-15` 是指针指向了别处，这次是指针所指的容器被改坏。共同点值得单独记：**修复动作发生在 A 处，损坏落在 B 处，而门禁只看 A**。所以「修完跑绿」这件事对这类缺陷零信息量——它和「没改过」在门禁眼里一样。

**这一轮的实测**：`AC1`–`AC5` 全 `exit 0`；`python scripts/validate_kit.py .` → `PASS (246 files checked)`、`exit 0`；锚点与上一轮逐字节相同（`git ls-files -s` `d534ad515ce454d1…` 34,241 B、`git status --porcelain` `483cea696dfdb171…` 4,816 B / 79 行）；HEAD `d6eff20`。六份读集反引号全部偶数（project 664 / handoff 298 / current-task 450 / lessons 40 / reuse-discovery 260 / roadmap 212）。

**仍开着的**：`NF-09` / `NF-24` / `NF-26` / `NF-31` 仍是 `PARTIAL` / `NOT_CLOSED`，等 `REV-CHARTER-17` 判；`D-07`（证据文件自身过期与 glob 计数变化不在门禁内）仍是 `OPEN`，E1 / E4 两个探针今天仍全绿；`docs/SELF-AUDIT.md` 正文自身的 `file:line` 与计量数归属仍未裁定。

## 9.10.19 REV-CHARTER-17：判准撤回 —— 三次机械化失败之后的收敛

`REV-CHARTER-17`（fresh 只读，仓外副本自证 548 文件清单前后 diff 0 行）判 `REQUEST_CHANGES`，并给出这一句：**这条判准现在不能判自己**。

| 检查项 | 判定 | 实测 |
|---|---|---|
| `NF-09` / `NF-24` / `NF-26` / `NF-31` | `PARTIAL` ×4 | 前一轮点名的 5 处阿拉伯数字确已改指针；但同类病灶以**中文数词**存活；`六条` 与同条 `Evidence` 枚举的 8 个 id 已不一致 |
| `ac-liveness` 的 REV-14 单份正文 | `CLOSED` | 该段 = 标题 1 + 一张 5 行表 + 一对 anchor + 一条合并注 |
| 第 4 节 `INDEPENDENT_REVIEW` 表格行 | `CLOSED` | 每行 pipes=5 / cells=4，表未被切，轴名齐全 |
| 判准 v4 自判 | **失败** | 8 个自造探针：5 漏、2 假阳；P2 / P5 在两种忠实读法下判定相反 |

**三种失败形状分属三轮**：v2 豁免按行（一行里出现 id，整行的数全放过）、v3 收窄到子句（聚合词搬进无数字子句即全句豁免）、v4 写三处硬边界（跨行聚合、括号内数字、两种读法相反）。加上中文数词兼作冠词，这条路线到此为止：

1. 中文数词兼作冠词（「一个」「一次」「一种」），词法判不出是在计数还是在指称；
2. 「同一事实」是语义概念，聚合、跨行、括号是它的变形而不是枚举；
3. 同一段条文在两种忠实实现下给出相反结论 —— 判准的实际判决力来自实现者的分类器。

**处置：撤回机械判据**，不写 v5。不变量里 ① / E1 / E2 / ③ 判定程序整段删除，改为一句「这条不变量由 Review A 判，不由扫描器判」+ 三轮失败形状 + 记成 `D-08`（`OPEN`）。缺口没有藏：`D-07`（证据文件可自证）与 `D-08`（读集数值副本无机检）都开着，`LS-003` 记下「把治理规则写成散文判据并期待机检」这个坑与唯一出路——**闭集可机检，会变的量只有「一处存放 + 人判」或真校验器两条路**。

同时按 `NF-45` 立了一条新纪律并当场执行：**任何处置行必须写「如何在产物里验证」（命令 + 期望输出），写不出的当场改判 `NOT_CLOSED`**。`REV-CHARTER-17` 的处置表是本链第一张每行都带验证列的表。

内容漂移也照实清掉（`NF-40`）：`两条 blocker` → 「当时的 blocker 全是」、`六条同族 finding` → 「同族 finding」、`连续五轮` → 「连续多轮」、`三类成因` → 「成因包括」。

**本轮实测**：`AC1`–`AC5` 全 `exit 0`；`validate_kit.py .` → `PASS (246 files checked)`、`exit 0`；锚点与上一轮逐字节相同（`d534ad515ce454d1…` 34,241 B、`483cea696dfdb171…` 4,816 B / 79 行）；HEAD `d6eff20`；六份读集反引号全偶数（project 674 / handoff 300 / lessons 56）。

**留下的代价，明写**：读集里的中文数词计数从今天起没有机器拦，只能靠每轮 Review A 手工扫。下一轮审阅者若仍扫出活的副本，那是 `D-08` 的实证，不是新缺陷类型——这条判据不再迭代。

## 9.10.20 REV-CHARTER-18：撤回只收敛了一半，抓到一个在伪造结论的执行方式

`REV-CHARTER-18`（fresh 只读，仓外副本 `_rev18` 自证 549 文件、`diff -r` 零差异）判 `REQUEST_CHANGES`，对主问题的判词是 **收敛了一半**：承认不可机检是真收敛（v4 程序整段删净、无活悬空引用、`D-08` 没写成已解决、`LS-003` 不是重复造条），但没交出「谁在哪一步看什么」——`review.md` 的 `CHK1`–`CHK13` 没有一项覆盖「读集只写指针」，所以「由 Review A 判」当时是一句**指不到任何检查项的口号**。

它同时抓到撤回过程本身新增的两处「说已落地、产物里没有」：`D-07` / `D-08` 行各 6 格而表头 5 格（渲染后 State 列变成 `YG`，决定表里读不出 `OPEN`）；`E1 计数器自属` 豁免随 v4 一起消失，使 `lessons.md` 的 `Hits` 变成规则明文禁止却在读集使用的活副本。

| 处置 | 结果 |
|---|---|
| `NF-47`：门指名到检查项 | `review.md` 新增 `CHK14`、`contract-migrations.md` 的 Checks 表加行、`project.md` 第 4 节与不变量末句点名 |
| `NF-46` / `NF-51`：决策表列数 | 两行重写为 5 格，settle 格由「已采证据」改成结算条件；新开验收项 `AC6` 机检列数 |
| `NF-48`：`Hits` 冲突 | 不变量补「计数器自属」与「边界」（规则参数、结构常量不算计量副本） |
| `NF-49`：投影清单 | 第 2 节清单改为实际集合、声明 `handoff` 不持有取值；`handoff` 的 gate 与 pytest 两行改指针 |
| `NF-50` / `NF-52` / `NF-53` / `NF-54` | 结算条件与已采证据分离；处置纪律补「属性为假时必须失败、断言结构而非子串」；`REV-CHARTER-17` 表格竖线转义（只改渲染）；四处活副本分别落位 |

**本轮最重要的发现：我的执行方式在伪造结论。** 用 `subprocess.run(payload, shell=True)` 跑多行 `python -c "…"` 载荷时，Windows 上 shell 解到 `cmd.exe`，多行载荷被静默丢弃、stdout / stderr 全空而**返回码是 0**。也就是说此前那些「验收项全 exit 0」里有假绿（`AC1` / `AC2` / `AC3` / `AC6` 都是多行载荷）。改成走 stdin（`[sys.executable, "-"]` + `input=`）后，`AC6` 立刻打印出真实表头与逐行格数。记入 `LS-002`（命中 4 → 5）。

这一条与 `LS-002` 已记的假红是同一件事的两面：**执行器坏掉时两个方向都会伪造结论**，而绿的那一面更难发现——因为它符合期望。旁证：同一条 `M1` 突变（决策表多一格），旧执行方式得 **0**、新执行方式得 **1**。

七条突变的活性矩阵（每条施加后立即还原，还原后 tree 逐字节相同）：`M1` 决策表多一格 → 只有 `AC6` 红；`M2` 叶 Status 改 `PASS_CLOSED` → 只有 `AC1` 红；`M3` roadmap gate 改 `COMPLETE` → 只有 `AC3` 红；`M4` 新建 `docs/other-probe.md` → 只有 `AC2` 红；`M5`（控制组）新建 `.charter/probe-allowed.md` → 全绿；`M6` 破坏镜像 → 只有 `AC4` 红；`M7` AC5 里的 SHA 改 `deadbeef` → 只有 `AC5` 红；baseline 与还原后全 0。

**范围是这一轮唯一的扩张**：`NF-47` 要求改 `portable/` 模板，而本叶原范围只有 `.charter/**` 与 `docs/SELF-AUDIT.md`，`AC2` 因此如实变红（不是误报）。按叶的 Ruling 协议记了一条：Allowed paths 增加两个模板文件、两个 target 镜像与 builder 生成物；基线随之重新生成（`# diff-sha256: 3483dd379a600563…`，仍是 79 行 = 77 `M` + 2 `??`）。

**这一轮实测**：`AC1`–`AC6` 全 `exit 0`（stdin 执行）；`python scripts/validate_kit.py .` → `PASS (246 files checked)`、`exit 0`；`python -m pytest tests -q` → 298 passed, 519 subtests（145.14s）；HEAD `d6eff20`；`.charter/records/` 现有十二份审阅记录。

**仍开着的**：`NF-09` / `NF-24` / `NF-26` / `NF-31` 仍未全关（`D-08` 覆盖「缺机检」，覆盖不了「规则自相矛盾」与「状态副本不在清单」，后者已按 `NF-48` / `NF-49` 改掉）；`D-07`（证据文件自身过期）与 `D-08`（读集数值副本没有机检）仍是 `OPEN`；条款仍等 `REV-CHARTER-19`。

**给下一轮的一句话**：这一轮新增的两个门（`CHK14` 与 `AC6`）是不是真门，唯一的检验方式是有人造一次反例看它红不红——所以下一轮的主判定只需要问这件事，不必再重验已经 `CLOSED` 的九条。

## 9.10.21 REV-CHARTER-19：门加上了，但输入、集合、红的机会三样都缺一样

`REV-CHARTER-19`（fresh 只读 subagent，实验全在仓外副本内做）判 `REQUEST_CHANGES`。上一轮新增的两个门得到不同判定：`AC6` 是**真门**（它亲手做了五个突变：加一格 / 删一格 / 子串陷阱都只红这一条，只改单元格文字的控制组保绿），`CHK14` 只能算**半真门**。

### 四条 finding 与处置

| id | 病灶的一句话 | 处置落到哪一层 |
|---|---|---|
| `NF-55` | **名字对了，集合不对**：章程声明「唯一投影是第 6.1 节的 gate 与 freshness 两行」，但第 1 节 gate 行、第 6.1 节 RD 行、`handoff` 的 RD 与候选版本都不在清单里；而 `AC3` 用 `re.search` 只取**首个**匹配，恰好是第 1 节那一处 → 改第 6.1 节时六条 AC 全绿 | 判据层：`AC3` 改成逐点断言（四个 gate 点 / 三处 freshness / 三处 RD，每个标签按行标签恰好命中一次、值必须同一、gate 还在枚举内）；声明层：章程第 2 节的投影清单改为逐点名单；取值层：`handoff` 不再持有 RD 与候选版本 |
| `NF-56` | **修复改变了被验证对象**：`AC6` 数裸竖线，`REV-CHARTER-17` 处置表为渲染加了转义 → 同一条命令成了两个断言（raw 源形态实测 287 行、渲染形态 1 行）；反方向也成立，合法转义 `Y\|G` 让 `AC6` 假红 | 判据层：`AC6` 改为转义感知逐字符计数；记录层：那两条命令改成不含竖线的 `python -c` 写法（用 `chr(124)` 数行）；纪律层：章程第 2 节写死「命令里不许出现裸竖线」，并点名这是"为了让表格好看"顺手改坏断言的实例 |
| `NF-57` | **自证机制对所证对象全盲**：`.charter/` 未跟踪，`git ls-files .charter` = 0、`git status --porcelain` 只有一行 `?? .charter/`；删掉记录里十行后，章程规定的成对锚点一字未变。而 `handoff` 恰好**禁止**用能覆盖它的自建遍历 | 锚点改三段：① `git ls-files -s | sha256sum`；② `git status --porcelain | sha256sum`；③ `cd .charter && find . -type f -name '*.md' -print0 | sort -z | xargs -0 sha256sum | sha256sum`。原禁令不是错，但它只否定了「口径不可复现」的自建遍历，没给出替代品 —— 于是留下一块盲区。修法是把口径写死到可以逐字重放，而不是取消覆盖 |
| `NF-58` | **门要求一句答案，却没有一步要求谁交出它**：叶合同里 `例外/exception` 命中 0；18 份记录只有 4 份带 `## Checks performed`，造出 `CHK14` 的那一轮自己也没有；删掉一份记录的整段后 validate 与六条 AC 全绿 | 模板层：`## Checks performed` 改成必填段，缺段则该记录标 `INVALID`；规则层：`CHK14` 第三子句的输入生产者改为审阅记录自己（无例外必须写 `Exceptions claimed: none`）；机检层：新增 `AC7`（序号 ≥19 的记录必须含该段，且段内点名 `CHK14`） |

### 活性（实测，每次施加后按字节还原，还原后全 0）

| 场景 | 期望 | 实测 |
|---|---|---|
| baseline | 七条全 0 | `AC1`…`AC7` 全 0 |
| M1 只改第 6.1 节 gate | 只有 `AC3` 红 | `AC3`=1，其余 0 |
| M2 `D-03` 的 Owner 写合法转义（渲染仍 5 格） | 全 0 | 全 0 |
| M3 给 `D-01` 多加一格 | 只有 `AC6` 红 | `AC6`=1，其余 0 |
| M4 删掉 `REV-CHARTER-19.md` 的 `## Checks performed` 整段 | 只有 `AC7` 红 | `AC7`=1，其余 0 |
| M5 同上，看三段锚点 | ③ 变、①② 不变 | ③ `76a43552…` → `016c1b41…`，①② 逐字节相同 |

### 这一轮自己踩到的工具坑（两次都是「检查器先骗了我」）

1. `AC7` 第一版用 `t.find` 找 `## Checks performed`，把正文里**被反引号包着的同一串**当成了标题 → 删掉真段仍然绿；再版用 `re.search` 时把 `h.end()` 当成 `flags` 传（Python 三参数签名的第三个位置是 flags，不是 pos）→ 段落在标题之前、切出空串。两处都靠「先让它必须变红」的对照才发现。这与 `LS-002` 是同一条：检查器会双向伪造结论，假红和假绿一样要证伪。
2. `AC3` 的取值要先按全角括号截尾、再取 ` / ` 之前的一段 —— 第 6.1 节那行是 `PENDING / 2026-10-19`，只截括号会把日期并进取值，变成第四次「同名不同值」。

### 一条可以推广的判据

这一轮的四个病灶指向同一件事：**加一个门的那一刻要同时回答三个问题，缺任何一个它只是文本**——

1. 谁交出判断所需的输入？（`NF-58`：没有生产者 → 门永远不会被真的执行）
2. 判据覆盖的集合与规则声明的集合是否同一个？（`NF-55`：声明四点的，断言只取一点）
3. 它在什么情况下会红，那个情况能否被真的造出来？（`NF-56`：口径互斥，造出来的红是假的）

附带第 4 问：**用来证明「没人动过它」的机制，覆盖范围是否包含被保护的东西本身**（`NF-57`：锚点覆盖 tracked，治理集 untracked）。

## 9.10.22 REV-CHARTER-20：不再逐条修，改成「一条规则一个实现」并封存审阅链

`REV-CHARTER-20` 的判词是 `REQUEST_CHANGES`，主判定一句话：**天平仍偏向「按点名修」**。按形态修的只有两处（`AC6` 的转义感知量具、`AC3` 的逐点断言）；其余五点仍是「改被指出的那一行」——同形态的六处取值副本可以被改成互相矛盾而七门全绿，兄弟量具 `AC1` 仍在裸切格并会假红，只读锚点只盖 `*.md` 所以删掉一份证据文件三段锚点一字不变，删掉 `CHK14` 那一行门照样绿。它的原话是「前十九轮的病灶没有被消灭，只是被挪到了没点名的地方」。

### 这一轮换的不是修法，是所有权

二十轮里同一个病灶换十几个位置被点名，每轮我只修被点名的那一处。根因不是懒，是**判据没有单一实现**：同一条规则既写在叶合同的验收项里（内联 `python -c`），又隐含在别处或根本不存在，于是「改一处、另一处照旧漂」，而每一处单独看都是绿的。

处置是把判据的所有权收进一个文件：

| 做法 | 落点 | 它解决的问题 |
| --- | --- | --- |
| 全部可机检判据只实现一次 | `.charter/checks.py`（`AC1`…`AC9`，`--only <id>` 单跑，`--anchor` 出三段锚点） | 同一个判据不再有两份实现 |
| 验收项载荷只许委托 | 叶合同九条 `check:` 全写成 `python .charter/checks.py --only ACn` | 「修一处、另一处漂」失去载体 |
| 抽取规则本身被机检 | `AC8`：每块恰一个 `check:` 标签、载荷不含裸竖线 | 上一版这条纪律只有规定、零生产者（`NF-61`） |
| 不许内联被判据机检 | `AC9`：载荷必须精确等于委托形式 | 防止下一轮又出现第二份实现 |
| 本叶三行复用取值并入 `AC3` | material / coverage-result / final route 对权威记录 | `NF-59`：六处副本可改成互相矛盾而全绿 |
| 例外必须结构化 | `AC7`：`CHK14` 行恰一行且含 `item` / `clause` / `basis` 或 `Exceptions claimed: none` | `NF-62`：存在性断言冒充实质断言 |
| 锚点覆盖全部治理文件 | 锚点 ③ 不再按扩展名过滤 | `NF-60`：删掉一份证据文件锚点不变 |

### 活性矩阵（每次施加后按字节还原，树哈希前后相同）

| 突变 | 只跑 | 观测 |
| --- | --- | --- |
| 叶 `Status` 改 `PASS_CLOSED` | `AC1` | 红 |
| 一个 gate 点改 `COMPLETE` | `AC3` | 红（值不同） |
| 一条搜索记录 `Result` 改 `NO_MATCH` | `AC3` | 红（本叶 coverage 对不上） |
| 决策表某行多一格 | `AC6` | 红 |
| 删 `CHK14` 那一行 | `AC7` | 红 |
| 再写一个 `check:` 标签 | `AC8` | 红 |
| 载荷换成内联 `python -c` | `AC9` | 红 |
| 新增白名单外文件 | `AC2` | 红 |
| 新增白名单内文件（控制组） | 全部 | 绿 |

计数、退出码与三段锚点的具体值只落 `.charter/evidence/ac-liveness-2026-10-19.txt`（本节不复述——这正是 `LS-001` 的代价）。

### 封存：没有 `APPROVE`，不许写成「已解决」

按用户指示（「不要像打地鼠一样」）不再派 `REV-CHARTER-21`。链封存的事实必须写成事实：**章程级链没有拿到过 `APPROVE`**。`REV-CHARTER-20` 的 `REQUEST_CHANGES` 只是被部分消解——六条 findings 处置了，但「同形态还有没点名的地方」这一类风险不会消失，它只是被换成了结构（单一实现 + 机检 + 全覆锚点 + 结构化例外）。因此新增决定 `D-09`：封存本身需要 YG 裁决，选项是「接受带限度的封存」或「另起一次独立复验」。

顺带一条教训（已立 `LS-004`）：**一条规则两份实现**，是二十轮里最贵的一个病灶形态。判据要只有一个实现，否则每一次修都只是在给漂移换位置。

## 9.11 P1-3 回滚：删掉读集增长规则（2026-10-19，用户裁决）

用户原话：「把P1-3回滚回去」。

`P1-3` 从头不是用户批准的条目：m00600 的裁决里它在「不做」一栏，是我在 m00737（稳定性判据）之后自行改判为「做」的，形态又从「绝对字节上限」改成「成长形态 + 扇出触发」。它落地三处：

- `DEVELOPMENT_CHARTER.md` §7 的读集增长规则（实体型 / 历史型、历史型不进读集、扇出触发 60 / 12、判据用行数不用字节、拆分不是删除）；
- `portable/templates/roadmap.md` 首段的 `Growth` 引线；
- `portable/templates/project-charter.md` §10 末尾指向 §7 的那句话（`P1-2` 落地时加的指路）。

三处连同两个实例副本 `.charter/roadmap.md` 与 `.charter/project.md` 的同名内容全部删除。

保留一处并说明理由：`portable/references/contract-migrations.md` 的 `### Renamed members` 表（`APPROVED → DECIDED`）。它服务的是 `P1-2` 的枚举改名——归档记录里的旧名必须仍有解释，否则迁移表断掉一条；当初把它记成 `P1-3` 的产物是记账错误，回滚不该连带删掉另一条已批准条目的迁移记录。

回滚的连带成本（如实记录）：

- 三份手工源 + 两个 target 树的镜像 + 三次 builder `--sync`（codex / zcode / dsh），因为镜像纪律是字节一致；
- 叶合同 §4 再增三份手工源，§6 记一条 Ruling（回滚不在原叶范围内）；
- `AC2` 基线第二次重算：`# diff-sha256:` 由 `3483dd37…` 变为 `512cb8ca…`，行集不变（79 行 = 77 ` M` + 2 `??`）；
- 回滚之后「读集里三件无上限」这个缺口回到原位，且**此前没有决策行跟踪它**（`D-01` 管的是模板体积阈值，不是读集增长）。按章程「一个 agent 看不见的否决，就是它会重新提一遍的否决」的同一条道理，缺口也必须有一行看得见：本轮新增 `D-10`。

校验：`.charter/checks.py` 九条全 `ok` / `RESULT PASS`；`validate_kit.py .` exit 0；`pytest -q` 全绿（输出与条数只落在 `.charter/evidence/` 下的两份证据文件，本节不复述会变的数）。

## 9.12 YG 追认 `P1-1`，净在册 15 条（2026-10-20）

18 条面板的裁决里，`P1-1` 属「待定」两条之一（另一条是后来撤回的 `P0-2`）。我在批 6 判做并落地，这是**偏离裁决**：裁决「不定」，动作「做」。YG 于 m03465 追认：『留着吧，就按照这15条来』。

追认后的口径：

| 状态 | 条目 | 数 |
| --- | --- | --- |
| 在册（已批准） | `P0-1` `P0-4` `P2-6` `P1-4` `P0-3` `P2-3` `P1-2` `P2-1` `P2-2` `P2-4` `P2-5` `P1-5` `P1-6` `P2-7` `P1-1` | 15 |
| 撤回 | `P0-2`（三档路由：档位等于允许某个单位少治理，与稳定性判据反向） | 1 |
| 回滚 | `P1-3`（读集增长规则，按 YG 命令删除，回到原裁决的「不做」） | 1 |
| 不做 | `P3-1`（`handoff.md` 已有结构性界，只缺半句措辞澄清；登记不改） | 1 |

### 这一条被点出来时暴露的记账缺口

从批 6 落地到 2026-10-20 追认，中间隔了整轮自举与二十轮章程级审阅，而**没有任何文件记录过「`P1-1` 偏离了 YG 的裁决」**——它只存在于对话里。处置表写着「已落地」，产物里确实有；但「它是不是被授权做的」这一格既没有值，也没有指针。

这与 §9.10.19 记的「处置行不可被产物否决」是同一族缺陷的另一半：**产物能证明动作发生了，证明不了动作被授权过**。

处置：追认本身落在这一节；后续任何偏离裁决的动作，落地当轮就要在同一份批表里写明「裁决是 X，实际做 Y，待追认」，而不是等被问到才记。
}
