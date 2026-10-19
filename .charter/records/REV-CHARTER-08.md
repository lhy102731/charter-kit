# REV-CHARTER-08 — 章程级窄范围复验记录

## Review identity

- Review ID: `REV-CHARTER-08`
- Task ID: `CHARTER`
- Candidate revision: 工作区 `.charter/` 第 0.2 版（F-20 收尾与 F-21…F-25 处置后），base `d6eff20`，未提交
- Reviewer: fresh subagent `41ad8598-3558-424c-8cef-b3f743166775`
- Review type: `CHARTER_INDEPENDENT`（窄范围：F-20 收尾 + F-21…F-25 + 机械核对）
- Freshness (Review A): `fresh-subagent`
- Applicability: `REQUIRED`（`REV-CHARTER-07` 规定复验）
- Timestamps: 批次写入标签，未记录实测审阅起止时刻。

## Independence declaration

- Different from implementer: `yes`
- Fresh context / fresh process: `yes` / `yes`
- Read implementer report before testing: `no`
- Limitation: 只读；全部写入落在仓外 `%TEMP%/rev08`；收尾 `git status --porcelain` 仍 79 行、HEAD 未变。未做突变实验，故本轮无副本与前后树哈希对；只给两个只读自证锚——跳过 `.git`/`.jspace`/缓存 490 文件聚合哈希、只跳 `.git` 535 文件聚合哈希。
- 披露：审阅者指出 `SELF-AUDIT` 上一条记的 533 文件 / `3fe761862ed9…` 是 `REV-CHARTER-06` 时点、不同 skip 集，与本轮口径不可直接相减。

## Verdict

`REQUEST_CHANGES`

F-22 / F-24 / F-25 与 F-20 收尾四项 `CLOSED`；F-21 与 F-23 判 `PARTIAL` —— 指针与字面落点都已到位，但同一批编辑把 `project.md:70` 改成「已跑七轮」的同时，`project.md:30`、`:172`、`handoff.md:84`、`:89` 仍写「六轮 / 六次 `01…06`」，而 `.charter/records/` 实有七份记录。同一事实两值并存，按章程不变量「同一事实只有一处权威，不一致是阻塞发现」判 `REQUEST_CHANGES`，记 NF-01。另开 NF-02（`handoff.md:72` 的 seam 停在第七轮之前且用会漂的「本轮」）与 NF-03（`SELF-AUDIT` 把 `REV-05` 的计数写成 10 行，实为 findings 5 行 + 复验判定表 5 行）。

## Findings（上一轮六条的判定）

| ID | 严重度 | 判定 | 依据 |
|---|---|---|---|
| F-21 | P3 | `PARTIAL` | 指针已修（`:30` 指向 §4 的 `project.md:70`，`第 6 项` 在 `project.md` 零命中）；但同一批编辑把 `:70` 改成七轮、按旧指令把 `:30`/`:172` 写成六轮 → 并入 NF-01 |
| F-22 | P3 | `CLOSED` | 三处 diff 区间齐备且正是 `project.md` 内 `6c2a9bf` 的全部三处命中；`:172` 枚举括注完整；`REV-CHARTER-06.md:36` 的更正行已立且 `:34` 原行逐字未改 |
| F-23 | P3 | `PARTIAL` | `handoff.md:84` / `:89` 字面已改六轮 / 六次并带 REV-03 的 `BLOCK` 说明；但 `:43` 已列到 REV-07 并写「待 REV-08」，同文件内七环对六轮 → 并入 NF-01 |
| F-24 | P3 | `CLOSED` | `handoff.md:72` 两个时刻并列；文件证据 `control.json` / `CONTROL.md` / `control.lock` 的 mtime 均为 `12:48:01Z` |
| F-25 | P3 | `CLOSED` | 全仓「23 个」九行，八行带限定；唯一未带的 `REV-06.md:42` 是把该短语作为被点名的失配项引述 |
| F-20 收尾 | P3 | `CLOSED` | `REV-CHARTER-07.md` 存在，findings 表五行 F-21…F-25 处置列全非空、Disposition 全 `CLOSED` |

## Findings（本轮新开）

| ID | 严重度 | 位置 | 问题 | 处置（本轮已落地） | Disposition |
|---|---|---|---|---|---|
| NF-01 | P2 | `project.md:30`、`:172`、`handoff.md:84`、`:89` | 四处写「章程级六轮」/「六次 `REV-CHARTER-01…06`」，而 `records/` 实有七份、`project.md:70` 与 `handoff:43` 已列到 `REV-CHARTER-07` | **不按「改成七轮」处置，而是把轮数从散文里删掉**：四处改为「轮次与判词以 `.charter/records/REV-CHARTER-*.md` 的文件集合为唯一权威，其他位置不重复计数」，`project.md:70` 保留为章程里的唯一投影。理由见下节 | `CLOSED` |
| NF-02 | P3 | `handoff.md:72` | 最近 seam 仍写 `REV-CHARTER-06` 的 F-18…F-20，且用会随轮次滚动的「本轮」 | seam 改为 `REV-CHARTER-08` 的 NF-01…NF-03 处置完成，并写明「本行的『本轮』随每轮重算，不是历史」 | `CLOSED` |
| NF-03 | P3 | `docs/SELF-AUDIT.md:880` | 「findings 表机械计数……`REV-05` 10 行」，而 `REV-CHARTER-05.md` 的 findings 表实为 5 行（10 = findings 5 + 复验判定表 5） | 改为「`REV-05` findings 表 5 行 + 复验判定表 5 行」，与同节已记的「两条允许路径控制 vs 3 行」同一写法 | `CLOSED` |

## 为什么 NF-01 不按建议处置

审阅者建议把四处改成「七轮 / 七次 `01…07`」。照做会在下一轮再次失配——每加一份记录，散文里的数字就落后一轮，这正是 F-15 → F-18 → F-21 → NF-01 连续四轮同一病灶的生成机制：**计数被复制到多处，而只有一处会被想起来更新**。

本轮采用更深的一层修法：把「几轮」从散文里整体删掉，只留一处权威（`.charter/records/` 的文件集合）和一处投影（`project.md:70`，每轮维护一次）。删掉之后，**轮数**这一项不再可能在两处打架：不是这一次写对了，而是没有第二个地方可写这个数。

同一处置也应用到了 `handoff.md`：`:42` 的 Open findings 与 `:43` 的 Review status 原来各自复述整条审阅链，现在改为指向 `project.md:70` 与 `.charter/records/`，不再复述整条链。状态行里仍留着几个会变的事实（`:42` 的「当前未闭合项」、`:43` 的「叶级 Review A 尚无」、`:89` 的可用性说明），`REV-CHARTER-09` 把其中两处判为 NF-06 / NF-07。

## 审阅者实测的数字（逐项）

- `git rev-parse HEAD` = `d6eff20240adbcce327ca7cffe27053a6df6bd02`；`git status --porcelain | wc -l` = 79（77 ` M` + 2 `??`：`.charter/`、`tests/test_absorption_contract.py`）
- `python scripts/validate_kit.py .` → `PASS (246 files checked)`，11 项子检查逐行、exit 0
- 五条 AC 从 `.charter/current-task.md:91/105/117/121/138` 抽原文、在仓根执行 → 全 `exit 0`；附注：AC 依赖 cwd = 仓根，从仓外执行会全红（实测 1/1/1/2/1）
- 证据表突变表 `:86-:107` = 22 行（19 红 / 3 控制绿），与四处记载一致
- 全仓 grep 七模式（自建遍历 490 文件）：`6c2a9bf` 13 行、`git diff ` 31 行、`五轮` 8 行（全为历史引述）、`六轮` 12 行（4 行为现状断言 → NF-01）、`七轮` 3 行、`23 个` 9 行、`第 6 项` 3 行（全为历史 finding 描述）
- findings 表机械计数：REV-01 15 / 02 10 / 03 9 / 04 14 / 05 5（另复验判定表 5）/ 06 3 / 07 5

审阅者明确**未验**：`pytest -q` 的 298 passed / 519 subtests；`validate_kit.py` 11 项子检查的逐条断言；五条 AC 的活性（本轮无突变）；REV-01…REV-05 findings 的实质内容；CHK 全表；已 `CLOSED` 的 F-01…F-19 与 O-01 / O-02；D-01…D-06；三个 builder 的 `--check`；叶级 Review A；`.charter/` 是否单独提交与批准动作本身。

## Re-review trigger

NF-01 / NF-02 / NF-03 的关闭需 `REV-CHARTER-09` 窄范围复验（只核这三条的落点，以及「散文里是否还残留轮数」）。任何对目标、不变量、授权边界、成功等级的改动；或章程走向批准。本记录不自我批准。
