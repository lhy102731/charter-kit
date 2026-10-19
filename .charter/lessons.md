# Lessons

**Bounded size.** This file is in the required-start read set whenever it exists, so every
resume pays for it. Keep it at or under 64 KB. When it exceeds the bound, archive the weakest
entries (lowest hit count first, then oldest) to `.charter/lessons-archive.md` — outside the
required-start read set — and leave one pointer line per archived entry in the Archive
pointers section. Never archive an entry that a leaf cites as its defense basis or that
carries an open `GENERALIZE` candidacy; that promotion sweep mirrors the handoff archive
rule.

**One pitfall, one entry.** Before adding an entry, check whether the pitfall already has
one: a repeat hit updates that entry (hit count +1, evidence appended, defense revised)
instead of creating a duplicate. `LS-NNN` IDs are frozen, including after archival, so one
ID never names two different pitfalls. An entry whose pitfall no longer applies is marked
`RETIRED` rather than deleted, so its ID stays meaningful.

## Entries

- LS-001 | Status: ACTIVE | Hits: 6 | Source: `R1.1-S1-L1` Review（REV-CHARTER-05…11 的同族 finding）| Date: `2026-10-19`
  - Pitfall: 把一个会随事件变化的数或状态复制到多处散文里，只更新其中一处——审阅链连续多轮查到同一病灶，每次落在不同文件的不同行，而每一轮都以为这一次改对了。
  - Evidence: `.charter/records/REV-CHARTER-05.md` … `.charter/records/REV-CHARTER-10.md`（F-10 / F-15 / F-18 / F-21 / NF-01 / NF-05 / NF-09 / NF-15 同族；NF-15 是行号寻址——行号本身就是会随插行变化的数。`Hits` 记的是同一病灶被复现的次数，`Evidence` 列的是承载它的记录与 finding id，两者不必相等）
  - Next defense: 每写一句含计量词或状态词的现状断言，先问「它下一次会因为什么而变」；答得出来的，按 `project.md` 不变量「会变的事实只有一个落点」照做——计量数只落 `.charter/evidence/`，状态只落唯一投影，别处写指针。规则本体在不变量里，本条只记代价，不重复规则正文。
  - Generalize candidate: NO


- LS-002 | Status: ACTIVE | Hits: 5 | Source: `R1.1-S1-L1` Review（REV-CHARTER-05/06 的执行器、REV-CHARTER-07 与 10 的载荷抽取）| Date: `2026-10-19`
  - Pitfall: 检查器或执行器自身坏掉时会**双向伪造结论**——假红（把正确当失败）与假绿（把失败当通过）长得都像结论。成因包括：整条命令链被一个坏的 shell 桩接管（每条命令都失败，于是控制组与打红项一起被误判）、载荷抽取把下一个小节的文字并进命令（孤立复跑却是好的）、抽取规则取错反引号位置（命令里混进散文）。条数与每次的退出码逐条见 `records/REV-CHARTER-05.md`、`REV-CHARTER-06.md`、`REV-CHARTER-07.md`、`REV-CHARTER-10.md`，本节只留因果，不复制数字。
  - Evidence: `.charter/records/REV-CHARTER-05.md`、`.charter/records/REV-CHARTER-06.md`（WSL 桩）与 `.charter/records/REV-CHARTER-07.md`、`.charter/records/REV-CHARTER-10.md`（抽取）、`.charter/records/REV-CHARTER-18.md`（执行方式：多行载荷经 shell 被静默丢弃并返回 0 —— 假绿；同一棵树上换成 stdin 执行后同一条检查立刻变红）
  - Next defense: ① 每条突变实验必须有**控制组保持绿**的对照，只有红没有绿等于没跑；② 执行器写绝对路径，不靠 PATH；③ 检查载荷的抽取规则要**显式写进证据文件并可被第三方重放**——本轮定的是「每个验收项块内 check 标签恰好一次，载荷取其后第一个反引号串」；④ 一条命令孤立复跑通过、而抽取器说它是红时，先怀疑抽取器；⑤ 指针按行标签定位，不按行号。
  - Generalize candidate: NO

- LS-003 | Status: ACTIVE | Hits: 3 | Source: `R1.1-S1-L1` Review（`REV-CHARTER-14` / `REV-CHARTER-16` / `REV-CHARTER-17` 三次判准评审）| Date: `2026-10-19`
  - Pitfall: 把一条治理规则写成**散文判据**并期待它能被机检。三轮的失败形状各不相同：v2 豁免按行（一行里只要出现 id，整行的数都放过）、v3 收窄到子句（聚合词搬进无数字子句即全句豁免）、v4 再写三处硬边界（跨行聚合、括号内数字、同一句两种合法读法结论相反）。每一版都只在被点名的那几个句子上成立，换个形状即绕过；而写判据的人和被测对象是同一个人，绕过的形状他不会自己想到。
  - Evidence: `.charter/records/REV-CHARTER-16.md`（C5b / C5c / C5e 修好）、`.charter/records/REV-CHARTER-17.md`（八个自造探针五漏两假阳，并证明同一段条文在两种忠实实现下判定相反）
  - Next defense: 判据要能机检，只有当它约束的量是**闭集**（枚举、编号、状态词、文件集合）。凡约束的是「会变的量」——计数、字节、耗时、轮次——只剩两条路：① 让值只存在一个地方（证据文件），读集只写指针，这一条是人判的；② 建真正的校验器（`D-05`）。不要写第三条路：把判据写成散文然后指望下一个人更严格。
  - Generalize candidate: NO


- LS-004 | Status: ACTIVE | Hits: 1 | Source: `R1.1-S1-L1` Review（`REV-CHARTER-20`）| Date: `2026-10-19`
  - Pitfall: 一条规则**两份实现**。判据写在叶合同的验收项里（内联 `python -c`），同一条规则的另一个实现又在别处或根本不存在，于是「改一处、另一处照旧漂」，而每一处单独看都是绿的。表现是同形态的问题一轮轮被点名，每轮只修被点名的那一处。成因是修被指出的那一行比找同形态的所有位置便宜。
  - Evidence: `.charter/records/REV-CHARTER-20.md`（`NF-59` 六处取值副本、`NF-61` 兄弟量具仍裸切格、`NF-62` 存在性断言冒充实质断言、`NF-63` 声明比断言宽）
  - Next defense: 判据只允许有一个实现——叶的验收项载荷写成 `python .charter/checks.py --only <id>`，规则本体只在该脚本里；`AC8` 守抽取规则，`AC9` 守不许内联。加新规则时先加 `checks.py` 的检查函数，再在合同里引用它。
  - Generalize candidate: NO

## Archive pointers

尚无归档条目。
