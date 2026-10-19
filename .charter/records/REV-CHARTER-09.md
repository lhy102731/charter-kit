# REV-CHARTER-09 — 窄范围复验（NF-01 / NF-02 / NF-03 + 一条一致性）

- Reviewer: fresh subagent `62cf97e1-6161-43e5-b681-7ce990e38768`，独立上下文，只读
- Independence declaration: 未读本次处置的任何说明，未参与任何一处编辑；实验只在 `cp -a` 副本里做，真实仓库开工/收尾非 `.git` 树聚合哈希相同（354 文件，`051a6a6dc9992d280d078b99d4acf8af8ba29eec460f1a031efb4bdbc64170ed`），`git status --porcelain` 收尾仍 79 行
- Scope: 只核 `REV-CHARTER-08` 的 NF-01 / NF-02 / NF-03 与一条一致性；不重做 CHK 全表，不重验已 `CLOSED` 的 F-01…F-25 与 O-01 / O-02
- Verdict: `REQUEST_CHANGES`

## 逐条判定

| 项 | 判定 | 依据 |
|---|---|---|
| NF-01 | 字面 `CLOSED` / 目的 `NOT CLOSED` | 四处轮数断言确已清零（`project.md:30`、`:172`、`handoff.md:84`、`:89`），`project.md:70` 为唯一逐轮枚举处，`handoff.md:42` / `:43` 已改指针；但全仓 grep 后仍有两处「会随每轮变化却写在散文里」的现状断言 → NF-05 / NF-06 / NF-07 |
| NF-02 | `CLOSED` | `handoff.md:72` 的 seam 已是 `REV-CHARTER-08` 的 NF-01…NF-03，并写明「本行的『本轮』随每轮重算，不是历史」 |
| NF-03 | 点名位置 `CLOSED`，缺陷本体存活 | `SELF-AUDIT.md:880` 已是「findings 表 5 行 + 复验判定表 5 行」（实测 5 + 5）；但同一测量在 `:902` 仍写「05 10」→ NF-04 |

## Findings 与处置

| ID | 严重度 | 文件:行号 | 问题 | 处置 |
|---|---|---|---|---|
| NF-04 | P3 | `docs/SELF-AUDIT.md:902` | 「机械计数（… / 05 10 / …）」与同文件 `:880` 的「5 行 + 5 行」冲突；同一现行文件对同一次测量给出两个值。附带指出：`:920` 明文规定「原行不改、更正另起一行」，而 NF-03 的处置是就地改写，同一文档并存两套更正惯例 | 就地把跨节汇总的计数列表整段删掉，改为「每轮的行数写在该轮自己的记录里，本节不再汇总裁数」；并在 `SELF-AUDIT` 里立一条分界：**历史判词与记录用「原行不改 + 更正行」，跨节复制的计量数一律就地删除、不允许两个值并存**（`CLOSED`） |
| NF-05 | P2 | `.charter/project.md:172` | 「章程级审阅链的每一轮都判 `REQUEST_CHANGES`」是 `:70` 之外的第二个写值处；下一轮判 `APPROVE` 即与 `:70` 相撞 | 删掉该聚合分句，改为「逐轮判词见 `project.md:70` 的枚举（本行不聚合判定）」（`CLOSED`） |
| NF-06 | P3 | `.charter/handoff.md:89` | 「截至最近一轮判词全是 `REQUEST_CHANGES`…尚无一份记 `APPROVE`」与 `:43` 重复同一会变事实 | `:89` 只留 fresh-subagent 的方法断言，状态改指 `:43`（`CLOSED`） |
| NF-07 | P3 | `records/REV-CHARTER-08.md:51`、`:53`；`docs/SELF-AUDIT.md:916`、`:918` | 「缺陷类型在结构上不再可能发生」「handoff 只保留『当前有没有 APPROVE、待哪一轮』这一个会变的事实」与产物不符 | 四处声称收窄为「删掉了**轮数**这一项」，并点名残余的 `:172` 与 `:89`（`CLOSED`） |

## 为什么 NF-05 是 P2 而不是 P3

NF-01 的处置把「轮数」这一维关掉了，但「判词聚合」是同一类的另一维：`project.md:70` 的枚举会随每轮增长，而散文里的「每一轮都判 X」是一个**永远会过期的全称断言**。它与 `REV-CHARTER-08` 的 NF-01 同源，且落在章程正文里——读章程就会撞见，所以按 P2 记。这一轮的教训是：**删掉一个会变的数，不等于删掉所有会变的事实**；每一处「现状断言」都要问一句「它下一次会因为什么而变」。

## 审阅者自跑的机械核对（未引用他人数字）

- `git rev-parse HEAD` = `d6eff20240adbcce327ca7cffe27053a6df6bd02`；`git status --porcelain` = 79；`git ls-files` = 332
- `ls .charter/records/` = 8（`REV-CHARTER-01…08`），与 `project.md:70` 的逐轮枚举逐项一致
- `validate_kit.py .` → `PASS (246 files checked)`，11 项子检查全绿，exit 0
- AC1–AC5 从叶合同 `check:` 原文抽取、cwd = 仓根 → 全 exit 0
- findings 行数（按标题分组数数据行）：01 15 / 02 10 / 03 9 / 04 14 / 05 **5**（另复验判定 5）/ 06 3 / 07 5 / 08 6+3；唯一冲突是 `:902` 的「05 10」
- 零改动自证：354 文件聚合 sha256 `051a6a6dc9992d280d078b99d4acf8af8ba29eec460f1a031efb4bdbc64170ed`，开工 = 收尾

## 明确未验

`pytest`（`SELF-AUDIT` 声称 298 passed / 519 subtests，审阅者未跑，不作为证据）；已 `CLOSED` 的 F-01…F-25 与 O-01 / O-02；CHK 全表；`plugins/` 三份生成副本与 `.charter/` 的同步一致性；`.jspace` ledger 本体；`review.md` / `roadmap.md` / `decision.md` 的逐行内容。

## Re-review trigger

本轮不自我批准。需 `REV-CHARTER-10` 窄范围复核：只核 NF-04…NF-07 四处处置是否成立、更正惯例那条分界是否写进文档且无第二个值并存，以及「删掉一个会变的数不等于删掉所有会变的事实」这条教训是否已被落地为可检查的规则；不重做 CHK 全表，不重验已 `CLOSED` 项。
