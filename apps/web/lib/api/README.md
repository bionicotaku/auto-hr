# apps/web/lib/api

前端 API 封装目录。

当前文件：

- `client.ts`：基础 `fetch` 封装、base URL、错误解析
- `types.ts`：API DTO 定义
- `jobs.ts`：Job 相关 API 调用

规则：

- 请求函数按资源拆分
- 不把所有请求堆在单一 `api.ts`

