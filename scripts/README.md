# scripts

项目脚本目录。

当前已有：

- `bootstrap.sh`
- `dev.sh`
- `dev-web.sh`
- `dev-api.sh`
- `migrate-api.sh`
- `cleanup_drafts.py`
- `lint.sh`
- `format.sh`
- `test.sh`

规则：

- 根目录统一命令入口通过这里落地
- `dev.sh` 负责同时启动前端和后端
  - 前后端各自运行在独立进程组
  - 第一次 `Ctrl+C` 优雅停止两边
  - 第二次 `Ctrl+C` 强制停止残留进程
- `migrate-api.sh` 负责执行后端 Alembic 迁移
- `cleanup_drafts.py` 负责清理长时间未更新的 Job draft，默认 dry-run
