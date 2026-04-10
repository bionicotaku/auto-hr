# scripts

项目脚本目录。

当前已有：

- `bootstrap.sh`
- `dev.sh`
- `dev-web.sh`
- `dev-api.sh`
- `migrate-api.sh`
- `lint.sh`
- `format.sh`
- `test.sh`

规则：

- 根目录统一命令入口通过这里落地
- `dev.sh` 负责同时启动前端和后端
- `migrate-api.sh` 负责执行后端 Alembic 迁移
