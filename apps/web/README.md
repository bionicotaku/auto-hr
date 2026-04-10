# apps/web

前端应用目录。

后续将放置：

- `app/`：Next.js App Router 页面
- `components/`：组件
- `lib/`：API 与 query 封装
- `tests/`：前端测试

规则：

- 前端运行时代码放这里
- 设计文档不放这里，统一放 `docs/`
- 本地开发优先从仓库根目录执行 `./scripts/dev-web.sh`
- `./scripts/dev-web.sh` 会自动把根目录 `.env` 中的 `NEXT_PUBLIC_*` 变量注入给前端
- `./scripts/dev-web.sh` 同时会刷新 `apps/web/.env.local`
- 如果单独在 `apps/web` 内运行，也可以手动创建 `apps/web/.env.local`
