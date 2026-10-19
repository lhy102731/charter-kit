# Review record — REV-CHARTER-14

## Review identity

- Review ID: `REV-CHARTER-14`
- Scope: charter-level。受审对象 `.charter/project.md`（`Charter version: `0.2``、`Status: `DRAFT``）、`.charter/roadmap.md`、叶 `R1.1-S1-L1` 的合同 `.charter/current-task.md`、`.charter/handoff.md`、`.charter/reuse-discovery.md`、`.charter/lessons.md`、`.charter/records/REV-CHARTER-13.md`、`.charter/evidence/` 全部证据文件。
- Reviewer: fresh-context subagent `dedec5d6-6183-401b-815d-fd4a56a41af3`，只读，未继承实现会话历史。
- Date: 2026-10-19。
- Template: `portable/templates/review.md`（Contract version 0.4，CHK1–CHK13 冻结）。

## Independence declaration

- 实现方与审阅方不是同一上下文；审阅者在派单时不知道实现方将如何修。
- **原仓零改动自证**：审阅者对所有 545 个文件做前后 sha256 比对，结果 changed 0 / missing 0 / added 0，HEAD 仍 `d6eff20240adbcce327ca7cffe27053a6df6bd02`。全部实验在仓外副本（`%TEMP%\rev14\mut2`、`mut3`、`rev14_init`）进行。
- 它没有停在「被点名的都修了」，而是**用我上一轮写下的判准自己扫**，并据此判我的判准本身不合格。

## Verdict

`REQUEST_CHANGES`

## 四项点名答案

| 项 | 判定 | 依据 |
|---|---|---|
| NF-23 | `CLOSED` | 读集 `18432` / `18,432` / `18 KB` 三个形态 0 命中；`36 KB` 仅存于带指针的位置与模板原文；实测 `leaf-task.md` = 18,349 字节、`validate_kit.py:133` 的 `LEAF_CONTRACT_CEILING_KB = 36`、`:1662` 的一半断言 36,698 ≤ 36,864、余量 83，与 `template-budget-2026-10-19.txt` 逐项一致 |
| NF-24 | **NOT_CLOSED**（审阅者上调 P2） | 读集仍三处现在时可变计量数，见下节 ①②③ |
| NF-09 | 保持 `PARTIAL` | 判据「读集清零」未达成，同 NF-24 三处 |
| 判准 | **有漏洞** | 过宽、过窄、过强、同类不同处置，见 NF-26 |

### NF-24 的三处残留（审阅者实测）

| 位置 | 残留 | 为什么是计量数 |
|---|---|---|
| `.charter/current-task.md` 的 init 检查行 | 「文件数从 0 到 10」 | 与 `inventory` 的第四个计数是同一事实的两个落点，且口径不自洽：`init_project.py` 实产 10 个 `.md` + 1 个 `evidence/dependency-check.log` = 11 个文件 |
| `.charter/project.md` 的 `INDEPENDENT_REVIEW` 格 | 「与证据表 22 行不是同一套」 | 22 是 `ac-liveness` 证据 `## Mutations` 段的数据行数（实测 :86–107 恰 22 条），随一次普通追加就会变 |
| `.charter/handoff.md` 的证据行 | 「五条 AC 的检查原文…本行不复述计数」 | 同一行里既声明不复述计数又写出「五条」，自相矛盾 |

## 判准的判准：NF-25 / NF-26 / NF-27 / NF-28

| id | 严重度 | 审阅者的判据 | 处置 |
|---|---|---|---|
| NF-25 | P2 | `project.md` 的不变量（计量数只落 `.charter/evidence/`）与同一文件里的投影格互斥：投影格枚举的是状态，但它携带的是可数的量 | 在不变量里加入**投影例外**：唯一投影处可以逐一枚举状态，但不得写出汇总后的数量；数量若必须出现，落 `.charter/evidence/` |
| NF-26 | P2 | 判准过宽（字面实现出 72 个候选，多为「一个 / 一次」这类指称）、过窄（REV-13 的标题与派单把它收窄成「可变文件数」，条数 / 行数 / 个数 / 字节数 / 测试数全在判准外，②③ 正因此漏网）、过强（与 `portable/templates/lessons.md` 的 `Hits` 字段冲突）、同类不同处置（「五份」改成「所有」，「十处同步位置」却留着） | 把判准从一句散文改写成**三问 + 两条豁免 + 投影例外 + 适用范围**（见下） |
| NF-27 | P3 | `lessons.md` 的 `Hits: 6` / `Hits: 4` 是计数器，需要显式豁免「拥有该计数器的记录本身」 | **E1 计数器自属**豁免 |
| NF-28 | P3 | `docs/SELF-AUDIT.md` 的 D-01 遗留行以现在时持有 `18,432`，是读集外的第二落点；「唯一落点」不变量的适用范围未写清 | 该行改为指针；不变量补**适用范围**：约束启动读集与所有投影处，历史档案按第 ③ 问处理 |

### 判准改写后的正文（已落进 `.charter/project.md` 的不变量）

**三问（按顺序，命中即停）**：① **它是数得出来的量吗**（份 / 件 / 个 / 条 / 行 / 字节 / 测试数 / 轮数）——是，则只准出现在证据文件里，或作为某个唯一投影处的成员名称出现，散文写指针；「一个」「一次」「一种」这类量词是在指称而不是在计数。② **它是会变的状态吗**——是，则只准写在声明的唯一投影处，别处写指针并注明「本行随 X 重算」。③ **它是某一次运行或某一轮判定的观测吗**——是则允许保留，但豁免只覆盖**紧跟其 `REV-` id / 时间戳 / 轮次标记的那一个子句**。

**两条豁免**：**E1 计数器自属**——以计数器为设计的那份记录（`lessons.md` 的 `Hits:`、证据文件自己的计数行）只有它自己能写那个计数。**E2 结构常量**——命名一个由设计固定、变更须走章程级改动的集合时（宿主、route、builder、启动读集成员），其中的数不是测量值，但必须能答出「这个集合的成员由哪个文件定义」。

**投影例外**：唯一投影处可以逐一枚举状态（轮次与判词），但不得写出汇总后的数量。

**适用范围**：约束启动读集与所有投影处；历史档案（`docs/`、`records/`）记的是观测，按第 ③ 问处理，同一个值不得同时在档案里以现在时出现。

## 审阅者的探针（副本内，非空口）

| id | 动作 | 观测 |
|---|---|---|
| E1 | 在副本的 `ac-liveness` `## Mutations` 表加 1 行（22→23，属 `AC2` 允许的 `.charter/` 普通改动） | `validate_kit.py .` exit 0、`AC1`–`AC5` 全 exit 0，而 `project.md` 仍写 22 行 → 门禁看不见这类过期 |
| E2 | 把 `project.md` 的 D-01 行换回 `18,432` 字面量 | 规则 R1 命中（说明扫描程序本身有效） |
| E3 | 把某处换成「（10 份）」 | 规则 R2 命中 |
| E4 | 按模板生成 `.charter/lessons-archive.md`，使 `.charter/*.md` 变 11 | `inventory` 仍记 10、叶合同仍写 0→10，门禁全绿 → 计数过期无声 |
| C1 | 指针行 | 不报 |
| C2 | 历史叙述「REV-CHARTER-06 那一轮 19 条突变」 | 不报 |
| C3 | 「三个宿主」 | **误报** → 需要 E2 结构常量 |
| C4 | 同句带 `REV-` id | 不报 |
| C5 | 同句不带 id | 报 |

### C4 / C5 揭出的机制（本轮最重要的一条）

豁免是**行级**的：一行里只要出现 `REV-` id，整行的裸数字都被放过。`project.md` 的投影格正是一行装下整条审阅链，所以「22 行」这类数字逃过了我自己的自查。处置是把豁免从**行级**收到**子句级**：只豁免紧跟 id 的那一个括注。

## 其余处置

| 位置 | 处置 |
|---|---|
| `.charter/current-task.md` 的 init 检查行 | 「从 0 到 10」改为「从 0 变为 `.charter/evidence/inventory-2026-10-19.txt` 记录的数（该文件的 update rule 定义计数口径）」 |
| `.charter/project.md` 的投影格 | 「与证据表 22 行」改为「与证据文件 `## Mutations` 段」 |
| `.charter/project.md` 的 D-01 行 | 「十处同步位置」改为「所有同步位置（清单见 `inventory` 的 update rule）」 |
| `.charter/handoff.md` 的证据行 | 「五条 AC 的检查原文」改为「各验收项的检查原文」 |
| `.charter/lessons.md` 的 LS-002 | 「三次实例」补成「三次实例（均为历史观测，逐条见 `REV-CHARTER-05` / `06` / `07` / `10` 记录）」，让第 ③ 问的 id 标记在子句内可判 |
| `docs/SELF-AUDIT.md` 的 D-01 遗留行 | 改成指针（数字落 `template-budget-2026-10-19.txt`） |

## 审阅者的其余机械核对（其报告内，实现方未改）

- HEAD `d6eff20240adbcce327ca7cffe27053a6df6bd02`；`git status` 79 条 dirty；`.charter/` 整个 untracked。
- `python scripts/validate_kit.py .` → exit 0、PASS (246 files checked)；`AC1`–`AC5` 全 0（用 `argv` 重建与真 `bash.EXE` 双执行器各跑一遍，结果一致）。
- AC 块切分：AC1 :91–104、AC3 :105–116、AC4 :117–118、AC2 :121–137、AC5 :138，每块 `check: ` 标签恰 1 次。
- 四计数实测 templates 10 / references 5 / scripts 7 / `.charter/*.md` 10，与 `inventory` 一致。

### 它指出的结构性盲点（未列入 findings，但记在本记录里）

`.charter/` 整个 untracked，而 `AC2` 又把 `.charter` 排除在 diff-sha 之外 —— 治理事实源不在受版本控制的增量里，所以「静默过期」连 `git diff` 都看不见，只能靠审阅者逐字节重算。这一点要等章程批准（批准动作含把 `.charter/` 单独提交）才能改变。

## 明确未验

- 未核 CHK1 / 2 / 6 / 8 / 9 / 11 / 12 对应的面。
- 未跑全量 pytest。
- 未核 `targets/**` 与 `plugins/**` 的镜像一致性。
- 未读 `DEVELOPMENT_CHARTER.md` 正文。

## Re-review trigger

本记录不自我批准。下一步 `REV-CHARTER-15` 窄范围复验：

1. NF-24 三处残留是否改净（指针 / 去量化），且改后 `inventory` 的计数口径与叶合同的 init 检查一致。
2. 判准三问 + 两条豁免 + 投影例外 + 适用范围是否真落进读集，能否在副本上重跑 E1 / E4 两个探针而不产生「散文过期却全绿」。
3. C3（结构常量）不再误报、C4 / C5 的子句级豁免能否区分。
4. NF-09 能否转 `CLOSED`。

`APPROVE` 之前章程不得从 `DRAFT` 转出，叶 `R1.1-S1-L1` 不得从 `DRAFT` 转出。