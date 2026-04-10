# AI 工作流设计

## 1. 文档目标

本文档定义当前 Demo 的 AI 真值，覆盖两条主链路：

- Job 生成、编辑与保存
- Candidate 分析与入库

所有描述均以当前代码实现为准。

---

## 2. 全局 AI 约束

所有 AI 调用统一遵循：

- OpenAI Responses API
- 模型固定为 `gpt-5.4`
- `reasoning = medium`
- 严格 JSON Schema 输出
- 统一通过后端 AI client 发起

长耗时链路不允许前端等待单个同步长请求。当前统一走：

- `AnalysisRun`
- `AnalysisRunEvent`
- `SSE`

---

## 3. Job 工作流

### 3.1 创建初稿

Job draft 创建负责生成：

- `title`
- `summary`
- `structured_info_json`
- `description_text`
- draft `rubric_items`

这里不会生成正式评分富化字段。

### 3.2 编辑页交互

编辑页有三类 AI 行为：

- 获取建议
  - 只返回建议文本
  - 不覆盖当前编辑态
- 生成新版
  - 覆盖当前编辑态
  - 更新 `title`、`summary`、`structured_info_json`、`description_text`、`responsibilities`、`skills`、`rubric_items`
- 保存
  - 不直接同步入库
  - 启动 `job_finalize` analysis run

### 3.3 保存定稿

`job_finalize` analysis run 内部拆为两个 AI 子阶段：

1. 重新生成最终 `title` 和最终 `summary`
2. 为每个 rubric 项生成正式富化字段：
   - `scoring_standard_items`
   - `agent_prompt_text`
   - `evidence_guidance_text`

确定性逻辑全部由代码处理：

- `weight_normalized` 由代码计算
- rubric 项合并与对齐由代码处理
- weighted 总和为 0 时直接失败

### 3.4 Job finalize 进度

`job_finalize` 的 AI 总步数固定为：

- `1 + rubric_items 数量`

含义：

- `1` 步：标题与摘要生成
- `N` 步：每个 rubric 项富化

每个 AI 子调用成功后，进度才前进一步。

---

## 4. Candidate 工作流

### 4.1 输入

Candidate 分析接收：

- `raw_text_input`
- 原始 PDF 文件

系统保留原始文本与原始 PDF，但不提取、不保存 PDF 文本内容。

### 4.2 标准化

Candidate 标准化负责输出：

- 轻量标准化档案
- 原始文件索引
- 资料有效性判断

当前有效性字段固定为：

- `is_candidate_like`
- `invalid_reason`

如果出现以下情况，标准化应返回 `is_candidate_like = false`：

- 无法识别为候选人资料
- 文本无关或混乱
- 识别到多位候选人

### 4.3 入库门槛

Candidate 允许入库的条件只有：

- AI 调用链成功
- Schema 校验成功
- `is_candidate_like = true`
- 提取出有效姓名

以下内容不再阻断入库：

- `hard_requirement_overall`
- `recommendation`

### 4.4 rubric 逐项分析

Candidate 标准化完成后，系统按 Job 当前 rubric 逐项分析：

- weighted 项输出评分与证据
- hard requirement 项输出 `pass / borderline / fail`

每个 rubric 项是独立 AI 调用。

### 4.5 supervisor 汇总

supervisor 负责生成：

- `ai_summary`
- `evidence_points`
- `tags`
- `recommendation`
- `hard_requirement_overall`
- `overall_score_percent`

这里不再存在：

- 旧的 5 分总分字段

`recommendation` 只表示 AI 汇总结论，不再作为入库门槛。

### 4.6 默认标签

Candidate 成功入库后，系统会在 supervisor 标签基础上补默认 AI 标签：

- `has_fail` → `硬性要求未通过`
- `has_borderline` → `需要复核`

这些标签只影响展示与筛选，不阻断入库。

### 4.7 Candidate 分析进度

`candidate_import` 的 AI 总步数固定为：

- `2 + rubric_items 数量`

含义：

- `1` 步：Candidate 标准化
- `N` 步：每个 rubric 项分析
- `1` 步：supervisor 汇总

`prepare` 与 `persist` 只显示阶段文案，不计入分母。

---

## 5. Candidate 原始文件

Candidate 原始文件链路固定为：

- 后端保留原始 PDF
- Candidate 详情页通过 `file_url` 打开 PDF
- 文件名按 `[候选人姓名]-[标号].pdf` 转正
- 前端不展示服务器本地路径
- 前端不展示提取文本

---

## 6. 当前固定结论

当前 AI 工作流的关键真值如下：

- Job 保存与 Candidate 分析都是异步 run
- Job 保存不是同步 finalize 请求
- Candidate 分析不是同步 import 请求
- Candidate 不保存 PDF 文本内容
- Candidate 不保留旧的 5 分总分字段
- 硬门槛不阻断 Candidate 入库
- Candidate 列表和详情页都围绕当前生效数据与当前 AI 结果展示
