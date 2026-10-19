# REV-CHARTER-17 — 章程级独立审阅（章程 0.2 / 叶 R1.1-S1-L1）

> 审阅记录，不是批准。审阅者与执行者不是同一个 agent；本文件由执行者按审阅者报告整理，事实以审阅者给出的实测为准。

## Review identity

- Reviewer: fresh subagent `e3f0c3a5-7a1b-432b-825a-fa5e6f8c911a`（全新上下文，只读）
- Mode: `CHARTER_INDEPENDENT`（章程级），窄范围复验
- Target: `HEAD d6eff20240adbcce327ca7cffe27053a6df6bd02` + 未跟踪的 `.charter/`；工作树 `git status --porcelain` 79 行（77 ` M` + 2 `??`）
- Date: 2026-10-19（记录标签）

## Independence declaration

- 实验全在仓外 `outputs/charter-kit/_rev17/`：`scan_v4.py`（判准实现）、`run_ac.py`、`inject_e1.py`、`chk1..chk10.py`，副本 `copyA` / `copyB` / `copyC`。
- 未改仓库任何文件：开工 `baseline_all_files.sha256` 与收尾 `after_all_files.sha256` **diff 0 行**；`.charter/*.md` 前后均 10 份；`lessons-archive.md` 在仓库中不存在。
- 执行器自检：用绝对路径的 `bash.EXE` 跑 `echo hi` → `hi` / rc=0；全程未用裸 `bash`。

## Checks performed

| 项 | 结果 |
|---|---|
| `validate_kit.py .` | exit 0；`PASS (246 files checked)` |
| 五条验收项（字节同一副本） | AC1–AC5 全 0 |
| `ac-liveness` 的 REV-14 段 | **CLOSED** —— 标题 1 个、一张 5 行表、一对 anchor、一条合并注；全文 8 次 `| AC1 | 0 |` 分属 8 个不同轮次小节 |
| 第 4 节表格结构 | **CLOSED** —— 每行 pipes=5 / cells=4，`INDEPENDENT_REVIEW` 行以 `|` 起头，表未被切，轴名齐全 |
| 两个门禁探针（E1 / E4） | 仍全绿 —— 缺陷未变，见 `D-07` |

## Findings

| id | 严重度 | 位置 | 问题 |
|---|---|---|---|
| `NF-40` | P2 | `project.md` 的 pain 行、`lessons.md` 的 `LS-001` 与 `LS-002` | 计量副本以**中文数词**形态留在读集：`两条 blocker`、`六条同族 finding`、`连续五轮`、`三类成因`；且 `六条` 与同条 `Evidence` 行枚举的 8 个 id **已经不一致** —— 不是理论风险，是已发生的量测失真 |
| `NF-41` | P2 | `project.md` 不变量 ③ 的 ① 与 E2；`current-task.md` 的 AC5 | ① 无判定谓词（裸实现跑出 34 行候选，多数假阳：节号、SHA 片段、版本号、代码字面量）；E2 要求同格指出定义位置，读集至少四处集合计数没有同格指针；AC5 内嵌整条 HEAD SHA 无归类 |
| `NF-42` | P2 | 判准 v4 的三处硬边界本体 | 自判失败：跨行聚合、同窗口多数字、双 id 单加总、ASCII 计数名词、量词分离、括号内数字搭便车全漏；`公共` 的「共」与括号内聚合词造成两处假阳；同一段条文在「id 在前」与「距离 ≤24 对称」两种忠实读法下 **判定相反** |
| `NF-43` | P2 | `ac-liveness` 的 `## Mutations` 表与 `D-07` 行 | 证据文件可以**自证**：手写一行从未执行的记录，`validate` 与五条 AC 全绿；造 `lessons-archive.md` 使 `.charter/*.md` 变化同样全绿 |
| `NF-44` | P3 | 各轮 anchor 段 | 锚点体例夹带「文件数」这类会漂移的计数（上一轮记 547，本轮实测 548，差 1 未归因，缓存目录随运行增删） |
| `NF-45` | P3 | 处置表体例 | 处置行以「已落地」表述对产物负责，而本轮两处「落地」实为换形状；处置表因此失去「可被产物否决」的性质 |

判定表：`NF-09` / `NF-24` / `NF-26` / `NF-31` 均 `PARTIAL`；`ac-liveness` 单份正文与第 4 节表格行两项 `CLOSED`。

## Verdict

`REQUEST_CHANGES`。审阅者明确的一句：**这条判准现在不能判自己** —— 三个给定形状确已修好（C5b 2/2、C5c 1/1、C5e 2/2，v3 为 1/2、1/1、0/2），但八个自造形状里五漏两假阳。

## Dispositions（本轮执行者的处置；每行都给出「如何在产物里验证」，这是本轮新立的处置纪律）

| id | 处置 | 如何在产物里验证 |
|---|---|---|
| `NF-40` | 四处中文数词计数逐处清掉：`两条 blocker` → 「当时的 blocker 全是」；`六条同族 finding` → 「同族 finding」；`连续五轮` → 「连续多轮」；`三类成因` → 「成因包括」 | `grep -n '两条 blocker\|六条同族\|连续五轮\|三类成因' .charter/*.md` → 0 命中；`grep -c '当时的 blocker 全是' .charter/project.md` → 1（实测均符合） |
| `NF-41` / `NF-42` | **撤回机械判据**：不变量 ③ 的 ① / E1 / E2 / ③ 判定程序整段删除，改为一句「这条不变量由 Review A 判，不由扫描器判」+ 三轮失败形状 + 记成 `D-08` | `grep -c '判定程序' .charter/project.md` → 0；`grep -c '由 Review A 判' .charter/project.md` → 2（不变量正文与处置纪律各一处） |
| `NF-43` | `D-07` 保持 `OPEN`，行内补记「`REV-CHARTER-17` 重放 E1 / E4 两个探针，仍全绿，缺陷未变」，并写明与 `D-05` 一起裁 | `python -c "import io;BAR=chr(124);print(sum(1 for l in io.open('.charter/project.md',encoding='utf-8') if l.startswith(BAR+' D-07 ')))"` → 1，且行内出现 `REV-CHARTER-17` 与 `OPEN` |
| `NF-44` | `ac-liveness` 结尾新增 `## Anchor convention`：锚点只记成对 sha256 与字节数，**不记文件数**，并写明原因（缓存目录随运行增删，写进锚点会与别轮不符） | `grep -c 'Anchor convention' .charter/evidence/ac-liveness-2026-10-19.txt` → 1；`grep -c '不记文件数'` → 1 |
| `NF-45` | 处置纪律写进读集：不变量末句「任何处置行必须写明『如何在产物里验证』（命令 + 期望输出）；写不出的当场改判 `NOT_CLOSED`，不得用『已落地』结案」；本表即按此体例执行 | `grep -c '如何在产物里验证' .charter/project.md` → 1 |
| （新增） | `D-08`：读集数值副本没有机检，判据机械化三轮全被绕过，已撤回扫描器路线；与 `D-05` / `D-07` 的分工写明「承认人工门」或「交给下游校验器」 | `python -c "import io;BAR=chr(124);r=[l for l in io.open('.charter/project.md',encoding='utf-8') if l.startswith(BAR+' D-08 ')];print(len(r),[c.strip() for c in r[0].split(BAR)][5])"` → 1 与 OPEN |
| （新增） | `LS-003`：把治理规则写成散文判据并期待机检 —— 三轮失败形状与唯一出路（闭集可机检；会变的量只能靠「一处存放 + 人判」或真校验器） | `grep -c 'LS-003' .charter/lessons.md` → 1 |


> 本表两处命令在 `REV-CHARTER-18` 轮被转义成 `\|`，当时的判断是「只改渲染、不改断言内容」——这个判断是错的：raw 源形态下 `grep -c '^\| D-07 \|'` 实测 287 行、渲染形态 1 行，同一条命令成了两个断言。`REV-CHARTER-19` 的 `NF-56` 把它改成不含竖线的 `python -c` 写法（用 `chr(124)` 数行），期望输出写在同格；原判词按 A 类惯例保留不改，此行是更正。

## 为什么撤回判据，而不是出 v5

审阅者的建议是继续补：给中文数字补一条明文、给 ① 补白名单、把 (c) 扩到 ±1 行窗口、把 (b) 改成括号内片段单独成句。按字面执行会得到 v5，而这条链已经证明：**每一版都只在被点名的那几个句子成立，换个形状即绕过，而写判据的人与被测对象是同一个人，绕过的形状他想不到**。三轮的失败形状互不相同（行级豁免、子句级豁免、三处硬边界），这不是参数没调对，是这类量根本不适合纯语法判据：

- 中文数词兼作冠词（「一个」「一次」「一种」），使其无法用词法判定；
- 「同一事实」是语义概念，聚合、跨行、括号都是它的变形，不是它的枚举；
- 同一段条文在两种忠实实现下能给出相反结论 —— 判准的实际判决力来自实现者的分类器。

所以处置改成：**能机检的只有闭集**（枚举、编号、状态词、文件集合 —— 这些已经有 `AC1` / `AC3` / `CLOSED` 的断言在守）；**会变的量只剩两条路**：只存在一个地方且读集只写指针（由 Review A 判），或建真校验器（`D-05`）。撤回不是把问题藏起来：三轮的失败形状写进了 `LS-003`，缺口本身记成 `D-08` 的 `OPEN` 决定，`D-07` 仍开着。

这条处置的代价也要写明：读集里的中文数词计数从今天起**没有机器拦**，只能靠每轮 Review A 手工扫；如果下一轮审阅者仍能扫出活的副本，那是 `D-08` 的实证，不是新缺陷类型。

## 未验清单（审阅者声明，节选）

- 全量 `pytest` 未跑；`246 files checked` 的构成未核；547 / 548 的差 1 未归因。
- `D-02`…`D-06` 各行现状未逐行核；`roadmap.md`、`reuse-discovery.md` 只用扫描器跑过，未通读。
- `records/REV-CHARTER-01..14` 的判词与第 4 节格内枚举未逐轮对齐（只核 15 / 16）。
- `evidence/` 其余 8 份未与读集指针逐条对表；五条 AC 未在 REPO 原位跑（惯例是副本，副本与 REPO 清单 diff 0）。
- (b) 的切分只覆盖 `。；？！，—`，未测 `、` 与半角 / 全角混排。

## Re-review trigger

需 `REV-CHARTER-18`（窄范围：判「撤回判据」这个处置是收敛还是逃避；自己扫读集里的计量数副本并判是否已在 `D-08` 如实披露；核 `D-08` 的 `OPEN` 与三份决定的分工；核处置纪律是否落地；核上一轮两项 `CLOSED` 是否仍成立）。本记录不自我批准；未拿到 `APPROVE` 之前，章程与叶都停在 `DRAFT`。

（记录按 A 类惯例：原判词不改，后续更正另起一行并指名被更正行。本轮由执行者按审阅者报告整理。）
