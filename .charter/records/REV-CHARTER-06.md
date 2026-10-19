# REV-CHARTER-06 — 章程级窄范围复验记录

## Review identity

- Review ID: `REV-CHARTER-06`
- Task ID: `CHARTER`
- Candidate revision: 工作区 `.charter/` 第 0.2 版（F-13…F-17 处置后），base `d6eff20`，未提交
- Reviewer: fresh subagent `b05307dc-46e4-462d-91b3-754e661c3bd7`
- Review type: `CHARTER_INDEPENDENT`（窄范围：F-13…F-17 五条 + 自查有无别的行停在旧轮次）
- Freshness (Review A): `fresh-subagent`
- Applicability: `REQUIRED`（`REV-CHARTER-05` 规定复验）
- Timestamps: 批次写入标签，未记录实测审阅起止时刻。

## Independence declaration

- Different from implementer: `yes`
- Fresh context / fresh process: `yes` / `yes`
- Read implementer report before testing: `no`
- Limitation: 只读；突变全部在临时副本 `kitpristine` → `kitwork` 内跑；真实仓库非 `.git` 树 533 个文件逐字节与开工快照一致，聚合 `sha256 = 3fe761862ed9cb6813aa1cde1bc961fb3cc2ea3cd8c3f6e9df50ad085409e018`，HEAD 仍 `d6eff20`、`git status` 仍 79 行。
- 审阅者自查披露：第一版突变驱动用裸 `bash`，命中 PATH 上的 WSL 桩 `C:\Windows\System32\bash.exe`，基线也一律 rc=1、22/22 假红，整轮作废；改用 `@dsh-ops/bash-win32-x64/usr/bin/bash.EXE` 重跑，报告里所有数字取自重跑。

## Verdict

`REQUEST_CHANGES`

F-13 / F-14 / F-15 / F-17 四条 `CLOSED`；F-16 的四个计分项（22 条 / 19 红 / 3 控制绿 / AC2 九种六红三控制）与证据表逐项相符，但**同一病灶**在「突变场景总数」上留下 23 与 22 两个数并存，另有两处同源投影停在旧轮次或缺记录指针。按本仓不变量「同一事实多处只有一处权威，不一致是阻塞发现」判 `REQUEST_CHANGES`。

## Findings

| ID | 严重度 | 位置 | 问题 | 处置（本轮已落地） | Disposition |
|---|---|---|---|---|---|
| F-18 | P3 | `.charter/handoff.md:42`、`.charter/project.md:70`、`.charter/records/REV-CHARTER-04.md:25` | 三处写「审阅者独立跑了 23 个突变场景」，与证据表 22 行并存，读起来像证据表少一行 | 三处都改成「23 个**自己的**突变场景（与证据表 22 行不是同一套，两者不必相等）」。保留 23 而不是简单改 22，因为 23 是审阅者自跑的集合，22 是证据表的行数，两者本来就不是同一个量 | `CLOSED` |
| F-19 | P3 | `.charter/handoff.md:72` | Session ledger 仍写「最近 seam = 章程级 REV-CHARTER-02 的 N-01…N-10 处置完成」 | 改为「最近 seam = 章程级 `REV-CHARTER-06` 的 F-18…F-20 处置完成（本轮）」，并注明 `.jspace` ledger 自 2026-10-19T12:45Z 起未再更新、本节是它的权威投影 | `CLOSED` |
| F-20 | P3 | `.charter/project.md:30 / :154 / :172` | 三处把 `BLOCK` 当判词且不给记录指针；与「五轮全 `REQUEST_CHANGES`」并置时读起来像同一条线自相矛盾 | 三处都补上 `docs/SELF-AUDIT.md` 第 9.9 节的指针，并写明这是**套件级**的另一条审阅线（审 `git diff 6c2a9bf d6eff20`），与章程级六轮不是同一条链；`BLOCK` 按枚举读作「带未闭合 blocker 的独立判词」 | `CLOSED` |

更正（由 `REV-CHARTER-07` 的 F-22 提出）：F-20 那一行写的「三处都补上记录指针，并写明这是套件级的另一条审阅线（审 `git diff 6c2a9bf d6eff20`）」在写入当时并不成立 —— 三处指针落了，但 diff 区间在 `project.md` 里零命中、`:172` 的枚举括注缺失。这两项在 `REV-CHARTER-07` 轮才真正落进 `project.md`。原行不改，此行为更正并点名被更正的行。

## 审阅者实测的数字（逐项）

证据表 `.charter/evidence/ac-liveness-2026-10-19.txt` 的突变表：表头 `:84`、分隔 `:85`，数据行 `:86-:107` **共 22 行**——AC1 6 行全 exit 1；AC3 4 行全 1；AC2 9 行（1,1,0,0,1,1,0,1,1）；AC5 2 行全 1；AC4 1 行 = 1。合计 **19 条 exit 1 + 3 条 exit 0**，AC2 九行其中三行是控制组。

比对：`handoff.md:54`、`REV-04.md:48`、`REV-05.md:50`、`ac-liveness:130` 全部相符；唯一不符的是「23 个突变场景」（→ F-18）。审阅者在 `cp -a` 副本里逐条重建树，22/22 的 exit 与证据表逐条相同。

审阅者明确**未验**：`pytest -q` 的 298 passed / 519 subtests；REV-01/02 记录条目内容（只取计数）；validate 的 11 项子检查逐项断言；D-01 / D-02 决策记录；三个 builder 的 `--check`；叶级 Review A（尚不存在）；`.charter/` 是否应单独提交；`.jspace` ledger 的语义（只读了 `control.json` 的 goal/next）。

## Re-review trigger

F-18 / F-19 / F-20 的关闭需 `REV-CHARTER-07` 窄范围复验；任何对目标、不变量、授权边界、成功等级的改动；或章程走向批准。本记录不自我批准。
