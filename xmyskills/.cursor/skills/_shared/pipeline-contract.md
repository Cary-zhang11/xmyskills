# Pipeline Contract

## 阶段定义
1. Core：仅生成 p0/p1 核心用例
2. Expand：补齐 p2/p3 与专项维度
3. Audit：生成完整性检查报告

## 输入输出契约
- Input A：`{需求名}.docx`
- Output A：`{需求名}.md`
- Output B：`{需求名}测试用例-core.md`
- Output C：`{需求名}测试用例-full.md`
- Output D：`{需求名}测试用例-audit.md`

## 串行规则
- 严禁并行跳步
- 任一步失败需停止并返回修复建议

## 质量门禁
- 覆盖率 < 90% 或编号冲突：不可直接提测
- 高影响待澄清项 >= 3：高风险，建议先澄清
