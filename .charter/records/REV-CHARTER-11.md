# REV-CHARTER-11 — 复核 REV-CHARTER-10 的七条处置、AC 抽取规则，以及那一轮自己的副作用

- Reviewer: fresh subagent `f645e7c3-94f9-4180-96a1-77ec6a5df994`，独立上下文，只读
- Independence declaration: 未参与任何一处编辑；实验全部在 `%TEMP%/rev11` 的 `cp -a` 副本（含 `.git`）上做；真仓开工与收尾 `HEAD` 恒为 `d6eff20`、`git status --porcelain` 恒为 79 行、`git ls-files .charter` 恒为 0，两个零改动锚点与修复前的记录逐字节相同
- Scope: `REV-CHARTER-10` 的 NF-08…NF-14 七条 + 本轮 AC 抽取规则（假红）修复；不重做 CHK 全表，不重验已 `CLOSED` 项
- Verdict: `REQUEST_CHANGES`

## 逐项判定

| 项 | 判定 | 依据 |
|---|---|---|
| NF-08 规则没有读集落点 | `CLOSED` | 规则本体落在 `.charter/project.md:50` 不变量；`lessons.md` 的 `LS-001` 明写「规则本体在不变量里，本条只记代价，不重复规则正文」，无第二份规则正文 |
| NF-09 计量数副本 | **`PARTIAL`** | `docs/SELF-AUDIT.md:880` 的跨节汇总列表确已删；但同一计量数「79 行 = 77 `M` + 2 未跟踪」在读集散文仍有两份副本（`handoff.md:53` 的 Evidence 表括注、`current-task.md:50` 的字段值），而它已有的唯一落点是 `baseline-2026-10-19.txt:3` |
| NF-10 handoff 不变量含会变的数 | `CLOSED` | 现文只留「必须 exit 0 且无 side-effect 警告」，数字指向证据文件 |
| NF-11 三处判词副本 | `CLOSED` | `:42`/`:43`/`:89` 都只写指针 + 重算子句，不复述判词。指针**地址**本身失效另记 NF-15 |
| NF-12 现在时写工作区计数 | `CLOSED` | `:35` 与叶合同 Q1 均改为「以 `git status --porcelain` 为准」 |
| NF-13 零改动锚点可重放 | `CLOSED` | 照抄 `handoff` 的两行命令实跑，与证据记录逐字节一致：`git ls-files -s` → `d534ad515ce454d1…`（34241 字节）、`git status --porcelain` → `483cea696dfdb171…`（4816 字节）；执行器非 WSL 桩（`bash=/usr/bin/bash`、`BASH_VERSION=5.3.15(2)`） |
| NF-14 解析不了的指针 | `CLOSED` | 句子已自洽；其中 `project.md` 的指向错行另记 NF-15 |
| AC 抽取规则（假红） | `CLOSED` | 规则两处写清、第三人一次跑通；按规则 AC1–AC5 全 exit 0；**反向对照**：把规则改回「最后一个反引号」在同一副本上 → AC4 载荷 94 字节、exit 1，其余 0 —— 证明修复不是空转；`LS-002` 与 `LS-001` 不是同一病灶 |

## 新 findings（本轮修复自带的副作用）

| ID | 严重度 | 位置 | 问题 | 处置 |
|---|---|---|---|---|
| NF-15 | P1 | `handoff.md` 的 `:42`/`:43`/`:59`/`:89`；`project.md:30`/`:174` | 读集里 6 处「`project.md:70`」全部指向行号漂移后的另一行——`:70` 现在是 `SYNTHETIC` 格，唯一权威逐轮投影实际在 `:72`。成因是 NF-08 的修复本身：为写不变量在 `project.md` 插入两行，把 `:70` 推成 `:72`。按 `project.md:49`「不一致是阻塞发现」，这是阻塞项 | 6 处指针全部改成**行标签寻址**（「`project.md` 第 4 节的 `INDEPENDENT_REVIEW` 行」+ 明写「按行标签定位，不按行号——行号会随任何一次插行漂移」）；`LS-001` 命中 +1（行号本身就是会变的数） |
| NF-16 | P2 | `handoff.md:46` | Lessons 状态 `active 1 / 最新条目 LS-001（Hits 5）` 已过期：本轮新立了 `LS-002`，真实状态是 active 2、最新条目 `LS-002` | 改成「条数、最新条目与各条 Hits 一律以 `.charter/lessons.md` 的 Entries 段为准」，本行不计数、不复述条目名 |
| NF-17 | P2 | `handoff.md:53`、`current-task.md:50` | 基线计数「79 行 = 77 `M` + 2 未跟踪」在散文有两份副本，唯一落点是 `baseline-2026-10-19.txt:3` | 两处都改成「行数与分解见该文件首行注释，此处不复制」 |
| NF-18 | P3 | `evidence/ac-liveness-2026-10-19.txt` | 同一标题「Re-run after REV-CHARTER-10 dispositions」的小节出现两次、逐行相同，读者无法判断是复制还是两次独立运行的相同结果 | 合并为一份，并在原位置写明「本小节被追加过两次，两次运行独立、输出逐行相同；合并为一份，这一事实保留」 |

## 这一轮说明了什么

前三轮的模式是「投影停在一轮前」。这一轮是新的模式：**修复自己制造了下游缺陷**。我给章程插两行写不变量，就把整个读集里 6 处指向同一行的指针全部推歪；那些指针在写下的那一刻都是对的，坏掉是因为另一个文件发生了变化。

所以真正的处置不是把 `:70` 改成 `:72`——那只是把这一次写对，下一次插行还会再错一次。处置是把**寻址方式**换掉：按行标签定位，不按行号。这与 `LS-001` 是同一条：行号也是一个会随事件变化的数，复制到六处就必然漂。所以 `LS-001` 命中 +1，而不是新开一条。

顺带记下审阅者的一个可复用动作：它用**反向对照**证明修复非空转——把规则改回旧写法，同一份副本上 AC4 立刻变红；只有红没有绿不算跑过，只有绿没有红也不算。

## 审阅者自跑的机械核对

- `HEAD d6eff20240adbcce327ca7cffe27053a6df6bd02`；`git status --porcelain` 79；`git ls-files .charter` = 0
- `validate_kit.py .` → `PASS (246 files checked)`，11 项子检查全绿，exit 0
- 按文档化抽取规则重放 AC1–AC5：真仓五条全 exit 0；未突变副本五条全 0（控制组保持绿）；旧规则副本 AC4 exit 1
- `.charter/records/` 10 份，与 `project.md` 第 4 节 `INDEPENDENT_REVIEW` 行的逐轮枚举一致

## 明确未验

AC5 的副本突变；`ac-liveness` 22 行突变表逐行复核；全量 `pytest`；`roadmap.md` / `reuse-discovery.md` 的投影值；`records/` 里 24 处历史行号引用是否都要补更正行（按 A 类惯例「原行不改」，本行保持原样）；`project.md` 里两处历史计数（`271 条基线 + 27 条守卫`、`36,731 字节`）的规则层裁定；CLS7 校验器对 `handoff` Lessons 行的断言实现。

## Re-review trigger

本轮不自我批准。需 `REV-CHARTER-12` 窄范围复核 NF-09 的残留与 NF-15…NF-18 四条处置，重点两项：① 读集里是否已无现在时的行号指针，且行标签寻址是否真能经受「有人插一行」；② 计量数是否已只剩 `.charter/evidence/` 一处落点。不重做 CHK 全表，不重验已 `CLOSED` 项。
