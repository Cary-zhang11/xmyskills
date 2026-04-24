# 旧结构到新结构映射

## 你原先的单技能结构
- 需求解析
- 用例生成（p0~p3）
- 完整性检查报告
- 待澄清问题管理

## 新结构映射
- `requirement-to-testcases-core`
  - 负责：需求解析 + p0/p1核心用例 + 最小待澄清清单
- `testcases-expand-coverage`
  - 负责：p2/p3、UI、浮层、网络、兼容性补全
- `testcases-audit-report`
  - 负责：覆盖率统计、维度检查、参数提取核验、审计结论

## 使用顺序
1. 先运行 core 产出 `{需求名}-core.md`
2. 再运行 expand 产出 `{需求名}-full.md`
3. 最后运行 audit 产出 `{需求名}-audit.md`
