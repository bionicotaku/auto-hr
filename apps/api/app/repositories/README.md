# apps/api/app/repositories

Repository 目录。

规则：

- 只负责数据库读写
- 不写业务判断和 AI 调用
- `candidate_repository.py` 负责 Candidate 全量入库读写
