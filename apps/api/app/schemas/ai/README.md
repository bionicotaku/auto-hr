# apps/api/app/schemas/ai

AI 结构化输出 schema 目录。

规则：

- 所有可落库 AI 输出都要先经过这里定义的严格 schema
- `job_definition.py`：Job 创建、编辑、定稿 schema
- `candidate_standardization.py`：Candidate 标准化 schema 与内部准备输入结构
- `candidate_rubric_result.py`：Candidate rubric 逐项评分结果 schema
- `candidate_supervisor.py`：Candidate supervisor 汇总 schema
