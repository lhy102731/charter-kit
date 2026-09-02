# Charter Kit v1 发布验证收据

日期：2026-09-03（最终复核）
候选分支：`codex/charter-kit-v1`
验证范围：Portable Core、Charter/模板、工作流 Skill、Codex 适配与发行包

## 结论

`PASS`（Portable Core 与 Codex 目标）。当前仓库唯一有真实安装和启动 smoke-test 证据的 Harness 是 Codex。DSH 文件仍作为未来适配开发材料保留，只完成结构一致性检查，状态为 `experimental / unverified`，不构成安装或运行时支持承诺。

## Review A：合同与范围审阅

- 审阅人/上下文：独立审阅代理 `review_fix_check`，只读检查最终工作树。
- 范围：Context Router、Change Triage、Leaf 状态、Reuse Gate 字段语义、工作集职责、发行包自足性和个人领域去耦合。
- 结果：发现的术语漂移、入口路由、镜像同步、状态命名、`UNKNOWN` 语义、Verification 顺序、工作集分类、README 路径和 Resume 顺序问题均已在 canonical 文件及生成镜像中统一；未留下阻塞项。

## Review B：新鲜上下文行为审阅

- 审阅人/上下文：独立新鲜审阅代理 `final_review_retry`。
- 结果：`final_review_retry` 返回 `PASS`；最终镜像字节一致；Reuse Gate 为 `PENDING | COMPLETE | BLOCKED`，Coverage/Result/Final route 分离；`UNKNOWN`、未授权和工具阻塞不会被写成 `NO_MATCH`；DSH 仅作实验性结构检查。
- 限制：本收据不把结构测试当作 DSH 宿主 smoke；Codex smoke 证据单独记录如下。

## 可重查验证命令

以下命令均在最终工作树执行：

| 检查 | 实际结果 |
|---|---|
| `python -m pytest -q` | `124 passed, 143 subtests passed in 55.67s` |
| `python -B -m unittest discover -s tests -p "test_*.py" -q` | `Ran 124 tests in 57.493s ... OK` |
| `python scripts/validate_kit.py .` | `PASS (155 files checked)` |
| `python scripts/build_codex_plugin.py --check` | `PASS` |
| `python scripts/build_dsh_plugin.py --check` | `PASS (experimental / unverified structural check)` |
| `python .../validate_plugin.py plugins\\charter-kit` | `Plugin validation passed` |
| `python -X utf8 .../quick_validate.py`（canonical、Codex target、发行包各一次） | `Skill is valid!` |
| `git diff --check` | 退出码 `0`（仅换行格式提示） |

## Codex 宿主 smoke

- 本机插件列表观察：`charter-kit@personal` 为 `installed, enabled`，版本 `0.2.0+codex.20260902153901`。
- 新 Codex CLI 进程只读加载检查返回：

  ```text
  AVAILABLE C:/Users/Administrator/.codex/plugins/cache/personal/charter-kit/0.2.0+codex.20260902153901/skills/charter-workflow/SKILL.md
  ```

- 官方 Codex 本地插件校验器通过。

## 边界与未纳入项

- 不自动安装第三方 Skill、插件、依赖、Harness 或服务。
- 不建立跨 Agent/跨 Harness 通信、中央服务或共享运行时。
- `$null` 是历史 DSH 探测产生的未跟踪临时文件，未纳入发布提交；除非维护者另行决定，不应把它当作产品文件。
- DSH 的构建器和发行目录只证明文件结构可生成，不证明 DSH 命令注册、安装或运行时行为。
