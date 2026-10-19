# REV-CHARTER-16 — 章程级独立审阅（章程 0.2 / 叶 R1.1-S1-L1）

> 这是一份**审阅记录**，不是批准。它不是自证：审阅者与执行者不是同一个 agent，记录由执行者按审阅者的报告整理，正文里的事实以审阅者给出的实测为准。

## Review identity

- Reviewer: fresh subagent `44d88954-bb8f-4437-9a73-fafa2585a0ee`（全新上下文，只读；不看执行者的推理过程）
- Mode: `CHARTER_INDEPENDENT`（章程级），窄范围复验
- Target: `HEAD d6eff20240adbcce327ca7cffe27053a6df6bd02` + 未跟踪的 `.charter/` 工作区（工作树 79 行 dirty，77 ` M` + 2 `??`）
- Date: 2026-10-19（记录标签；精确时刻见证据文件的时间戳）
- 范围: 上一轮四条的收尾 —— `NF-09` / `NF-24` / `NF-26` / `NF-31` 能否转 `CLOSED`，`NF-33` 是否真合并，以及本轮新暴露的缺陷

## Independence declaration

- 实验全在仓外：`outputs/charter-kit/_rev16_workspace`（`cp -a` 副本）与 `outputs/charter-kit/_rev16_tools`（脚本）。
- REPO 内只做 read / grep / glob 与一次 `PYTHONDONTWRITEBYTECODE=1 python -B scripts/validate_kit.py .`（不落字节码）。
- 自证：开工前后各算一次 `find … -type f -print0 | xargs -0 sha256sum | sort -k2`，**547 行、`diff` 输出 0 行**；`git status --porcelain` 前后均 79 行、sha256 均 `483cea69…`；HEAD 未变。探针改动后按字节还原（`aadf9681…`），造出的 `lessons-archive.md` 已删除、副本 `.charter/*.md` 回到 10。

## Checks performed

| 项 | 结果 |
|---|---|
| `validate_kit.py .`（REPO 上，禁写字节码） | exit 0；首行 `Charter Kit validation: PASS (246 files checked)`；尾四行子检查含 `no install side effect is declared` |
| 验收项活性（仓外字节同一副本，按 `handoff.md` 的抽取规则） | AC1–AC5 全 exit 0；每块 `check:` 恰 1 个 |
| 反引号奇偶 | 六份读集全偶数；被吞的标题 0 |
| `36 KB` 出现位置 | 只在 `current-task.md` 的定义处与 `portable/templates/leaf-task.md` |
| 探针 E1 / E4 | 今天仍 validate exit 0 且 AC 全 0 —— 门禁看不见证据文件自身过期（与 `D-07` 记成 `OPEN` 一致） |

## Findings

| id | 严重度 | 位置 | 问题 | 为什么重要 |
|---|---|---|---|---|
| `NF-34` | P2 | `ac-liveness` 的 REV-14 两段 | 同一 run（14:41Z）正文两份：两行 intro、两张 5 行 exit 表、四行 anchor，而注里写「Merged into one copy」 | 处置表说「已合并」、产物里只删了标题 —— 本链反复出现的「说已落地、产物里没有」，而这份文件是验收项活性的唯一证据 |
| `NF-35` | P2 | `handoff.md` 的 Open 行 | 现在时副本「Open: D-01…D-05」缺 `D-06`（DEFERRED）与 `D-07`（OPEN） | 第 10 节是决定状态的唯一权威；接手者按 handoff 读到的是「没有 D-07」 |
| `NF-36` | P2 | `handoff.md` 三处证据行与 `current-task.md` 的 AC4 | 逐字复述实测退出码，同行注却写「本行不计数」 | v4 ① 把「实测退出码」列入只准落在 evidence 的类目；注文与同行数字直接相反 |
| `NF-37` | P3 | `lessons.md` 的 `LS-002` | 数字靠一串非相邻 id 借豁免 | 正是 `NF-31` 点名的那类「数字靠 id 借豁免」留在读集 |
| `NF-38` | P3 | `project.md` 的判准正文 | 聚合词规则是子句局部 + 词面相邻 → 聚合词放进无数字子句即全句豁免（C5b 1/2、C5c 1/1、C5e 0/2） | 判准抓得到「整句聚合」，抓不到「位次搬家」 |
| `NF-39` | P3 | `project.md` 与 `reuse-discovery.md` | 同一条规则参数（20 分钟 / 6 条具名查询）两份读集各写一次、互不指向 | 第二个落点会独立漂移；两处都像定义处等于指不出定义处 |

前一轮的判定：`NF-25` / `NF-29` / `NF-30` / `NF-32` `CLOSED`；`NF-09` / `NF-24` / `NF-26` `PARTIAL`；`NF-31` / `NF-33` `NOT_CLOSED`。

## Verdict

`REQUEST_CHANGES` —— 不是 `APPROVE`。理由：`NF-34` / `NF-35` / `NF-36` 三条 P2 都是「读集里的现状断言今天是错的」，而判定批准的正是读集能不能如实回答现状。

## Dispositions（本轮执行者的处置，不构成自我批准）

| id | 处置 | 落点 |
|---|---|---|
| `NF-34` | 两份正文合并为一份，注改为「两次独立运行（14:41:08Z 与 14:41:44Z）追加过同一段正文；除时间戳外逐行相同，故合并」 | `.charter/evidence/ac-liveness-2026-10-19.txt`，标题只剩 1 个 |
| `NF-35` | 改为指向第 10 节决策表的指针，不枚举 | `.charter/handoff.md` 的 Open 行 |
| `NF-36` | 四处删掉 exit 数字，只留证据指针 | `handoff.md` 三处 + `current-task.md` 两处（AC4 与 Whole-suite 行） |
| `NF-37` | 改为「三类成因 + 条数与每次退出码逐条见 records/…，本节只留因果，不复制数字」 | `.charter/lessons.md` |
| `NF-38` | 判准 v4：③ 问补三处写死的边界 —— (a) 紧跟 ≤24 字符且不跨句末标点；(b) 子句以句号/分号/问号/叹号/逗号/破折号切分、括号不外切；(c) 聚合词或计数名词出现在同一行任何位置即取消该行全部 ③ 豁免 | `.charter/project.md` 不变量正文 |
| `NF-39` | 第二个落点改为指针，写明「不重复数值，也不构成第二个定义处」 | `.charter/reuse-discovery.md` |

顺带处置（审阅者列为「未核」而执行者自查命中）：`project.md` 历史叙述里的「2 blocker + 7 major + 7 minor」按 v4 属测量值 → 改为指向 `docs/SELF-AUDIT.md` 第 9.9 节的指针，并注明那是历史观测。

## 本轮自己抓到的自伤（审阅者未指出）

第 15 轮把 `project.md` 第 4 节成功等级表的 `INDEPENDENT_REVIEW` 行整格重写时，**丢了表格行结构**：该行变成表外段落，且丢了轴名，把一张表切成两半 —— 而 `validate_kit.py` 与五条 AC 全绿，因为它们都不读章程的表格结构。本轮已重建为四列表格行。

这一类与 `NF-15`（行号漂移）同族但方向相反：`NF-15` 是指针指向了别处，这一次是指针所指的容器本身被改坏。共同点：**修复动作发生在 A 处，损坏落在 B 处，而门禁只看 A**。

## 未验清单（审阅者声明）

- 未跑全量 `pytest`；`pytest-2026-10-19.txt` 的 298 passed / 519 subtests 未复跑。
- 未核 `init_project.py` 零状态产出，也未核旧观测「在 .charter 下产出 11 个文件」。
- 未核 `project.md` 里那句 suite 级审阅的条数与 `docs/SELF-AUDIT.md` 第 9.9 节是否一致。
- 未复核 REV-CHARTER-01…14 记录自身的判断（超出窄范围）。
- 未核 `validate_kit.py` 的「246 files」构成，也未核 baseline / reuse-probe / sizes / template-budget 的内部自洽（只核本轮用到的字段）。
- AC 在副本而非 REPO 上跑（守只读）；副本开工时与 REPO 的 547 文件 sha256 manifest 全等，故退出码可迁移，但属间接执行。

## Re-review trigger

需 `REV-CHARTER-17`（窄范围：`NF-09` / `NF-24` / `NF-26` / `NF-31` 能否转 `CLOSED`；判准 v4 三处边界用 C5b / C5c / C5e 重跑；`ac-liveness` 的 REV-14 是否真只剩一份正文；第 4 节的 `INDEPENDENT_REVIEW` 是否仍是表格行）。本记录不自我批准；未拿到 `APPROVE` 之前，章程与叶都停在 `DRAFT`。

（记录按 A 类惯例：原判词不改，后续更正另起一行并指名被更正行。本文件由执行者按审阅者报告整理，报告原文在父会话可见。）
