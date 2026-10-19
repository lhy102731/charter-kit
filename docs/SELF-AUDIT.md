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
