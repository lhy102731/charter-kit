# Charter Change Log

| Version | Date | Change | Reason | Approved by |
|---|---|---|---|---|
| 0.1 | 2026-10-19 | 初始章程：目标、非目标、六条不变量、效果边界、`MANUAL` 授权、D-01 至 D-05 五个待决 | 套件首次纳入自己的治理，把已发生的工程事实与既有规则写成可复核记录 | `UNDECIDED` — 待批准（`project.md` 第 11 节批准后回填） |
| 0.2 | 2026-10-19 | `REV-CHARTER-01` 十五条 findings 的处置落地：门禁退回 `PENDING`、补 freshness 投影与断言、叶补负向验收与基线清单、新增 `D-06` | 审阅判 `REQUEST_CHANGES`，修复改变了章程正文与叶合同，故按版本记录，不修改 0.1 行 | `UNDECIDED` — 待批准（`project.md` 第 11 节批准后回填） |
| 0.3 | 2026-10-20 | 0.2 获批（正文未改）：第 11 节批准记录填实；`D-09` 转 `DECIDED`（接受带限度的封存，到期 2027-01-20）；`D-10` 仍 `OPEN`；第一个叶 `R1.1-S1-L1` 获批 | 0.2 行的 `Approved by` 记的是 `UNDECIDED - 待批准`；批准动作本身需要一个版本行，否则下一次会话分不清「已批准」与「没人批准」 | `YG` |

## Rules

- One row per version, one version per approval. A row with no approval reference
  records a change nobody authorized.
- New rows append at the bottom. A row is never edited after the version it records
  has been used by a session; a correction is a new row naming the row it corrects.
  The number identifies a charter approval, not a document revision.
- `Change` says what moved; `Reason` says why it had to. A row that says only
  "updated" is a row the next session will re-litigate.
- A row that supersedes a decision records that decision's id, so the change and
  the decision can be read together.

## When a row is required

The list that decides whether a row exists also lives in `project.md` section 12, which
is read on resume and this file is not. A row is required by these changes, and nothing
else:

- any narrowing of `RVB1`-`RVB5` or of another risk trigger, because the next session
  reads the narrow trigger as the whole rule;
- any new mandatory contract field or checklist item, because an archived leaf that
  lacks it can no longer be read as compliant;
- any charter-level migration recorded in `references/contract-migrations.md`;
- any change to `Invariants` or to the effect boundary, because both decide what a
  later session may do without asking.

`Reason` names what the row excludes or replaces. A row whose `Reason` only says the
change was needed cannot be told apart from a row nobody reasoned about.
`Approved by` is never blank: a change made before approval is recorded as
`UNDECIDED - <why the change could not wait for approval>`, which a later session can
read and act on, where a blank cell is a state it has to guess.

## Growth

This is the one file in `.charter/` expected to grow without bound: it grows by
history, not by live state, which is why nothing reads it by default. When it
becomes hard to scan, split it by charter major version into `changelog-v<N>.md`
files with one index row per file. The split is a move, never a deletion, and the
row order is preserved.

## Migration from section 12

A charter whose history still sits in its own section 12 moves the table here
unchanged: same rows, same order, same version numbers. Then that section becomes
the pointer sentence. Nothing is renumbered - a version number is what an
archived approval cites.
