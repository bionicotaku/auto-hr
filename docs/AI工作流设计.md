# AI 流设计文档（Demo 最终版）

## 1. 文档目标

本文档用于定义 Demo 中两条 AI 主流程的最终设计：

- **AI 流一：工作描述处理流**
    
- **AI 流二：Candidate 分析流**
    

本期目标不是构建完整招聘 AI 平台，而是完成一条可解释、可落地、可展示的最小闭环：

**工作描述与 rubric 生成/编辑 → 最终定稿生成评估规范 → Candidate 原始资料临时接收 → Candidate 标准化 → 基于 rubric 的多维子分 → 总分 + summary + 证据点**

---

## 2. 本期固定设计边界

### 2.1 保留的能力

本期保留以下核心能力：

- 工作描述生成与编辑
    
- rubric 生成与编辑
    
- 完成时生成正式 Candidate 评估规范
    
- Candidate 原始资料接收与成功后保存
    
- Candidate 资料标准化
    
- 基于 rubric 的逐项分析
    
- supervisor 汇总总分、summary、证据点、标签和推荐结论
    

### 2.2 暂不处理的能力

本期明确不处理：

- Job 评估规范版本管理
    
- 历史 Candidate 绑定旧版本规范
    
- 超重的 ATS 全量 Candidate schema
    
- 复杂自治 agent 编排
    
- 自动发布职位、自动抓取候选人
    

本期固定为：

**一个 Job 只保存一套当前评估规范。**

---

# 3. 总体设计原则

## 3.1 所有 LLM 输出必须走严格 JSON Schema

所有 AI 输出都必须满足后端预定义的 JSON Schema。  
后端在任何入库前都必须校验：

- 结构合法
    
- 字段完整
    
- 枚举值合法
    
- 数值范围合法
    

不合法则不入库。

## 3.2 统一 AI 调用规范

本期 Demo 中所有 AI 调用统一采用同一套技术约束：

- 统一通过 **OpenAI Responses API** 发起调用
    
- 统一使用 **`gpt-5.4`**
    
- 统一设置 **`reasoning = medium`**
    
- 统一从项目 `.env` 中读取 **`OPENAI_API_KEY`**
    
- 统一要求模型按后端定义的 **JSON Schema** 严格输出
    
- 在 Responses API 中，结构化输出统一使用 **`text.format`**
    
- 带文件 input 的调用也走同一套 Responses API 约束，不单独切换其他调用方式
    

这条规则适用于：

- B 页面普通对话
    
- B 页面 Agent 模式
    
- B 页面点击“保存”后的最终定稿调用
    
- Candidate 标准化调用
    
- rubric 逐项子 agent 调用
    
- supervisor 汇总调用
    

本期不允许出现：

- 某个流程单独换模型
    
- 某个子 agent 单独降级 reasoning
    
- 某个调用返回自由文本后再靠正则或字符串解析落库
    
- 某个文件输入调用绕开 Responses API 或绕开 `text.format`
    

如果未来需要切换模型或推理强度，也必须作为全局配置统一修改，而不是在单个流程中局部漂移。

## 3.3 原始输入、标准化结果、分析结果分层保存

系统必须区分三层数据：

### 原始输入层

保存用户最初输入的文本和 PDF 文件。

### 标准化层

保存从原始资料中抽取出的轻量结构化 Candidate 信息。

### 分析结果层

保存 rubric 逐项分析结果、总分、summary、证据点和推荐结论。

## 3.4 B 页面当前编辑区内容始终是最新事实输入

在 B 页面中，以下内容构成后续 AI 调用的当前事实输入：

- 当前 title / summary
    
- 左侧工作描述编辑框
    
- 当前 responsibilities / skills
    
- 右侧 rubric + 权重编辑框
    

只要用户修改了其中任意内容，后续 AI 调用都必须基于当前值，而不是早前生成结果。

## 3.5 AI 负责辅助生成和分析，人类保留最终控制权

AI 可以：

- 生成工作描述
    
- 生成 rubric
    
- 生成评分标准
    
- 标准化 Candidate
    
- 分析 Candidate
    
- 生成邮件草稿
    

但最终保存 Job、推进/淘汰 Candidate、修改状态，均由人工控制。

---

# 4. AI 流总览

## 4.1 AI 流一：工作描述处理流

该流程负责生成和维护：

- Job 标题
    
- Job summary
    
- 结构化工作信息
    
- 工作描述正文
    
- rubric
    
- Candidate 逐项评估规范
    

## 4.2 AI 流二：Candidate 分析流

该流程负责完成：

- Candidate 原始资料临时接收与成功后保存
    
- Candidate 标准化
    
- 基于 rubric 的逐项分析
    
- supervisor 汇总总分、summary、证据点、标签和推荐结论
    

---

# 5. B 页面设计

## 5.1 页面结构

B 页面固定为三部分：

### 上方左侧

岗位定义编辑区：

- title / summary 展示
- 工作描述编辑框
- responsibilities 编辑框
- skills 编辑框

### 上方右侧

rubric + 权重编辑框。

编辑态下，每个 rubric 项固定包含：

- 评估项名称
    
- 评估项说明
    
- 权重输入

编辑页不展示：

- 类型切换
    
- 标准化权重
    
- 评分标准详情入口

### 下方

AI 对话区。

### 底部

按钮区：

- 获取建议
    
- 生成新版
    
- 保存
    
- 取消

---

## 5.2 B 页面对话上下文

B 页面中的 AI 调用分为两类。

普通对话与 Agent 模式下，固定传入：

- 当前标题与 summary
    
- 当前工作描述编辑框内容
    
- 当前 responsibilities
    
- 当前 skills
    
- 当前 rubric 编辑框内容
    
- 历史摘要
    
- 最近 5 轮对话
    
- 当前用户输入
    
- 当前交互模式

其中当前编辑区内容优先级最高。

---

## 5.3 B 页面中的 AI 模式

### 对话模式

AI 返回建议和修改意见，但不直接覆盖编辑区内容。

### Agent 模式

AI 返回新的岗位定义，并直接覆盖当前编辑区。

覆盖范围包括：

- title
    
- summary
    
- structured_info_json
    
- 工作描述正文
    
- responsibilities
    
- skills
    
- rubric

Agent 模式返回结果必须合法，否则不允许覆盖。

---

# 6. AI 流一：工作描述处理流

## 6.1 目标

工作描述处理流的目标不是只生成一段 JD，而是产出一个可用于 Candidate 统一分析的岗位定义对象。

该对象最终包含：

- Job 标题
    
- Job summary
    
- 结构化工作信息
    
- 工作描述正文
    
- rubric
    
- rubric 对应的 Candidate 评分标准
    
- rubric 对应的子 agent 提示词

---

## 6.2 输入

### 场景一：已有描述导入

输入：

- 已有工作描述原文

### 场景二：基础信息生成

输入：

- 工作基础信息表单输入

### 场景三：B 页面继续编辑

输入：

- 当前 title / summary
    
- 当前工作描述
    
- 当前 responsibilities
    
- 当前 skills
    
- 当前 rubric
    
- 历史摘要
    
- 最近 5 轮对话
    
- 用户当前输入
    
- 当前交互模式

补充规则：

- 普通对话与 Agent 模式都输入当前最新编辑态

---

## 6.3 首次输出

在新建流程中，首次生成的内容包括：

- Job 标题
    
- Job summary
    
- 结构化工作信息
    
- 工作描述正文
    
- rubric

这里的 rubric 只是 **可编辑草稿**，不是最终 Candidate 评估规范。

---

## 6.4 rubric 结构

编辑态下，每个 rubric 项固定包含：

- `name`
    
- `description`
    
- `weight_input`

`criterion_type` 由后端根据 `weight_input` 推导：

- `100` -> `hard_requirement`
    
- `1-99` -> `weighted`

---

## 6.5 分值和权重规则

### 分值范围

所有普通评分项固定使用 **0-5 分**。  
前端不显示分值范围配置，也不允许自定义。

### 权重规则

权重输入范围固定为 **1-100**。

其中：

- `1-99` 表示普通加权项
    
- `100` 表示硬门槛项

### 硬门槛项

硬门槛项不参与普通总分计算。  
它们单独输出 pass / borderline / fail。

---

## 6.6 AI 输出权重约束

当 AI 生成或 Agent 覆盖 rubric 时：

- 普通评分项只要求 `weight_input` 在 `1-99`
    
- 硬门槛项使用 `weight_input = 100`
    
- 普通项不要求在生成阶段就和为 100

最终归一化在保存时由代码统一完成。

---

## 6.7 人工编辑权重规则

在 B 页面中，用户可手动编辑权重。  
人工编辑时不要求普通项权重和实时等于 100。

但在点击“保存”时，系统会进入最终定稿流程，由 AI 基于最终内容输出可入库的正式结果。

---

## 6.8 B 页面点击“保存”时的最终定稿 Analysis Run

这是本设计中的关键步骤。

无论是：

- 新建 Job
    
- 编辑已有 Job

只要用户在 B 页面点击“保存”，系统都必须启动一次 `job_finalize` analysis run，并显示进度。

这个 run 不是普通对话，而是 **最终定稿编排**。

### 输入

固定输入：

- 当前最终版工作描述
    
- 当前最终版 responsibilities
    
- 当前最终版 skills
    
- 当前最终版 rubric

### 输出

编排固定拆成两类子任务：

- 1 个标题 / summary 任务
    
- N 个 rubric enrichment 任务

最终由代码重组得到：

- 最终 Job 标题
    
- 最终 Job summary
    
- 最终 rubric enrichment
    
    - 每项正式评分标准
        
    - 每项子 agent 提示词
        
    - 每项证据提取要求

`weight_normalized` 不由 LLM 生成，而是由代码统一计算。

### 保存规则

点击“保存”后：

- 页面进入 loading
    
- 在最终定稿编排成功前，不正式入库或更新
    
- 只有成功并通过 schema 校验后，才写入数据库
    
- 失败时保留当前编辑区内容，不丢失草稿

---

## 6.9 最终入库内容

当最终定稿调用成功后，Job 当前生效数据包含：

### Job 基本信息

- 标题
    
- summary
    
- 结构化工作信息（含 responsibilities / skills）
    
- 工作描述正文

### Job rubric

- rubric 列表
    
- 普通项归一化后的权重
    
- 硬门槛项标记

### Job 评估规范

- 每个 rubric 项的正式评分标准
    
- 每个 rubric 项的子 agent 提示词
    
- 每个 rubric 项的证据提取要求

### Job 原始信息

- 原始输入
    
- 历史摘要

本期不做版本化。  
数据库中只保存 **当前唯一生效的一套评估规范**。

---

## 6.10 权重归一化规则

最终入库时：

- 硬门槛项保持 `weight = 100`
    
- 普通项统一归一化，使总和为 100
    

如果人工编辑后的普通项总和为 0，则最终定稿必须失败，不允许完成保存。

---

# 7. AI 流二：Candidate 分析流

## 7.1 目标

Candidate 分析流固定采用以下链路：

**原始资料临时接收 → Candidate 标准化 → 按 rubric 逐项分析 → supervisor 汇总**

目标不是黑盒打总分，而是产出：

- 多维子分
    
- 总分
    
- summary
    
- 证据点
    
- 标签
    
- 推荐结论
    

---

## 7.2 输入

Candidate 分析流输入包括：

- 原始文本输入
    
- 最多 4 个 PDF 文件内容
    
- 所属 Job
    
- 当前 Job 的唯一生效评估规范
    

这里不做版本区分。  
Candidate 分析时直接读取当前 Job 入库的评估规范。

---

## 7.3 输出

Candidate 分析流最终输出：

- Candidate 默认姓名
    
- Candidate 标准化信息
    
- 各 rubric 项子分析结果
    
- 硬门槛判断
    
- 总分
    
- summary
    
- 证据点
    
- 标签
    
- 推荐结论
    

---

# 8. Candidate 标准化设计（轻量版）

## 8.1 设计目标

本期 Candidate 标准化只保留当前 demo 真正需要的字段：

- 能支撑后续评分
    
- 能支撑列表与详情展示
    
- 能尽量完整保留简历/问答关键信息
    
- 不把 schema 做得过重
    

其余信息统一进入补充区，后续再扩展。

---

## 8.2 保留的字段块

### A. 基本身份信息 `identity`

用于列表展示和基础识别。

字段：

- `full_name`
    
- `current_title`
    
- `current_company`
    
- `location_text`
    
- `email`
    
- `phone`
    
- `linkedin_url`
    

### B. 职业概览 `profile_summary`

用于快速理解候选人整体画像。

字段：

- `professional_summary_raw`
    
- `professional_summary_normalized`
    
- `years_of_total_experience`
    
- `years_of_relevant_experience`
    
- `seniority_level`
    

### C. 工作经历 `work_experiences`

这是最重要的一块，保留最核心的经历结构。

每段经历字段：

- `company_name`
    
- `title`
    
- `start_date`
    
- `end_date`
    
- `is_current`
    
- `description_raw`
    
- `description_normalized`
    
- `key_achievements`
    

### D. 教育经历 `educations`

保留核心教育信息即可。

每段教育字段：

- `school_name`
    
- `degree`
    
- `degree_level`
    
- `major`
    
- `end_date`
    

### E. 技能信息 `skills`

用于后续评分和展示。

字段：

- `skills_raw`
    
- `skills_normalized`
    

### F. 资格与偏好 `employment_preferences`

保留招聘中最常用、最影响硬门槛判断的字段。

字段：

- `work_authorization`
    
- `requires_sponsorship`
    
- `willing_to_relocate`
    
- `preferred_locations`
    
- `preferred_work_modes`
    

### G. 申请问答 `application_answers`

若有问答内容，则按统一结构保存。

每项字段：

- `question_text`
    
- `answer_text`
    

### H. 文档索引 `documents`

用于关联原始文件。

每项字段：

- `document_type`
    
- `filename`
    
- `storage_path`
    
- `text_extracted`
    

### I. 补充信息区 `additional_information`

用来安置标准字段之外但不能丢的信息。

字段：

- `uncategorized_highlights`
    
- `parser_notes`
    

---

## 8.3 精简理由

这版 schema 去掉了很多当前 demo 不急需的内容，例如：

- 详细奖项、论文、专利
    
- 多邮箱、多电话
    
- 复杂证书/培训分层
    
- security clearance 等更重字段
    
- 过细的来源和运营统计字段
    

原因很简单：

你现在的 demo 重点是 **Candidate 标准化 + 基于 rubric 的分析**，而不是先做完整 ATS 候选人档案系统。

所以当前应优先保留：

- 基本身份
    
- 经历
    
- 教育
    
- 技能
    
- 硬门槛相关偏好
    
- 问答
    
- 原始文件索引
    
- 补充安置信息
    

---

## 8.4 标准化输出要求

标准化输出必须：

- 固定输出完整 schema
    
- 缺失字段也保留空值
    
- 多余信息进入 `additional_information`
    
- 不允许模型自由删字段
    

---

## 8.5 Candidate 轻量标准化 JSON 结构

```json
{
  "identity": {
    "full_name": "",
    "current_title": "",
    "current_company": "",
    "location_text": "",
    "email": "",
    "phone": "",
    "linkedin_url": ""
  },
  "profile_summary": {
    "professional_summary_raw": "",
    "professional_summary_normalized": "",
    "years_of_total_experience": null,
    "years_of_relevant_experience": null,
    "seniority_level": ""
  },
  "work_experiences": [],
  "educations": [],
  "skills": {
    "skills_raw": [],
    "skills_normalized": []
  },
  "employment_preferences": {
    "work_authorization": "",
    "requires_sponsorship": null,
    "willing_to_relocate": null,
    "preferred_locations": [],
    "preferred_work_modes": []
  },
  "application_answers": [],
  "documents": [],
  "additional_information": {
    "uncategorized_highlights": [],
    "parser_notes": []
  }
}
```

---

# 9. Candidate 分析流详细步骤

## 9.1 第一步：原始资料临时接收

用户点击“生成”后，系统先接收并暂存：

- 原始文本输入
    
- 原始 PDF 文件
    
- 所属 Job
    
- 导入时间
    

这些原始资料在 Demo 阶段只作为本次分析输入。  
如果后续任一步失败，则不入库，并清理临时文件。

---

## 9.2 第二步：Candidate 标准化

系统使用文件 input 的 GPT API 进行标准化抽取。

输入：

- 原始文本
    
- PDF 抽取文本
    
- 文件元信息
    

输出：

- 上述轻量版 Candidate 标准化 schema
    

规则：

- 默认姓名由 AI 提取
    
- 允许人工后续修正
    
- 缺失字段填空
    
- 多余信息进入补充区
    

---

## 9.3 第三步：按 rubric 拆分任务

系统读取当前 Job 的 rubric 和评估规范，为每个 rubric 项创建独立分析任务。

区分两类：

### 硬门槛项

输出：

- `pass` / `borderline` / `fail`
    
- 理由
    
- 证据点
    
- 是否建议人工复核
    

### 普通评分项

输出：

- 0-5 分
    
- 理由
    
- 证据点
    
- 不确定性说明
    

---

## 9.4 第四步：子 agent 逐项分析

每个 rubric 项由一个独立子 agent 处理。

子 agent 输入包括：

- 该 rubric 项定义
    
- 该 rubric 项正式评分标准
    
- 该 rubric 项正式提示词
    
- Candidate 标准化信息
    
- 原始资料摘要
    
- Job 描述摘要
    

子 agent 输出包括：

- 子分或门槛判断
    
- 理由
    
- 证据点
    
- 不确定性说明
    

---

## 9.5 第五步：supervisor 汇总

所有子 agent 完成后，由 supervisor 汇总：

- 硬门槛结果
    
- 普通项结果
    
- 总分
    
- summary
    
- 证据点
    
- 标签
    
- 推荐结论
    

supervisor 不重新定义每项逻辑，只做统一整理。

---

# 10. 子分、总分与推荐规则

## 10.1 子分范围

所有普通评分项固定使用 **0-5 分**。

## 10.2 总分计算

普通项按归一化后的权重加权：

`score × weight_percent`

最终得到一个 0-5 的总分。  
前端可显示为百分制。

## 10.3 硬门槛项

硬门槛项不参与总分计算，但影响推荐结论。

## 10.4 推荐结论

推荐结论固定为有限枚举：

- `advance`
    
- `manual_review`
    
- `hold`
    
- `reject`
    

---

# 11. Candidate 分析结果保存

Candidate 分析结果仅在整条流程成功后分三层保存。

## 11.1 原始层

保存：

- 原始文本
    
- 原始文件
    
- 文件元信息
    

## 11.2 标准化层

保存：

- Candidate 轻量标准化结果
    

## 11.3 分析层

保存：

- 每个 rubric 项的分析结果
    
- 总分
    
- summary
    
- 证据点
    
- 标签
    
- 推荐结论
    

---

# 12. 失败与重试规则

## 12.1 B 页面最终定稿失败

若点击“保存”后的最终调用失败：

- 不入库
    
- 不更新 Job
    
- 保留当前编辑内容
    
- 显示错误信息
    

## 12.2 Candidate 标准化失败

若标准化失败：

- 不创建任何 Candidate 相关数据库记录
    
- 清理本次临时文件
    
- 返回错误给前端
    

## 12.3 某个子 agent 失败

若某一 rubric 项失败：

- 整个 Candidate 分析流程视为失败
    
- 不创建任何 Candidate 相关数据库记录
    
- 清理本次临时文件
    
- 返回错误给前端

补充说明：

- 未来可以扩展为保留导入记录、分析失败记录或部分失败标记
    
- 但 Demo 阶段不启用这些失败中间态持久化设计
    

---

# 13. 前端展示影响

## 13.1 B 页面

B 页面上方固定为：

- 左侧工作描述编辑框
    
- 右侧 rubric + 权重编辑框
    

点击“保存”后必须显示 loading。  
只有最终定稿成功后，才允许真正保存并跳转。

## 13.2 Candidate 列表页

至少展示：

- 姓名
    
- AI summary
    
- 总分
    
- 当前状态
    

## 13.3 Candidate 详情页

至少展示四部分：

- 原始输入
    
- 标准化信息
    
- rubric 逐项分析结果
    
- supervisor 汇总结果
    

---

# 14. 最终结论

本期 Demo 的 AI 主链路最终固定为：

**工作描述与 rubric 生成/编辑 → B 页面点击保存时最终定稿并生成正式评估规范 → Candidate 原始资料临时接收 → Candidate 轻量标准化 → 基于 rubric 的子 agent 逐项分析 → supervisor 汇总总分、summary 与证据点**

同时，本期设计做了两项关键收敛：

第一，**不处理评估规范版本**，每个 Job 只保存当前唯一生效的一套评估规范。  
第二，**Candidate 标准化 schema 采用轻量方案**，只保留当前 demo 真正有价值的核心字段，其余信息统一进入补充区。

这样既能保证 demo 足够完整、可解释、可落地，也不会因为过重的 schema 和版本设计把实现复杂度拉得太高。
