# Agent Handoff Packet

Use this file as the resume packet for another actor. It records the current task state, evidence, and exact next action; it is not a second state machine or a transcript.

**Bounded size.** This file is in the required-start read set, so every actor pays for it on every resume and it must not grow with the project. Keep the active leaf and at most the one most recently closed leaf. When a third per-leaf block would appear, append the oldest block to `.charter/handoff-archive.md` — append-only, outside the required-start read set — and leave one line naming it. Roll cumulative facts up into a single current line (one baseline count, not one line per closed leaf), and reference evidence by path under `.charter/evidence/` instead of restating it here. An unbounded handoff packet is a defect, not a history.

**Promotion before archiving.** A per-leaf block is rarely pure history. Before archiving it, promote anything that still binds future work: a convention that later leaves inherit goes into `project.md` Invariants (or the `Do not do` section below); an unresolved negative result keeps its own line in `Do not do` until it is dispositioned; a cross-leaf progress fact is rolled into the Current facts line. Archiving by leaf ID without this promotion sweep is the same defect as deleting acceptance checks to save size — it silently removes a binding rule from every later reader. Archive entries carry one line plus a pointer (`<leaf> : see roadmap row / evidence path`), never more prose than the roadmap row they mirror.

## Snapshot

- Protocol / kit version: `charter/v1 / 0.6.0`
- Project: `Charter Kit`
- Goal reference: `.charter/project.md` 第 2 节
- Task ID: `R1.1-S1-L1`
- Current state: `DRAFT`
- Snapshot time: `2026-10-19T13:10:00Z`
- Handoff producer: `lead / DeepSeek Harness + charter-workflow Skill`

## Goal and boundary

- Approved result: 已批准（2026-10-20）——让 `.charter/` 成为套件自身的治理事实源；第一个叶只做「用模板填出可读工作集」这一件可观察的事
- Non-goals relevant to this task: 不改 `portable/`、`targets/`、`scripts/`、`tests/`；不发布、不 push、不动版本号
- Invariants that must remain true: 镜像字节一致；编号只增不改；一条规则只有一个落点；`validate_kit.py .` 必须 exit 0 且无 side-effect 警告（数字落点 `.charter/evidence/validate-2026-10-19.txt`，此处不写数）
- Allowed effects: `read_only`、`sample_run`、`code_write`（限 `.charter/` 与 `docs/SELF-AUDIT.md`）；`local_merge` 未授权、不勾选。以叶 `.charter/current-task.md` 第 4 节与第 7 节为准；章程第 5 节（Scope and effects）定义更宽的效果边界，章程第 9 节只给 `MANUAL` 任务授权（本版为空），两者都不能放宽本叶。
- Forbidden effects: `push`、打 tag、发布、写全局目录、把源码或密钥外发

### Change Triage

- Record the event kind and route from the bundled Change Triage reference whenever a new requirement or constraint appears: `portable/references/change-triage.md` in the full kit or `references/change-triage.md` in the self-contained Skill.
- New requirement must not silently expand the current Leaf.

## Current facts

- Last accepted event: 2026-10-19 `d6eff20` 提交完成（自检通过，计数见证据文件）；其后各轮审阅的 findings 修复已完成但未提交

- 2026-10-19：用户裁决「把 P1-3 回滚回去」并已执行——`DEVELOPMENT_CHARTER.md` §7 的读集增长规则、`portable/templates/roadmap.md` 的 `Growth` 引线、`project-charter.md` §10 末尾的指路句，以及两个实例副本的同名内容全部删除；`contract-migrations.md` 的 `### Renamed members` 保留（它服务 `P1-2` 的 `APPROVED → DECIDED`）。叶 §4 增三份手工源、§6 记 Ruling，`AC2` 基线第二次重算；详见 `docs/SELF-AUDIT.md` 第 9.11 节
- Baseline revision/workspace: `main` @ `d6eff20`，工作区差值以 `git status --porcelain` 为准；基线清单见 `.charter/evidence/baseline-2026-10-19.txt`（本行不写现在时的计数）
- Current candidate revision: 未提交（工作区）
- Predecessor receipts: 无（本叶是第一个叶）
- Reuse discovery ID / gate status / selected revisions: 一律读唯一的投影处（RD 与 freshness 见 `project.md` 第 6.1 节的三行，候选与版本见 `reuse-discovery.md` 的候选表）——本行不持有任何取值（`REV-CHARTER-19` 的 NF-55）
- Verified facts (current rollup; superseded per-leaf detail belongs in `.charter/handoff-archive.md`):
  - `validate_kit.py .`：输出与退出码都只落在 `.charter/evidence/validate-2026-10-19.txt`（逐条子检查同理，本行不复述任何取值）
  - `pytest -q`：结果与条数只落在 `.charter/evidence/pytest-2026-10-19.txt`（本行不复述任何取值）
- Open findings: 逐轮 findings 与处置见 `.charter/records/REV-CHARTER-*.md`，汇总投影见 `project.md` 第 4 节的 `INDEPENDENT_REVIEW` 行（按行标签定位，不按行号）。当前未闭合：无——`D-09` 已按 YG 裁决转 `DECIDED`（带限度），`D-10` 仍 `OPEN` 属已知缺口（见 `project.md` 第 10 节）。本行随每轮审阅或每次决策结算重算
- Review status: 章程级审阅链逐轮判词见 `project.md` 第 4 节 `INDEPENDENT_REVIEW` 行（唯一投影）。链已于 2026-10-20 按 `D-09` 封存并由 YG 批准章程 0.3；至此仍无一份记录给出 `APPROVE`，这一点已写进第 11 节的批准条件。叶级 Review A 尚无
  - `leaf-task.md` 体积对体积阈值的一半还剩多少：阈值是规则参数（定义见 `portable/templates/leaf-task.md` 的 Bounded size 段与 `scripts/validate_kit.py` 的 `LEAF_CONTRACT_CEILING_KB`），换算值与实测字节见 `.charter/evidence/template-budget-2026-10-19.txt`（D-01 未决）
  - 套件本体此前不受自己治理；本次自举是第一次纳管，回溯性证据是否算数见 D-02
- Lessons status: 条数、最新条目与各条 Hits 一律以 `.charter/lessons.md` 的 Entries 段为准（本行不计数、不复述条目名，避免第二份会变的副本）；open `GENERALIZE` 候选：无

## Evidence

| Reference | Kind | Candidate / scope | Producer | Result | Limitation |
|---|---|---|---|---|---|
| `.charter/evidence/dependency-check.log` | `verification` | 依赖探测两段：全仓 2026-10-19T12:43:28Z、复用阶段 12:54:05Z（后者另存 `.charter/evidence/reuse-probe-2026-10-19.txt`） | `check_dependencies.py` | `AVAILABLE` python / git / superpowers / j-space / grill-me / reuse-first / framework-first-coding / reduce-reinvention / find-skills；`UNVERIFIED` independent-review、subagent | 探测不能证明 fresh 上下文可用，只能在使用时验证；日志不记 argv 已记为 D-06 |
| `.charter/evidence/baseline-2026-10-19.txt` | `verification` | 叶开始前的 `git status --porcelain` 快照（行数与分解见该文件首行注释，此处不复制） | `git status` | AC2 的比对基准：本叶不得让 `portable/`、`targets/`、`scripts/`、`tests/` 新增改动行 | 清单只覆盖叶开始时刻；叶内新增的合法改动必须落在 `.charter/` 与 `docs/SELF-AUDIT.md` |
| `.charter/evidence/ac-liveness-2026-10-19.txt` | `verification` | 各验收项的检查原文、原样运行与对象侧突变表（该文件的 `## Mutations` 段是权威，本行不复述计数、分项与退出码） | 宿主 shell / python | 哪一条突变打红、哪一条控制组应保持绿，全部只看该文件的表；每次突变后按字节还原 | AC4 继承校验器的失败模式，本轮用「给 `portable/templates/review.md` 追加换行」触发 |
| `.charter/evidence/validate-2026-10-19.txt` | `verification` | `python scripts/validate_kit.py .` 的终态输出 | 宿主 shell | 输出与退出码只在该文件里（其圆点行即子检查的权威清单） | 校验只证明套件自一致，不证明章程内容正确 |

## Exact next action
执行叶 `R1.1-S1-L1`（状态 `APPROVED`，授权只覆盖这一片叶）。顺序：
① 跑 `python .charter/checks.py`（九条验收项必须全 `ok`）、`python scripts/validate_kit.py .`（exit 0）、`python -m pytest tests -q`；
② 把三次输出写进 `.charter/evidence/`（各自带时间戳与退出码），不要只贴结论；
③ 关闭要四层证据齐：退出码、原始物重算、独立上下文 Review A（`REV-<TASK-ID>-<nn>` 新文件）、集成后验证；
④ 关闭决定按 `CLS1`…`CLS10` 逐条作答，任何一项空缺即视为未关闭；
⑤ 关闭后同步 `roadmap.md` 的七态投影与 `Next authorization`，并清 `Active leaf`。

仍开着的决策不阻塞这一片叶（`D-10` 是读集增长，属章程级；`D-01`…`D-08` 各自有结算条件，见 `project.md` 第 10 节）。
本行不复制清单：逐条验收项以 `.charter/current-task.md` 第 5 节为准，处置与判词以 `.charter/records/` 为准。
## Do not do

- Do not start `R1.2-S1-L1` until the current task is `PASS_CLOSED` and authorization exists.
- Do not use sensitive or real data, release systems, external network, or push unless an approval reference is listed above.
- Do not treat a report, old test run, or self-review as fresh evidence.
- This section is also the promotion target when archiving handoff blocks: a convention that later leaves inherit or an unresolved negative result moves here (or into `project.md` Invariants) before its block is archived — see Promotion before archiving above.

## Session ledger

- Ledger mode (this session): `jspace.py controller ENABLED`（形态见下；`.jspace/` 已在 `.gitignore`）
- Ledger location: `.jspace/`（工作区根；靠 `.gitignore` 的显式条目留在版本控制之外，而不是靠记性）—— 新克隆上账本会消失，只有本节承载它的状态
- Last seam / state: `control.py init` 已执行（2026-10-19T12:45Z，level `medium`，goal 与 next 已写入 `.jspace/control.json`）；最近 seam = `REV-CHARTER-20` 的 `NF-59`…`NF-64` 处置完成与「一条规则一个实现」改造（九条验收项载荷全部委托 `.charter/checks.py`）（本行的「本轮」随每轮重算，不是历史；`.jspace` ledger 自 init（记录标签 12:45Z，最后写入 12:48:01Z）起未再更新，本节是它的权威投影）
- Five-line snapshot (if controller unavailable):

```text
Goal:      用本仓自己的模板建立 .charter 工作集并给出第一个叶合同
Core:      .charter/ 是治理事实源；镜像字节一致；validate 必须 exit 0
Verified:  validate 与 pytest 均全绿（计数落点 `.charter/evidence/`）
Open:      见 `project.md` 第 10 节的决策表（本行不枚举、不复述状态；`DEFERRED` 与 `OPEN` 的判定只在那张表里）
```

## Capability notes

- Dependency/independent-review gaps: `AVAILABLE` python、git、superpowers、j-space、grill-me、reuse-first、framework-first-coding、reduce-reinvention、find-skills；`UNVERIFIED`+`FALLBACK` independent-review 与 subagent（本地探测无法确认，但本会话实测可用：干净上下文 subagent 完成了章程级审阅链的每一轮（`REV-CHARTER-01` 起至最近一轮；轮次以 `.charter/records/REV-CHARTER-*.md` 为唯一权威，本文件不重复计数），未出现执行器不可用）。`grill-me` 为 `AVAILABLE` 但本会话未调用，按 `PORTABLE_FALLBACK` 记录：意图已由本会话确立，改用 `references/design-interview.md` 的六簇清单补齐。

- Git / isolated workspace: `main`，无 worktree；镜像比对是字节比对，`core.autocrlf=true` 的宿主上工作树比对会变红，复现校验要在 LF 归一化的树上或 `git archive HEAD` 之后执行
- Governance tracked / ledger ignored: `.charter/` 随首次提交进版本控制；`.jspace/` 已在 `.gitignore`
- Subprocess / test runner: `python -m pytest tests -q`（全量耗时与条数见 `.charter/evidence/pytest-2026-10-19.txt`；外层执行预算必须显式给足，默认预算会在中途打断，见同一证据文件的记录）
- Fresh context or independent reviewer: 宿主 `subagent`（fresh）；本会话实测：章程级每一轮均由 fresh subagent 完成（轮次以 `.charter/records/` 为唯一权威，本文件不重复计数）；当前有无 `APPROVE`、待哪一轮见本文件 `Review status` 行与 `project.md` 第 4 节的 `INDEPENDENT_REVIEW` 行（均按行标签定位，不按行号；记录文件集合在 `.charter/records/`），本行不复述判词
- Zero-change anchor (reproducible, for read-only reviewers): **三段**，写在同一条里 —— ① `git ls-files -s | sha256sum`；② `git status --porcelain | sha256sum`；③ 治理读集与证据的内容哈希 `cd .charter && find . -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum`（相对路径排序 + 逐文件内容哈希，不带会漂移的文件数；**不按扩展名过滤** —— 证据 `.txt` 与正文同样被覆盖，`REV-CHARTER-20` 的 NF-60 指出按 `*.md` 过滤时删掉一份证据文件锚点一字不变）。①② 对未跟踪文件全盲——`.charter/` 未提交时它们只反映一行 `?? .charter/`，所以 ③ 不是可选项；删改任何一份记录都必须改变 ③ 而 ①② 不变，这就是它的活性（`REV-CHARTER-19` 的 NF-57）。 ③ 不能等于它自己的写后值——记录 ③ 的那一块本身就是被哈希的文件之一；可核的是性质（删改任一文件 ③ 必变、①② 逐字节不变），不是与记录值相等。不要用自建文件数或自建聚合哈希——口径不可复现（`REV-CHARTER-10` 的 NF-13）
- Acceptance extraction rule (reviewers replay this verbatim): an acceptance item is the block from the AC item marker to the next AC item or the next level-two or level-three heading; that block must contain exactly one occurrence of the check label; the payload is the FIRST backticked span after it. Recorded because a payload carrying a second backticked span (an evidence pointer) was once misread and produced a false red. **The execution method is part of the rule too**: a multi-line payload handed to the shell (cmd.exe on Windows) is silently dropped and returns 0, which is a false green; run the code through stdin (`python -`) instead. This round measured both ways on the same tree and they disagree - see the REV-CHARTER-18 section of `.charter/evidence/ac-liveness-2026-10-19.txt`.
- Network / external service: 本版未授权外部读取（`LOCAL_ONLY`）

- Persistent state / resume: `.charter/` 启动读集 + `docs/SELF-AUDIT.md`（自审与执行日志）
- Missing capability and required fallback: 无阻塞；`independent-review` 的可用性在使用时确认

## Resume instructions

1. Read `.charter/project.md`.
2. Read `.charter/roadmap.md`.
3. Read `.charter/reuse-discovery.md` and confirm its gate status and recheck date.
4. Read `.charter/current-task.md`.
5. Check the current candidate and evidence references.
6. Perform only the exact next action above; update this packet after the next seam.
