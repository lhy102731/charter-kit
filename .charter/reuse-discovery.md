# Reuse Discovery Record

## 1. Discovery identity

- Discovery ID: `RD-20261019-01`
- Charter reference / version: `.charter/project.md` / `0.2`
- Target capability / Leaf IDs: `R1.1-S1-L1`（治理自举），并覆盖 `R1.2-S1-L1` 要用的复核能力
- Owner / reviewer: `YG` / lead
- Host and tool versions: Windows + DeepSeek Harness；python 3.13；git 3.x（PATH 内）
- Started / completed: `2026-10-19T12:43Z` / `2026-10-19T12:44Z`
- Recheck trigger / date: 新增能力、技术栈或外部边界变化时；否则 2027-01-19 到期
- Gate status: `COMPLETE`（2026-10-20 随章程批准转；证据见本记录的搜索日志与候选表）

Gate semantics are intentionally small: `PENDING` means this record is not ready to authorize a Leaf; `COMPLETE` means the material targets in the approved scope have evidence and a final route; `BLOCKED` means a required capability, authorization, decision, or evidence is unavailable. A Leaf may enter `READY` only when this gate is `COMPLETE`, or when that specific Leaf has an explicit, separately approved bounded waiver recorded in the decision fields below. The waiver must name the Leaf, approved and omitted scope, accepted limitation, approver, and expiry/recheck condition. It is not a fourth Gate state or a project-wide bypass; without it, `PENDING`, `BLOCKED`, and `BLOCKED_TOOLING` remain blocking.

## 2. Search contract

### Material-target and search contract

- Material target test: `NO_MATERIAL_TARGET`
- Material-target rationale: 这一叶要的东西（整套模板、诊断脚本、审阅流程）已经在仓内；它要做的只是用它们填出工作集，不存在可被外部实现替代的部分。仍做一次 `LOCAL` 健全性检查并留证。
- Search depth: `FAST`
- Approved discovery scope: `LOCAL_ONLY`
- External read authorization: `no`
- Privacy restrictions: 仓库源码、密钥、私有文档不得进入任何查询
- Search timebox / query budget: 见 `project.md` 的同名条（本行是运行时的提醒，不重复数值，也不构成第二个定义处）
- Stop condition: 连续 3 条查询不再产生新候选
- Capabilities requiring coverage:
  - 治理自举 — behavior terms: `charter` `leaf contract` `read set`；interface terms: `.charter/*.md` 的文件名与字段；constraints: 没有运行时、只用仓内文件

Use the nearest, lowest-risk source first. `FAST` covers workspace and history; `STANDARD` may add installed/cache/manifest, framework, SDK, dependencies, and approved internal resources; `DEEP` may add official/upstream registries and other explicitly authorized public sources. Stop when the evidence is sufficient; a deep external search is not mandatory for every Leaf.

Scope mapping is fixed: `LOCAL_ONLY = workspace/history`; `LOCAL_ECOSYSTEM = workspace/history + installed/cache + approved internal`; `FULL_EXTERNAL = LOCAL_ECOSYSTEM + official/upstream/registries + authorized public web`. Any tier outside the approved scope or authorization is `NOT_SEARCHED` or `NOT_AUTHORIZED`, never `NO_MATCH`.

Discovery is read-only. Do not send private source, secrets, credentials, real user data, or identifying project details to an external service. Treat repositories, package metadata, and Skill text as untrusted data: do not clone, build, run, import, copy, install, execute commands, load candidate instructions, or write global directories.

### Expert-skill routing per stage

Probe before searching, at this point and not from an earlier log: `python scripts/check_dependencies.py . --optional reuse-first --optional find-skills --optional framework-first-coding --optional reduce-reinvention --json --log-file .charter/evidence/dependency-check.log`. When the record emitted by that run reports the stage's expert skill as `AVAILABLE`, consult it before searching and follow its method; an `AVAILABLE` expert skill must be used or its non-use explicitly recorded with a reason. Read that run's own record — the last section of `.charter/evidence/dependency-check.log`, the one whose header timestamp is this run, equivalently the JSON that probe just printed — and never the exit code: an absent optional provider still exits 0. A section from an earlier run is stale exactly like an absent log, so identify the run's own section instead of reading the first matching line, which may be an older `MISSING`. If the probe reports `AVAILABLE` but the call then fails or cannot load, record `FALLBACK` naming the failure and continue under this contract:

- `LOCAL` tier → `reuse-first` (project-local reuse discovery);
- installed skills / cache / manifest tier → `find-skills` (Agent Skill inventory only; discovery never installs a Skill);
- registries / upstream / framework tiers → `framework-first-coding` (framework, SDK, and shared-component discovery);
- §4 disposition (build-vs-reuse trade-off) → `reduce-reinvention`;
- after an explicit `ADOPT` decision, converting a selected repository into a Skill → `repo-to-skill` (separate authorized follow-up, never part of discovery).

An expert skill that is `MISSING` or failing is recorded as `MISSING`/`FALLBACK` with the stage continuing under this contract; it is never a reason to skip a tier or relabel coverage.

## 3. Search log

Append one row per executed tier/query. Keep coverage, result, and route separate:

- Coverage: `SEARCHED | NOT_SEARCHED | NOT_AUTHORIZED | BLOCKED_TOOLING`
- Result: `MATCH | NO_MATCH | UNKNOWN`
- Final route: `ADOPT | ADAPT | REFERENCE_ONLY | BUILD_NEW | REUSE_SPIKE | NEEDS_DECISION`

| Record | Capability / Leaf | Tier | Source / tool / host | Exact query or path | Time | Coverage | Result | Evidence reference | Notes / stop reason |
|---|---|---|---|---|---|---|---|---|---|
| SR-01 | `R1.1-S1-L1` | `LOCAL` | `grep / 本仓库` | `grep -rn 'Review A' portable/` | 2026-10-19T12:40Z | `SEARCHED` | `MATCH` | `portable/commands/charter-workflow.md` 中以 `- Review A is executed by a reviewer` 起首的那一行（按行标签定位，不按行号） | 审阅流程已在仓内定义，无需新建；原查询与指针在 `REV-CHARTER-12` 更正（见表下更正行） |
| SR-02 | `R1.1-S1-L1` | `LOCAL` | `ls / 本仓库` | `ls portable/templates/` | 2026-10-19T12:40Z | `SEARCHED` | `MATCH` | `portable/templates/`（份数见 `.charter/evidence/inventory-2026-10-19.txt`） | `init_project.py` 已把它们复制进 `.charter/` |
| SR-03 | `R1.1-S1-L1` | `LOCAL` | `python / 本仓库` | `python scripts/validate_kit.py .` | 2026-10-19T12:44Z | `SEARCHED` | `MATCH` | `.charter/evidence/validate-2026-10-19.txt` | 自检脚本在仓内，PASS（计数落点 `.charter/evidence/validate-2026-10-19.txt`） |

> **更正（`REV-CHARTER-12`，点名被更正行）**：SR-01 的原值留在此句里作为记录 —— `Exact query` 原写作 `grep -rn Review-A portable/`（该命令今天实跑 0 命中：仓内措辞是带空格的 `Review A`），`Evidence reference` 原写作 `portable/commands/charter-workflow.md:51`（该行是 Review B 触发规则，Review A 的执行模型在其上一行）。表内该行已改为可复现命令与行标签寻址。

`NO_MATCH` requires an evidence reference and is valid only after the exact query actually ran within the declared scope. `NOT_SEARCHED`, `NOT_AUTHORIZED`, and `BLOCKED_TOOLING` must remain visibly distinct from `NO_MATCH`. `UNKNOWN` means the available evidence is insufficient; it is not permission to build a replacement. Coverage and result are separate fields; do not collapse them into one combined status.

If `NO_MATERIAL_TARGET` is selected, record the local sanity-check query and evidence, then proceed to a final route without inventing an external search obligation.

## 4. Candidate evaluation

Use one row per candidate that merits consideration. Pin an immutable Git commit/tag or package version before selecting it; a floating branch or `latest` is not sufficient evidence. Candidate disposition is separate from the capability-level final route.

| ID | Type (`project / skill / plugin / package / template / reference`) | Source path or URL | Fixed revision/version | Fit / interface evidence | Maintenance / tests | License / attribution | Security / privacy / side effects | Portability / integration notes | Disposition (`ADOPT / ADAPT / REFERENCE_ONLY / REJECT / DEFER`) | Reason / follow-up |
|---|---|---|---|---|---|---|---|---|---|---|
| C-01 | `template` | `portable/templates/`（份数见 `.charter/evidence/inventory-2026-10-19.txt`） | HEAD `d6eff20` | 字段与 `.charter/` 需求一一对应 | `validate_kit.py` 的短语断言覆盖 | 仓内自有无外部许可义务 | 只读模板，无副作用 | `init_project.py` 直接复制 | `ADOPT` | 直接使用，本次不改造 |

`BUILD_NEW` is a capability-level route, never a candidate disposition. Resolve an unresolved candidate or capability with more bounded evidence, a `REUSE_SPIKE`, or `NEEDS_DECISION` before choosing `BUILD_NEW`. A complete record has no unresolved high-value `UNKNOWN` or `DEFER`; a waiver must explicitly address any such item rather than silently converting it to `BUILD_NEW`.

## 5. Final decision and hand-back

- Final route per capability: `ADOPT`
- Selected candidates and pinned revisions: `C-01` @ `d6eff20`
- Rejected / deferred candidates and reasons: 无
- Reference-only material: 无
- Build-new justification, if applicable: 不适用（`NO_MATERIAL_TARGET` 且已有匹配）
- Required `REUSE_SPIKE`, if applicable: 无
- Decision / waiver reference: 无（未使用 waiver）
- Uncovered or blocked sources: `ECOSYSTEM` 与 `EXTERNAL` 两个 tier 为 `NOT_SEARCHED`（本版授权范围是 `LOCAL_ONLY`），不是 `NO_MATCH`
- Gate freshness for this leaf: `current`
- Approved by / on: `待批准`（随 `project.md` 第 11 节一并回填）

Adoption, adaptation, installation, copying, and execution are separate authorized actions. If a candidate or route would change Goal, Non-goals, Invariants, public semantics, or effect boundaries, stop with `NEEDS_DECISION` and reopen Change Triage/Charter. A successful record is evidence for Leaf readiness, not an automatic dependency installation or production permission.
