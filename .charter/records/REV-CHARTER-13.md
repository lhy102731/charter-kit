# Review record — REV-CHARTER-13

## Review identity

- Review ID: `REV-CHARTER-13`
- Scope: charter-level. 受审对象是 `.charter/project.md`（`Charter version: `0.2``，`Status: `DRAFT``）、`.charter/roadmap.md`、叶 `R1.1-S1-L1` 的合同 `.charter/current-task.md`、`.charter/handoff.md`、`.charter/reuse-discovery.md`、`.charter/lessons.md`、`.charter/records/REV-CHARTER-12.md` 与 `.charter/evidence/` 下全部证据文件。
- Reviewer: fresh-context subagent `f2ead4b5-88df-4609-9bde-c1eedc32475b`，只读，未继承实现会话的历史，只持有派单 brief。
- Date: 2026-10-19。
- Template: `portable/templates/review.md`（叶合同 Contract version 0.4，CHK1–CHK13 编号已冻结）。

## Independence declaration

- 审阅者与实现者不是同一上下文：审阅者是独立派发的只读 subagent，本轮实现（NF-19…NF-22 处置）由主会话完成，审阅者在派单时不知道实现者将如何修。
- 审阅者自带验证：在仓库副本上跑 `grep -rn 'Review A' portable/` 得到 rc=0 / 11 hits / 9 files，与 `SR-01` 行自述逐项相符；跑行标签 vs 行号分水岭实验（副本顶部插一空行）得到行标签仍指向同一段文本哈希 `aa2f8e43…`，而行号 `project.md:70` 从 `SYNTHETIC` 漂到 `COMPONENT`、`:72` 从 `INDEPENDENT_REVIEW` 漂到 `INTEGRATED`。
- 它明确声明未验的事项（见末节），不把「没查」写成「没问题」。

## Verdict

`REQUEST_CHANGES`

理由：`NF-19` / `NF-20` / `NF-21` / `NF-22` 全部 `CLOSED`、`NF-15` 转 `CLOSED`；`NF-09` 仍判 `PARTIAL`（读集里已无证据值副本，但仍有以现在时持有可变文件数的散文）；另新开 `NF-23` / `NF-24` 两条 P3。判词按 `portable/templates/review.md` 的 Verdict 枚举取值。

## Findings 判定

| id | 上一轮判定 | 本轮判定 | 依据 |
|---|---|---|---|
| NF-19 | PARTIAL | `CLOSED` | `SR-01` 的命令可复现（rc=0、11 hits / 9 files），指针已改行标签且标签全文唯一（count=1）；表下更正行点名的两个原值只出现在更正行里 |
| NF-20 | PARTIAL | `CLOSED` | `handoff` 两处子检查条数已改指针，且「本行即全套计量数的唯一落点」这类不成立的自称已删除 |
| NF-21 | PARTIAL | `CLOSED` | `246 / 298 / 271 / 36731 / 18349 / 18432` 六个值在启动读集里全部 0 命中；`project.md` 两处改指针，值落进 `pytest-2026-10-19.txt` 与 `sizes-2026-10-19.txt` |
| NF-22 | PARTIAL | `CLOSED` | `handoff` 的突变计数（22 / 19 / 3 / per-AC）已改指针，证据文件 `## Mutations` 段是唯一落点 |
| NF-15 | PARTIAL | `CLOSED` | 读集里其余 `file:line` 指针已清零（全 `.charter` 正则命中 78 行全部落在 `records/` 的历史叙述里）；分水岭实验证明行标签寻址在插行后仍解析到同一事实 |
| NF-09 | PARTIAL | `PARTIAL` | 见新开 NF-23 / NF-24：还有两处现在时可变数（体积阈值数字、可变文件数） |

## 本轮处置

| id | 严重度 | 位置 | 处置 | 证据 |
|---|---|---|---|---|
| NF-23 | P3 | `.charter/project.md` 体积阈值行 | 删掉 `18,432` 字面量，改为「36 KB 阈值与『模板不超过其一半』的换算关系；数字落点 `.charter/evidence/template-budget-2026-10-19.txt`」 | 读集反查 `18432` 0 命中 |
| NF-24 | P3 | 读集散文四处（模板份数、参考份数、脚本份数、工作集份数） | 新建 `.charter/evidence/inventory-2026-10-19.txt` 承载四个计数 + update rule，读集里删数字只留指针 | 实测 `[10, 5, 7, 10]` 与证据文件逐项一致 |

顺带清掉同一形态的其余中文计数：`一处改动五份一起改` → `一处改动所有副本一起改`；`六件启动读集` → `启动读集（成员由入口命令点名）`（`project.md` 两处、`handoff.md` 一处、`current-task.md` 三处）；`十件工作集` / `十件模板` → `整套工作集` / `整套模板`。判准：**计数若会随一次普通改动而变，就不能以现在时留在读集散文里**；它要么是指向证据文件的指针，要么是历史叙述（记录某一次运行或某一轮判定），后者允许保留。

## 为什么 NF-24 的修法是新建证据文件而不是把数字改写得更准

这些数字（模板份数、脚本份数、工作集份数）写在一段枚举前面，读者会以为枚举与数字互相印证。但枚举变了数字不会跟着变——数字与枚举是两份事实，只有一份会被想起来更新。把数字搬进 `.charter/evidence/inventory-2026-10-19.txt` 后，它有一条 update rule 与一个测得时刻，读集只留指针，于是「谁该在什么时候重算这个数」第一次被写下来。继续把数字改准只会把它写对一次，改不了它下次会错。

## 审阅者自跑的机械核对（其报告内，实现方未改）

- HEAD `d6eff20240adbcce327ca7cffe27053a6df6bd02`；`git status --porcelain` 79 行（77 ` M` + 2 `??`）。
- `grep -rn 'Review A' portable/`：rc=0、11 hits / 9 files；`SR-01` 的标签行全文唯一。
- 全 `.charter` 的 `file:line` 正则命中 78 行，全部落在 `records/`。
- 证据值反查 `246 / 298 / 271 / 36731 / 18349 / 18432`：六件读集 0 命中。
- 5 个对象侧突变 + 1 个控制组：roadmap `DRAFT→READY` 打红 `AC1`；新增未跟踪文件打红 `AC2`；`PENDING→COMPLETE` 打红 `AC3`；`portable/templates/review.md` 追加换行打红 `AC4`（连带 `AC2`）；空提交打红 `AC5`（连带 `AC2`）；控制组 `lessons.md` 追加换行保持全绿。`AC4`/`AC5` 连带 `AC2` 是预期耦合（两者都改动工作区）。

## 明确未验

- 未跑全量 `pytest`（只核了证据文件里记录的数值与 `--collect-only` 分解）。
- 未逐条重建 `AC1`…`AC5` 的历史突变表（只做了本轮 5 条）。
- 未按 `CHK1`–`CHK13` 全表勾选。
- 未审计 `DEVELOPMENT_CHARTER.md` 与 `targets/` / `plugins/` 的镜像正文。
- 未复核 `REV-CHARTER-01`…`12` 的 findings 实质，只核了它们是否被写入 `records/` 与是否被 `project.md` 的 `INDEPENDENT_REVIEW` 行枚举。

## Re-review trigger

本记录不自我批准。下一步需 `REV-CHARTER-14` 窄范围复验：

1. `NF-23` / `NF-24` 是否真关闭（读集里现在时可变数是否清零，证据文件是否逐项一致）。
2. `NF-09` 能否从 `PARTIAL` 转 `CLOSED`——判据是「读集散文里是否还有会随一次普通改动而变的数」，本轮已把判准写进本记录与 `docs/SELF-AUDIT.md` 的对应小节。
3. 抽 `inventory` 证据里的四个计数，实际数一遍目录，确认 update rule 可执行。

`APPROVE` 之前章程不得从 `DRAFT` 转出，叶 `R1.1-S1-L1` 不得从 `DRAFT` 转出。