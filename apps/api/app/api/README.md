# apps/api/app/api

API 层目录。

- `router.py`：聚合路由入口
- `deps.py`：依赖注入
- `routers/`：按资源拆分的 router 文件

规则：

- API 层只负责 HTTP 语义和响应转换
- 不在这里直接写事务和 AI 调用
