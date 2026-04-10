# apps/api/app/schemas/ai

AI 结构化输出 schema 目录。

规则：

- 所有可落库 AI 输出都要先经过这里定义的严格 schema
- `job_definition.py`：Job 创建、编辑、定稿 schema
- `candidate_standardization.py`：Candidate 标准化 schema 与内部准备输入结构
