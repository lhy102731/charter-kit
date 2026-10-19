# REV-CHARTER-01 — 章程级独立审阅记录

## Review identity

- Review ID: `REV-CHARTER-01`
- Task ID: `CHARTER`（章程本体，无叶任务）
- Candidate revision: 工作区 `.charter/` 初版（未提交，base `d6eff20`）
- Reviewer: fresh subagent `79041d37-2b22-4b36-a172-2f13625685c3`
- Host / process / session: DSH 子代理进程，只读，cwd = 仓库根
- Review type: `CHARTER_INDEPENDENT`
- Freshness (Review A): `fresh-subagent`（子代理未持有实现上下文）
- Freshness (Review B): 不适用（未触发 RVB1–RVB5）
- Applicability: `REQUIRED`（章程首次批准前由用户显式要求）
- Trigger or bounded omission reason: 首次自举，无前次审阅可引用
- Started: 2026-10-19T12:45Z
- Finished: 2026-10-19T12:52Z

## Independence declaration

- Different from implementer: `yes`
- Fresh context: `yes`
- Fresh process: `yes`
- Read implementer report before testing: `no`
- Limitation on independence: 子代理只读、不能落地 records/ 与 evidence/；这两件由实现侧在本次修复中补齐，其内容不被本条审阅背书。

## Checks performed

审阅按六个角度进行（填充完整性 / 三处投影 / 内部矛盾 / 事实核对 / 门禁合规 / 边界合规），未按 CHK1–CHK13 逐项勾选——这是本条审阅的已知覆盖缺口，复验 `REV-CHARTER-02` 需按 `CHK1`–`CHK13` 完整过一遍。

## Findings

| ID | Finding severity | Remediation change class | Finding | Evidence reference | Required action | Disposition |
|---|---|---|---|---|---|---|
| F-01 | P1 | B | 门禁（复用发现）先于章程批准即写成 `COMPLETE` 并签 `Approved by YG`，早于 `Status: DRAFT` 的批准动作 | `.charter/reuse-discovery.md` 第 5、11 节 | 退回 `PENDING` 或改为随批准生效 | `CLOSED` — 三处 gate 全部退回 `PENDING`，签批人改「待批准」 |
| F-02 | P1 | B | `project.md` 缺 `freshness` 字段，recheck trigger 写「无」，与复用记录的 2027-01-19 到期相反 | `.charter/project.md` 第 5 节 / `.charter/reuse-discovery.md` 第 2 节 | 三处投影同一次改动对齐 | `CLOSED` — 新增 `Reuse discovery freshness: current`，触发条件改为同值 |
| F-03 | P1 | B | 审阅与收据记录文件不存在（`.charter/records/` 为空），却在两处被当证据引用 | `.charter/project.md` 第 4 节 / `.charter/current-task.md` 证据索引 | 用实跑输出建记录 | `CLOSED` — 本文件 + `.charter/evidence/validate-2026-10-19.txt` + `.charter/evidence/reuse-probe-2026-10-19.txt` |
| F-04 | P1 | B | `changelog.md` 的 0.1 行三处占位未填 | `.charter/changelog.md:10` | 填实或写未决 | `CLOSED` — 填实，签批人记 `UNDECIDED — 待批准` |
| F-05 | P1 | B | 设计树给出两条互相矛盾的 Recommended；工作区改动数写「21+」实测 77 M + 2 未跟踪 | `.charter/current-task.md` 第 10 节 / `.charter/handoff.md` | 统一推荐并写实测数 | `CLOSED` — Q1 推荐改为「不连带提交 77 个改动」，handoff 写实测 |
| F-06 | P2 | B | 探测日志只有一段，无法证明是复用阶段那次运行（日志不记 argv / `--optional`） | `scripts/check_dependencies.py:1084` `write_log` | 日志记 argv，重跑并替换 | `DECIDED_BACKLOG` — 已重跑并把本次运行独占一段（2026-10-19T12:54:05Z），并捕获 `.charter/evidence/reuse-probe-2026-10-19.txt`；日志加 argv 记入 `D-06`，recheck 触发：下次修改 `check_dependencies.py` |
| F-07 | P2 | B | `SR-03` 与依赖证据行错引不含 `validate` 输出的日志 | `.charter/reuse-discovery.md:61` | 指向真实产物 | `CLOSED` — 三处证据行改指 `.charter/evidence/validate-2026-10-19.txt` 与 `reuse-probe-2026-10-19.txt` |
| F-08 | P2 | B | `AC3` 用 `grep -c ... >= 1`，在任何差异下都不动退出码 | `.charter/current-task.md` 第 5 节 | 换成能移动退出码的检查 | `CLOSED` — AC1/AC3 换成 `python -c` 断言，实测 exit 0，且改坏即非零 |
| F-09 | P2 | B | 叶合同的 effects 八项全空、修复次数 2 与模板占位冲突、实现计划为空 | `.charter/current-task.md` 第 4、6 节 | 按本叶真实范围填写 | `CLOSED` — 勾 read_only/sample_run/code_write，不勾 local_merge，补三条实现计划与禁止项 |
| F-10 | P2 | B | 门禁路线 `ADOPT@d6eff20` 依赖仍 `OPEN` 的 D-02 | `.charter/project.md` 第 10 节 | 消解或降级依赖 | `CLOSED` — gate 退回 `PENDING`，D-02 不再被未批准门禁前置 |
| F-11 | P2 | B | 停止条件「三条 tier 均 SEARCHED」在 `LOCAL_ONLY` 授权下不可满足 | `.charter/project.md` 第 6 节 | 改为 scope 内成立 | `CLOSED` — 改为 scope 内 tier 全 SEARCHED，scope 外记 NOT_SEARCHED/NOT_AUTHORIZED |
| F-12 | P2 | B | `handoff.md` 缺 lessons 状态行 | `.charter/handoff.md` | 补 | `CLOSED` — 补「active 0 / archived 0；最新条目：无」 |
| F-13 | P3 | C | 七个实例文件残留「Copy this file to …」模板前言 | `.charter/*.md` | 删除 | `CLOSED` — 六份含该块的实例文件全部删除（三份格式文件本无） |
| F-14 | P3 | C | `roadmap.md` 的 DEC 占位行、lessons 的 LS-001 示例条目仍以示例形态存在 | `.charter/roadmap.md` 第 8 节 / `.charter/lessons.md` | 换成实态 | `CLOSED` — roadmap 写「尚无影响路线的决定」，lessons 写「尚无条目/尚无归档条目」 |
| F-15 | P3 | C | 事实性小误：「六份参考」实测 5 个、「约 35 KB」实测 36,731 字节；成功等级把叶级 Review A 与章程级审阅混为一档 | `.charter/project.md` 第 4、5 节 | 改实测数、拆档 | `CLOSED` — 两处数字改实测，第 4 节按章程级/叶级分开记 |

## Verdict

`REQUEST_CHANGES`

理由（审阅当时）：初版 `.charter/` 有 5 条 P1 不一致，其中两条是「先完成门禁再等批准」的顺序错误与三处投影互斥——按 `.charter/project.md` 自己的规则，任何未对平的分歧保持 `BLOCKED`。审阅侧事实核对全部属实（validate PASS 246、pytest 298 passed/519 subtests、`leaf-task.md` 18,349 字节 vs 阈值 18,432、余量 83）。

处置后状态：F-01 … F-05、F-07 … F-15 已在本会话同一批修复中关闭，证据逐条列在上表；F-06 转 `DECIDED_BACKLOG`（承载于 `D-06`）。**本记录不自我批准**：修复后的章程需要一次新的独立复验 `REV-CHARTER-02`，在此之前 `.charter/` 的诚实状态是「已按 findings 修完，未复验」。

## Re-review trigger

任何对 `.charter/project.md` 目标、不变量、授权边界、成功等级的改动；任何 findings 处置被推翻；章程从 `DRAFT` 走向批准；或 `D-06` 到期。复验须按 `review.md` 的 `CHK1`–`CHK13` 完整勾选，并保持与实现者不同上下文。
