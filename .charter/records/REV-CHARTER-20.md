# REV-CHARTER-20 — 独立审阅记录

## Review identity

- Review id: `REV-CHARTER-20`
- Reviewer: fresh-context subagent `9cf249aa-bab2-45cf-abb7-6add7c76e58f`（独立上下文，未参与本轮任何编辑）
- Date: `2026-10-19`
- Scope: 只核 `REV-CHARTER-19` 的四条处置（`NF-55`…`NF-58`）与它新增的两个门（`AC6`、`CHK14`）。不重做 `CHK1`–`CHK13` 全表，不重验已 `CLOSED` 的历史项。
- Verdict: `REQUEST_CHANGES`

## Independence declaration

审阅者声明：全部实验在仓库副本 `outputs/charter-kit/_rev20_workspace/copy` 上执行，真仓库只读；它撞过一次 WSL 桩 `bash`（`C:\Windows\system32\bash.exe`，每条命令 `rc=1`、stdout 空）把 `AC4` 误判成假红，改用绝对路径后 `AC4` 归零——这次自证恰是 `LS-002` 说过的「执行器会双向伪造结论」。

## 判词

主判定：**混合，天平偏向按点名修**。按形态修的只有两处：`AC6` 的转义感知量具、`AC3` 的十点逐点断言。其余仍是点名修——同形态的六处取值副本改到互相矛盾仍七门全绿；兄弟量具 `AC1` 仍裸竖线切格并会假红；锚点只盖 `*.md`，证据 `.txt` 改或删皆盲；删掉 `CHK14` 那一行门照样绿。

> 前十九轮的病灶没有被消灭，只是被挪到了没点名的地方。

## Findings 与处置

| id | 级别 | 问题 | 处置（落点） |
| --- | --- | --- | --- |
| `NF-59` | P1 | 六处 reuse 取值副本（`project.md` 第 1 节一行、第 6.1 节两行含 `2027-01-19`、`roadmap.md` 的 `### Reuse Check projection` 三行、`current-task.md` 第 1 节三行含 `C-01 @ d6eff20`）都不在投影清单、`AC3` 一个都不读；把它们改成互相矛盾（`NO_MATCH` / `BUILD_NEW` / `NOT_SEARCHED`）七门全绿 | 选 (b)：`AC3` 并入本叶三行复用取值对权威（material 对 `Material target test`、coverage/result 对 Search log 的 `Coverage` / `Result` 两列、final route 对候选表 `Disposition` 单元格）；章程与 `roadmap` 的六处取值行改指针 |
| `NF-60` | P2 | 锚点 ③ 只哈希 `.charter/**/*.md`；删掉 `D-07` 引用的 `probes-2026-10-19.txt` 后三段锚点一字未变 | 锚点 ③ 去掉扩展名过滤，改为 `.charter` 全文件内容哈希（含证据 `.txt` 与本轮新增的 `.charter/checks.py`） |
| `NF-61` | P2 | `AC1` 载荷仍 `c.split('|')` 裸切格；roadmap 叶行插一处合法转义即假红 | `AC1` 的实现搬进 `.charter/checks.py`，用转义感知的 `split_cells`；合同载荷改为单行委托 |
| `NF-62` | P2 | `AC7` 只要段内出现字符串 `CHK14`：只删那一行、或缩成 `- [x] CHK14 - PASS` 仍绿；例外写成散文也绿 = 存在性断言冒充实质断言 | `AC7` 改为「以 `- [x] ` + 可选反引号 + `CHK14` 起首的行**恰一行**，且该行必须给出 `item` / `clause` / `basis` 或 `Exceptions claimed: none`」；本记录按此写 |
| `NF-63` | P3 | 章程不变量末句点名七组投影点，`AC3` 只读三个文件十个标签；第 4 节 `INDEPENDENT_REVIEW` 行与第 10 节决策表都不在断言内 → 声明比断言宽 | 不变量末句收窄为「可机检部分由 `AC3` 断言；`INDEPENDENT_REVIEW` 行与决策表由 Review A 判」，声明与断言同宽 |
| `NF-64` | P3 | `docs/SELF-AUDIT.md` 活性表记的锚点值与证据文件实测值不一致，且两侧都没写删段的起止行与删后字节数 | 锚点值只以证据文件为权威；自审文档不再复制数值，只留配方指针 |

## Checks performed

- [x] `CHK1` 语义与章程一致 — PASS（本记录只点名规则，不转述子句）
- [x] `CHK7` 迁移文档与模板版本一致 — PASS（本轮未改模板与 `Contract version`）
- [x] `CHK11` 集成要求不与叶的 `Merge` 许可互斥 — N/A（本轮不改集成路径）
- [x] `CHK14` 计量数指唯一落点、会变状态只在声明投影、例外逐项列名 — PASS（item: 本轮九条验收项的**载荷文本与其哈希**；clause: 章程第 2 节「会变的事实只有一个落点」的 A 类判例——某一轮自己那一次的校验行可留，跨节汇总别轮的数必须删；basis: 它们是本轮自己的观测与常量，不是别轮计量的副本。例外：`REV-CHARTER-20` 环里的判词枚举属 B 类历史叙述，按 A 类惯例保留原文）

## 本轮的结构性处置：从「按点名修」改成「一条规则一个实现」

二十轮里同一病灶（同一条规则存在第二份实现或第二个值）换了十几个位置被点名，每轮只修被点名的那一处。本轮的处置不是再修六处，而是把判据的**所有权**收进一个文件：

1. `.charter/checks.py` 是全部可机检判据的唯一实现（`AC1`…`AC9`，`--only <id>` 单跑、`--anchor` 出三段锚点）。
2. 叶合同的九条验收项载荷一律写成 `python .charter/checks.py --only ACn`，**不内联实现**；`AC9` 机检这一点。
3. `AC8` 机检抽取规则本身（每块恰一个 `check:` 标签、载荷不含裸竖线）——上一版这条纪律只有规定、零生产者。
4. `AC3` 覆盖四 gate 点、三 freshness、三 RD、本叶三行复用取值；`AC7` 要求结构化例外。
5. 锚点 ③ 覆盖 `.charter` 全部文件，含证据与脚本本身。

## 活性矩阵（每次施加后按字节还原，树哈希前后相同）

| 突变 | 目标 | 只跑 | 观测 |
| --- | --- | --- | --- |
| M1 叶 `Status` 改 `PASS_CLOSED` | `current-task.md` | `AC1` | `rc=1` |
| M2 一个 gate 点改 `COMPLETE` | `project.md` 第 6.1 节 | `AC3` | `rc=1`（值不同） |
| M3 一条搜索记录 `Result` 改 `NO_MATCH` | `reuse-discovery.md` | `AC3` | `rc=1`（本叶 coverage 对不上） |
| M4 决策表某行多一格 | `project.md` 第 10 节 | `AC6` | `rc=1` |
| M5 删 `CHK14` 那一行 | 本记录 | `AC7` | `rc=1` |
| M6 再写一个 `check:` 标签 | `current-task.md` | `AC8` | `rc=1` |
| M7 载荷换成内联 `python -c` | `current-task.md` | `AC9` | `rc=1` |
| M8 新增白名单外文件 | `docs/zzz-probe.md` | `AC2` | `rc=1` |
| C1 新增白名单内文件（控制组） | `.charter/zzz-probe.md` | 全部 | `rc=0` |

完整表与每条的退出码只落 `.charter/evidence/ac-liveness-2026-10-19.txt`（本记录不复述计数）。

## 明确未验

未重跑全量 `pytest`；未按 `CHK1`–`CHK13` 全表逐条勾选；未重验 `REV-CHARTER-01`…`REV-CHARTER-18` 的实质；未核证据文件内数值的真伪；未做多宿主重放；未逐字段复算 `AC2` / `AC4` / `AC5`。

## 封存（`D-09`）与仍开着的项

按用户指示（「不要像打地鼠一样」）不再派 `REV-CHARTER-21`。链在此封存，**没有 `APPROVE`**：本轮的 `REQUEST_CHANGES` 只被部分消解——`NF-59`…`NF-64` 六条已处置，但「审阅者提出的其余同形态位置」这一类风险不会因此消失，它被换成了结构（单一实现 + 机检 + 全覆锚点）。

封存时仍开着的：`D-01`…`D-08`，以及本轮新增的 `D-09`（本封存自身需要 YG 裁决：接受带限度的封存，或另起一次独立复验）。叶级 `Review A` 尚未执行。

## Re-review trigger

若 YG 选择「另起一次独立复验」：只核 `NF-59`…`NF-64` 六条的产物侧证据、九条 `AC` 的活性矩阵能否复现、以及 `.charter/checks.py` 是否是唯一实现（`grep` 合同里的 `check:` 载荷必须全部是委托形式）。不重做 `CHK` 全表。本记录不自我批准。
