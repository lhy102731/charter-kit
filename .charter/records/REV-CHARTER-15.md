# REV-CHARTER-15 — 章程级独立审阅（判准本身第三次成为被测对象）

> 本记录由实现方根据审阅者报告写成，不是审阅者亲自签署的文本。凡引用其原话处用「」标出；凡我方判读处写明「实现方读法」。

## Review identity

- 角色：`CHARTER_INDEPENDENT` 审阅（章程级），fresh 上下文，只读。
- 审阅者：subagent `b911224f-0420-4eb4-8b7d-a69f49c3ac1e`。
- 对象：`.charter/` 工作集（`project.md` 作为章程 0.2 草案、`roadmap.md`、`reuse-discovery.md`、`current-task.md` 作为叶 `R1.1-S1-L1`、`handoff.md`、`lessons.md`），以及写进 `project.md` 的那条不变量本身。
- 起始状态：`REV-CHARTER-14` 处置完成之后的状态。

## Independence declaration

- 它没有写仓库：514 文件 manifest sha256 `624a3367b53170faf85d428f549c87ffaf8bb2c2db241be1c48222e2b3b20cca` 开工与收尾一致，`git diff` 为空，`git status` 79 → 79，HEAD 未变。
- 全部实验在仓外 `../_rev15_workspace/{copy15,c345,initprobe}`。

## Verdict

`REQUEST_CHANGES`。

## Judgements on earlier items

| 项 | 判定 |
|---|---|
| `NF-23`（体积上限的第二落点） | `CLOSED` |
| `NF-24`（读集现在时持有可变数） | `NOT_CLOSED`，上调 P2 |
| `NF-09`（计量数副本） | 仍 `PARTIAL`（P1） |
| `NF-25`（不变量与投影格互斥） | 仍 `PARTIAL` |
| `NF-26`（判准的可判定性） | 仍 `PARTIAL`：判准能被第三方执行了，但执行出来不合格 |

本次记录只收录它明确给出判定的项。未出现在其报告里的旧项按「未复核」处理，不写成 `CLOSED`——把没查过的写成查过的，正是这条链上前几轮抓到的缺陷类型。

## Findings and dispositions

| finding | 它说的 | 处置 | 落在哪 |
|---|---|---|---|
| `NF-09` P1 | `handoff.md` 的 Subprocess 行以现在时写实测耗时与外层预算毫秒数、无 id 标记；`project.md` 的 D-01 行两次写 36 KB，而 `docs/SELF-AUDIT.md` 的 D-01 被要求改纯指针，同类不同处置 | D-01 改纯指针；Subprocess 行只留指针；另外把 `project.md` 的 R1.3 投影行与 `handoff.md` 的 D-01 待决行也改成「阈值是规则参数，定义位置在哪，换算值与实测字节在哪」——只写参数名不写定义位置的，仍然算复述，因为读者无法据它核对 | `project.md` §10 D-01 行、§3 树 R1.3 行；`handoff.md` Subprocess 行、D-01 待决行 |
| `NF-24` P2 | 读集仍三处现在时可变数 | 不追着被点名的短语打补丁：整格重写投影格、D-01 改纯指针、inventory 重写口径 | `project.md` §4 投影格、§10 D-01 行；`.charter/evidence/inventory-2026-10-19.txt` |
| `NF-25` P2 | 投影格里「四条 P2 与三条 P3」「三处」这类汇总量，与投影例外互斥 | 投影格整格改为逐轮枚举：每轮一句判词 + 一句该轮病灶，不出现任何汇总量、不出现聚合词 | `project.md` §4 投影格 |
| `NF-26` P2 | 判准过宽（72 候选多为「一个 / 一次」指称）、过窄（① 问类目漏实测耗时 / 退出码 / 比值 / 阈值换算出的字节数）、过强（与 `lessons.md` 的 `Hits` 冲突）、同类不同处置（`NF-28`） | 判准改 v3：① 问补入它点名漏掉的类目；③ 问的豁免只覆盖紧跟其 id 或时间戳的那一个观测；新增聚合词规则（合计 / 共 / 另有 / 其余 / 累计 / 加上 / 总计 一经出现即取消豁免）；新增多 id 规则（两个以上 id 同句只覆盖各自那一次的观测，跨轮相加的数不豁免）；E2 从「结构常量」扩为「结构常量与规则参数」，并加前置条件——同一行或同一格必须能指出定义位置，指不出的一律按 ① 处理 | `project.md` §2 不变量条 |
| `NF-29` P3 | inventory 的计数口径未定义（`init_project.py` 实测在 `.charter` 下产出 11 个文件，而 inventory 记 `.charter/*.md: 10`） | 重写 inventory，把 count basis 定义成「该行写的 glob，非递归，排除隐藏文件」，并写明它刻意不是「the working set」（那个说法没有定义），另加一行说明 `evidence/`、`records/` 与日志不匹配任何 glob | `.charter/evidence/inventory-2026-10-19.txt` |
| `NF-30` P2 | 派单行把已修项当现存缺陷转述；该行反引号 11 个（全文奇数），把 `## Do not do` 起的四个小节标题吞进 inline code | 派单行重写，只写本轮范围与指针；全部读集文件做反引号奇偶自检，现全为偶数 | `handoff.md` Exact next action 行；六个读集文件 |
| `NF-31` P2 | 豁免边界从行级漏洞换成子句级漏洞：C5b（同句带 id 让相邻的跨轮汇总量搭便车）、C5c（整句聚合），而真实语料 `project.md` 的投影格正是这形状 | 用聚合词规则与多 id 规则正面处理（见 `NF-26` 处置），并把投影格本身重写掉。**不声称这一类已关闭**：`REV-CHARTER-16` 被要求重跑 C5b / C5c | `project.md` §2 不变量条、§4 投影格 |
| `NF-32` P2 | 证据落点自身过期在门禁之外：E1 把 `ac-liveness` 的突变表加一行、E4 造出 `.charter/lessons-archive.md` 使 `.charter/*.md` 由 10 变 11，`validate` 与五条 AC 全绿 | 不静默保留：记成决定 `D-07`（`OPEN`），写明「校验落在套件自检还是 D-05 的下游校验器」这个问题本身待裁，并把 E1 / E4 两个探针写成实证 | `project.md` §10 D-07 行 |
| `NF-33` P3 | `ac-liveness` 里 REV-14 的小节出现两次（14:41:08Z / 14:41:44Z），上一轮同类重复明确合并过 | 合并为一份并加注：曾被两次独立运行追加、除时间戳外相同；把 `The 22-row table above` 改为 `The table above`（同一病灶：散文里复述表行数） | `.charter/evidence/ac-liveness-2026-10-19.txt` |

## What this round changed structurally

判准第三次成为被测对象。三轮下来浮出三条模式：

1. **豁免的范围只能和它计量的单位一样窄**。先是行级（一行有 id 就整行放过），改成子句级后仍然可以搭便车。两轮的真实教训不是「再收窄一格」，而是：聚合词本身就是豁免不应覆盖的信号——把它们列成清单，比继续讨论「子句到哪里结束」更能判。
2. **只写参数名、不写定义位置的指针，仍然是复述**。D-01 行里 36 KB 出现过两次却无法被读者核对，因为「36 KB」在散文里既像参数又像结论。改成「阈值是规则参数 + 定义在哪个文件哪一处 + 换算值在哪个证据文件」之后，同一句话既能被判准检查，也能被第三人复算。
3. **门禁的盲区只能被记成决定，不能被宣布修好**。证据文件自己过期、glob 型计数变化，都不会让 `validate` 变红；本轮能做的是把它写成 `D-07` 并附实证，而不是再写一句「已修复」。

## Mechanical checks it ran (its numbers)

- `scan_invariant.py`（它把 `project.md` 的不变量逐字实现成扫描器，用法 `python scan_invariant.py <repo> <out.json>`，stderr 打 `TOTAL=69 LIVE_paren=41 LIVE_flat=47`）。
- 六份读集 LIVE 命中按文件：project.md 18 / current-task.md 7 / lessons.md 5 / reuse-discovery.md 4 / handoff.md 4 / roadmap.md 3；它判为真违规 13、E2 豁免 17、误报 11。
- `leaf-task.md` 18,349 字节；模板断言 36698 ≤ 36864；余量 83。
- `validate_kit.py .` exit 0、`PASS (246 files checked)`。
- AC1–AC5 原样全 exit 0，每块 `check: ` 恰一次。
- 四计数 10 / 5 / 7 / 10 与 inventory 一致。

## Not verified by it

- 全量 pytest。
- `CHK1`–`CHK13` 全表勾选。
- `DEVELOPMENT_CHARTER.md` 与 targets / plugins 镜像。
- `REV-CHARTER-01` … `REV-CHARTER-14` 的 findings 实质重验。
- 它建议的两条 `validate_kit` 自洽断言是否真能写出来。

## Re-review trigger

派 `REV-CHARTER-16`，窄范围：

1. 读集里的现状断言是否已按三问 + 两条豁免 + 投影例外处置，重点是实测耗时与体积阈值的散文副本；
2. 上一轮揭出的两处门禁盲区是否被记成 `OPEN` 决定（`D-07`）而不是被静默保留；
3. `NF-09` 能否转 `CLOSED`；
4. 反引号配对缺陷是否已修、六个读集文件的代码跨度是否成对。

它仍须把判准当被测对象，重跑 `E1` / `E4` / `C5b` / `C5c` 四个探针。

本记录不自我批准。在拿到 `APPROVE` 之前，章程 `Status` 不得改为 `APPROVED`，叶 `R1.1-S1-L1` 不得离开 `DRAFT`。
