# Auto HR

Auto HR 是一个面向招聘后处理链路的全栈 Demo。  
它不负责职位发布和候选人抓取，而是聚焦这条闭环：

**岗位创建与编辑 → 岗位保存定稿 → Candidate 分析 → Candidate 展示 → 状态、标签、备注与邮件草稿**

当前仓库已经完成主业务闭环，适合用于：

- 本地演示
- 产品/设计对齐
- 工程实现参考
- 后续功能扩展

## 当前能力

### 岗位

- 从已有描述创建岗位初稿
- 从基础信息创建岗位初稿
- 在统一编辑页维护：
  - 标题
  - 摘要
  - 职位描述
  - responsibilities
  - skills
  - rubric 评估项
- AI 获取建议
- AI 生成新版
- 通过异步 analysis run 保存岗位定稿

### Candidate

- 提交原始文本和 PDF
- 异步执行 Candidate 分析
- 标准化 Candidate 档案
- 按岗位 rubric 做逐项分析
- supervisor 汇总结论、标签和推荐
- 展示 Candidate 详情：
  - 标准化信息
  - 原始输入
  - 汇总结论
  - 逐项分析
  - 处理状态
- 支持：
  - 更新状态
  - 添加人工标签
  - 添加备注
  - 生成邮件草稿

## 当前产品语义

### Job

- `/jobs` 只展示已生效岗位，不展示 `draft`
- 新建岗位首次生成后先创建 `draft`
- 点击“保存”不会直接同步入库，而是启动一次 `job_finalize` analysis run
- 已生效岗位再次编辑时：
  - 如果没有改动，保存等同直接返回详情页
  - 如果有改动，保存会重新跑一次 `job_finalize`

### Candidate

- Candidate 页面按钮文案是“分析”
- Candidate 分析走 `candidate_import` analysis run
- Candidate 只有在分析成功、资料有效、且识别出有效姓名时才入库
- `hard_requirement_overall` 和 `recommendation` 不阻断入库
- `has_fail` 会自动加 `硬性要求未通过`
- `has_borderline` 会自动加 `需要复核`

### 原始文件

- 系统保留原始 PDF
- 不提取、不保存 PDF 文本内容
- Candidate 详情页通过“查看原文件”链接在浏览器中打开 PDF
- 正式文件名格式为：`[候选人姓名]-[标号].pdf`

### 长耗时 AI 链路

所有长耗时链路统一采用：

- `AnalysisRun` 持久化状态快照
- `AnalysisRunEvent` 持久化事件流
- `SSE` 向前端推送进度
- API 进程内后台执行

当前接入的 run 类型：

- `job_finalize`
- `candidate_import`

## 技术栈

- 前端：Next.js App Router + TypeScript + Tailwind CSS + React Query
- 后端：FastAPI + SQLAlchemy 2.0 + Alembic
- 数据库：SQLite
- AI：OpenAI Responses API
- 模型：`gpt-5.4`
- 文件存储：本地目录

## 仓库结构

```text
auto-hr/
  docs/          项目级文档
  apps/web/      前端应用
  apps/api/      后端应用
  data/          SQLite、上传文件、临时目录
  scripts/       启动、迁移、测试、清理脚本
  Makefile       根命令入口
```

关键目录职责：

- `apps/web`
  - 页面、业务组件、hooks、API client、query hooks
- `apps/api`
  - 路由、service、workflow、repository、模型、迁移
- `data`
  - `app.db`
  - Candidate 原始 PDF
  - 临时导入目录
- `docs`
  - 架构、实现、数据模型、页面设计、实施步骤

## 环境要求

本地需要：

- `node`
- `pnpm`
- `python3`

所有 Python 相关命令统一通过仓库根目录虚拟环境运行：

- 虚拟环境路径：`./.venv`
- Python：`./.venv/bin/python`
- Pip：`./.venv/bin/pip`

不在 `apps/api` 内单独创建虚拟环境。

## 环境变量

根目录 `/.env` 是项目运行时环境变量的唯一来源。  
前端开发所需的 `NEXT_PUBLIC_*` 变量会由脚本自动同步到 `apps/web/.env.local`。

至少需要准备：

```bash
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-5.4
OPENAI_REASONING=medium
OPENAI_TIMEOUT_SECONDS=180
API_PORT=8000
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

可参考：

- [.env.example](/Users/evan/Downloads/auto-hr/.env.example)

## 快速开始

### 1. 初始化

```bash
./scripts/bootstrap.sh
```

这个脚本会：

- 创建 `./.venv`
- 安装后端依赖
- 安装前端依赖
- 同步前端公开环境变量
- 执行数据库迁移

### 2. 启动开发环境

```bash
make dev
```

会同时启动：

- 后端：`http://localhost:8000`
- 前端：`http://localhost:3000`

也可以分别启动：

```bash
make dev-api
make dev-web
```

### 3. 常用命令

```bash
make bootstrap
make dev
make dev-api
make dev-web
make migrate-api
make cleanup-drafts
make lint
make format
make test
```

说明：

- `make migrate-api`
  - 手动执行数据库迁移
- `make cleanup-drafts`
  - 清理长时间未更新的 Job draft
  - 默认由脚本自身控制 dry-run / apply

## 脚本行为

当前脚本约定如下：

- `./scripts/bootstrap.sh`
  - 安装依赖
  - 同步前端环境变量
  - 执行后端迁移
- `./scripts/dev-api.sh`
  - 加载根 `.env`
  - 检查端口占用
  - 自动执行 `alembic upgrade head`
  - 启动 FastAPI
- `./scripts/dev-web.sh`
  - 加载根 `.env`
  - 同步 `NEXT_PUBLIC_*`
  - 检查端口占用
  - 启动 Next.js
- `./scripts/dev.sh`
  - 同时启动前后端
  - 任一进程退出时整体退出
  - 第一次 `Ctrl+C` 时优雅停止两边
  - 第二次 `Ctrl+C` 时强制停止残留进程

## API 概览

当前关键接口包括：

### Job

- `POST /api/jobs/from-description`
- `POST /api/jobs/from-form`
- `GET /api/jobs`
- `GET /api/jobs/{job_id}`
- `GET /api/jobs/{job_id}/edit`
- `POST /api/jobs/{job_id}/chat`
- `POST /api/jobs/{job_id}/agent-edit`
- `POST /api/jobs/{job_id}/finalize-runs`
- `GET /api/jobs/{job_id}/candidate-import-context`
- `GET /api/jobs/{job_id}/candidates`
- `POST /api/jobs/{job_id}/candidate-import-runs`

### AnalysisRun

- `GET /api/analysis-runs/{run_id}`
- `GET /api/analysis-runs/{run_id}/events`

### Candidate

- `GET /api/candidates/{candidate_id}`
- `GET /api/candidates/{candidate_id}/documents/{document_id}/file`
- `PATCH /api/candidates/{candidate_id}/status`
- `POST /api/candidates/{candidate_id}/tags`
- `POST /api/candidates/{candidate_id}/feedbacks`
- `POST /api/candidates/{candidate_id}/email-drafts`

## 数据与文件

### 数据库

当前迁移历史已经压平成单条初始链：

- `20260410_0007_initial_schema`

也就是说：

- 全新环境会直接创建当前真值结构
- 不再保留历史过渡 migration 链

### 文件

Candidate 文件流程：

1. 上传时进入临时目录
2. 分析成功后移动到正式目录
3. 转正时按候选人姓名重命名
4. 通过后端文件接口访问

## 文档阅读顺序

如果要理解当前系统，建议按这个顺序阅读：

1. [docs/工程实现文档.md](/Users/evan/Downloads/auto-hr/docs/工程实现文档.md)
2. [docs/页面路由与前端状态设计.md](/Users/evan/Downloads/auto-hr/docs/页面路由与前端状态设计.md)
3. [docs/AI工作流设计.md](/Users/evan/Downloads/auto-hr/docs/AI工作流设计.md)
4. [docs/数据模型设计文档.md](/Users/evan/Downloads/auto-hr/docs/数据模型设计文档.md)
5. [docs/前端实现规范文档.md](/Users/evan/Downloads/auto-hr/docs/前端实现规范文档.md)
6. [docs/后端实现规范文档.md](/Users/evan/Downloads/auto-hr/docs/后端实现规范文档.md)
7. [docs/README.md](/Users/evan/Downloads/auto-hr/docs/README.md)

## 开发约束

- 用户界面不得展示技术实现细节
- 设计与实现冲突时，以 `docs/` 中主真值文档为准
- 当前 Demo 只保留当前唯一生效的 Job 评估规范，不做版本化
- Candidate 分析失败不保留中间数据库记录
- 旧的同步 finalize/import 语义已经废弃

## 当前已知边界

- 当前后台任务执行仍在单 API 进程内完成，不使用分布式任务队列
- 文件存储仍是本地目录，不是对象存储
- 当前只服务 Demo 闭环，不做 ATS 全量能力

## 参考文档

- [文档索引](/Users/evan/Downloads/auto-hr/docs/README.md)
- [工程实现文档](/Users/evan/Downloads/auto-hr/docs/工程实现文档.md)
- [实施步骤文档](/Users/evan/Downloads/auto-hr/docs/实施步骤文档.md)
