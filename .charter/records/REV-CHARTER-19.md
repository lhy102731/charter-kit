# REV-CHARTER-19 — 章程级独立审阅（第 19 环）

## Review identity

- Reviewer: fresh read-only subagent `9909fc3a-0eb4-412a-bf02-754084c5dad8`, cwd = 仓库根，实验在仓外副本 `outputs/charter-kit/_rev19_workspace/copy` 内做，REPO 未改任何文件。
- Scope: 只核 `REV-CHARTER-18` 的九条处置（NF-46…NF-54）与它新增的两个门（`AC6`、`CHK14`）。不重做 `CHK1`–`CHK13` 全表，不重验已 CLOSED 的历史项。
- Verdict: `REQUEST_CHANGES`。

## Independence declaration

审阅者自证：开工与收尾同一对锚点 `git status --porcelain | sha256sum` = `483cea696dfdb171c3af1bdaf8fa814c6a429589213e17d9cb40005fb9584d12`、`git ls-files -s | sha256sum` = `d534ad515ce454d12816adea750f920be2ae076b80f5e4568585af7488b2e4cc`；`diff -r --brief -x .git REPO COPY` 零差异；`HEAD` = `d6eff20…`。执行器为 msys bash 5.3.15（`/usr/bin/bash`），未用 WSL 桩。

> 独立性由它自己补充了一句更硬的证据：它用 `NF-57` 的实验证明上面这对锚点对 `.charter/` 全盲 —— 删掉记录里十行之后两个哈希一字未变。也就是说本轮之前，所谓「独立性声明」在结构上不可证。这条观察促成了本轮 `NF-57` 的修法（锚点改三段）。

## Verdict justification

两个新门的判定不同：`AC6` 是**真门**（它亲手做了五个突变：加一格 / 删一格 / 子串陷阱都只红这一条，只改单元格文字的控制组保绿），`CHK14` 只能算**半真门**（四处文本同义，但第二子句的判据输入与实际投影集合不符、第三子句没有任何一步要求谁交出答案）。九条处置里 NF-46 / NF-48 / NF-50 / NF-51 / NF-52 确已落地，NF-47 部分落地，NF-53 未闭。

## Checks performed

- [x] `CHK1` 叶合同的结果句、允许路径、验收项与停止条件互不矛盾 — PASS（读了 `.charter/current-task.md` 的 §2/§4/§5/§6）
- [x] `CHK2` 每个验收项都能移动退出码 — PASS（七条全是 `python -c` 或 `validate_kit.py`，载荷可执行）
- [x] `CHK3` 证据指针指向真实存在的文件 — PASS（`evidence/` 六个文件全部存在）
- [x] `CHK4` 状态机转移都有授权前提 — PASS（章程 `MANUAL` 模式，叶仍 DRAFT）
- [x] `CHK5` 负向验收存在 — PASS（`AC2` / `AC5` 在 `Negative behavior / boundaries` 下）
- [x] `CHK6` 编号只增不改 — PASS（`AC1`–`AC7` 连续，`AC7` 为本轮新增，无重编号）
- [x] `CHK7` 迁移文档与模板版本一致 — PASS（`contract-migrations.md` 的 CHK14 行与本次改写同轮落地）
- [x] `CHK8` 读集成员都在工作集内 — PASS（读集 ⊆ 工作集，有守卫用例覆盖）
- [x] `CHK9` 三处投影同步 — PASS（`AC3` 已扩为逐点断言，见下方活性表 M1）
- [x] `CHK10` 处置行都写明「如何在产物里验证」 — PASS（本表每行带命令与期望输出）
- [x] `CHK11` 集成与合并后验证 — N/A（本叶不产生提交）
- [x] `CHK12` 默认值可见性 — N/A（本叶未改任何默认值）
- [x] `CHK13` findings 全部处置且非 CLOSED 者进章程 §10 — PASS（NF-55…NF-58 全部 CLOSED，D-07 / D-08 已记在章程第 10 节）
- [x] `CHK14` 计量数指唯一落点、会变状态只在声明投影、例外逐项列名 — PASS（item: 本记录里的 `AC` 载荷长度与哈希；clause: 章程第 2 节「会变的事实只有一个落点」的 A 类判例，某一轮自己的校验行可留、跨节汇总别轮的数必须删；basis: 它们是本轮自己的观测，不是别轮计量的副本）

## Findings and dispositions

| id | 严重度 | 问题 | 处置（全部已落盘） | 如何在产物里验证 |
|---|---|---|---|---|
| `NF-55` | P2 | 声明投影 ≠ 实际副本：第 1 节 gate 行、第 6.1 节 RD 行、`handoff.md` 的 RD 与候选版本都不在声明清单内，而 `AC3` 只取首个匹配 → 只改第 6.1 节 gate 时六条 AC 全绿 | ① `AC3` 重写为逐点断言：四个 gate 点（第 1 节 / 第 6.1 节 / `roadmap.md` / `reuse-discovery.md`）、三处 freshness、三处 RD，每个标签按行标签**恰好命中一次**，值必须同一，gate 还必须在枚举内；② 章程第 2 节的投影清单改为逐点名单，把第 1 节 gate 行、第 6.1 节三行、`roadmap.md` 三行、`reuse-discovery.md` 三字段全部点名；③ `handoff.md` 的 RD 与候选版本改指针，不再持有取值；④ 第 4 节 `INDEPENDENT_REVIEW` 行改为只点名 `CHK14`，不再转述子句（上一版漏掉第二子句，漏掉的正是会被证伪的那条） | `python -c "…"` 打开七个点逐点取值（见 `AC3` 载荷）→ 基线 rc=0 且打印 `PENDING` 四次；只把第 6.1 节 gate 改成 `COMPLETE` → rc=1。实测见下方活性表 M1 |
| `NF-56` | P2 | 两套互斥的格数口径：`AC6` 数裸竖线，而 `REV-CHARTER-17` 处置表按 GFM 转义写，同一行量出 5–6 格；反向也成立 —— 合法转义 `Y\|G` 让 `AC6` 假红 | ① `AC6` 改为转义感知切分（逐字符扫描，`chr(92)` 后的竖线不算分隔符）；② `REV-CHARTER-17` 处置表两条命令改成不含竖线的 `python -c` 写法（用 `chr(124)` 数行），期望输出写在同格；③ 章程第 2 节的处置纪律加一条：命令里不许出现裸竖线 —— 表格单元格里的合法转义会让 raw 源形态与渲染形态指向不同断言 | `documented command` → 输出 `1` 与 `1` + `OPEN`；活性见下方 M2（合法转义保绿）与 M3（真多一格变红） |
| `NF-57` | P2 | 只读锚点对读集全盲：`.charter/` 未跟踪，`git ls-files .charter | wc -l` = 0、`git status --porcelain` 只有一行 `?? .charter/`，删掉记录里十行后成对哈希一字未变；而 `handoff.md` 恰好禁止用能覆盖它的自建遍历 | 锚点改**三段**写在同一条：① `git ls-files -s | sha256sum`；② `git status --porcelain | sha256sum`；③ `cd .charter && find . -type f -name '*.md' -print0 | sort -z | xargs -0 sha256sum | sha256sum`（相对路径排序 + 逐文件内容哈希，不带会漂移的文件数），并写明 ①② 对未跟踪文件全盲、所以 ③ 不是可选项 | 删改任意一份记录 → ③ 变、①② 不变；实测见下方 M5 与证据文件 `ac-liveness-2026-10-19.txt` 的锚点段 |
| `NF-58` | P3 | `CHK14` 第三子句没有任何一步要求谁交出答案：叶合同 `例外` 命中 0，18 份记录只有 4 份带 `## Checks performed`，造出 CHK14 的那一轮自己也没有；删掉一份记录的整段后 validate 与六条 AC 全绿 | ① `portable/templates/review.md` 把 `## Checks performed` 写成**必填段**：缺段则记录标 `INVALID`，不得省略；② `CHK14` 重写为三子句，第三子句的输入改写为「本审阅主张的每个例外写成 `item / clause / basis` 一行，无例外写 `Exceptions claimed: none`」——输入的生产者变成审阅记录自己；③ 新增 `AC7`：从本记录起的每份记录必须含该段，且段内至少引用一次 `CHK14` | `python -c` 扫 `records/REV-CHARTER-*.md`，对序号 ≥19 的记录判「段存在 且 段内 CHK14 ≥1」→ 基线 rc=0；删掉本记录该段 → rc=1（见下方 M4） |
| `NF-47` | 残留 | 第 4 节只复述了第 1、3 子句 | 已并入 `NF-55` 的第 ④ 项：只点名不转述 | `grep -c 'CHK14' .charter/project.md` → 2（不变量末句 + 第 4 节行），且两处都不再列举子句 |
| `NF-53` | 残留 | 转义改了 raw 命令的断言（同一命令两个含义） | 已并入 `NF-56` 的第 ② ③ 项 | 见 `NF-56` 行 |

## Liveness evidence

七条验收项按 `handoff.md` 的抽取规则取出、走 stdin 执行；每条突变后立即按字节还原，还原后 `sha256` 与基线相同。

| 场景 | 期望 | 实测 |
|---|---|---|
| baseline | 全 0 | `AC1`=0 `AC3`=0 `AC4`=0 `AC6`=0 `AC7`=0 `AC2`=0 `AC5`=0 |
| M1 只把第 6.1 节 gate 改成 `COMPLETE`（第 1 节与 roadmap 不动） | 只有 `AC3` 红 | `AC3`=1，其余 0 |
| M2 把 `D-03` 的 Owner 写成合法转义 `Y\|G`（渲染仍 5 格） | 全 0（假红已修） | 全 0 |
| M3 给 `D-01` 多加一格 | 只有 `AC6` 红 | `AC6`=1，其余 0 |
| M4 删掉本记录的 `## Checks performed` 整段 | 只有 `AC7` 红 | `AC7`=1，其余 0 |
| M5 删掉本记录十行后重算三段锚点 | ③ 变、①② 不变 | 见 `ac-liveness-2026-10-19.txt` 的 REV-19 段 |

## Not verified

- 未对 freshness 做突变实验（只做了 gate 与 RD）。
- 未验证 `AC2` 对其它 `git status` 形态（v2、忽略规则、`core.fileMode`）是否仍然可靠。
- 未核 `evidence/` 其余文件（baseline / inventory / template-budget / validate / pytest / reuse-probe）的数值与真实产物是否一致。
- 未审 `docs/SELF-AUDIT.md` 第 9.9 节的套件级 BLOCK 主张，也未审 `handoff.md` 的其余段。
- 未逐条勾 `CHK1`–`CHK13`，未复核已 CLOSED 的历史项。

## Re-review trigger

本记录不自我批准。需 `REV-CHARTER-20` 窄范围复核：`NF-55` 的逐点断言与投影清单是否真的同步（而不是又只改被点名的那一处）、`NF-56` 的转义感知计数是否在七条 AC 之外也不留第二套口径、`NF-57` 的三段锚点是否可被第三人逐字重放、`NF-58` 的 `AC7` 是否真的会因为删段变红。
