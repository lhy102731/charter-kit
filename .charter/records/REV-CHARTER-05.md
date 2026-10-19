# REV-CHARTER-05 — 章程级窄范围复验记录

## Review identity

- Review ID: `REV-CHARTER-05`
- Task ID: `CHARTER`
- Candidate revision: 工作区 `.charter/` 第 0.2 版（F-01…F-09 与 F-10/O-01/O-02 处置后），base `d6eff20`，未提交
- Reviewer: fresh subagent `d8f6aaac-b669-4ae9-903b-005378a98416`
- Review type: `CHARTER_INDEPENDENT`（窄范围：F-10 / F-11 / F-12 / O-01 / O-02 五条 + 两条新突变可复现性）
- Freshness (Review A): `fresh-subagent`
- Applicability: `REQUIRED`（`REV-CHARTER-04` 规定复验）
- Timestamps: 批次写入标签，未记录实测审阅起止时刻（F-11 的教训）。

## Independence declaration

- Different from implementer: `yes`
- Fresh context / fresh process: `yes` / `yes`
- Read implementer report before testing: `no`
- Limitation: 只读；突变全部在 `cp -a` 副本（含 `.git`）内，真实仓库全仓文件哈希开工前后均为 `c5c5ce1cf465b314cf71831e977e1d591d157e3b3d9b8c611615b7f2bfa73f30`。
- 审阅者的自查披露：第一版突变驱动用裸 `bash`，PATH 命中 WSL 桩 `C:\Windows\System32\bash.exe`，每条都返回 rc=1，把 3 条控制组误判成 MISMATCH；该轮结果整份作废，改用 dsh-ops 自带 bash 重跑并加逐条树哈希完整性断言。

## Verdict

`REQUEST_CHANGES`

F-11 / F-12 / O-01 / O-02 四条 `CLOSED`；F-10 **NOT CLOSED** —— `.charter/handoff.md:43` 仍把 `REV-CHARTER-03` 记成 `BLOCK`，与 `.charter/records/REV-CHARTER-03.md:24` 和 `.charter/project.md:70` 的 `REQUEST_CHANGES` 冲突，且 `BLOCK` 不在 Verdict 枚举内。

## Findings

| ID | 严重度 | 位置 | 问题 | 处置（本轮已落地） | Disposition |
|---|---|---|---|---|---|
| F-13 | P2 | `.charter/handoff.md:43` | 审阅状态行仍写 `REV-CHARTER-03` = `BLOCK` | 改为 `REQUEST_CHANGES`，保留「原判词写作 `BLOCK`」并说明按枚举读作带未闭合 blocker 的 `REQUEST_CHANGES`；三处投影自此一致 | `CLOSED` |
| F-14 | P3 | `.charter/handoff.md:43`、`.charter/project.md:70` | 两处写「新增 F-10 与三条 P3」，同文件 :42 与 REV-04 表都是四条 | 两处都改为「四条 P3」 | `CLOSED` |
| F-15 | P3 | `.charter/project.md:70` | 「章程级已跑三轮」但同格列了四轮 | 改为「四轮」 | `CLOSED` |
| F-16 | P3 | `.charter/handoff.md:54`、本记录 | 正文称 21 条突变（18 红 / 3 绿）、AC2 八种；实测证据表 22 行 = 19 红 + 3 绿，AC2 占 9 行 | 正文与记录都改为「22 条（19 打红、3 控制组绿）」「AC2 九种（六红三控制）」，并显式计入 AC4 一条；审阅者已按表复现 22/22 与 exit 列一致，错的是正文计数不是证据 | `CLOSED` |
| F-17 | P3 | `.charter/evidence/ac-liveness-2026-10-19.txt:82` | 小节标题写「each applied to the working tree」，而两条 AC5 突变实际改的是检查文本 | 标题改为「applied to the working tree, except the AC5 rows which mutate the check text itself, as their wording says」 | `CLOSED` |

## 上一轮五条的闭合判定

| 条目 | 判定 | 依据 |
|---|---|---|
| F-10 | `NOT CLOSED` → 本轮修完（F-13 / F-14 / F-15） | :59 上轮已修；:43 本轮修 |
| F-11 | `CLOSED` | REV-03:12 / :13 明确时刻取自文件 mtime、是批次写入标签 |
| F-12 | `CLOSED` | REV-03:24 与 project.md:70 均为 `REQUEST_CHANGES`，落在 `portable/templates/review.md` 的枚举内 |
| O-01 | `CLOSED` | 说明与检查均为完整 SHA 全等；缩成 7 位 → exit 1，换 deadbeef → exit 1 |
| O-02 | `CLOSED` | `len(sn)==1` 进判定；追加第二条 Status 行 → exit 1 |

## 复核的活性证据

审阅者在副本内先跑无突变基线（AC1–AC5 全 exit 0），再逐条跑 **22 条突变，22/22 与证据表的 exit 列一致（19 红 / 3 控制绿）**，每条突变前后断言副本树哈希等于基线（`9f53c0dd942f5330b21f106e714a74a615296279edc3b029eebb04ff0b2038af`），收尾哈希 IDENTICAL。抽查四条：AC1 第二条 Status 行 → 1、AC5 期望 SHA 缩 7 位 → 1、AC2 允许路径内改名（控制组）→ 0、AC2 允许路径外改名 → 1。

审阅者明确**未验**：`pytest -q` 298 passed / 519 subtests；REV-01/02 条目内容（只用其计数）；validate_kit 的 11 项子检查逐项断言；D-01 / D-02 决策记录；三个 builder 的 `--check`；叶级 Review A（尚不存在）；`.charter/` 是否应单独提交；F-01…F-09 的关闭状态。

## Re-review trigger

F-13…F-17 的关闭需 `REV-CHARTER-06` 窄范围复验；任何对目标、不变量、授权边界、成功等级的改动；或章程走向批准。本记录不自我批准。
