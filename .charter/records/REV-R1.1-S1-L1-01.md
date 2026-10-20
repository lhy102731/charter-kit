# Review Record

## Review identity

- Review ID: `REV-R1.1-S1-L1-01`
- Task ID: `R1.1-S1-L1`
- Candidate revision: `main` @ `bd25d42d08d96cda002e7cca5fbabe26f30b9307`（工作区除本记录外只有一份未跟踪证据文件，见 F-12）。叶 §7 点名的三个内容提交 = `0bb410f` / `5e1e6c3` / `a2e876e`；本记录的判定对象是这三个提交加上其后的记录提交 `bd25d42` 的树。
- Reviewer: 独立叶级审阅 subagent（无实现上下文；输入 = 任务书 + 叶合同 + 章程 + 章程级 records + 自跑的门输出）
- Host / process / session: DeepSeek Harness；父会话 `session-9d5abb53-9872-4273-9f60-931b56f702ba` 派出的子会话；执行器 `run_code` + 仓内 python/git
- Review type: `A_SPEC_AND_CODE`
- Freshness (Review A): `fresh-subagent`（无实现上下文；只拿到本合同、章程、`.charter/records/` 与自跑输出）
- Freshness (Review B): 不适用本记录；`RVB1`–`RVB5` 的适用性与 `NOT_REQUIRED` 理由归属叶 §9 第二行（`.charter/current-task.md:231`），本记录不代答。
- Applicability: `REQUIRED`
- Trigger or bounded omission reason: 每个叶必备 Review A（`portable/templates/review.md:28`）；不适用 `B_FRESH_BEHAVIOR` 的判读留给 §7.1 与 §9。
- Started: `2026-10-20T01:20:05+08:00`（时间来源：本会话的首个运行时取样）
- Finished: `2026-10-20T01:26:00+08:00`（时间来源：写本记录前的一次 `date +%Y-%m-%dT%H:%M:%S%z`）
- 钉住的候选侧 blob（供下一位复算）：`HEAD:.charter/checks.py` = `a048e3ef78f681df600c543c3d1db8c5955bfad8`；`HEAD:.charter/current-task.md` = `e226130d5e1ccc4bcc7154b9c196e6eda0417c02`；`HEAD:.charter/evidence/baseline-2026-10-19.txt` = `eeaca9ac73d40f69edf415ca8a3c9a18c4da1caf`

## Independence declaration

- Different from implementer: `yes`
- Fresh context: `yes`
- Fresh process: `yes`（独立子会话、独立 shell 进程）
- Read implementer report before testing: `yes`，但顺序是「先自跑门与 diff，后读自述收据」；凡与自述冲突处一律以自跑输出为准，两处冲突已在 F-01、F-06 记明。
- Limitation on independence: ① `charter_review` 工具在当前 DSH 运行时不可用（实现者自述见 `.charter/evidence/fixes-15-2026-10-20.md:79`，报 `scope.subagents.start is not a function`），本记录由 `subagent` 通道派出，与那条自述的「判词等价」是被审查对象，不是本记录的前提；② 我读不到对话，无法核对 `m03465` / `m03483` 的授权原文，只能判记录成色（F-05）；③ 全部负向实验在仓外副本 `%TMP%/revA/repo` 上做，真仓库未改动（除本记录）。

## Checks performed

- [x] `CHK1` 目标与任务合同一致 —— 观察：叶 §2 的目标（把 `.charter/` 变成套件自身的治理事实源、第一个叶只做「用模板填出可读工作集」）与产物一致，9 条 AC 全部可跑（见 `CHK4`）。不一致落在合同内部：§2 的 explicit non-results（`.charter/current-task.md:36`）写着「不改 `portable/`、`targets/`、`scripts/`、`tests/`」，而 §4 Allowed paths（`:57-64`）明列三份 `portable/` 手工源与两份 `targets/` 镜像 —— 同一份合同两个口径，记 F-05。
- [x] `CHK2` 设计访谈记录存在且分支已解决或显式推迟 —— 观察：叶 §8 记 `Design interview record: PORTABLE_FALLBACK`（`.charter/current-task.md:205`），未解决分支集中在章程 §10 决策表（`.charter/project.md:227-237`），唯一仍开的是 `D-10`（`:237`，`OPEN`，带复核触发），属显式推迟。ok。
- [x] `CHK3` Allowed paths 与 effects 被遵守 —— 观察：见 `CHK5` 的复算；路径侧 5 条提交路径只靠基线豁免过关（F-01），效果侧有一次「写全局目录」的实作（`.charter/evidence/fixes-15-2026-10-20.md:63-75` 覆盖安装 `~/.agents/skills/charter-workflow`），而 `.charter/handoff.md:25` 把「写全局目录」列在禁止效果里（F-04）。
- [x] `CHK4` 正向验收检查通过 —— 观察（本审阅实跑 `python .charter/checks.py`，2026-10-20T01:25+08:00）：`AC1`…`AC9` 逐条 `ok`，`RESULT PASS`，rc=0；`AC2` 打印 `whitelist=7E/5P dirty_bad=[] dirty=1 diff=e3b0c44298fc committed=121 committed_bad=[]`，`AC5` 打印 `head=bd25d42d08d9 start=d6eff20240ad commits_since_start=4`。正向面成立。
- [x] `CHK5` 负向与边界检查通过 —— 观察：不通过。三组仓外突变（副本 `%TMP%/revA/repo`，真仓库未动）：
  - `E1`：写一份不含 `## Checks performed` 的 `.charter/records/REV-R1.1-S1-L1-01.md` 后跑 `--only AC7` → `ok AC7 records=2 bad=[]`，rc=0（F-10）。
  - `E2`：把 `.charter/checks.py` 的 `allowed()` 改成无条件 `return True` 后跑全量 → 九条全 `ok`、`RESULT PASS`、rc=0（F-03）。
  - `E3`：先加一个探针提交，再往 `.charter/checks.py` 追加一行注释并提交第二个探针提交 → `--only AC2` rc=0（`committed=122 committed_bad=[]`）、`--only AC5` rc=0（`commits_since_start=6`）（F-02）。
  - 路径覆盖复算（读真仓库、只读）：`committed` = 121，白名单覆盖 116，仅靠 `base_paths` 豁免 5，两者都不覆盖 0；5 条全部由 `0bb410f` 引入（F-01）。
- [x] `CHK6` 测试断言行为而非实现细节 —— 观察：`tests/test_absorption_contract.py` 的断言对象是模板对外契约（编号闭集、`CLS` 冻结区间、每条验收项必须点名一条能移动退出码的检查、记录一文件一份、读集 ⊆ 工作集、决策不落共享文件等，如 `:74` `:116` `:136` `:154` `:262` `:394`），不是内部实现细节；对一套纯文档套件这是可接受的「行为」定义。ok —— 但该文件本身不在 §4 白名单内，记在 F-01。
- [x] `CHK7` 候选引用就是实际被审的那个版本 —— 观察：不通过。叶 §7 的候选写成「`d6eff20` + 三个内容提交 + 其后只追加记录与证据」（`.charter/current-task.md:185`），§9 的 `Final candidate` 仍是占位 `<revision>`（`:235`），`handoff.md:38` 给的又是「`main` @ `5e1e6c3` + 第三个提交（工作区…）」；实际被审的 `bd25d42` 在三个载体里都没有被点名。记 F-06，并与 F-02 同源。
- [x] `CHK8` 复用发现记录最新、候选有明确处置、选定版本与许可已钉 —— 观察：`.charter/reuse-discovery.md` 的 `Gate status` `COMPLETE`（roadmap `:30` 同步投影）、`Discovery ID` `RD-20261019-01`、`Discovery freshness` `current`（`:33`）；`SR-01`…`SR-03` 全部 `SEARCHED`/`MATCH`（`:59-61`）；候选 `C-01` 版本钉在 `HEAD d6eff20`、处置 `ADOPT`、许可「仓内自有无外部许可义务」（`:75`）。ok。
- [x] `CHK9` 任何 `UNKNOWN` / `DEFER` / `NO_MATCH` 或缺搜索层都有记录的限度 —— 观察：无 `DEFER` 候选、无 `NO_MATCH`；两条 `UNVERIFIED` 能力（independent-review、subagent）在 `handoff.md:54` 记了限度（「探测不能证明 fresh 上下文可用，只能在使用时验证」）。本次审阅即为该能力的实测：fresh 子会话已派出并完成判定。ok。
- [x] `CHK10` 既有用户改动与无关失败被分开 —— 观察：不通过。基线快照有 79 条（77 `M` + 2 `??`，`.charter/evidence/baseline-2026-10-19.txt`），其中 5 条被折进 `0bb410f`，提交正文与 `docs/SELF-AUDIT.md` 都没有点名（F-01 / F-05）。另外本审阅跑门时 `dirty=1`：`.charter/evidence/fixes-15-2026-10-20.md` 未跟踪（F-12）。
- [x] `CHK11` 集成与合并后要求已理解 —— 观察：§7 写 `Merge allowed: no`（`:187`）、`Push allowed: no`（`:188`），必要集成动作是「在 `main` 上追加本地提交 + `python scripts/validate_kit.py .`」；路线图要求 `VERIFIED` 与 `PASS_CLOSED` 之间必须有集成与集成后验证证据（`.charter/roadmap.md:75`），而 §9 的 `:236-237` 仍是占位。要求本身清楚，但状态投影已落后（F-07）。
- [x] `CHK12` 本叶触及的每条默认值规则都在下一会话会读的文件里可见 —— 观察：`P0-1` 的三个钩子 `DOP1`–`DOP3` 落在 `portable/references/default-on-policy.md:34-49`，接线在 `DEVELOPMENT_CHARTER.md:190`（§2.8 第九条）与 `portable/templates/review.md:53`（`CHK12` 原文引 `DOP3`）；未收窄任何既有默认值。ok。
- [x] `CHK13` 每个 finding 都有 `Disposition`，非 `CLOSED` 的写明限度、到期或复查触发与承载条目 —— 观察：本记录 12 条全为 `OPEN`，与 `REQUEST_CHANGES` 配对（`portable/templates/review.md:69-71`）；每条都写了「最小修法」，并要求关闭提交把它们落进 `.charter/project.md` §10（`D-11` 起）或 `.charter/records/DEC-*.md`（`:72-77`）。载体尚未存在，是本记录的 `CLS3` 答 `否` 的直接原因。
- [x] `CHK14` 读集里的计量数指唯一权威而不复制值；会变状态只出现在章程声明的投影里；本审阅声称的例外逐条写成 `item | clause | basis` —— 观察：读集里没有发现新的计量值副本（`handoff.md:42-43` / `roadmap.md:34` / `.charter/current-task.md:111` 都只给指针，条数落在 `.charter/evidence/`）；投影声明点名了全部承载处（`.charter/project.md:50`）。`INDEPENDENT_REVIEW` 行（`.charter/project.md:72`）自称「链在此封存」且「尚无 `APPROVE`」——本审阅抽查 `.charter/records/REV-CHARTER-*.md` 全部 20 份，无一份给出 `APPROVE`/全票通过，该句成立。本记录为复算留痕所写的计数（`committed` 121 / 白名单 116 / 仅豁免 5 等）以本记录 `CHK5` 段的命令输出为准，别处不复制。
  - `Exceptions claimed`:
    - `本记录的计数留痕 | project.md:50 不变量「计量数只落 .charter/evidence/」 | review.md:83-89 要求 finding 的现场复算必须带可核对的取值；若只给命令不给期望输出，下一位无法判断复算是否跑对`
    - `本记录不复制 15 条修复的落点行号 | project.md:50「同一事实只有一处权威」 | 逐条收据的唯一权威是 .charter/evidence/fixes-15-2026-10-20.md:36-52，本记录只抽样并指出与批表冲突处`

## Change Triage

- 事件种类与路由：本叶绝大多数改动 `IN_CONTRACT`；两项走了 `LEAF_CHANGE` 并在 §6 记了 `Ruling` —— `P1-3` 回滚入本叶（`.charter/current-task.md:180`，§4 同时增三份手工源）与「提交」从禁止项解禁（`:181`，勾 `local_merge`）。
- 未走路由的一处：`0bb410f` 一并提交的 5 条路径（`portable/commands/charter-workflow.md`、`portable/templates/changelog.md`、`portable/templates/leaf-task.md`、`targets/zcode/commands/charter-workflow.md`、`tests/test_absorption_contract.py`）既未进 §4、也没有 `Ruling`，改由 `.charter/checks.py:174` 的基线豁免顶替。这是「新事实静默扩大本叶」的形态，记 F-01 / F-05。
- 结论：`LEAF_CHANGE`（需补记，非 `CHARTER_CHANGE`；`ROADMAP_CHANGE` 不需要）。

## Findings

| ID | Finding severity (`P0 / P1 / P2 / P3`) | Remediation change class (`A / B / C`) | Finding | Evidence reference | Required action | Disposition |
|---|---|---|---|---|---|---|
| F-01 | `P1` | `B` | `AC2` 条件 ③ 的文字是「提交本身不豁免边界」，实现却在提交范围上继承基线脏路径的豁免。复算：`git diff --name-only d6eff20..HEAD` 共 121 条，白名单覆盖 116，**仅靠 `base_paths` 才通过 5 条**，两者都不覆盖 0 条。5 条全部由 `0bb410f` 带入历史：`portable/commands/charter-workflow.md`（+2/−2，基线 ` M`）、`portable/templates/changelog.md`（+3/−1，` M`）、`portable/templates/leaf-task.md`（+13/−13，` M`）、`targets/zcode/commands/charter-workflow.md`（+2/−2，` M`）、`tests/test_absorption_contract.py`（+440/−0，基线为 `??` 未跟踪）。叶 §6 把代价写成「若第三个提交碰了白名单外的路径就当场红」，实际不会红；豁免理由（字节不由本叶产生、提交只移动状态）在提交后不可复核：基线只存 `(status,path)` 与聚合摘要，工作区已空，条件 ② 退化为空串摘要 `e3b0c44298fc` 恒真（本次实跑正是这个值）。对比同一提交为 `P1-3` 回滚**确实**改了 §4 增三份手工源，却没为这 5 条改 §4 | `.charter/checks.py:174`（`and n not in base_paths`）；`.charter/checks.py:146-149`（`base_paths` 来源于基线文件）；`.charter/current-task.md:107`（`AC2` 正文）；`.charter/current-task.md:181`（Ruling 的代价自述）；`docs/SELF-AUDIT.md:1329`（豁免理由）；复算输出见本记录 `CHK5` 段 | 二选一，不可两做：① 把 5 条点名进 §4 并对每一类给出理由（`P1-3` 回滚就是这么做的），再在 §6 补 `Ruling`；② 删掉 `checks.py:174` 的基线豁免，提交范围只认 `contract_allowed()`，把 5 条从历史里剥出（新提交撤销）或改成逐条点名的显式豁免清单。任一路径都要把 `.charter/current-task.md:181` 的代价句改写成与实现一致 | `OPEN` |
| F-02 | `P1` | `B` | `AC5` 从「HEAD 全等」改成「后代关系」后丢掉的那条断言——提交之后内容可以继续追加而不被发现——没有被任何 AC 兜住。`AC2` 的条件 ③ 只读路径列表（`git diff --name-only`），不看内容；叶 §7 的「其后的提交只追加记录与证据、不改变本叶内容」没有任何检查；§9 的 `Final candidate` 仍是占位 `<revision>`。实测 `E3`：在两个内容提交之后再提交两次（第二次只往 `.charter/checks.py` 追加一行注释），`AC2` 与 `AC5` 仍双双 rc=0 | `.charter/current-task.md:108`（`AC5` 正文）；`:185`（候选定义）；`:235`（`<revision>` 占位）；`.charter/checks.py:256-262`（`AC5` 只判 `merge-base --is-ancestor`）；`.charter/checks.py:172-174`（`AC2` 只看路径名）；本记录 `CHK5` 的 `E3` | 新增或扩写一条 AC，把候选钉成可判的形态：把 §7 点名的候选 revision 的 `git rev-parse <rev>^{tree}` 落进 `.charter/evidence/`，并断言 `git diff --stat <rev>..HEAD` 的路径集合 ⊆ {`.charter/records/`**, `.charter/evidence/`**}；同时把 §9:235 填成具体 revision（不能是提交列表） | `OPEN` |
| F-03 | `P1` | `B` | 检查门自身在白名单内，且没有任何 AC 或证据锚定它的内容，于是它可以被改弱而九条全绿。实测 `E2`：把 `allowed()` 改成无条件 `return True`，`python .charter/checks.py` 仍九条 `ok` / `RESULT PASS` / rc=0（`AC2` 还打印 `dirty_bad=[]`、`committed_bad=[]`）。这与 `lessons.md` 的 `LS-002` 同族：检查器自身坏掉时双向伪造结论 | `.charter/checks.py:139-178`（`allowed()` 定义在 `:143-144`，取值决定 `:174`）；`.charter/current-task.md:57`（`.charter/**` 在白名单内）；`lessons.md:26-30`（`LS-002`）；本记录 `CHK5` 的 `E2` | ① 把门的 blob sha 由审阅钉住并要求下一位复算（本记录已在 identity 段钉了 `HEAD:.charter/checks.py` = `a048e3ef…`）；② `AC4` 的锚点覆盖范围加上 `.charter/checks.py`，使「改了门」在锚点上也留痕；③ 在 `checks.py` 头注写明「门的改动必须与它的证据同一次提交」 | `OPEN` |
| F-04 | `P1` | `B` | 效果越界：把 `~/.agents/skills/charter-workflow` 整目录覆盖安装（旧版 22 文件 → 23 文件，含用安装版起新项目的冒烟），而 `.charter/handoff.md:25` 把「写全局目录」列在禁止效果里，§4 的 `code_write` 限 Allowed paths、`external_service`/`irreversible` 均未勾选。本审阅独立复核：`diff -rq skills/charter-workflow "$HOME/.agents/skills/charter-workflow"` 只多 `scripts/__pycache__`，备份目录 `.backup/charter-workflow-20261020T0115` 存在（可回滚） | `.charter/evidence/fixes-15-2026-10-20.md:63-75`（安装与冒烟）；`.charter/handoff.md:25`（禁止效果）；`.charter/current-task.md:65-72`（Allowed effects 勾选）；本记录 `CHK3` | 二选一：① 在叶 §4 补一条 `Ruling` 明确允许这次安装并给出回滚指针，同时清掉 `scripts/__pycache__`；② 记为越界动作（`docs/SELF-AUDIT.md` 新增小节）并把「重新安装」降为下一叶的授权事项。任一选择都要进 §10 或 `records/DEC-*.md`，不能只留在收据里 | `OPEN` |
| F-05 | `P1` | `B` | 授权链的记账成色够，缺的是把授权**范围**落笔。`P1-1` 的偏离裁决有明确追认（`m03465`）且已写进 §9.12，「先动后补」（`m03483`）也已在 §6 记 `Ruling`——这两件都不需要重走授权。真正没落笔的是范围：§4 至今没纳入那 5 条路径，改由 `checks.py:174` 的豁免顶替；同时 §2 的 non-results（`:36`「不改 `portable/`、`targets/`、`scripts/`、`tests/`」）与 §4 Allowed paths 相互矛盾，而 `0bb410f` 已经在 `portable/`、`targets/`、`tests/` 上落了改动。一个事实两个落点，正是 §9.12 与 `LS-004` 记的形态 | `.charter/current-task.md:36`、`:57-64`；`docs/SELF-AUDIT.md:1288-1289`（追认）；`:1299-1305`（记账缺口与处置纪律）；`:1331-1337`（先动后补的判读）；`.charter/checks.py:174`；`lessons.md:39-40`（`LS-004`） | 在关闭提交里把 §2:36 与 §4 收到同一口径：要么把 5 条点名进 §4，要么把 §2 改成「不改 §4 之外的 `portable/`/`targets/`/`tests/`」；并让白名单实现随合同文字同一次移动。追认本身不重做 | `OPEN` |
| F-06 | `P2` | `B` | 三个载体对「被审候选」各说一套，且 handoff 落后两个提交：`handoff.md:38` 仍写「`main` @ `5e1e6c3` + 第三个提交（工作区，仅 `.charter/` 四个文件）」，`:34` 的 `Last accepted event` 仍写「本叶的两个提交完成」，而实际 HEAD 是 `bd25d42`、工作区干净；`a2e876e` 的提交正文自称已同步 handoff 的 candidate revision，实际同步到的是前一提交。另外 `handoff.md:24` 把 `code_write` 收窄成「限 `.charter/` 与 `docs/SELF-AUDIT.md`」，与 §4 的白名单不同 | `.charter/handoff.md:24`、`:34`、`:38`；`.charter/current-task.md:185`；`git log --oneline`（HEAD = `bd25d42`）；`git status --porcelain`（空工作区） | 关闭提交里把 handoff `:24`/`:34`/`:38` 三行改到与 §4/§7 同值并点名 `bd25d42`；`code_write` 的收窄按 F-05 的口径一并对齐 | `OPEN` |
| F-07 | `P2` | `B` | 七态投影跳档且自述与事实相反：`roadmap.md:17` 的本叶仍是 `APPROVED`，`:26` 的注仍写「`APPROVED`；实现与关闭尚未开始」，而实现已完成、本审阅已派发；`READY`/`IN_PROGRESS`/`REVIEW` 三个态在两个载体里从未出现，`:75` 却要求按序镜像。`AC1` 只断言「两处相等」，跳档与自述都不在门的视野里 | `.charter/roadmap.md:17`、`:26`、`:75`；`.charter/current-task.md:15`（`Status: APPROVED`）；本记录 `CHK1` 段 | 关闭时一次把 `roadmap.md:17`/`:26`、`.charter/current-task.md:15` 与 Review 态对齐（不要一份文件领先于审阅）；「先实现、后置态」这件事本身值得一条 `lessons` 条目（`LS-001` 同族） | `OPEN` |
| F-08 | `P2` | `B` | 15 条修复的核心证据不可复算：突变矩阵的脚本放在 `.git/mut15.py` 与 `.git/mut2.py` 并明写「不进版本库」。本审阅实测这两个文件存在（2819 B / 1789 B），但不在候选树内，任何后来者无法重放收据 §2 的 `M0`–`M6`；`.git/` 也不是 §4 的落点 | `.charter/evidence/fixes-15-2026-10-20.md:18-32`（矩阵）、`:90`（脚本位置与「不进版本库」）；`ls -l .git/mut15.py .git/mut2.py`（本审阅实跑） | 把两个脚本移进可提交位置（下一叶的 `tests/` 或 `.charter/evidence/mut/`），或在收据里给出可重放的最小命令序列（含控制组）；证据的复算代价必须落在候选树里 | `OPEN` |
| F-09 | `P2` | `B` | §8 执行记录没对账：Events 表只有一行 `2026-10-19T12:50Z DRAFT`（`:218`），`APPROVED`、三个内容提交、`bd25d42`、Review A 一条都没有进表；Evidence index 仍写「尚无收据：本叶尚未执行验证」（`:224`），而 `.charter/evidence/` 实有 14 份文件。§9 明写：无对账也无 `NOT_ENABLED` 豁免者不得以 `PASS_CLOSED` 关闭（`:233`） | `.charter/current-task.md:216-224`、`:233`；`ls .charter/evidence/` | 关闭提交前把 Events 表补到当前状态并让 Evidence index 指向收据文件；若本叶不打算维护 ledger，则按 `:233` 记 `NOT_ENABLED` 豁免并写明理由 | `OPEN` |
| F-10 | `P3` | `A` | `AC7` 的文字是「从 `REV-CHARTER-19` 起的**每份审阅记录**」，实现把范围收窄成只认 `REV-CHARTER-*`，于是任何叶级审阅记录（包括本记录与下一位的判词）不在覆盖内。实测 `E1`：写一份不含 `## Checks performed` 的 `REV-R1.1-S1-L1-01.md`，`--only AC7` 仍 `ok`、`records=2`、rc=0 | `.charter/checks.py:277-279`（`re.search(r"REV-CHARTER-([0-9]+)")` 且 `< 19` 跳过）；`.charter/current-task.md:99`（`AC7` 正文）；本记录 `CHK5` 的 `E1` | 把过滤条件改成 `.charter/records/REV-*.md`；若坚持只覆盖章程级链，就把 `:99` 的文字同步收窄——不要留两份口径 | `OPEN` |
| F-11 | `P3` | `A` | 门与叶绑定得太死：`EXPECTED_HEAD` 硬编码基线 SHA、`AB`-前缀判断硬编码本叶 ID，脚本单叶专用；下一位必须整体重写，而没有任何文本要求「每叶重建门并钉住它」。这与 F-03 合起来意味着门的可信度靠人记得住，不靠文件 | `.charter/checks.py:25`（`EXPECTED_HEAD = "d6eff20240ad…"`）；`.charter/checks.py:134`（叶 ID 判断）；`.charter/current-task.md:189-198`（§7 只要求跑 `validate_kit`） | 在 `checks.py` 头注或叶模板的 Review A 段写一句「每叶重建 `checks.py`、把它与叶合同的 blob sha 钉进证据、由 Review A 复算」 | `OPEN` |
| F-12 | `P2` | `A` | 15 条修复的收据 `.charter/evidence/fixes-15-2026-10-20.md` **未被跟踪**（`git status --porcelain` = `?? .charter/evidence/fixes-15-2026-10-20.md`，创建于最后一个提交之后），只存在工作区。它正是 `CHK2`/`CLS2` 里「语义层」证据的落点，也是本审阅判 F-04 / F-08 的直接依据；一旦工作区丢失，本叶「15 条修复」的第三层与「`charter_review` 不可用、改用 subagent 通道」这条偏离记录就一起消失。门看不见它：`.charter/**` 在白名单内，`AC2` 当前仍打印 `dirty=1 diff=e3b0c44298fc` 全绿 | `git status --porcelain`（本审阅实跑，2026-10-20T01:25+08:00）；`ls -l .charter/evidence/fixes-15-2026-10-20.md`（9703 B，mtime 01:23，晚于 `bd25d42` 的 01:10）；`.charter/checks.py:159`（`dirty_bad` 只判白名单） | 关闭提交里显式 `git add` 该文件；若不愿把它留在证据目录，把其中仍成立的事实并进已提交的证据文件后删除。门的这类盲区（白名单内的未跟踪证据）建议在下一叶记成条目——它与 F-01 的条件 ② 退化是同一机制 | `OPEN` |

## Closure answers

| CLS id | 回答 | 证据 |
|---|---|---|
| `CLS1` | **部分成立，不能作为关闭依据。** 目标层（`.charter/` 成为套件自身治理事实源、证据可复核）在产物里成立：门可跑、证据可复算、章程 §10 决策表自洽。但「事实源是唯一权威」这条在两条边界 AC 的实现上买了折扣：`AC2` 的提交边界被基线豁免削掉（F-01）、`AC5` 之后没有内容锚点（F-02） | `.charter/project.md:44-50`；本记录 `CHK4`/`CHK5` |
| `CLS2` | **四层证据形式上齐备，但第四层现判不通过，第三层动作本身越界。** 结构层 `validate_kit.py` PASS（246 files）；语义机检层 `pytest` 298 passed / 519 subtests；实战位置层有安装与冒烟；独立审阅层 = 本记录。第三层的安装动作越出 `handoff.md:25` 的禁止效果（F-04），其收据还未跟踪（F-12） | `.charter/evidence/validate-2026-10-19.txt`、`.charter/evidence/pytest-2026-10-19.txt`、`.charter/evidence/fixes-15-2026-10-20.md`、本记录 |
| `CLS3` | **否。** 本记录 12 条 finding 全为 `OPEN`，一条都还没有落进 `.charter/project.md` §10 或 `.charter/records/DEC-*.md`；按 `review.md:72-77`，`OPEN` 只能与 `REQUEST_CHANGES` 配对，因此现在不能写 `PASS_CLOSED` | 本记录 `## Findings` 的 `Disposition` 列；`portable/templates/review.md:69-77` |
| `CLS4` | **未对账。** Events 表只有 `DRAFT` 一行，Evidence index 仍称「尚无收据」，而 `.charter/evidence/` 有 14 份文件；既无对账也无 `NOT_ENABLED` 豁免 | `.charter/current-task.md:216-224`、`:233`（F-09） |
| `CLS5` | **未做，且现在不能做。** §9 的 `Target-branch integration receipt` 与 `Post-merge verification` 仍是占位（`:236-237`）；`Merge allowed: no`（`:187`）意味着本叶的「集成」= 在 `main` 上追加本地提交，其后的集成后验证必须落在同一个候选上 | `.charter/current-task.md:236-237`、`:187`；`.charter/roadmap.md:75` |
| `CLS6` | **未做。** `handoff.md` 的提升扫掠没有对「先动后补」「门自弱」「豁免宽于文字」这三条仍生效的判断做过；而且 handoff 自身的 `code_write` 收窄与候选修订两行已与 §4/§7 不一致（F-06） | `.charter/handoff.md:7`（提升规则）、`:24`、`:34`、`:38` |
| `CLS7` | **未评估。** 本轮至少有三个够格的事件：① 先动后补（已写进 §9.13，但 `lessons.md` 里没有对应条目）；② 门自身无锚定（`LS-002` 同族，本条把「检查器坏掉」从执行器扩到了门本身）；③ 白名单文字与豁免实现两个落点（`LS-004` 同族，`Hits` 应 +1）。另有两件待判：七态跳档（F-07）、白名单内未跟踪证据（F-12） | `lessons.md:19`（`LS-001`）、`:26`（`LS-002`）、`:39`（`LS-004`）；`docs/SELF-AUDIT.md:1331-1337` |
| `CLS8` | **否。** 合同 §7 点名三个内容提交 + 「其后只追加记录与证据」；handoff 的候选仍停在 `5e1e6c3`；roadmap 的本叶状态与注停在「实现尚未开始」。三份载体在同一时刻说了三套话（F-06 / F-07） | `.charter/current-task.md:185`；`.charter/handoff.md:38`；`.charter/roadmap.md:17`、`:26` |
| `CLS9` | **关闭决定现在只能是 `PARTIAL` 或 `NEEDS_DECISION`，不能是 `PASS_CLOSED`。** 逐条 AC 对本记录的确认：`AC1` ok（`missing=[] status='APPROVED' rows=1`）；`AC2` **表面 ok、实质不通过**（F-01，且条件 ② 已退化）；`AC3` ok（`gate=COMPLETE leaf=['ADOPT'] bad=[]`，四 gate 点 / 三 freshness / 三 RD 逐点断言）；`AC4` ok（`rc=0`）；`AC5` **表面 ok、实质不足**（F-02）；`AC6` ok（`header=5 rows=10 bad=[]`）；`AC7` **表面 ok、覆盖不足**（F-10）；`AC8` ok（`blocks=9`，每块 `check` 标签恰一次、载荷无裸竖线）；`AC9` ok（载荷全部指向 `checks.py --only <id>`）。决定理由：九条门全绿，但其中三条的绿是「实现比文字窄」造成的，而合同级事实（5 条越界路径、提交后追加窗口、审阅记录覆盖面）需要先改合同或改门、再重跑一次 Review A | 本记录 `CHK4`/`CHK5` 的实跑输出；`.charter/current-task.md:95-111` |
| `CLS10` | **否，有四个未检查的边界。** ① 提交后追加内容的窗口（F-02）；② 门自身内容（F-03）；③ `AC7` 对叶级审阅记录不覆盖（F-10）；④ 白名单内的未跟踪证据（F-12）。四条都必须先「检查」或「带复查触发进 §10」才能关闭：F-01/F-02 适合做 AC 扩展，F-03/F-11 适合在门头注 + 审阅钉 sha 落地，F-05 的范围裁定属人判 | 本记录 `## Findings`；`.charter/project.md:50`（`CLS10` 的落点规则） |

## Verdict

`REQUEST_CHANGES`

Reason: 候选 `main @ bd25d42` 的正向面成立——九条 AC 我独立复跑全 `ok`（`.charter/checks.py` 输出 `RESULT PASS`），章程 §10 决策表自洽，镜像字节一致，复用门 `COMPLETE` 且候选 `C-01` 版本已钉。不通过的是边界：`AC2` 条件 ③ 的合同文字写着「提交本身不豁免边界」，实现（`.charter/checks.py:174`）却在提交范围上继承基线脏路径的豁免，实测 121 条提交路径里有 5 条只靠豁免通过，且全部由 `0bb410f` 引入；叶 §6 对被削掉的代价写的是「碰了白名单外就当场红」，与实测相反。`AC5` 改成后代关系后留下的「提交后追加内容」窗口没有任何 AC 兜住（仓外副本实测：追加内容甚至改写门本身，两条边界 AC 仍全绿），`AC7` 把「每份审阅记录」实现成只认 `REV-CHARTER-*`，门自身也没有任何锚定（实测把 `allowed()` 改成恒真后九条仍全绿）。效果侧另有一次「写全局目录」的实作落在 `handoff.md:25` 的禁止清单里，其收据还停留在工作区未跟踪。这些都不是措辞问题：它们让「全绿」比它覆盖的范围更宽。修法已在 12 条 finding 的 `Required action` 里逐条给出，且都能在候选树上用我列出的命令复算。修完后需要一次新的 Review A（不能拿本记录当补丁通过）。

## Re-review trigger

F-01 与 F-02 的任一条改动（`.charter/checks.py` 的提交范围判定、`AC2`/`AC5` 正文、`.charter/current-task.md:107-108`）、`AC7` 的过滤条件、`.charter/handoff.md:24/34/38` 的候选与效果表述、`.charter/roadmap.md:17/26` 的状态、或 `bd25d42` 之后出现任何改变本叶内容的提交，都必须重新派 Review A，并以新的记录文件承载判词。

VERDICT: REQUEST_CHANGES
