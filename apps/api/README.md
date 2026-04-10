# apps/api

后端应用目录。

- `app/`：应用代码
- `alembic/`：数据库迁移
- `tests/`：后端测试
- `pyproject.toml`：Python 项目配置

运行约定：

- 使用仓库根目录 `./.venv`
- 常用命令：`../../.venv/bin/python -m uvicorn app.main:app --reload`
