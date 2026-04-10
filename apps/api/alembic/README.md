# apps/api/alembic

Alembic 迁移目录。

- `env.py`：迁移环境配置
- `script.py.mako`：revision 模板
- `versions/`：迁移版本文件

规则：

- 所有数据库结构变更通过这里管理
- 不手工改写已发布迁移的历史语义
