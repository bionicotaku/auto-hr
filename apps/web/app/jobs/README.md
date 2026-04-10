# apps/web/app/jobs

Job 相关路由目录。

当前职责：

- `/jobs`：Job 工作台与岗位列表入口
- `/jobs/new`：新建入口选择页
- `/jobs/new/from-description`：已有描述导入页
- `/jobs/new/from-form`：基础信息生成页
- `/jobs/[jobId]`：Job 详情与 Candidate 列表页
- `/jobs/[jobId]/edit`：draft 承接占位页

规则：

- 这里只放路由页面，不放复杂业务逻辑
- 业务逻辑继续下沉到 `components/job/` 和 `lib/`
