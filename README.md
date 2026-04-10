# auto-hr

## 开发约定

本仓库所有 Python 相关命令统一通过仓库根目录虚拟环境运行，不在 `apps/api` 内单独创建虚拟环境。

- 虚拟环境路径：`./.venv`
- Python 可执行文件：`./.venv/bin/python`
- Pip 可执行文件：`./.venv/bin/pip`

常用命令示例：

```bash
./scripts/bootstrap.sh
./.venv/bin/python -V
make dev
```

开发启动入口：

- `make dev`：同时启动前端和后端
- `make dev-api`：只启动后端
- `make dev-web`：只启动前端
- `make migrate-api`：手动执行后端数据库迁移
- 如果端口被占用，启动脚本会先打印占用该端口的进程，再退出

当前约定：

- `./scripts/bootstrap.sh` 会自动安装后端 Python 依赖到 `./.venv`
- `./scripts/bootstrap.sh` 会自动执行一次后端迁移
- `./scripts/dev-api.sh` 启动前也会自动执行 `alembic upgrade head`

前端开发时，`NEXT_PUBLIC_*` 环境变量需要能被 `apps/web` 读取。当前仓库默认通过根目录 `.env` 维护，`./scripts/dev-web.sh` 会自动注入这些 `NEXT_PUBLIC_*` 变量。

如果你单独在 `apps/web` 内启动 Next，也可以改用 `apps/web/.env.local`。

当前统一约定：

- 根目录 `/.env` 是本项目运行时环境变量的唯一来源
- `./scripts/bootstrap.sh` 会先安装后端依赖，再同步前端公开环境变量并执行迁移
- `./scripts/dev-api.sh` 会先加载根目录 `/.env`
- `./scripts/dev-web.sh` 会先加载根目录 `/.env`，再把其中的 `NEXT_PUBLIC_*` 同步到 `apps/web/.env.local`
- `./scripts/bootstrap.sh`、`./scripts/lint.sh`、`./scripts/test.sh` 也会同步前端公开环境变量，保证脚本行为一致

## 文档目录

设计、架构、规范、实施类文档统一放在 [`docs/`](/Users/evan/Downloads/auto-hr/docs/README.md)。
各工程目录自己的 `README.md` 保留在目录内部，用于说明该目录职责、关键文件和局部约束。

补充约束：

- 用户界面不得展示技术实现细节，这类内容只允许留在 `docs/` 或工程目录 `README.md`
- 如果使用子 agent，统一只允许 `gpt-5.4`

- [文档索引](/Users/evan/Downloads/auto-hr/docs/README.md)
- [工程实现文档](/Users/evan/Downloads/auto-hr/docs/工程实现文档.md)
- [实施步骤文档](/Users/evan/Downloads/auto-hr/docs/实施步骤文档.md)
