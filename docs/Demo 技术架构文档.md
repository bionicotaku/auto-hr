# Demo 技术架构文档

## 1. 文档目标

本文档描述当前 Demo 的技术架构真值，用于解释系统如何支撑岗位编辑、Candidate 分析和人工处理闭环。

---

## 2. 技术选型

- 前端：Next.js App Router + TypeScript + Tailwind CSS + React Query
- 后端：FastAPI + SQLAlchemy + Alembic
- 数据库：SQLite
- AI：OpenAI Responses API
- 文件：本地目录

---

## 3. 总体架构

### 3.1 前端

负责：

- 页面布局与导航
- 本地交互状态
- 请求封装
- React Query 服务端状态
- `AnalysisRun + SSE` 进度消费

### 3.2 后端

负责：

- API
- 数据库事务
- AI Workflow
- 文件落盘与文件访问
- `AnalysisRun` 状态与事件流

### 3.3 数据与文件

负责：

- SQLite 持久化业务数据
- 保存原始 PDF
- 保存 analysis run 状态与事件

---

## 4. Job 数据流

### 4.1 创建与编辑

1. 前端创建 Job draft
2. 进入编辑页
3. 获取建议或生成新版
4. 点击“保存”
5. 后端创建 `job_finalize` analysis run
6. 前端通过 `SSE` 显示进度
7. run 成功后更新 Job 当前生效内容

### 4.2 Job finalize

`job_finalize` 不是同步 finalize 调用，而是异步 analysis run。

内部包含两类 AI 工作：

- 生成最终标题与摘要
- 逐项生成 rubric 正式富化字段

进度条按真实 AI 调用步数推进，不是单步 loading。

---

## 5. Candidate 数据流

### 5.1 Candidate 分析

1. 前端提交原始文本与 PDF
2. 后端创建 `candidate_import` analysis run
3. 前端通过 `SSE` 显示进度
4. 后端依次执行：
   - 输入准备
   - Candidate 标准化
   - 资料有效性判断
   - rubric 逐项分析
   - supervisor 汇总
   - 入库与文件转正

### 5.2 Candidate 入库

Candidate 只有在以下条件满足时才入库：

- 分析链路成功
- `is_candidate_like = true`
- 存在有效姓名

`hard_requirement_overall` 与 `recommendation` 不再是入库门槛。

### 5.3 Candidate 分析结果

Candidate 分析结果包含：

- 标准化档案
- rubric 逐项结果
- supervisor 汇总结论
- 默认 AI 标签
- 人工状态与后续处理信息

不再包含：

- 旧的 5 分总分字段

---

## 6. Candidate 原始文件架构

当前原始文件链路固定为：

- 保留原始 PDF
- 不提取、不保存 PDF 文本内容
- 后端内部保留文件路径
- 前端通过文件访问接口拿到 `file_url`
- 点击后在浏览器新标签页打开原 PDF

正式文件转正时，文件名统一改为：

- `[候选人姓名]-[标号].pdf`

---

## 7. 前端状态与 URL

当前前端设计中：

- 长耗时流程统一通过 `AnalysisRun + SSE` 驱动
- Job 详情页 Candidate 列表筛选不进入 URL
- 页面内排序、状态筛选、标签筛选、搜索都属于本地状态

这样可以避免：

- 页面滚回顶部
- 输入焦点中断
- URL 驱动导致的整页刷新感
