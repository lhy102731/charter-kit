# REV-CHARTER-18 —— 章程级独立审阅（审阅结论与处置记录）

## Review identity

- Review id: `REV-CHARTER-18`
- 审阅者：fresh-context subagent `b8ebb8ad-32c6-42a3-a595-4ddc3020c56b`（只读，cwd = 仓库根）
- 对象：`.charter/` 的六件启动读集、`docs/SELF-AUDIT.md` 第 9.10 节、`portable/templates/review.md` 与 `portable/references/contract-migrations.md` 的检查清单
- Verdict：`REQUEST_CHANGES`

## Independence declaration

审阅者在仓外同级目录 `outputs/charter-kit/_rev18` 建了全量副本（`COPY` / `COPY2`），所有写盘动作（validate、五条 AC、全量 pytest、E1 / E4 探针）都在副本内执行；收尾用 `diff -r --brief` 自证零差异（两侧非缓存文件均 517，全树 549）。开工与收尾的三对锚点相同：`git status --porcelain` 79 行、`git ls-files -s` 332 行、HEAD 未变。

## Verdict 与主判定

`REQUEST_CHANGES`。审阅者对主问题（「这次撤回是收敛还是把问题藏起来」）的判词：**收敛了一半**。

- 是收敛的一半：v4 判定程序整段删净，读集里没有仍生效的悬空引用；`D-08` 写明「已撤回扫描器路线」而没有写成已解决；`LS-003` 是一次真正的抽象升级，不构成重复造条。
- 没收敛的一半：读集说「由 Review A 判」，而 `portable/templates/review.md` 的 `CHK1`–`CHK13` 没有一项覆盖这件事——**把缺口从「判据失效」搬到了「门不存在」**。
- 撤回过程中新增的产物级缺陷两处：`D-07` / `D-08` 行各 6 格而表头 5 格（渲染后 State 列变成 `YG`）；`E1 计数器自属` 豁免随 v4 一并消失，使 `lessons.md` 的 `Hits` 成为规则明文禁止却在使用的活副本。

## Findings 与处置（NF-46 到 NF-54）

| id | 严重度 | 审阅者判定 | 本轮处置 | 如何在产物里验证（命令 + 期望输出） |
|---|---|---|---|---|
| `NF-46` | P1 | `project.md` 第 10 节 `D-07` / `D-08` 各 6 格 vs 表头 5 格，GFM 截断后 State 列成 `YG` | 两行重写为 5 格；`D-07` 的 settle 格改成结算条件，已采证据移进 `evidence/probes-2026-10-19.txt`；并新开验收项 `AC6` 机检列数 | `AC6` 在真树上 exit 0；给任一行多加一格后 **只有 AC6 变红**（本轮实测 M1） |
| `NF-47` | P1 | 「由 Review A 判」指不到任何检查项 | `review.md` 新增 `CHK14`（读集只写指针 / 会变状态只在声明投影 / 例外逐项列名带依据），`contract-migrations.md` 的 Checks 表加行，`project.md` 第 4 节 `INDEPENDENT_REVIEW` 行与不变量末句点名 | 三个文件各至少一次命中：`review.md` 1、`contract-migrations.md` 1、`project.md` 4 |
| `NF-48` | P2 | `Hits` 失去豁免却在读集使用，而 `handoff` 又宣布它是权威 | 不变量补「计数器自属」段与「边界」（规则参数与结构常量不算计量副本） | 带数字的 `Hits` 只出现在 `.charter/lessons.md`（3 条），其余读集文件 0 |
| `NF-49` | P2 | 投影清单与实际投影不符，`handoff` 有第 4 份 gate 副本且不在 AC3 断言内 | 第 2 节投影清单改为实际集合并声明 `handoff` 不持有取值；`handoff` 的 gate 与 pytest 两行改指针 | `handoff.md` 里 `PENDING` / `COMPLETE` / `BLOCKED_TOOLING` 命中数均为 0，且有一句「门状态与 freshness 一律读 …」 |
| `NF-50` | P2 | `D-07` 的 settle 格写的是已采证据，而图例要求写「什么证据会结算它」 | settle 格改为结算条件（下游校验器原型能对 inventory 的四条 glob 返回非 0；或 D-05 裁不建时转 `DECIDED` 并带接受限度与到期日） | `D-07` 的 settle 格不含「已采证据」「仍全绿」；探针重放记录只出现在 `probes-2026-10-19.txt`（replay 行 4 条） |
| `NF-51` | P3 | `D-05` / `D-07` / `D-08` 不互斥，后两者结算都归到 D-05 | 两行各写明「D-05 裁不建时本行转 `DECIDED` 的接受限度」 | 第 10 节里点名 `D-05` 的行只有 D-05 自身与 D-07 / D-08（D-07 命中 1、D-08 命中 2） |
| `NF-52` | P3 | 处置纪律只要求「命令 + 期望输出」，没要求「属性为假时必须失败」 | 纪律末句补「验证命令必须在属性为假时返回非 0 或空输出，并断言结构（格数、列位、计数）而不是子串」 | `project.md` 命中该句 1 次；「写不出的当场改判」1 次 |
| `NF-53` | P3 | `REV-CHARTER-17` 处置表两处命令含未转义竖线，行被切成 5 格 | 转义为 `|`（**只改渲染，不改断言内容**；原行内容与期望输出一字未动） | 该表每行按未转义竖线切分后格数恒为 3（表头 3 格） |
| `NF-54` | P3 | 读集活副本实测 4 处 | 四处分别落位：`Hits` → NF-48 的计数器自属；`handoff` 的 gate 第 4 副本 → 删除改指针；`handoff` 的「pytest → 全绿」→ 改指针；`reuse-discovery` 的「连续 3 条查询」→ 属第 2 节「边界」里的规则参数，明确不在约束内 | `handoff` 无 gate 取值；`pytest` 结果行只写证据落点；「连续 3 条查询」只在 `reuse-discovery.md` 出现 1 次 |

## 本轮暴露的新缺陷类型：执行方式造成的假绿

处置过程中发现一个此前八轮都没抓到的漏洞，而且它在**伪造结论**，方向与 `LS-002` 已记的假红相反：

- 用 `subprocess.run(payload, shell=True)` 执行多行 `python -c "…"` 载荷时，Windows 上 shell 解到 `cmd.exe`，多行载荷被**静默丢弃**，stdout / stderr 全空而返回码是 **0**。实测：单行载荷正常输出；多行载荷（无论 `sys.exit(0)` 还是 `sys.exit(3)`）一律 rc = 0 且无输出。
- 后果：此前用该方式跑的验收项「全 exit 0」是**假绿**——`AC1` / `AC2` / `AC3` / `AC6` 的载荷都是多行的。
- 修法：`python -c "…"` 形状的载荷改为 `subprocess.run([sys.executable, "-"], input=code)` 走 stdin；其余形状仍走 shell。改后 `AC6` 立刻打印出真实表头与逐行格数。
- 记入 `lessons.md`：`LS-002` 命中数 4 → 5，Evidence 追加本轮，Next defense 写明「多行载荷必须走 stdin」；`handoff.md` 的验收项抽取规则也补了同一句（执行方式同样是规则的一部分）。

## 活性矩阵（每条突变施加后立即还原，还原后 tree 逐字节相同）

| 突变 | 期望 | 实测 |
|---|---|---|
| baseline（无突变） | 六条全 0 | 全 0 |
| M1 第 10 节 D-01 行多一格 | 只 AC6 红 | **只有 AC6 = 1** |
| M2 叶 Status `DRAFT` → `PASS_CLOSED` | 只 AC1 红 | 只有 AC1 = 1 |
| M3 roadmap gate `PENDING` → `COMPLETE` | 只 AC3 红 | 只有 AC3 = 1 |
| M4 新建 `docs/other-probe.md` | 只 AC2 红 | 只有 AC2 = 1 |
| M5（控制组）新建 `.charter/probe-allowed.md` | 必须全绿 | 全 0 |
| M6 给 `portable/templates/review.md` 追加换行（镜像破坏） | 只 AC4 红 | 只有 AC4 = 1 |
| M7 把 AC5 检查里的完整 SHA 换成 `deadbeef` | 只 AC5 红 | 只有 AC5 = 1 |
| 还原后 | 六条全 0 | 全 0 |

附注：M1 在旧执行方式（shell 传多行载荷）下得 0——同一条检查、同一棵树，两种执行方式结论相反。这是本轮第二个实证：**执行器坏掉时两个方向都会伪造结论**。

## 范围扩大（Ruling，已写进叶合同第 6 节）

`NF-47` 要求改 `portable/` 模板，而本叶原范围只有 `.charter/**` 与 `docs/SELF-AUDIT.md`，因此 `AC2` 如实变红（不是误报）。处置：叶第 4 节 Allowed paths 增加 `portable/templates/review.md`、`portable/references/contract-migrations.md`、两个 target 树的镜像、`skills/charter-workflow/**` / `plugins/**` / `.codex-plugin/plugin.json`（builder 生成物）；`code_write` 括注改为「限本节 Allowed paths 列出的路径」；forbidden 行改为「改上列之外任何 `portable/` 文件、根 `DEVELOPMENT_CHARTER.md`…」；第 6 节记 Ruling 一行。

为什么：一条没有人被要求守的规则与不存在等价。判断错了的代价：范围扩大、Review A 覆盖面变大、`AC2` 白名单与基线摘要都要重算、改动会进入下一次发版。

基线因此重新生成：`.charter/evidence/baseline-2026-10-19.txt` 首行注明按新 Ruling 重新基线，`# diff-sha256: 3483dd379a600563…`，`git diff` 的排除表扩到与 Allowed paths 一致；仍然 79 行（77 `M` + 2 `??`）。

## 机械核对（本轮实测）

| 项 | 结果 |
|---|---|
| `python scripts/validate_kit.py .` | exit 0，首行 `Charter Kit validation: PASS (246 files checked)` |
| `python -m pytest tests -q` | 298 passed, 519 subtests（145.14s） |
| 六条验收项（stdin 执行） | AC1–AC6 全 exit 0 |
| 镜像与生成物 | 两个 target 树已 cp，三个 builder `--sync` 已跑 |
| 工作区 | `git status --porcelain` 79 行 |
| HEAD | `d6eff20240adbcce327ca7cffe27053a6df6bd02` |

## 明确未验

1. 本轮没有独立审阅者的第二次复核（这要等 `REV-CHARTER-19`）。
2. `CHK1`–`CHK13` 没有逐条整表勾选，只核了与 NF-46…NF-54 相关的那几条。
3. 全量 pytest 只跑一次；`REV-CHARTER-18` 自己的 144.92s 与本轮 145.14s 的差异未追查。
4. `REV-CHARTER-01`–`REV-CHARTER-17` 的历史记录实质未重验。
5. 未在当前阶段实跑 `init_project.py --add-missing` 的生成物；inventory 的四条 glob 只做了重算。

## Re-review trigger

本条记录**不自批准**。`D-08` 的处置是「把人工门指名到 `CHK14`」，它是否真的有人守、`AC6` 是否真的会红、`REV-CHARTER-17` 的表格渲染是否已修好，都需要 fresh 上下文的 `REV-CHARTER-19` 复核。在 `REV-CHARTER-19` 给出 `APPROVE` 之前，章程不得批准，叶不得离开 `DRAFT`。