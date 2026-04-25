# AGENTS

## 目标
在本仓库中执行“需求文档 -> 测试用例”任务时，统一遵循可追溯、可迭代、可验收的流程。

## 强制流程
1. 输入必须来自 `@xxx.docx` 或由其转换得到的 `@xxx.md`。
2. 用例必须通过 skill 生成，不允许脚本直接写 `core/full/audit`。
3. 固定产出文件：
   - `{需求名}.md`
   - `{需求名}测试用例-core.md`
   - `{需求名}测试用例-full.md`
   - `{需求名}测试用例-audit.md`
4. 先生成，再校验，再优化；未通过不得宣称完成。

## 可用 Skill
- `requirement-to-testcases-pipeline`：单次串行生成（core/full/audit）。
- `docx-skill-md-loop`：多轮循环优化（生成 -> 校验 -> 修复 -> 复跑）。
- `requirement-to-testcases-core`：仅核心用例（p0/p1）。
- `testcases-expand-coverage`：扩展用例（p2/p3 + 专项维度）。
- `testcases-audit-report`：审计报告。

## 校验规则
- 通用校验：`core/full/audit` 结构完整。
- 模板校验：仅比较 `full vs 模板`。
- 优先级：功能拆分与维度覆盖 > 编号样式。
- 编号样式差异默认可作为 warning（非阻塞），除非用户明确要求阻塞。

## 生成约束（强制）
- 禁止模板直拷贝充当 `full`。
- 禁止临时脚本（python/ps1/bash）直接覆盖 `core/full/audit`。
- 每轮必须重新生成产物，禁止复用上一轮文件仅做校验。

## 迭代建议
- 默认先跑 1 轮验证链路，再按用户要求跑 3 轮。
- 每轮记录：
  - 本轮输入
  - 校验命令
  - 失败项/提示项
  - 下轮修复动作

## 推荐命令
```powershell
powershell -ExecutionPolicy Bypass -File "run_pipeline.ps1" "D:/path/需求.docx" -TemplatePath "D:/path/需求测试用例-模板.md" -MaxRounds 3
```

