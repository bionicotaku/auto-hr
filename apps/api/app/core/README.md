# apps/api/app/core

后端基础设施目录。

- `config.py`：环境配置
- `db.py`：数据库连接与 session
- `logging.py`：日志初始化
- `exceptions.py`：统一异常结构

规则：

- 这里定义全局基础约束
- 关键语义文件不应被随意改动
