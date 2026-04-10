# apps/api/app/services

Service 目录。

规则：

- 负责业务编排和事务边界
- 不直接暴露 HTTP 语义
- `candidate_analysis_service.py` 负责 Candidate 分析能力层的内部串联，不写数据库
- `candidate_import_service.py` 负责 Candidate 真实导入、成功入库与失败清理
