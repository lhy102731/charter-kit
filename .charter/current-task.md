# Leaf Task Contract

> **Write the delta, not the project.** A clause whose authoritative source is already in the required-start read set may be carried by an explicit reference plus this leaf's delta — for example `project.md section 5 baseline, plus: <leaf-specific item>` for forbidden effects, or `roadmap.md verification commands` for the standard checks. Anything that narrows, widens, or contradicts that baseline is written out here in full. Never replace a leaf-specific field with a reference: the result sentence, allowed paths, acceptance checks, repair budget, and any stop condition that differs from the standard list are always inline. A reference names its source file and section so the archived contract stays resolvable at the commit that recorded it.

> **Bounded size.** Keep this contract under 36 KB. Every resume re-reads it, so its length is paid by every later actor — but the bound is also a reading of the leaf, not a budget: a contract that needs more than this has almost always absorbed material that belongs to a file already in the read set, or it is more than one leaf. Move goal or scope prose to `project.md`, sequencing to `roadmap.md`, candidate evidence and pinned versions to `reuse-discovery.md`, and command output to `.charter/evidence/`; if nothing belongs elsewhere, the result sentence is what should be split. Past the bound, record a Ruling that says why this leaf needs it and what you gave up — raising the number is a deliberate change to every document that states it, never a silent edit. Never buy the reduction by deleting acceptance checks, stop conditions, allowed paths, or effects: a contract that no longer states what the gate needs is a worse defect than a long one.

## 1. Identity

- Task ID: `R1.1-S1-L1`
- Parent task: `R1.1-S1`
- Project goal reference: `.charter/project.md` 第 2 节 Goal
- Title: `用本仓自己的模板建立 .charter 工作集并给出第一个叶合同`
- Owner / implementer: `lead / DeepSeek Harness`
- Mode: `MANUAL`
- Status: `APPROVED`
- Leaf approval / preauthorization reference: `NOT_GRANTED`
- Contract version: `0.4` — a contract predating a field this workflow now requires is migrated, and its version bumped, before the next state transition: `portable/references/contract-migrations.md` in the full kit or `references/contract-migrations.md` in the self-contained Skill

## 2. Result contract

### One result sentence

> 给出 `.charter/` 的整套工作集之后，一个只读启动读集的会话就能复述目标、活动叶、授权引用与下一步动作。

### Why this leaf matters

`project.md 第 3 节的产品回路`：把「治理自举」这一步写成可复核的记录，之后每个叶都从这份记录开始。

### Change Triage

- Record the Change Triage event kind and route from the bundled reference: `portable/references/change-triage.md` in the full kit or `references/change-triage.md` in the self-contained Skill.
- New requirement must not silently expand the current Leaf.

### Explicit non-results

- This task does not: 改 `portable/`、`targets/`、`scripts/`、`tests/`（这些属于 R1.2 及后续叶）
- This task does not: 提交任何东西；本叶不产生 commit，也不 push。

## 3. Preconditions

- [ ] Project charter is approved.
- [ ] Reuse discovery record: `.charter/reuse-discovery.md` has been read; its gate is `COMPLETE`, or this specific Leaf has an explicit, separately approved bounded waiver recording the approved/omitted scope, limitation, approver, and expiry/recheck condition, before this leaf becomes `READY`. The waiver is not a fourth gate state or project-wide bypass.
- Reuse assessment: `NO_MATERIAL_TARGET` — 模板与脚本都已在仓内（`SR-01` 至 `SR-03`），本叶只做填空。
- Reuse coverage / result: `SEARCHED` / `MATCH`
- Reuse final route / candidate IDs: `ADOPT` / `C-01` @ `d6eff20`
- [ ] The reuse record is current for this leaf; if its recheck trigger/date applies, a targeted recheck is linked. Without the leaf-specific waiver above, `PENDING`, `BLOCKED`, and `BLOCKED_TOOLING` are not approval; resolve the evidence or authorization gap before continuing. Any limitation or waiver is recorded in the decision field with approver, omitted scope, and recheck condition.
- [ ] This leaf is approved under its selected mode and the authorization reference is recorded.
- [ ] Predecessor tasks: `—`（本叶是第一个叶）
- [ ] Baseline revision/workspace: `main` @ `d6eff20`
- [x] User's existing changes recorded and protected —— 基线清单 `.charter/evidence/baseline-2026-10-19.txt`（行数与分解见该文件首行注释，此处不复制），由 AC2 逐行比对；限制记作 `HOLDS_BY_DECLARATION`：它是声明出来的起始状态，不是对改动来源的证明。
- [ ] Required host abilities available: `python 3.13`、`git`、宿主 `subagent`
- [ ] Dependency check evidence: `.charter/evidence/dependency-check.log`（复用阶段运行独占一段，2026-10-19T12:54:05Z；独立捕获 `.charter/evidence/reuse-probe-2026-10-19.txt`）；`AVAILABLE` python / git / superpowers / j-space / grill-me / reuse-first / framework-first-coding / reduce-reinvention / find-skills；`UNVERIFIED`+`FALLBACK` independent-review、subagent
- [ ] Required authorization references: 无（`MANUAL` 模式，等用户批准本叶）

## 4. Scope

### Allowed paths / artifacts

- `.charter/**` —— 工作集、records/、evidence/
- `docs/SELF-AUDIT.md` —— 仅在需要记录本轮时
- `portable/templates/review.md` 与 `portable/references/contract-migrations.md` —— `CHK14` 的手工源（见本节 Ruling）
- `targets/codex/skills/charter-workflow/**` 与 `targets/zcode/skills/charter-workflow/**` —— 上述两份手工源的镜像，必须字节一致
- `DEVELOPMENT_CHARTER.md`、`portable/templates/roadmap.md`、`portable/templates/project-charter.md` —— `P1-3` 回滚的手工源（见 §6 的 Ruling）；它们的镜像与生成物已在上两条覆盖范围内
- `skills/charter-workflow/**`、`plugins/**`、`.codex-plugin/plugin.json` —— 三个 builder 的 `--sync` 生成物

### Allowed effects

- [x] `read_only`
- [x] `sample_run`
- [x] `code_write`（限本书 Allowed paths 列出的路径）
- [x] `local_merge`（本叶落地为三个本地提交，见 §6 的 Ruling；不含分支合并、不含 push）
- [ ] `external_service`
- [ ] `sensitive_data`
- [ ] `release`
- [ ] `irreversible`

### Forbidden effects

- `.charter/project.md` 第 5 节 forbidden effects 基线 `—` 本叶不新增、不收窄任何效果
- 本叶额外禁止：改上列之外任何 `portable/` 文件、根 `DEVELOPMENT_CHARTER.md`、push、打 tag（`提交` 一项经 §6 的 Ruling 解禁：YG 于 m03483 授权把本叶产物落成三个本地提交）。

## 5. Acceptance

### Acceptance items

Number every item `AC1`, `AC2`, ... in the order it must hold. An `AC` id is
created once and never renumbered, re-scoped, or reused; a withdrawn item keeps
its id and is marked withdrawn with the reason. Each `AC` names the check that moves an
exit code when the item is false, or records `N/A` plus why it cannot be checked; an
item that does neither is a wish. `CLS9` confirms each `AC` against its check.
Ids run `AC1`-`AC9` and are frozen by id, not by position: `AC2` and `AC5` are boundary checks, so they sit under `Negative behavior / boundaries`. Cite them by id, never by order.

### Positive behavior

- [ ] `AC1` 启动读集齐全且非空，叶的 Status 行恰好出现一次，且该值与 roadmap 中该叶那一行的 Status 单元相等 - check: `python .charter/checks.py --only AC1`（实现唯一：`.charter/checks.py` —— 本行不内联实现。REV-CHARTER-20 的主判定就是「按点名修」：同一条规则两份实现，改一处另一处照旧漂）
- [ ] `AC3` gate 值、RD 编号、freshness 值与本叶三行复用取值，在章程声明的每个投影点上都等于权威记录（四个 gate 点、三处 freshness、三处 RD；本叶的 material target 对 `Material target test`、coverage/result 对 Search log 的 Coverage/Result 两列、final route 对候选表的 `Disposition` 单元格；每个标签在各自文件里必须恰好命中一次） - check: `python .charter/checks.py --only AC3`（实现唯一：`.charter/checks.py` —— 本行不内联实现。REV-CHARTER-20 的主判定就是「按点名修」：同一条规则两份实现，改一处另一处照旧漂）
- [ ] `AC4` `.charter/ 的存在不破坏镜像比对与自检` - check: `python .charter/checks.py --only AC4`（实现唯一：`.charter/checks.py` —— 本行不内联实现。REV-CHARTER-20 的主判定就是「按点名修」：同一条规则两份实现，改一处另一处照旧漂）
- [ ] `AC6` 章程第 10 节决策表的每一行格数都等于表头格数（按 GFM 语义数未转义的竖线：单元格内的 `\|` 是合法转义、不算分隔符；多一格会把 State 列渲染成别的列值，`OPEN` 就读不出来） - check: `python .charter/checks.py --only AC6`（实现唯一：`.charter/checks.py` —— 本行不内联实现。REV-CHARTER-20 的主判定就是「按点名修」：同一条规则两份实现，改一处另一处照旧漂）
- [ ] `AC7` 从 `REV-CHARTER-19` 起的每份审阅记录都带 `## Checks performed` 段，且该段内至少引用一次 `CHK14`（`REV-CHARTER-19` 的 NF-58：门要求一句答案，但没有任何一步要求谁交出它） - check: `python .charter/checks.py --only AC7`（实现唯一：`.charter/checks.py` —— 本行不内联实现。REV-CHARTER-20 的主判定就是「按点名修」：同一条规则两份实现，改一处另一处照旧漂）

- [ ] `AC8` 每个验收项块内 `check:` 标签恰好一次，且任何载荷都不含裸竖线 - check: `python .charter/checks.py --only AC8`（实现唯一：`.charter/checks.py` —— 本行不内联实现。REV-CHARTER-20 的主判定就是「按点名修」：同一条规则两份实现，改一处另一处照旧漂）

- [ ] `AC9` 每条验收项的载荷都指向 `.charter/checks.py --only <id>`，不得内联实现 - check: `python .charter/checks.py --only AC9`（实现唯一：`.charter/checks.py` —— 本行不内联实现。REV-CHARTER-20 的主判定就是「按点名修」：同一条规则两份实现，改一处另一处照旧漂）

### Negative behavior / boundaries

- [ ] `AC2` 允许路径之外的改动为零，三个条件同时成立：① 工作区 `git status --porcelain` 的每个路径都落在 Allowed paths 白名单内；② 工作区非空时，`git diff` 对非白名单缺省范围的摘要仍等于 `.charter/evidence/baseline-2026-10-19.txt` 首部的 `diff-sha256`（提交后工作区为空，此条自动退化为真，见 §6 的 Ruling）；③ `git diff --name-only d6eff20240adbcce327ca7cffe27053a6df6bd02..HEAD` 的每个路径同样落在白名单内 —— 提交本身不豁免边界 - check: `python .charter/checks.py --only AC2`（实现唯一：`.charter/checks.py` —— 本行不内联实现。REV-CHARTER-20 的主判定就是「按点名修」：同一条规则两份实现，改一处另一处照旧漂）
- [ ] `AC5` 本叶不重写历史：`HEAD` 必须是叶开始修订 `d6eff20240adbcce327ca7cffe27053a6df6bd02` 的后代（`git merge-base --is-ancestor` 退 0）；本叶产生的提交数量是记录事实、落在 §7，不再要求 `HEAD` 与该 SHA 全等 —— 旧写法在提交存在的瞬间必然为红，等于用验收项禁止收尾动作本身，见 §6 的 Ruling - check: `python .charter/checks.py --only AC5`（实现唯一：`.charter/checks.py` —— 本行不内联实现。REV-CHARTER-20 的主判定就是「按点名修」：同一条规则两份实现，改一处另一处照旧漂）
### Suite verification

- [ ] Whole-suite verification: `python -m pytest tests -q`（结果落点 `.charter/evidence/pytest-2026-10-19.txt`；本行不写预期退出码）`—` 该运行暴露的无关失败要按名字写进 Evidence index；看到红却不报，等于用省略伪造记录。

### Review focus

The spec implies inputs and failure modes that no acceptance check above exercises. Name the ones most likely to bite a user of this leaf, most likely first, each with the check that pins it — add that check to Positive or Negative behavior, or record here why it cannot run:

- `空目录或首次 init：init_project.py 必须建出整套工作集，且 --add-missing 不覆盖已有文件` `—` 检查：本仓实跑后工作集成员数从 0 变为 `.charter/evidence/inventory-2026-10-19.txt` 记录的数（该文件的 update rule 定义计数口径），再跑一次不减少

If none are identified, state `none identified` in one line; the declared absence is the field's value, not an omission.

### Evidence to attach

- Command or operation:
- Expected observation:
- Actual observation:
- Raw output reference:
- Coverage limitation:

A receipt asserts checkable facts: the recorded command is re-run before the receipt is
committed; a statement of fact is checkable in the same commit, or marked aspirational;
the receipt names the commit a proof describes (a guard added after the write describes
the re-run, not the write); a result boolean is named after the assertion it makes; and a
self-verification recomputes each asserted value from the originals — a check that
re-reads the field it certifies proves at most that the file was not edited, and a
tampered copy must fail it. When the measuring criteria change, the before/after
comparison runs under one ruler, with a per-item delta.

### Check discipline

A check this leaf delivers — acceptance script, gate, self-verification — answers three
questions before its result is trusted: **it reads the object under test** (a check whose
inputs come from the artifact it certifies can pass a mutated copy); **every instance is
covered** (an existence-shaped assertion is survived by the second occurrence — uncovered
instances fail the check, they are not printed); **it moves the exit code** (a printed
violation that cannot fail the run is a log line, not a gate, and a crash-caused non-zero
exit is not a verdict — the liveness test asserts the failure reason).

Delivery includes a liveness test: an injected violation goes red, and a real input shows
a non-zero match count. A check over a set of inputs also validates the set against its
baseline (a shrunken input list is indistinguishable from a real decline); "not scanned"
is registered with the reason; a claim about an external source is worded as "not found
this pass", never as "does not exist". Failures are classified: present and wrong is a
failure; not-yet-downloaded, pre-listing, or out-of-scope is pending — the exit code
reflects only failures. After changing behavior, search for what still asserts the old
one: reproduction scripts, docstrings, and summary prints.

## 6. Stop conditions and repair budget

Stop and write a decision record when:

- the goal, scope, authority, or public meaning would change;
- a required capability is unavailable;
- a predecessor is not actually closed;
- the same class of failure repeats after `2` repair attempts;
- the next fix would touch a forbidden path or effect;
- existing user changes could be overwritten.

### Rulings protocol

Everything the stop list above does not name is decided, not stalled. When the contract, the spec, and what the work actually found disagree on a point no stop condition covers, record one line in the Events table —

- `Ruling: <what was decided> — <why> — <what it costs if wrong>` —

and keep going. Deviating without a recorded Ruling is a decision made in secret; a Ruling the closure review disagrees with is one line to overturn, not a hidden fork.

- Maximum repair iterations: `2`
- WIP limit: `1`
- Escalation owner: `YG`
- Ruling: 把 `CHK14` 的落地纳入本叶 —— 为什么：`REV-CHARTER-18` 的 `NF-47` 判定「由 Review A 判」指不到任何检查项；章程自己的不变量写着「没有运行时，写在读集之外的规则等于不存在」，一条没有人被要求守的规则与不存在等价，本叶若只在 `.charter/` 里留下这句话，就是把缺口从「判据失效」搬到「门不存在」。 —— 若判断错了，代价：本叶范围由「只碰 `.charter/` 与 `docs/SELF-AUDIT.md`」扩大到两份手工模板加它们的镜像与生成物，Review A 覆盖面更大，`AC2` 的白名单与基线摘要都要重算，且这次模板改动会进入下一次发版。
- Ruling: 把 `P1-3` 的回滚纳入本叶 —— 为什么：用户直接裁定「把 P1-3 回滚回去」；`P1-3` 是我在 m00843 之后自行改判落地的条目（用户原裁决是「不做」），它新增的读集增长规则与 roadmap 的扇出引线已按令删除，删除动作必须同时改三份手工源及其镜像。 —— 若判断错了，代价：本叶范围再扩大三份手工源，`AC2` 的白名单与基线摘要第二次重算；回滚删掉的是读集体积的机械触发条件，「读集无界增长」这个缺口重新回到无人管的 `D-01`。
- Ruling: 本叶产出落成三个本地提交，并把两条「状态锁死」的验收项改写成不变量形式 —— 为什么：YG 于 m03483 明确授权按默认收尾路径执行，其中包含提交；而原叶 §4 把「提交」列为禁止、§7 写 `Merge allowed: no`，我拿到授权后先提交、再回看合同，这是先动后补的偏离，故按 Ruling 体例补记，而不是把它写成「本来如此」；同时 `AC5` 原文要求 `git rev-parse HEAD` 全等于 `d6eff20…`、`AC2` 原文要求工作区摘要等于基线 —— 这两条在提交存在的瞬间必然为红，等价于用验收项禁止收尾动作本身；改成「白名单 + 历史不被重写」后，两条都变成对最终状态成立的不变量。 —— 若判断错了，代价：`AC2` 新增的条件 ③ 把提交范围也纳入边界检查，若第三个提交碰了白名单外的路径就当场红；`AC5` 失去「HEAD 全等」这条最强的防篡改断言、只保留后代关系，任何人若在本叶内把历史改写成另一个仍含 `d6eff20` 的形态，检查发现不了。

## 7. Integration policy

- Candidate revision reference: `main` @ `d6eff20` + 本叶三个本地提交（`0bb410f` 套件侧、`5e1e6c3` 治理工作集、第三个把两条验收项改写成不变量形式并补记 §6 的 Ruling）
- Target branch or destination: `main`
- Merge allowed: `no`（只是在 `main` 上追加本地提交，没有分支合并；`local_merge` 已勾选，语义按 §4 的注：本地提交算 `local_merge`，分支合并与 push 仍禁止）
- Push / PR / deployment allowed: `no`
- Required post-integration verification: `python scripts/validate_kit.py .` 与 `git status --porcelain .charter` 复核
- Governance-record discipline: in the main worktree, stage explicit paths only — never a
  directory, `-A`, or `.`; read `git diff --cached --name-only` before every commit and
  confirm each path is one this leaf owns; a dirty or untracked count that moved without
  this task touching it is an alarm. Governance records are committed before they are at
  risk: the outgoing contract is archived to
  `.charter/evidence/<date>-<leaf>-contract-archive.md` and committed in the same session
  as its closure, before `current-task.md` is overwritten — with an incremental edit,
  never a whole-file rewrite — and a record left uncommitted in a leaf worktree dies with
  the worktree.

## 8. Execution record

### Design and plan

- Design note: 不另立设计文档；设计树见第 10 节，两个问题都已裁定
- Design interview record: `PORTABLE_FALLBACK` `—` 用 `references/design-interview.md` 的六簇清单补齐；`grill-me` 探测为 `AVAILABLE` 但未调用，理由记在 `.charter/handoff.md` 的 Capability notes
- Reuse discovery evidence reviewed: `RD-20261019-01`，`SEARCHED`/`MATCH`，`C-01` @ `d6eff20`，本地健全性检查即 `SR-01` 至 `SR-03`
- Long-task ledger: `jspace.py controller`（状态在 `.jspace/control.json`）；`.charter/` 仍是治理事实源
- First failing check (RED): 尚无代码可失败；本叶的 RED 是「`.charter/` 不存在之前，启动读集读不出任何东西」这一事实
- Minimal implementation plan:
  1. 用 `init_project.py` 建工作集，再按模板逐份填写（本步已完成，记录在此备查）
  2. 对 `project.md` 跑 `grep -n '<'`，确认只剩第 10 节的文字例子
  3. 跑 `python scripts/validate_kit.py .` 与三条投影一致性检查，把输出落进 `.charter/evidence/`

### Events

| Time | State / event | Actor | Evidence reference | Note |
|---|---|---|---|---|
| `2026-10-19T12:50Z` | `DRAFT` | `lead` | `.charter/project.md` | 初始合同；项目批准不授权本叶。 |

### Evidence index

| ID | Kind (`test / review / verification / integration`) | Candidate | Producer | Result | Raw reference |
|---|---|---|---|---|---|
| — | — | — | — | — | 尚无收据：本叶尚未执行验证，收据在第一次实跑后落成 |

Ids are scoped by this Task ID: a bare `E-01` collides across leaves. Each receipt is its own file at `.charter/records/<ID>.md`, never appended to a shared file, never overwritten; this table indexes them.

## 9. Review and closure

- Review A: `<path, reviewer, candidate, verdict, freshness: fresh-subagent | same-context (FALLBACK recorded, naming the lost independence)>` — executed by a reviewer holding no implementation context; see project.md section 7.1 and the kit's default-on policy
- Review B / fresh behavior check: `<REQUIRED with the RVB id(s) hit plus path/reviewer/freshness/verdict, or NOT_REQUIRED naming the RVB ids considered plus the bounded omission reason, or WAIVED only for a triggered review whose reviewer was unavailable and whose bounded waiver the user approved>` — the judgments come from `.charter/project.md` section 7.1; cite ids, do not re-argue them here, and do not cite a sibling leaf in place of the ids
- Readiness record: `<RDY1-RDY13 PASS with the evidence source, then one | RDY# | result | evidence | row for every item that is not a plain PASS — UNVERIFIED, a bounded waiver, or its own evidence path; cite items by number plus a short label, never by restating the checklist text>`
- Ledger reconciliation: `<execution-ledger Verified summary mirrored into Events/Evidence>` — a leaf with neither reconciliation nor a recorded `NOT_ENABLED` waiver in its Events table must not close as `PASS_CLOSED` (close `PARTIAL` with the reason instead)
- Pre-integration verification receipt: `<path, command, candidate, result>`
- Final candidate: `<revision>`
- Target-branch integration receipt: `<path or not yet>`
- Post-merge verification: `<path, command, result>`
- Unrelated failures and limitations:

Required order: `Review → Verification → target-branch integration → post-integration verification`. Do not integrate directly from Review, and do not treat pre-integration Verification as post-integration proof.

Closure status is written only after the last review or verification returns, into
every carrier at once — contract §9, the roadmap status column, the handoff active-leaf
block — never one file ahead of the review; a claim corrected in one holder is corrected
in all of them in the same commit (mark superseded lines that carry priority flags). Before a CAPABILITY/SLICE container
row closes, its planned leaves are reconciled against the roadmap's implemented
rows; a leaf ID is checked against the full roadmap table when assigned — IDs are
single-use, and "planned but never opened" is adjudicated explicitly, never left silent.

### Closure checklist

Every row carries an answer before closure is written; a row that does not apply is answered `N/A` with its reason, and no row is deleted or left blank - a blank row reads as satisfied. `CLS` ids are kit-owned and append-only: a new item appends at the end, an id never moves to different text and never disappears.

| CLS id | Question | Answer | Evidence reference |
|---|---|---|---|
| `CLS1` | Goal re-read: the charter's Goal-level claims still hold | `<answer>` | `<raw ref>` |
| `CLS2` | All four evidence layers of charter 6.1 present, none substituted | `<answer>` | `<raw ref>` |
| `CLS3` | Every finding resolved, limited, or waived, and none left only in a review | `<answer>` | `<raw ref>` |
| `CLS4` | Execution ledger reconciled, or `NOT_ENABLED` waived in Events | `<answer>` | `<raw ref>` |
| `CLS5` | Integration and post-integration verification on the integrated candidate | `<answer>` | `<raw ref>` |
| `CLS6` | Handoff promotion sweep done for every rule still binding | `<answer>` | `<raw ref>` |
| `CLS7` | Lessons layer assessed, each qualifying event distilled or explicitly judged not worth an entry | `<answer>` | `<raw ref>` |
| `CLS8` | Contract, roadmap, and handoff agree on this leaf's state in one commit | `<answer>` | `<raw ref>` |
| `CLS9` | Closure decision chosen from the five options with its reason, and every `AC` confirmed against its check | `<answer>` | `<raw ref>` |
| `CLS10` | No boundary left unchecked: check it, or carry it in `project.md` section 10 with a recheck trigger | `<answer>` | `<raw ref>` |

`CLS3` is not an absence of findings: one recorded as `ACCEPTED_WITH_LIMITATION` or `DECIDED_BACKLOG` closes only when the same commit puts it where the next session meets it without the review. `CLS9` is answered last; a blank row above it makes the closure decision premature, not optional.

### Closure decision

Choose exactly one:

- `PASS_CLOSED` — acceptance, Review, pre-integration Verification, target-branch integration, and post-integration verification are all evidenced.
- `PARTIAL` — useful result exists but a stated requirement remains open.
- `BLOCKED` — an invariant, predecessor, or safety boundary prevents continuation.
- `BLOCKED_TOOLING` — a required host capability or independent context is unavailable.
- `NEEDS_DECISION` — a human choice or new authorization is required.

- Closure date:
- Closed by:
- Next candidate (informational only): `R1.2-S1-L1`
- Next authorization: `NOT_GRANTED`

## 10. Design tree

Resolve before implementation; draft it in the section 8 design phase and mirror each adjudication into Events. The current **frontier** lists questions whose prerequisites are settled — ask only what is answerable now, with your recommended answer attached.

Format per question:

1. **Q1 `—` 第一个叶只建工作集，还是连提交一起做？**
   - Recommended: 本叶只建工作集，不把工作区里已有的未提交改动一起提交；`.charter/` 本身在章程批准后立刻单独提交（那是批准动作的一部分，不是本叶的执行产出）
   - Reason: 工作区基线见 `.charter/evidence/baseline-2026-10-19.txt`，当前差值以 `git status --porcelain` 为准；叶边界一旦跨过，就没有一次能回到干净状态的 `git revert` 单位
   - Alternative: 一并提交 `—` 代价是自举记录与修复绑定，出错只能整块回退
   - Disclosed cost: 多一个叶（多一份合同与一次审阅），换两个可独立回滚的单位

2. **Q2 `—` 章程批准与叶批准是否合并成一次？**
   - Recommended: 分开。先批准并提交 `.charter/`，再单独批准叶
   - Reason: `project.md` 第 11 节明写「项目批准不隐含叶批准」；合并会让第一个叶永久失去独立批准的证据
   - Alternative: 合并成一次 `—` 代价是叶的 `Leaf approval` 只能写成「与章程同时批准」，不再是独立事件
   - Disclosed cost: 用户要看两次；否则少一条可引用的授权证据

A round closes when every question is settled or explicitly carried forward (named owner and leaf), and an empty frontier is stated in one line. **Provider line:** record which interview method ran (`grill-me` / `grilling` / the bundled design-interview) and whether it was verified `AVAILABLE`.
