# REV-CHARTER-04 — 章程级窄范围复验记录

## Review identity

- Review ID: `REV-CHARTER-04`
- Task ID: `CHARTER`
- Candidate revision: 工作区 `.charter/` 第 0.2 版（F-01…F-09 处置后），base `d6eff20`（full `d6eff20240adbcce327ca7cffe27053a6df6bd02`），未提交
- Reviewer: fresh subagent `dbcbbdaf-46b0-4f90-93ea-4771510a2c86`
- Review type: `CHARTER_INDEPENDENT`（窄范围：只核 F-01…F-09 是否关闭 + 活性证据能否复现）
- Freshness (Review A): `fresh-subagent`
- Applicability: `REQUIRED`（`REV-CHARTER-03` 规定复验）
- Timestamps: 本记录在处置完成后按批次写入；未记录审阅实测起止时刻（避免 `REV-CHARTER-04` 的 F-11 那类自相矛盾）。

## Independence declaration

- Different from implementer: `yes`
- Fresh context / fresh process: `yes` / `yes`
- Read implementer report before testing: `no`
- Limitation: 只读；全部突变实验做在 `cp -a` 的副本（含 `.git`）上，实验前后用 `diff -q` 自证副本逐文件一致，真实仓库 `git status` 仍 79 行、HEAD 仍 `d6eff20`。

## Verdict

`REQUEST_CHANGES`

理由（审阅者原文要点）：F-01…F-09 九条全部 `CLOSED`，活性证据可复现 —— 5 段检查文本与合同逐字节比对 5/5 相同，独立跑了 23 个自己的突变场景（与 .charter/evidence 表的 22 行不是同一套，两者不必相等），每条都在对象被改坏时变红、在允许路径与控制组上保持绿。但 F-10（P2，新）未闭合：`handoff.md` 第 43 行与第 59 行仍停在「待 / 派 `REV-CHARTER-03`」，与同文件第 42 行、`project.md:70`、`REV-CHARTER-03` 记录三处冲突；而 handoff 是六件启动必读件之一，照第 59 行执行会重派一个已完成的审阅。按章程不变量「投影不一致是阻塞发现」，判 `REQUEST_CHANGES` 而非 `APPROVE`。

## Findings

| ID | 严重度 | 位置 | 判定 | 处置（本轮已落地） | Disposition |
|---|---|---|---|---|---|
| F-01 | P1 | `.charter/current-task.md` AC2 | `CLOSED`（复现 10 个场景全部按预期） | 无 | `CLOSED` |
| F-02 | P2 | `.charter/current-task.md` AC1 | `CLOSED`（复现 7 个场景，含 decoy 与表头改名） | 无 | `CLOSED` |
| F-03 | P2 | `.charter/current-task.md` AC3 | `CLOSED`（复现 4 个场景，含格式合法的假 RD 号） | 无 | `CLOSED` |
| F-04 | P2 | `.charter/reuse-discovery.md:6` | `CLOSED` | 无 | `CLOSED` |
| F-05 | P2 | `.charter/project.md:70` | `CLOSED`（记录条数与半关闭计数自洽） | 本轮继续追加 `REV-CHARTER-04` 一轮 | `CLOSED` |
| F-06 | P2 | `.charter/handoff.md:42` | `CLOSED`，但同文件另有未跟进的两行 → F-10 | 第 42 行改写成 `REV-CHARTER-04` 结果并保留「不得写成无」 | `CLOSED` |
| F-07 | P3 | `.charter/evidence/ac-liveness-2026-10-19.txt` | `CLOSED`（结构完整、命令原文与合同逐字节一致） | 重跑并重生成（本轮 AC 变更后） | `CLOSED` |
| F-08 | P3 | `.charter/handoff.md:24` | `CLOSED`；建议加限定词指明是 `.charter/project.md` 的第 N 节 | 建议采纳：措辞改成带文件名 | `CLOSED` |
| F-09 | P3 | `.charter/project.md:231` | `CLOSED` | 无 | `CLOSED` |
| F-10 | P2 | `.charter/handoff.md:43` 与 `:59` | 投影停在上一轮 | 第 43 行改成四轮全记（01 → 02 → 03 = `REQUEST_CHANGES` → 04 = `REQUEST_CHANGES` → 待 05）；第 59 行改成派 `REV-CHARTER-05` 并写明只核 F-10 / F-11 / F-12 / O-01 / O-02 + 两条新突变 | `CLOSED` |
| F-11 | P3 | `.charter/records/REV-CHARTER-03.md:12` 与 `.charter/evidence/validate-2026-10-19.txt:1` | 记录 mtime 早于自述开始时刻 | `REV-CHARTER-03` 的起止行改为「批次写入标签」并注明取自文件 mtime、不是实测审阅时间；本记录不再写实测起止 | `CLOSED` |
| F-12 | P3 | `.charter/records/REV-CHARTER-03.md:1` 与 `.charter/project.md:70` | `BLOCK` 不在 `review.md` 的 Verdict 枚举内 | 两处都改用枚举词 `REQUEST_CHANGES`，并在 `REV-CHARTER-03` 里留一行说明「原判词 `BLOCK` 读作带未闭合 blocker 的 `REQUEST_CHANGES`」，此后记录只用枚举词 | `CLOSED` |
| O-01 | P3 | `.charter/current-task.md:138` | AC5 说明写全等、检查用前缀 | 检查改成全等（跟完整 SHA `d6eff20240adbcce327ca7cffe27053a6df6bd02` 比），说明与检查一致 | `CLOSED` |
| O-02 | P3 | `.charter/current-task.md:91` | 叶内第二条 `Status` 行不会被发现 | AC1 增加「`^- Status:` 必须恰好出现一次」，并新增一条突变（追加第二条 Status 行）证明会变红 | `CLOSED` |

## 活性证据（本轮重生成）

AC1 / AC2 / AC3 / AC4 / AC5 原样全部 exit 0。重生成后共 22 条突变：19 条打红、3 条控制组保持绿（允许路径内新建文件、允许路径内追加、允许路径内改名）。两条本轮新增、专为关闭 O-01 / O-02 而设：

| 突变 | 目标 | exit |
|---|---|---|
| 给叶追加第二条 `- Status: PASS_CLOSED` 行 | AC1 | 1 |
| 把检查里的完整 SHA 缩短成 7 位 `d6eff20`（前缀匹配） | AC5 | 1 |

另外两条把「不该红的时候不许红」写成断言：允许路径内改名（`.charter/changelog.md` → `.charter/changelog-moved.md`）必须 exit 0，而允许路径外改名（`portable/templates/review.md`）必须 exit 1。

## Re-review trigger

F-10 / F-11 / F-12 / O-01 / O-02 的关闭需 `REV-CHARTER-05` 窄范围复验；任何对目标、不变量、授权边界、成功等级的改动；或章程走向批准。本记录不自我批准。
