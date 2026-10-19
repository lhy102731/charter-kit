# REV-CHARTER-12 — 窄范围复核（NF-09 残留 + NF-15…NF-18）

## Review identity
- 轮次：`REV-CHARTER-12`（章程级 `CHARTER_INDEPENDENT` 审阅链第 12 轮）
- 审阅对象：`.charter/reuse-discovery.md` 的复用记录、六件读集（`project.md` / `roadmap.md` / `reuse-discovery.md` / `current-task.md` / `handoff.md` / `lessons.md`）里的指针与计量数
- 范围外（按派单约束跳过）：CHK 全表、F-01…F-25、NF-01…NF-14 的历史判词
- 审阅者：fresh subagent `0b221ae5-6175-4260-9f5b-cd3287fb903d`，无实现上下文、只读

## Independence declaration
- 审阅者由父 agent 在干净上下文里派出，只拿到派单文本与仓库本身，没有本会话的实现历史。
- 实验在 `%TEMP%/rev12/` 的 `cp -a` 副本（含 `.git`）内进行，真仓 0 写入。开工与收尾两个锚点逐字节相同：`git ls-files -s` 的 sha256 `d534ad515ce454d12816adea750f920be2ae076b80f5e4568585af7488b2e4cc`（34241 字节）、`git status --porcelain` 的 sha256 `483cea696dfdb171c3af1bdaf8fa814c6a429589213e17d9cb40005fb9584d12`（4816 字节）。
- 执行器自证不是 WSL 桩：`bash=/usr/bin/bash`、`BASH_VERSION=5.3.15(2)-release`、`uname=MINGW64_NT-10.0-26200`。

## Verdict
`REQUEST_CHANGES` —— NF-16 / NF-17 / NF-18 `CLOSED`，NF-15 与 NF-09 判 `PARTIAL`，另开 NF-19 … NF-22 四条。

## 判定表
| 项 | 判定 | 依据 |
|---|---|---|
| NF-15 行号寻址漂移（P1） | `PARTIAL` | 原六处 `project.md:70` 已全部改为行标签寻址；六件读集全扫后只剩 1 处 file:line 指针，即 `reuse-discovery.md` 的 `SR-01` 行（指向 `charter-workflow.md:51`，而 Review A 执行模型在 `:50`，`:51` 是 Review B 触发规则行；`git show HEAD:` 版本同样如此 → 不是插行漂移而是格错）。该行的 `Exact query` 写作 `grep -rn Review-A portable/`，实跑 rc=1、0 命中（仓内措辞是带空格的 `Review A`，11 行命中）→ 其 `MATCH` 用自身命令不可复现 |
| NF-09 计量数唯一落点（P2） | `PARTIAL` | 上轮点名的两处已修（`handoff` 的 Evidence 表基运行、叶合同的基线字段均改为「见该文件首行注释」）。仍违规四处：`handoff` 两处「子检查条数」副本（且其中一处自称「本行即全套计量数的唯一落点」，与另一处并存自相矛盾）；`project.md` 的测试规模分解与章程文件体积两处「散文持有数字、证据零落点」；`handoff` 的突变计数与 per-AC 分项是跨节汇总别轮观测的复制 |
| NF-16 Lessons 状态行（P2） | `CLOSED` | 已改为「条数、最新条目与各条 Hits 一律以 `.charter/lessons.md` 的 Entries 段为准（本行不计数、不复述条目名）」 |
| NF-17 基线计数散文副本（P2） | `CLOSED` | `handoff` 的 Evidence 表与叶合同两处均只写「行数与分解见该文件首行注释，此处不复制」 |
| NF-18 证据文件重复小节（P3） | `CLOSED` | 15 个二级标题 `uniq -d` 为空；合并说明写明「两次运行独立、输出逐行相同」 |

## 审阅者自跑的机械核对
- HEAD `d6eff20240adbcce327ca7cffe27053a6df6bd02`；`git status --porcelain` 79 行；`git ls-files .charter` 0 行；`.charter/records/` 11 份，与 `project.md` 第 4 节 `INDEPENDENT_REVIEW` 行的逐轮枚举一致（末句写「当前待 `REV-CHARTER-12`」）
- `python scripts/validate_kit.py .` → `PASS (246 files checked)`、11 条子检查、`validate exit=0`、rc=0
- 按文档化抽取规则重放五条 AC：`AC1` / `AC3` / `AC4` / `AC2` / `AC5` 全 rc=0

## 行标签寻址的分水岭实验（本轮最有价值的一步）
在 `cp -a` 副本里给首页文件顶部插一行空行，然后同时用两种寻址读同一个事实：

| 寻址方式 | 控制组（未突变） | 突变组（插一行） | 结论 |
|---|---|---|---|
| 行标签「第 4 节的 `INDEPENDENT_REVIEW` 行」 | 解析到第 72 行，文本 sha `aa2f8e43…` | 解析到第 73 行，文本 sha `aa2f8e43…`（同一行、同一文本） | 绿 |
| 行号 `project.md:70` | `d258c24b…`（`SYNTHETIC` 行） | `ca7ab19d…`（`COMPONENT` 行） | 红 —— 指向了别的事实 |
| 行号 `project.md:72` | `aa2f8e43…`（`INDEPENDENT_REVIEW` 行） | `9fb1d1af…`（`INTEGRATED` 行） | 红 |

这条实验同时说明 `reuse-discovery.md` 里留存的 file:line 指针天然不可靠：它今天没错，是因为今天没有人往那个文件里插行。

## 处置（NF-19 … NF-22，全部已落盘）
| Finding | 严重度 | 处置 | 落点 |
|---|---|---|---|
| NF-19 `SR-01` 指针格错 + 命令不可复现 | P2 | `Exact query` 改为 `grep -rn 'Review A' portable/`（可复现）；`Evidence reference` 改为行标签寻址「以 `- Review A is executed by a reviewer` 起首的那一行」；表下加一条更正行，点名原值「`grep -rn Review-A portable/` 与 `charter-workflow.md:51`」并把它们连同理由留在句子里 | `.charter/reuse-discovery.md` 的 `SR-01` 行与其下的更正行 |
| NF-20 两处「子检查条数」副本 + 不成立的唯一落点断言 | P2 | 两处都改为「逐条子检查见证据文件 / 该文件的圆点行即权威清单，本行不计数」；删掉「本行即全套计量数的唯一落点」这句自称 | `.charter/handoff.md` 的 `Verified facts` 段与 `## Evidence` 表的 validate 行 |
| NF-21 两处「散文持有计量数、证据零落点」 | P2 | 测试规模改为指针，并把分解（298 总数 / 27 守卫 / 271 基线，均由 `pytest --collect-only -q` 分别计数）写进 pytest 证据文件；章程文件体积改为指针，并新建 `sizes-2026-10-19.txt` 承载该字节数（并写明 leaf 模板的数在 `template-budget` 里，不在此文件，避免第二个落点） | `.charter/project.md` 的 §3 末行与 §11 KEEP 表、`.charter/evidence/pytest-2026-10-19.txt`、`.charter/evidence/sizes-2026-10-19.txt` |
| NF-22 突变计数与 per-AC 分项是跨节复制 | P3 | 该格只留「检查原文、原样运行与对象侧突变表见该文件 `## Mutations` 段」，删掉 22 / 19 / 3 与五种分项 | `.charter/handoff.md` 的 `## Evidence` 表 ac-liveness 行 |

### 为什么 NF-19 改命令而不是只改指针
审阅者指出这条记录的 `MATCH` 用自身命令复现不出来。只把 `:51` 改成 `:50` 会留下一个仍然不可复现的命令；两个都改，才让第三方能按记录重放一遍并得到同样的结论。所以处置分两半：命令换成可复现形式，指针换成不依赖行号的寻址，并把原值写进更正行动作记录 —— 既不掩盖原值，也不让下一个人踩着同一个坑。

## 明确未验（审阅者自陈，转记于此）
- `docs/SELF-AUDIT.md` 正文的 94 处 file:line 指针（本轮裁定范围只到六件读集）
- `docs/SELF-AUDIT.md` 全文未逐行普查计量数归属（只抽查了若干处）
- F-01…F-25、NF-01…NF-14 的历史判词未复核（按派单约束跳过）
- `.charter/review.md`、`decision.md`、`evidence-receipt.md`、`changelog.md`、`records/*.md` 正文的计量数落点未核（不在读集六件内）
- ac-liveness 的突变表未在真仓逐条重做（只重放五条 AC 的原样运行）
- 未构造「同一行标签在同一文件出现两次」的对抗用例（实测四个标签 `candidates=1`，只证明当前唯一性）

## 这一轮的病灶（我的判断，待下一轮验证）
前十一轮的病灶是「投影停在一轮前」；第十二轮暴露出第二种：**修复只改被点名的那一处，不改产生它的形态**。审阅者在六件读集里只找到一处剩余 file:line 指针，而这一处恰好是最早写下、从未被任何一轮点过的那一处 —— 说明前十轮每次都是「把被指出的行号改成标签」，而不是「扫一遍还有没有行号」。下一步应当把「用机械 grep 全扫读集」写进复核动作，而不是靠审阅者顺手发现。

## Re-review trigger
`REV-CHARTER-13` 窄范围复核：NF-19 … NF-22 是否 `CLOSED`；NF-15 / NF-09 的残留是否清零（要求用机械 grep 全扫六件读集，不抽查）。拿到 `APPROVE` 之前，章程与叶都不得批准，本记录也不自我批准。