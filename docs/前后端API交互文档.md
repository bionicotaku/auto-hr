# 前后端 API 交互文档

## 1. 文档目标

本文档只描述**当前代码真实实现**下的前后端 API 交互方式，重点回答：

- 前端页面会发哪些请求
- 每个请求的请求体、响应体和错误语义是什么
- 哪些请求是同步返回
- 哪些请求是“启动任务 + SSE 订阅进度”
- 页面拿到结果后如何收口到 UI 或跳转

本文档不讨论旧设计、不讨论废弃接口，也不做向后兼容说明。

---

## 2. 当前交互总览

当前项目的前后端交互分成两类：

### 2.1 直接请求

请求发出后，HTTP 响应直接返回业务结果。

当前主要包括：

- Job 创建
- Job 列表 / 详情 / 编辑页读取
- Job 普通对话
- Job 生成新版
- Job draft 删除
- Candidate 详情读取
- Candidate 状态更新 / 标签 / 备注 / 邮件草稿

### 2.2 运行任务型请求

请求发出后，HTTP 只返回一个 `run_id`；前端再用 SSE 订阅任务进度，直到完成或失败。

当前主要包括：

- Job 保存 / finalize
- Candidate 导入分析

---

## 3. 全局约定

## 3.1 API 根地址

前端统一通过 [client.ts](/Users/evan/Downloads/auto-hr/apps/web/lib/api/client.ts) 组装请求地址：

- `NEXT_PUBLIC_API_BASE_URL` 存在时，拼成完整后端地址
- 否则走相对路径

SSE 也复用同一根地址，见 [analysis-runs.ts](/Users/evan/Downloads/auto-hr/apps/web/lib/api/analysis-runs.ts)。

## 3.2 前端请求超时

前端统一超时配置在 [client.ts](/Users/evan/Downloads/auto-hr/apps/web/lib/api/client.ts)：

- `API_REQUEST_TIMEOUT_MS = 180000`

即所有普通 HTTP 请求默认等待 `180s`。

## 3.3 默认请求格式

### JSON 请求

如果 `body` 是字符串，前端自动补：

- `Accept: application/json`
- `Content-Type: application/json`

### multipart/form-data 请求

如果 `body` 是 `FormData`，前端不会手动设置 `Content-Type`，由浏览器自动带 boundary。

当前只有 Candidate 导入启动请求使用 `FormData`。

### SSE 请求

SSE 使用 `EventSource`，不走 `apiRequest`。

## 3.4 全局错误响应结构

后端统一错误结构在 [exceptions.py](/Users/evan/Downloads/auto-hr/apps/api/app/core/exceptions.py)：

```json
{
  "error": {
    "code": "domain_validation_error",
    "message": "可直接展示的错误文案",
    "details": {}
  }
}
```

前端错误解析逻辑在 [client.ts](/Users/evan/Downloads/auto-hr/apps/web/lib/api/client.ts)：

- 优先取 `error.message`
- 否则取 `message / detail / error`
- 再不行回退到 `请求失败（状态码）`

特殊情况：

- 请求超时：`请求超时，请稍后重试。`
- 网络异常：`网络连接失败，请稍后重试。`
- 请求被主动取消：`请求已取消。`

## 3.5 422 语义

请求参数校验失败时：

- 后端返回 `422`
- `message` 会尽量是首个字段级可读错误

例如：

- `description_text: Value error, description_text must not be empty.`
- `job_title: Value error, job_title must not be empty.`

---

## 4. 运行任务机制

## 4.1 启动任务

当前两个启动型接口：

- `POST /api/jobs/{job_id}/finalize-runs`
- `POST /api/jobs/{job_id}/candidate-import-runs`

统一返回 [analysis_runs.py](/Users/evan/Downloads/auto-hr/apps/api/app/schemas/analysis_runs.py) 中的 `AnalysisRunStartResponse`：

```json
{
  "run_id": "run_xxx",
  "run_type": "job_finalize",
  "status": "queued",
  "total_ai_steps": 5
}
```

## 4.2 读取任务快照

接口：

- `GET /api/analysis-runs/{run_id}`

返回：

- 当前状态
- 当前阶段
- 当前 AI 步数
- 完成结果资源
- 失败消息

当前前端主链路中，这个接口不是主要消费方式；页面更依赖 SSE。

## 4.3 SSE 事件流

接口：

- `GET /api/analysis-runs/{run_id}/events`

响应类型：

- `text/event-stream`

事件类型固定为：

- `connected`
- `progress`
- `completed`
- `failed`

SSE 事件由 [analysis_run_service.py](/Users/evan/Downloads/auto-hr/apps/api/app/services/analysis_run_service.py) 输出，前端消费逻辑在 [useAnalysisRun.ts](/Users/evan/Downloads/auto-hr/apps/web/hooks/useAnalysisRun.ts)。

## 4.4 前端运行态收口

前端通用运行态行为：

1. 调启动接口，拿到 `run_id`
2. 创建 `EventSource(/api/analysis-runs/{run_id}/events)`
3. 收到：
   - `connected`：进入运行中状态
   - `progress`：更新当前阶段和 AI 步数
   - `completed`：关闭连接并按结果资源跳转
   - `failed`：关闭连接并展示错误

当前两个页面都复用这套逻辑：

- Job edit 保存
- Candidate 导入分析

---

## 5. Job 相关交互

## 5.1 `/jobs` 岗位列表页

前端入口：

- [JobsOverview.tsx](/Users/evan/Downloads/auto-hr/apps/web/components/job/JobsOverview.tsx)

请求：

- `GET /api/jobs`

前端调用链：

- `useJobsQuery()` -> [jobs.ts](/Users/evan/Downloads/auto-hr/apps/web/lib/query/jobs.ts)
- `getJobs()` -> [jobs.ts](/Users/evan/Downloads/auto-hr/apps/web/lib/api/jobs.ts)

响应：

```json
{
  "items": [
    {
      "job_id": "job_xxx",
      "title": "...",
      "summary": "...",
      "lifecycle_status": "active",
      "candidate_count": 3,
      "updated_at": "2026-04-10T..."
    }
  ]
}
```

当前真实行为：

- 后端只返回 `active` Job
- 页面点击卡片统一进入 `/jobs/{jobId}`

失败处理：

- 页面显示错误卡
- 点击“重试”触发 `jobsQuery.refetch()`

## 5.2 `/jobs/new/from-description`

前端入口：

- [JobDescriptionDraftForm.tsx](/Users/evan/Downloads/auto-hr/apps/web/components/job/new/JobDescriptionDraftForm.tsx)

请求：

- `POST /api/jobs/from-description`

请求体：

```json
{
  "description_text": "..."
}
```

成功响应：

```json
{
  "job_id": "job_xxx",
  "lifecycle_status": "draft"
}
```

前端在 [jobs.ts](/Users/evan/Downloads/auto-hr/apps/web/lib/api/jobs.ts) 中做了一层兼容读取，最终统一成：

- `result.jobId`

成功后：

- 前端跳转 `/jobs/{jobId}/edit`

失败后：

- 保留输入内容
- 直接展示后端 `message`

## 5.3 `/jobs/new/from-form`

前端入口：

- [JobFormDraftForm.tsx](/Users/evan/Downloads/auto-hr/apps/web/components/job/new/JobFormDraftForm.tsx)

请求：

- `POST /api/jobs/from-form`

请求体：

```json
{
  "job_title": "...",
  "department": "...",
  "location": "...",
  "employment_type": "...",
  "seniority_level": "...",
  "business_context": "...",
  "requirements_summary": "..."
}
```

成功后：

- 跳转 `/jobs/{jobId}/edit`

失败后：

- 保留表单内容
- 直接展示后端 `message`

## 5.4 `/jobs/{jobId}/edit` 初始加载

前端入口：

- [JobEditWorkspace.tsx](/Users/evan/Downloads/auto-hr/apps/web/components/job/edit/JobEditWorkspace.tsx)

请求：

- `GET /api/jobs/{job_id}/edit`

用途：

- 加载当前编辑态
- 初始化本地真值

响应核心字段：

```json
{
  "id": "job_xxx",
  "lifecycle_status": "draft",
  "title": "...",
  "summary": "...",
  "description_text": "...",
  "structured_info_json": {},
  "responsibilities": ["..."],
  "skills": ["..."],
  "editor_history_summary": "...",
  "editor_recent_messages_json": [],
  "rubric_items": [
    {
      "sort_order": 1,
      "name": "...",
      "description": "...",
      "criterion_type": "weighted",
      "weight_input": 20
    }
  ]
}
```

前端加载后会转成本地受控状态：

- `title`
- `summary`
- `descriptionText`
- `structuredInfoJson`
- `responsibilitiesText`
- `skillsText`
- `rubricItems`
- `messages`

后续编辑不再自动被远端查询值覆盖。

## 5.5 Job 普通对话

前端触发：

- edit 页点击“获取建议”

请求：

- `POST /api/jobs/{job_id}/chat`

请求体：

```json
{
  "description_text": "...",
  "responsibilities": ["..."],
  "skills": ["..."],
  "rubric_items": [...],
  "recent_messages": [...],
  "user_input": "..."
}
```

成功响应：

```json
{
  "reply_text": "..."
}
```

前端行为：

- 向本地聊天区追加：
  - 用户消息
  - assistant 建议文本
- 不修改当前编辑内容

## 5.6 Job 生成新版

前端触发：

- edit 页点击“生成新版”

请求：

- `POST /api/jobs/{job_id}/agent-edit`

请求体与 chat 相同：

```json
{
  "description_text": "...",
  "responsibilities": ["..."],
  "skills": ["..."],
  "rubric_items": [...],
  "recent_messages": [...],
  "user_input": "..."
}
```

成功响应：

```json
{
  "title": "...",
  "summary": "...",
  "description_text": "...",
  "structured_info_json": {},
  "responsibilities": ["..."],
  "skills": ["..."],
  "rubric_items": [...]
}
```

前端行为：

- 直接覆盖当前本地编辑态：
  - `title`
  - `summary`
  - `description_text`
  - `structured_info_json`
  - `responsibilities`
  - `skills`
  - `rubric_items`
- 聊天区只追加一条系统化提示：
  - `已生成新版岗位定义。`

## 5.7 Job 保存 / finalize

前端触发：

- edit 页点击“保存”

请求不是直接 finalize，而是：

- `POST /api/jobs/{job_id}/finalize-runs`

请求体：

```json
{
  "description_text": "...",
  "responsibilities": ["..."],
  "skills": ["..."],
  "rubric_items": [...]
}
```

### active Job 的前端短路逻辑

如果当前编辑的是 `active` Job，前端会先比较“初始快照”和“当前快照”：

- 相同：不发请求，直接返回 `/jobs/{jobId}`
- 不同：才启动 finalize run

### 启动成功后的响应

```json
{
  "run_id": "run_xxx",
  "run_type": "job_finalize",
  "status": "queued",
  "total_ai_steps": 1 + rubric_items.length
}
```

### SSE 订阅

前端随后连接：

- `GET /api/analysis-runs/{run_id}/events`

### 运行过程

后端阶段来自 [job_finalize_run_service.py](/Users/evan/Downloads/auto-hr/apps/api/app/services/job_finalize_run_service.py)：

- `preparing`
- `finalizing_definition`
- `persisting`

AI 步进规则：

- `title_summary` 完成后，AI 步数 +1
- 每个 rubric enrichment 完成后，AI 步数再 +1

### 完成收口

收到 `completed` 事件后：

- 若 `result_resource_type === "job"`
- 前端跳转 `/jobs/{result_resource_id}`

### 失败收口

收到 `failed` 事件后：

- 保留当前编辑态
- 展示错误消息

## 5.8 draft 取消

前端触发：

- draft Job edit 页点击“取消”

请求：

- `DELETE /api/jobs/{job_id}/draft`

成功：

- 返回 `204 No Content`
- 前端跳转 `/jobs`

如果当前是 active Job：

- 不发删除请求
- 直接返回 `/jobs/{jobId}`

---

## 6. Job 详情与候选人列表交互

前端入口：

- [JobDetailWorkspace.tsx](/Users/evan/Downloads/auto-hr/apps/web/components/job/detail/JobDetailWorkspace.tsx)

当前页面会并行发两个请求。

## 6.1 读取 Job 摘要

请求：

- `GET /api/jobs/{job_id}`

响应：

```json
{
  "job_id": "job_xxx",
  "title": "...",
  "summary": "...",
  "description_text": "...",
  "lifecycle_status": "active",
  "candidate_count": 8,
  "rubric_summary": [...],
  "structured_info_summary": [...]
}
```

用于驱动：

- 顶部岗位摘要卡片

## 6.2 读取 Candidate 列表

请求：

- `GET /api/jobs/{job_id}/candidates`

查询参数：

- `sort`: `score_desc | score_asc | created_at_desc | created_at_asc`
- `status`: `all | pending | in_progress | rejected | offer_sent | hired`
- `tags`: 可重复 query 参数，按 OR 语义
- `q`: 关键词，搜索 `full_name + ai_summary`

示例：

```http
GET /api/jobs/job_123/candidates?sort=score_desc&status=all&tags=高匹配&tags=需要复核&q=java
```

响应：

```json
{
  "items": [
    {
      "candidate_id": "cand_xxx",
      "full_name": "...",
      "ai_summary": "...",
      "overall_score_percent": 84.2,
      "current_status": "in_progress",
      "tags": ["高匹配"],
      "created_at": "2026-04-10T..."
    }
  ],
  "available_tags": ["制造业经验", "管理经验", "..."]
}
```

前端行为：

- `sort / status / tags / q` 保存在页面本地状态
- 改变任一项时重新请求
- `placeholderData` 保留上一版列表，减少抖动

---

## 7. Candidate 导入页交互

前端入口：

- [CandidateImportWorkspace.tsx](/Users/evan/Downloads/auto-hr/apps/web/components/candidate/import/CandidateImportWorkspace.tsx)

## 7.1 读取导入页上下文

请求：

- `GET /api/jobs/{job_id}/candidate-import-context`

响应：

```json
{
  "job_id": "job_xxx",
  "title": "...",
  "summary": "...",
  "lifecycle_status": "active"
}
```

当前后端允许 `draft | active` 返回，但真实导入启动时只允许 `active`。

## 7.2 启动 Candidate 导入分析

请求：

- `POST /api/jobs/{job_id}/candidate-import-runs`

请求格式：

- `multipart/form-data`

字段：

- `raw_text_input`: 可选
- `files`: 可重复上传，最多 4 个 PDF

前端组装逻辑：

- 文本去首尾空格后写入 `raw_text_input`
- 每个文件逐个 append 到 `files`

启动成功响应：

```json
{
  "run_id": "run_xxx",
  "run_type": "candidate_import",
  "status": "queued",
  "total_ai_steps": 2 + job.rubric_items.length
}
```

## 7.3 Candidate 导入运行态

SSE 地址：

- `GET /api/analysis-runs/{run_id}/events`

后端阶段来自 [candidate_import_run_service.py](/Users/evan/Downloads/auto-hr/apps/api/app/services/candidate_import_run_service.py)：

- `preparing`
- `standardizing`
- `scoring`
- `summarizing`
- `persisting`

完成后：

- `result_resource_type === "candidate"`
- 前端跳转 `/candidates/{candidateId}`

失败后：

- 保留当前文本输入和已选文件
- 显示错误消息

---

## 8. Candidate 详情页交互

前端入口：

- [CandidateDetailWorkspace.tsx](/Users/evan/Downloads/auto-hr/apps/web/components/candidate/detail/CandidateDetailWorkspace.tsx)

## 8.1 读取 Candidate 详情

请求：

- `GET /api/candidates/{candidate_id}`

响应结构分成 5 大块：

```json
{
  "candidate_id": "cand_xxx",
  "job": {...},
  "raw_input": {...},
  "normalized_profile": {...},
  "rubric_results": [...],
  "supervisor_summary": {...},
  "action_context": {...}
}
```

页面据此渲染：

- 原始输入
- 标准化结果
- rubric 逐项结果
- supervisor 汇总
- 动作区

## 8.2 读取原始文件

文件 URL 不是前端拼的，而是后端在详情接口里生成：

- `file_url = /api/candidates/{candidate_id}/documents/{document_id}/file`

请求：

- `GET /api/candidates/{candidate_id}/documents/{document_id}/file`

返回：

- `FileResponse`
- `content_disposition_type = inline`

用于浏览器直接打开 PDF。

## 8.3 更新 Candidate 状态

前端入口：

- [CandidateActionPanel.tsx](/Users/evan/Downloads/auto-hr/apps/web/components/candidate/detail/CandidateActionPanel.tsx)

请求：

- `PATCH /api/candidates/{candidate_id}/status`

请求体：

```json
{
  "current_status": "in_progress"
}
```

成功后：

- 前端 `invalidateQueries(["candidate-detail", candidateId])`
- 重新拉详情页

## 8.4 添加人工标签

请求：

- `POST /api/candidates/{candidate_id}/tags`

请求体：

```json
{
  "tag_name": "需要复核"
}
```

成功后：

- 清空输入框
- 刷新 Candidate 详情

## 8.5 添加备注

请求：

- `POST /api/candidates/{candidate_id}/feedbacks`

请求体：

```json
{
  "note_text": "...",
  "author_name": "..."
}
```

成功后：

- 清空备注和署名输入
- 刷新 Candidate 详情

## 8.6 生成邮件草稿

请求：

- `POST /api/candidates/{candidate_id}/email-drafts`

请求体：

```json
{
  "draft_type": "advance"
}
```

成功后：

- 刷新 Candidate 详情
- 新草稿出现在动作区邮件草稿列表

---

## 9. 页面到接口的映射表

## 9.1 Job 页面

| 页面 | 触发动作 | 方法 | 路径 |
|---|---|---|---|
| `/jobs` | 加载岗位列表 | `GET` | `/api/jobs` |
| `/jobs/new/from-description` | 生成岗位初稿 | `POST` | `/api/jobs/from-description` |
| `/jobs/new/from-form` | 生成岗位初稿 | `POST` | `/api/jobs/from-form` |
| `/jobs/{jobId}/edit` | 加载编辑态 | `GET` | `/api/jobs/{jobId}/edit` |
| `/jobs/{jobId}/edit` | 获取建议 | `POST` | `/api/jobs/{jobId}/chat` |
| `/jobs/{jobId}/edit` | 生成新版 | `POST` | `/api/jobs/{jobId}/agent-edit` |
| `/jobs/{jobId}/edit` | 保存 | `POST` | `/api/jobs/{jobId}/finalize-runs` |
| `/jobs/{jobId}/edit` | 取消 draft | `DELETE` | `/api/jobs/{jobId}/draft` |
| `/jobs/{jobId}` | 加载岗位摘要 | `GET` | `/api/jobs/{jobId}` |
| `/jobs/{jobId}` | 加载候选人列表 | `GET` | `/api/jobs/{jobId}/candidates` |
| `/jobs/{jobId}/candidates/new` | 加载导入上下文 | `GET` | `/api/jobs/{jobId}/candidate-import-context` |
| `/jobs/{jobId}/candidates/new` | 启动候选人导入 | `POST` | `/api/jobs/{jobId}/candidate-import-runs` |

## 9.2 Candidate 页面

| 页面 | 触发动作 | 方法 | 路径 |
|---|---|---|---|
| `/candidates/{candidateId}` | 加载 Candidate 详情 | `GET` | `/api/candidates/{candidateId}` |
| `/candidates/{candidateId}` | 打开原始 PDF | `GET` | `/api/candidates/{candidateId}/documents/{documentId}/file` |
| `/candidates/{candidateId}` | 更新状态 | `PATCH` | `/api/candidates/{candidateId}/status` |
| `/candidates/{candidateId}` | 添加标签 | `POST` | `/api/candidates/{candidateId}/tags` |
| `/candidates/{candidateId}` | 添加备注 | `POST` | `/api/candidates/{candidateId}/feedbacks` |
| `/candidates/{candidateId}` | 生成邮件草稿 | `POST` | `/api/candidates/{candidateId}/email-drafts` |

## 9.3 运行任务接口

| 用途 | 方法 | 路径 |
|---|---|---|
| 读取任务快照 | `GET` | `/api/analysis-runs/{runId}` |
| 订阅任务事件 | `GET` | `/api/analysis-runs/{runId}/events` |

---

## 10. 当前实现的关键约束

1. Job 保存和 Candidate 导入都不是同步长请求返回最终结果，而是“启动 run + SSE 跟进度”。
2. edit 页本地真值优先，`GET /edit` 只负责初始化，不负责持续覆盖。
3. active Job 在 edit 页“保存”前会先比较快照；无修改时不发 finalize 请求。
4. `/jobs` 页面当前只展示 active Job，draft 不进入列表。
5. Candidate 详情页的所有动作型提交成功后，都通过 `invalidateQueries(["candidate-detail", candidateId])` 重新拉取完整详情，而不是手写局部 patch。
6. 当前前端没有全局状态库来缓存业务数据，页面主要通过 React Query + 本地状态组合完成交互。
