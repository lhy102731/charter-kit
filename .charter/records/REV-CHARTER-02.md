# REV-CHARTER-02 — 章程级独立复验记录

## Review identity

- Review ID: `REV-CHARTER-02`
- Task ID: `CHARTER`（章程本体）
- Candidate revision: 工作区 `.charter/` 第 0.1 版 + 十五条 findings 修复后（base `d6eff20`，未提交）
- Reviewer: fresh subagent `383cfdb5-e460-44f6-8c64-8a250da804fd`
- Host / process / session: DSH 子代理进程，只读，cwd = 仓库根
- Review type: `CHARTER_INDEPENDENT`
- Freshness (Review A): `fresh-subagent`（未持有实现上下文）
- Freshness (Review B): 不适用（未触发 RVB1–RVB5）
- Applicability: `REQUIRED`（`REV-CHARTER-01` 规定修复后必须复验）
- Trigger or bounded omission reason: 上一次审阅自陈未按 CHK1–CHK13 逐条勾选，本条补齐
- Started: 2026-10-19T12:58Z
- Finished: 2026-10-19T13:05Z

## Independence declaration

- Different from implementer: `yes`
- Fresh context: `yes`
- Fresh process: `yes`
- Read implementer report before testing: `no`
- Limitation on independence: 只读，不能落地任何修复或证据文件；本条审阅引用的证据全部由实现侧在同一批修复中生成，其真实性由本记录逐项复算，不由实现侧自述背书。

## Checks performed

按 `CHK1`–`CHK13` 逐条勾选（补上 `REV-CHARTER-01` 记录里的覆盖缺口）：PASS 11 项，FAIL 2 项 —— `CHK5`（负向与边界检查：叶无 `### Negative behavior / boundaries`、无负向 AC）与 `CHK11`（集成要求未统一：handoff 的 `local_merge` 与叶 §4/§7 互斥）。这两条即 N-01 与 N-04。

## Findings

### 十五条的复验结论：12 条真关闭，3 条半关闭

- 真关闭：F-01、F-02、F-03、F-04、F-07、F-09、F-10、F-11、F-12、F-13、F-14、F-15。
- 半关闭：F-05（Q1 的 Reason 仍写「21+ 个 `M`」）、F-06（D-06 写成 `OPEN`，章程要求 `DEFERRED`）、F-08（AC3 真修，AC1 的状态子句仍是存在性断言）。
- 结论：修复动作本身制造了新缺陷，共十条。

### 新发现与处置

| ID | 严重度 | 位置 | 问题 | 处置 | 处置后的证据 | Disposition |
|---|---|---|---|---|---|---|
| N-01 | P1 | `.charter/current-task.md` §5 | AC2 与整个 `### Negative behavior / boundaries` 块被删且无撤回记录；叶没有任何负向/边界验收项 | 恢复该节并给出两条负向项 `AC2`（允许路径外的改动为零，对标基线清单）与 `AC5`（本叶不产生提交） | `.charter/evidence/ac-liveness-2026-10-19.txt`：AC2 在基线新增一条 `portable/` 路径时 exit 1，干净时 exit 0；AC5 在期望提交不符时 exit 1 | `CLOSED` |
| N-02 | P2 | `.charter/current-task.md` §5 | AC1 用「状态词出现在 roadmap 全文」的存在性断言，改坏副本仍 exit 0 | 改为按 `|` 切 roadmap 中 `R1.1-S1-L1` 那一行、取 Status 单元与叶 `^- Status:` 比对 | 同一证据文件：叶 Status 改 `PASS_CLOSED` 时 exit 1，干净时 exit 0 | `CLOSED` |
| N-03 | P2 | `.charter/current-task.md` §10 Q1 | Reason 仍写「21+ 个 `M`」，与同段 Recommended 的 77 自相矛盾 | 改为「77 个 `M` + 2 个未跟踪（2026-10-19 实测）」并指向基线清单 | 与 `.charter/handoff.md` 的实测值同值 | `CLOSED` |
| N-04 | P2 | `.charter/handoff.md` §2 | Allowed effects 写 `local_merge`，与叶 §4/§7「不产生 commit、Merge allowed: no」互斥 | 改为只列 `read_only`、`sample_run`、`code_write`，写明 `local_merge` 未授权、以叶 §4/§7 为准 | handoff 与叶两处措辞一致 | `CLOSED` |
| N-05 | P2 | `.charter/project.md` §10 D-06 | `DECIDED_BACKLOG` 的 finding 落成 `OPEN`，与 §10 自己的状态映射互斥 | 改 `DEFERRED`，触发条件保留「一次 `check_dependencies.py` 的日志格式改动」 | D-06 行现为 `DEFERRED` | `CLOSED` |
| N-06 | P2 | handoff / roadmap / project 四处 | 「十六条 findings」与表内 15 行矛盾 | 四处统一为「十五条」 | `grep 十六条` 零命中 | `CLOSED` |
| N-07 | P3 | `.charter/current-task.md` §1 | `Mode` 仍是 `MANUAL | AUTO_DEV` 未替换占位 | 改为 `MANUAL`，与 §5 正文一致 | 字段与正文同值 | `CLOSED` |
| N-08 | P3 | `.charter/changelog.md` | 0.1 行说五个待决，§10 已有 D-06 | 追加 0.2 行记录本次修复，不修改 0.1 行；章程 `Charter version` 同步 0.1 → 0.2 | 两行并存，0.1 未被编辑 | `CLOSED` |
| N-09 | P3 | 三处 freshness | 字段名互不相同且无任何检查 | 字段名保留各自模板原名（改名会与模板分叉），把值纳入 AC3 的三处一致性断言 | AC3 现同时断言 gate 值、freshness 值、RD 编号；freshness 改 `stale` 时 exit 1 | `CLOSED` |
| N-10 | P3 | `.charter/current-task.md` §3 | 「用户已有改动已记录与保护」未勾选，隔离只是声称 | 勾选并写明基线清单 `.charter/evidence/baseline-2026-10-19.txt`（79 行 = 77 `M` + 2 未跟踪），由 AC2 逐行比对；限制记作 `HOLDS_BY_DECLARATION` | 该前置项已 `[x]`，AC2 会在清单变化时变红 | `CLOSED` |

## Verdict

`REQUEST_CHANGES`

理由（审阅当时）：十二条 findings 确已关闭，三条半关闭；更关键的是修复动作在叶合同里删掉了一整节负向验收并留下了存在性断言，这两处正好落在本套件最锋利的两条判据上（编号只增不改、检查必须能移动退出码）。按 `.charter/project.md` 第 5 节与 `roadmap.md` 的规则，未对平的分歧保持阻塞。

处置后状态：N-01 … N-10 已全部按上表处置，证据在 `.charter/evidence/ac-liveness-2026-10-19.txt`（五条 AC 全部在原样运行时 exit 0，且各自被一条真实突变打红）。**本记录不自我批准**：需要 `REV-CHARTER-03` 复验上述十条处置，之后才轮到用户批准章程。

## Re-review trigger

任何对 `.charter/` 目标、不变量、授权边界、成功等级的改动；任何 findings 处置被推翻；章程走向批准；或 `D-06` 到期。
