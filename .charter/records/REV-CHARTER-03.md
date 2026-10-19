# REV-CHARTER-03 — 章程级窄范围复验记录

## Review identity

- Review ID: `REV-CHARTER-03`
- Task ID: `CHARTER`
- Candidate revision: 工作区 `.charter/` 第 0.2 版（N-01…N-10 处置后），base `d6eff20`，未提交
- Reviewer: fresh subagent `63dd44b4-83da-48b0-8246-0fdc5f04ab0b`
- Review type: `CHARTER_INDEPENDENT`（窄范围：只核 N-01…N-10 与五条 AC 的活性）
- Freshness (Review A): `fresh-subagent`
- Applicability: `REQUIRED`（`REV-CHARTER-02` 规定复验）
- Timestamps: 本记录与 `.charter/evidence/validate-2026-10-19.txt` 在同一批次里写入，下面两个时刻取自文件 mtime（批次写入标签），不是审阅过程的实测起止时间 —— 见 `REV-CHARTER-04` 的 F-11。
- Started / finished (batch-write labels): 2026-10-19T13:10:14Z / 2026-10-19T13:10:18Z

## Independence declaration

- Different from implementer: `yes`
- Fresh context / fresh process: `yes` / `yes`
- Read implementer report before testing: `no`
- Limitation: 只读；突变实验在系统临时目录的副本上做（仓库零改动，复验前后 `git status` 均为 79 行、HEAD 均为 `d6eff20`）。

## Verdict

`REQUEST_CHANGES`（原判词写作 `BLOCK`）

> Verdict 词说明（见 `REV-CHARTER-04` 的 F-12）：`portable/templates/review.md` 的 Verdict 枚举只有 `APPROVE` / `APPROVE_WITH_LIMITATIONS` / `REQUEST_CHANGES` / `BLOCKED_TOOLING` / `NEEDS_DECISION`。本轮审阅者给出的 `BLOCK` 不在枚举内，按语义读作「有未闭合的 P1/P2 的 `REQUEST_CHANGES`」；本行已改成枚举词，原判词保留在这句里。此后所有记录只用枚举词。

理由：两条最锋利的判据仍有违反 —— N-02 的 `AC1` 对整个单元格列表做**成员测试**（叶 Status 改成 `LEAF` 仍是 exit 0），N-01 的 `AC2` 丢掉 porcelain 状态码且只比四个前缀（删除 guarded 文件、改 `DEVELOPMENT_CHARTER.md`、加 `plugins/` 都 exit 0）；再加上 0.2 bump 自身留下章程版本投影失同步（`reuse-discovery.md:6` = 0.1 对 `project.md:6` = 0.2）。N-03/N-05/N-06/N-07/N-08/N-09/N-10 判 CLOSED，N-01/N-02/N-10 与活性证据判 PARTIAL/NOT_CLOSED。

## Findings

|---|---|---|---|---|
| ID | 严重度 | 位置 | 问题 | 处置 | Disposition |
|---|---|---|---|---|
| F-01 | P1 | `.charter/current-task.md` AC2 | `l[3:]` 丢状态码，且只取 `portable/`/`targets/`/`scripts/`/`tests/` 四个前缀；删除 baseline 已列文件、改 `DEVELOPMENT_CHARTER.md`、加 `plugins/` 或 `docs/` 文件全部 exit 0，79 行基线里 56 行从未参与比对 | 换成「全量（状态码，路径）集合对比 + 允许路径白名单 `.charter/**` 与 `docs/SELF-AUDIT.md`」，并加一条 `git diff` 摘要 `diff-sha256` 覆盖「已脏文件被继续改写」这类 porcelain 看不出的变化（摘要记在基线文件首部） | `CLOSED` |
| F-02 | P2 | `.charter/current-task.md` AC1 | `s in cells` 是对整行所有单元的成员测试，不是 Status 单元比对 | 改为按 ID 单元（第 3 列）唯一定位行、按表头 `Status` 列取该行固定单元格与叶 `^- Status:` 比对；decoy 行会让命中数 ≠ 1 而变红 | `CLOSED` |
| F-03 | P2 | `.charter/current-task.md` AC3 | RD 子句是三处文件全文的 `in` 测试；把字段改成 `-99` 而旧 id 留在注释里仍 exit 0 | 改为按字段标签取**值**再比（三处 `Reuse discovery ID` / `Discovery ID`），并断言值以 `RD-` 开头 | `CLOSED` |
| F-04 | P2 | `.charter/reuse-discovery.md:6` | 仍写 `Charter reference / version: .charter/project.md / 0.1`，而 `project.md:6` 已是 `0.2` | 改为 `0.2`；这是 0.2 bump 自身制造的失同步，属阻塞类 | `CLOSED` |
| F-05 | P2 | `.charter/project.md:70` | `INDEPENDENT_REVIEW` 行仍写「复验 REV-CHARTER-02 待做」 | 改写为三轮全记（01 REQUEST_CHANGES / 02 REQUEST_CHANGES / 03 BLOCK）并写明「未拿到 APPROVE 前本行不得写 PASS」 | `CLOSED` |
| F-06 | P2 | `.charter/handoff.md:42` | 「Open findings: 无，N-01…N-10 已全部 CLOSED」与重算相反 | 改写为「REV-03 判 BLOCK，九条已处置，REV-04 未回，本行不得写成无」 | `CLOSED` |
| F-07 | P3 | `.charter/evidence/ac-liveness-2026-10-19.txt` | 只有结果行，无命令文本、无对象侧突变 | 重写证据：逐条抄录合同里的 check 原文，做**对象侧**突变（改叶 Status、改 roadmap 单元格、插 decoy 行、改 gate/freshness/RD 字段、加/删文件、改已脏文件、破坏镜像），每次突变后还原，最后 clean 复跑 | `CLOSED` |
| F-08 | P3 | `.charter/handoff.md:24` | 以「章程第 9 节」当更宽效果来源 | 改为章程第 5 节（Scope and effects），并写明第 9 节只给 `MANUAL` 任务授权、两者都不能放宽本叶 | `CLOSED` |
| F-09 | P3 | `.charter/project.md:231` | D-06 标 `DEFERRED` 但缺召回触发 | 补「召回触发：任何叶需要日志自证运行参数、或任何人改动该脚本的日志格式时回到 `OPEN`」 | `CLOSED` |

## 处置后的活性证据（同一次提交内的 `.charter/evidence/ac-liveness-2026-10-19.txt`）

原样运行：AC1 / AC2 / AC3 / AC4 / AC5 全部 exit 0。对象侧突变（每次突变后立即按字节还原）：

| 突变 | 目标 | exit |
|---|---|---|---|---|
| 叶 `Status` → `PASS_CLOSED` | AC1 | 1 |
| 叶 `Status` → `LEAF`（已存在的 Level 单元值，成员测试骗得过的那个） | AC1 | 1 |
| roadmap 真行 Status 单元格 → `READY` | AC1 | 1 |
| 表头之外插一行携带同 ID 的 decoy | AC1 | 1 |
| roadmap gate → `COMPLETE` | AC3 | 1 |
| reuse 记录 freshness → `stale` | AC3 | 1 |
| `project.md` RD 值 → `-99` | AC3 | 1 |
| RD 值 → `-99` 且旧 id 仍留在注释行 | AC3 | 1 |
| 新增 `portable/templates/zzz-probe.md` | AC2 | 1 |
| 新增 `docs/other-probe.md`（允许路径之外） | AC2 | 1 |
| 新增 `.charter/probe-allowed.md`（允许路径之内，**必须保持绿**） | AC2 | 0 |
| 删除基线已列出的 `portable/commands/charter-workflow.md` | AC2 | 1 |
| 对已脏文件 `DEVELOPMENT_CHARTER.md` 再追加一行 | AC2 | 1 |
| 抽出命令里的期望提交 → `deadbeef` | AC5 | 1 |
| 给 `portable/templates/review.md` 追加一个换行（破坏镜像） | AC4 | 1 |

突变全部还原后复跑：AC1 / AC2 / AC3 / AC4 / AC5 全部 exit 0；`git status --porcelain` 仍 79 行，HEAD 仍 `d6eff20`。

## Re-review trigger

任何对 `.charter/` 目标、不变量、授权边界、成功等级的改动；任何 findings 处置被推翻；章程走向批准；或 `D-06` 的召回触发命中。本记录不自我批准 —— 需要 `REV-CHARTER-04` 复验上述九条与活性证据。
