---
name: requirement-to-testcases-pipeline
description: 一次性执行从需求docx到测试用例与审计报告的全流程编排。用于用户希望自动按顺序完成文档解析、核心用例生成、扩展覆盖补全和完整性审计的场景。
---

# Requirement To Testcases Pipeline

## 目标
单次触发，自动串行执行：
1. docx 转 md
2. 核心用例（p0/p1）
3. 扩展用例（p2/p3）
4. 审计报告

## 输入
- `@xxx.docx`（必需）
- 可选：`@xxx.md`（若已存在可复用）
- 可选：`@xxx-模板.md`（用于 full 与模板对齐验收）

## 自动执行模式（强制）
- 收到 `@xxx.docx` 后，必须由 agent 主动执行脚本，不要求用户手动运行命令
- 默认命令：`python "d:/cursor_workspace/xmyskills/docx_to_md.py" "<docx绝对路径>" "<md绝对路径>"`（若仓库根路径不同，改为 `<仓库根>/xmyskills/docx_to_md.py`）
- 若传入的是 `@xxx.md` 且结构完整，可跳过转换步骤

## 输出文件（强制）
- `{需求名}.md`
- `{需求名}测试用例-core.md`
- `{需求名}测试用例-full.md`
- `{需求名}测试用例-audit.md`

## 执行顺序（强制）
1. 判断输入类型：
   - 传入 `@xxx.docx`：先执行脚本转换为 `md`
   - 传入 `@xxx.md`：直接进入第2步
2. 按 `requirement-to-testcases-core` 规则生成 `core.md`
3. 按 `testcases-expand-coverage` 规则生成 `full.md`
4. 按 `testcases-audit-report` 规则生成 `audit.md`
5. 若提供模板：执行 `full vs 模板` 对比校验并输出差异清单

## 编排约束
- 必须串行，不可并行跳步
- 每一步完成后再进入下一步
- 任何一步失败，输出失败原因和修复建议
- 禁止把“请先手动运行脚本”作为默认回复

## 产出格式
- 用例文档保持 XMind 友好 Markdown 层级
- 审计报告必须含覆盖率、维度检查、参数提取、风险结论

## 模板对齐模式（可选）
- 仅对 `full.md` 与模板做结构/维度优先对齐
- `core.md` 与 `audit.md` 仍遵循通用契约，不参与模板强比对
- 标题覆盖率门槛（通用 QA 口径）：`##` >= 85%，`###` >= 80%
- 维度覆盖门槛（通用 QA 口径）：关键测试维度（UI/浮层/网络/兼容）覆盖率 >= 80%
- 编号风格差异默认记为 warning，不作为阻塞项


## 引用规范
- core 规则参考：`../requirement-to-testcases-core/SKILL.md`
- expand 规则参考：`../testcases-expand-coverage/SKILL.md`
- audit 规则参考：`../testcases-audit-report/SKILL.md`
- 公共风格约束：`../_shared/testcase-style.md`
- 编排契约：`../_shared/pipeline-contract.md`
