# REV-CHARTER-07 — 章程级窄范围复验记录

## Review identity

- Review ID: `REV-CHARTER-07`
- Task ID: `CHARTER`
- Candidate revision: 工作区 `.charter/` 第 0.2 版（F-18…F-20 处置后），base `d6eff20`，未提交
- Reviewer: fresh subagent `58d8d174-f85f-4ea4-bbcf-c73aba93c5e7`
- Review type: `CHARTER_INDEPENDENT`（窄范围：F-18 / F-19 / F-20 三条 + 机械核对与计数）
- Freshness (Review A): `fresh-subagent`
- Applicability: `REQUIRED`（`REV-CHARTER-06` 规定复验）
- Timestamps: 批次写入标签，未记录实测审阅起止时刻。

## Independence declaration

- Different from implementer: `yes`
- Fresh context / fresh process: `yes` / `yes`
- Read implementer report before testing: `no`
- Limitation: 只读，未修改任何仓内文件；临时脚本写在仓外并已清除。披露一次失误——第一遍把辅助脚本误写进仓根，`AC2` 因多出一条白名单外未跟踪文件而变红；删除后重跑即 `exit 0`，收尾 `git status` 仍 79 行、HEAD 未变、仓内无残留。
- 两条可复用核对手法：① findings 表机械计数（REV-01 15 行 / 02 10 行 / 03 9 行 / 04 14 行 / 05 10 行 / 06 3 行）；② 真实仓库非 `.git` 树逐字节聚合哈希，开工与收尾必须相等（比 `git status` 有力，后者只看被跟踪路径）。

## Verdict

`REQUEST_CHANGES`

F-18 / F-19 判 `CLOSED`；F-20 判 `PARTIAL` —— 三处记录指针确实到位，但被处置表声称「已落地」的两项内容（`git diff 6c2a9bf d6eff20` 区间与 `:172` 的枚举括注）在 `project.md` 内零命中，属于声明与产物不符。另新开 F-21（两处仍写「章程级五轮」，且 `:30` 的「本文件第 6 项」悬空）、F-23（`handoff` 的 capability notes 停在第五轮）、F-24（`.jspace` 边界时刻取的是 init 标签而非最后写入时刻）、F-25（`docs/SELF-AUDIT.md:825` 缺同一限定语），四条同源或计数性 P3。按本仓不变量「同一事实只有一处权威，不一致是阻塞发现」判 `REQUEST_CHANGES`。

## Findings

| ID | 严重度 | 位置 | 问题 | 处置（本轮已落地） | Disposition |
|---|---|---|---|---|---|
| F-21 | P3 | `.charter/project.md:30`、`:172` | 两处仍写「章程级五轮」，而 `records/` 已有 REV-01…06 六份、同文件 `:70` 写「已跑六轮」；`:30` 的「本文件第 6 项」也不指向章程级投影（在 §4 的 `:70`，§6 是资产审计） | 两处改「六轮」；`:30` 的指针改为「本文件第 4 节 `INDEPENDENT_REVIEW` 行（`project.md:70`）」 | `CLOSED` |
| F-22 | P3 | `.charter/project.md:30`、`:154`、`:172` | 三处都没有「审 `git diff 6c2a9bf d6eff20`」；`:172` 还缺 `BLOCK` 的枚举括注。而 `REV-CHARTER-06` 记录与 `docs/SELF-AUDIT.md` 都以「本轮已落地」写下这两项 | 三处补 diff 区间，`:172` 补枚举括注；并在 `REV-CHARTER-06` 记录追加一行更正（原行不改，更正行点名被更正行）——那两项在 REV-06 轮确实没有落，是 REV-07 轮才落 | `CLOSED` |
| F-23 | P3 | `.charter/handoff.md:84`、`:89` | 「连跑五轮 `REV-CHARTER-01…05`」「本会话实测五次（…01…05）」——第六轮已回。`handoff` 是六件启动必读件之一，capability notes 的轮次是「独立审阅能力已实测」的唯一依据，少记一轮等于把最近证据漏在读集里 | 两处改六轮 / 六次，`REV-CHARTER-01…06`，并写明 REV-03 原判词写作 `BLOCK` | `CLOSED` |
| F-24 | P3 | `.charter/handoff.md:72` | 「`.jspace` ledger 自 2026-10-19T12:45Z 起未再更新」：`control.json` 与 `CONTROL.md` 的 mtime 为 2026-10-19 20:48:01 +0800 = 12:48:01Z。「未再更新」的关键是边界时刻可核，拿 init 标签当最后写入时刻与文件证据差 3 分钟 | 改为「自 init（记录标签 12:45Z，最后写入 12:48:01Z）起未再更新」 | `CLOSED` |
| F-25 | P3 | `docs/SELF-AUDIT.md:825` | §9.10 正文仍写「审阅者独立跑了 23 个突变场景」且无限定，是 F-18 同一句的第四处；而该文件正是 F-20 三处指针的落点，顺指针回到这里会重新读到未加限定的 23 | 补同一限定语，与 `handoff:42`、`project.md:70`、`REV-CHARTER-04:25` 同句 | `CLOSED` |

F-20 的最终判定在本轮处置后应读作「已关闭但需 REV-CHARTER-08 复核」，在复验给出 `CLOSED` 之前不改它的历史判词。

## 审阅者实测的数字（逐项）

- `git rev-parse HEAD` = `d6eff20240adbcce327ca7cffe27053a6df6bd02` → 一致
- `git status --porcelain | wc -l` = 79（77 ` M` + 2 `??`）→ 与 baseline 首部一致
- `python scripts/validate_kit.py .` → `PASS (246 files checked)`，exit 0 → 一致
- 五条 AC 从 `current-task.md` 抽原文原样运行（未用裸 `bash`）：AC1 0 / AC2 0 / AC3 0 / AC4 0 / AC5 0 → 全部 `exit 0`
- `AC2` 内部 `diff-sha256` 与 baseline 记录值相等；两侧 (status, path) 集合对称差 = 0
- 证据表突变表：表头 `:84`、分隔 `:85`、数据 `:86-:107` = 22 行；`exit 1` 19 条（AC1 6 / AC3 4 / AC2 6 / AC5 2 / AC4 1）、`exit 0` 3 条（`:98` 新建 `.charter/` 内文件、`:99` 追加 `docs/SELF-AUDIT.md`、`:102` `.charter/` 内改名）；`AC2` 9 行 exit 序列 `1,1,0,0,1,1,0,1,1`
- 套件级 Review A 条数：`docs/SELF-AUDIT.md` 第 9.9 节十六条 = 2 blocker + 7 major + 7 minor，与 `project.md:30` 一致
- 计数摩擦（非错误，记录在案）：`handoff.md:54` 括注写「两条允许路径控制」，该处控制组实为 3 行；同一句里 3 与 2 并置会误导下一轮读者，但计数本身以证据表为准

审阅者明确**未验**：`pytest -q` 的 298 passed / 519 subtests；`validate_kit.py` 11 项子检查的逐条断言；22 条突变逐条重建（本轮只读）；REV-01 / 02 / 03 findings 的实质内容（只取计数与判词）；`roadmap.md` 与 `reuse-discovery.md` 除 AC1 / AC3 已断言的三处投影之外的字段；D-01…D-06 决策行；三个 builder 的 `--check`；`6c2a9bf…d6eff20` 区间的实际 diff 内容；套件级 Review A 的十六项处置是否真落地。

## Re-review trigger

F-21 / F-22 / F-23 / F-24 / F-25 与 F-20 的关闭需 `REV-CHARTER-08` 窄范围复验；任何对目标、不变量、授权边界、成功等级的改动；或章程走向批准。本记录不自我批准。
