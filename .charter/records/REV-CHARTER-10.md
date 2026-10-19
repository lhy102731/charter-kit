# REV-CHARTER-10 — 复核 REV-CHARTER-09 的四条处置与判据落地情况

- Reviewer: fresh subagent `acdff5d7-26e6-425e-b30d-504b073211c1`，独立上下文，只读
- Independence declaration: 未参与任何一处编辑；临时脚本写在 `%TEMP%`，仓内 0 写入；开工与收尾 `git status --porcelain` 均为 79 行、HEAD 未变
- Scope: `REV-CHARTER-09` 的 NF-04…NF-07 四条处置 + 判据是否可检查／是否落地 + 机械核对；不重做 CHK 全表，不重验已 `CLOSED` 项
- Verdict: `REQUEST_CHANGES`

## 逐条判定

| 项 | 判定 | 依据 |
|---|---|---|
| NF-04（跨节汇总裁数 / 两套更正惯例） | **`PARTIAL`** | 点名的那一行（`docs/SELF-AUDIT.md:902`）已删；但同文件 `:880` 仍是跨节汇总的计数列表 —— 同一份文档里同一类缺陷两种处置。A/B 分界写清了，但没回答「记录正文里引用别轮计数算哪类」，也没被本轮执行 |
| NF-05（`:172` 逐轮聚合判词） | `CLOSED` | 该分句已删；`.charter/*.md`（排除 `records/`）里 `REQUEST_CHANGES` 字面只剩 `project.md:70`、模板 Verdict 枚举与 `changelog.md` 版本行，无第二处逐轮投影 |
| NF-06（`handoff.md:89` 只留方法断言） | `CLOSED`（带一处措辞缺陷） | 判词复述已删、状态指到 `:43`；句尾「本文件 `.charter/records/` 指针」在 `handoff.md` 内无对应行 → NF-14 |
| NF-07（四处过强声称收窄） | `CLOSED` | `REV-08` 记录两处 + `SELF-AUDIT` 两处都从「这一类已清零」收窄为「删掉的是轮数这一项」，并点名残余 |

## 判据判定的关键一句

> 判据**可检查**（审阅者按它自己扫就能机械扫出结果），但**没落地**：判据写下的同一轮，读集里仍有 4 类、合计 16 处以上它自己判为非法的现状断言。问题不是「又把这一次写对了」，而是**规则被写进了一个下一会话读不到、也没有任何检查指向的地方**。

## Findings 与处置

| ID | 严重度 | 文件:行号 | 问题 | 处置 |
|---|---|---|---|---|
| NF-08 | P2 | `SELF-AUDIT:937-945`；`lessons.md:19`；`handoff:46`/`:59`；`project.md:45`；`current-task:92` | 新判据与 A/B 分界只写进 `docs/SELF-AUDIT.md`，`.charter/` 里 0 命中；`project.md:45` 明写「写在读集之外的规则等于不存在」 | 规则本体写进 `project.md` 不变量（「会变的事实只有一个落点」，含 A/B 更正惯例与一条判例），`lessons.md` 立 `LS-001` 只记代价与防御指针、不复制规则正文（`CLOSED`） |
| NF-09 | P2 | `project.md:68`、`current-task:117`/`:141`、`handoff:23`/`:34`/`:40`/`:41`/`:55`/`:77`/`:78`、`reuse-discovery:61`、`SELF-AUDIT:880` | B 类（跨节复制的计量数一律就地删除）在它被写下的同一轮被违反：`246 files` 9 处、`298/519` 4 处、`18,349/18,432` 2 处、`十五条` 3 处；`:880` 仍留汇总列表 | 全部改成指针，数值唯一落点为 `.charter/evidence/`（新增 `pytest-2026-10-19.txt` 与 `template-budget-2026-10-19.txt`）；`:880` 的列表按 `:902` 的写法删除（`CLOSED`） |
| NF-10 | P2 | `handoff:23` | 把计量数写成不变量：「`validate_kit.py .` 必须 PASS (246 files)」 | 改成「必须 exit 0 且无 side-effect 警告」，数字指向证据文件（`CLOSED`） |
| NF-11 | P2 | `handoff:42`/`:43`/`:59`；`project.md:70` | 会变状态散在 4 处，除 `:70` 外都没声明为投影、没写重算子句 | `:42`/`:43` 改为指针 + 「本行随每一轮审阅回件重算」，删掉可由 `:70` 推导的聚合句；`:59` 只留动作（`CLOSED`） |
| NF-12 | P3 | `handoff:35`；`current-task:318-319` | 现在时写工作区计量，而下一步动作恰是提交 `.charter/`，一动就过期 | 改为基线指针 + 「当前差值以 `git status --porcelain` 为准」（`CLOSED`） |
| NF-13 | P3 | `records/REV-CHARTER-09.md:4`、`REV-CHARTER-06.md:19`、`SELF-AUDIT:922` | 零改动锚点口径未记、不可复现：记「354 文件 / `051a6a6d…`」，审阅者实测四种口径分别得 537 / 500 / 491 / 356，无一等于 354 | 写可复现配方进 `handoff` 的 Capability notes：`git ls-files -s | sha256sum` 与 `git status --porcelain | sha256sum` 成对记录；旧的两个哈希在本文与 `SELF-AUDIT` 里标注为不可复现（`CLOSED`） |
| NF-14 | P3 | `handoff:89` | 「见 `:43` 与本文件 `.charter/records/` 指针」——本文件内没有指向 `records/` 的行 | 改为「见 `:43` 与 `project.md:70` 的枚举（记录文件集合在 `.charter/records/`）」（`CLOSED`） |

## 这一轮为什么值得记

前九轮里，我一直在修**具体的那一处**；这一轮审阅者做的是另一件事：它拿我新立的那条判据，去扫我自己扫过的地方，然后指出**判据只兑现了它点名的那一处**。它还指出一个更根本的落点问题——判据写在 `docs/SELF-AUDIT.md`，它不在六件读集里，按章程自己的不变量「写在读集之外的规则等于不存在」，这条判据等于不存在。

所以本轮真正的处置不是「再改几处」，而是三件结构性的事：

1. **规则本体搬进读集**：`project.md` 不变量新增一条「会变的事实只有一个落点」，含计量数/状态两类落点、A/B 更正惯例，以及一条判例（某一轮自己那一次的校验行可留；跨节汇总别轮的数是复制，必须删）。
2. **代价记录进教训层**：`lessons.md` 立 `LS-001`，只记「连续五轮同族、每次落在不同位置」这个代价与防御指针，不复制规则正文——否则规则就有两个落点，正好违反它自己。
3. **计量数收进证据目录**：`.charter/evidence/` 新增 `pytest-2026-10-19.txt` 与 `template-budget-2026-10-19.txt`，读集里所有数字改成指针。

## 审阅者自跑的机械核对（未引用他人数字）

- HEAD `d6eff20240adbcce327ca7cffe27053a6df6bd02`；`git status --porcelain` 79 = 77 ` M` + 2 `??`；`git ls-files` 332；`git ls-files .charter` = 0
- `.charter/records/` 九份（01…09），与 `project.md:70` 的逐轮枚举逐项一致；findings 行数九轮逐项相符
- `validate_kit.py .` → `PASS (246 files checked)`，11 项子检查全绿，exit 0
- AC1–AC5 按「`- [ ]` 项边界 + 最后一个 backtick」抽取，cwd = 仓根，五条全 exit 0

## 明确未验

全量 `pytest`（只核了多处副本间的一致性，未验证数字本身）；突变实验；CHK 全表；已 `CLOSED` 项；`targets/` 与 `plugins/` 的 builder `--check`；`.charter/evidence/` 五个证据文件的内容真实性；`portable/templates/` 其余模板；D-01 / D-05 / D-06 的决策正确性。

## Re-review trigger

本轮不自我批准。需 `REV-CHARTER-11` 窄范围复核 NF-08…NF-14 七处处置，重点是两件：① 规则本体是否真的落在读集里且不与 `LS-001` 互相复制；② 照抄 `handoff` 的零改动锚点配方能否算出同一个哈希。不重做 CHK 全表，不重验已 `CLOSED` 项。
