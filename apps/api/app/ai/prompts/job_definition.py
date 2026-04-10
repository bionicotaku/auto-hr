import json


def build_create_draft_from_description_prompt(description_text: str) -> str:
    return f"""
你是招聘系统中的 Job 定义助手。

请基于用户提供的原始职位描述，输出一个可直接用于创建 Job draft 的严格 JSON。

要求：
1. 输出必须符合给定 JSON Schema。
2. 生成 title、summary、structured_info_json、description_text、rubric_items。
3. rubric_items 必须同时包含 weighted 和 hard_requirement 的合理划分。
4. hard_requirement 项必须设置 weight_input=100。
5. 不要生成 weight_normalized，后端会在接收后统一计算。
6. 不要生成 scoring_standard_items。
7. 不要生成 agent_prompt_text 和 evidence_guidance_text。
8. 不要输出额外说明，不要输出 markdown。

原始职位描述如下：
{description_text}
""".strip()


def build_create_draft_from_form_prompt(form_payload: dict) -> str:
    serialized = json.dumps(form_payload, ensure_ascii=False, indent=2)
    return f"""
你是招聘系统中的 Job 定义助手。

请基于用户填写的岗位基础信息，生成一个可直接用于创建 Job draft 的严格 JSON。

要求：
1. 输出必须符合给定 JSON Schema。
2. 生成 title、summary、structured_info_json、description_text、rubric_items。
3. description_text 需要扩写成可编辑的 JD 初稿。
4. rubric_items 需要覆盖岗位最重要的评估维度，并同时区分 weighted 与 hard_requirement。
5. hard_requirement 项必须设置 weight_input=100。
6. 不要生成 weight_normalized，后端会在接收后统一计算。
7. 不要生成 scoring_standard_items、agent_prompt_text、evidence_guidance_text。
8. 不要输出额外说明，不要输出 markdown。

岗位基础信息如下：
{serialized}
""".strip()


def build_job_chat_prompt(
    *,
    description_text: str,
    responsibilities: list[str],
    skills: list[str],
    rubric_items: list[dict],
    recent_messages: list[dict],
    user_input: str,
) -> str:
    serialized_rubric = json.dumps(rubric_items, ensure_ascii=False, indent=2)
    serialized_messages = json.dumps(recent_messages, ensure_ascii=False, indent=2)
    serialized_responsibilities = json.dumps(responsibilities, ensure_ascii=False, indent=2)
    serialized_skills = json.dumps(skills, ensure_ascii=False, indent=2)
    return f"""
你是招聘系统中的岗位编辑助手。

请基于当前岗位定义和用户的本轮要求，输出一个严格 JSON，只返回建议文本，不要改写岗位正文或 rubric。

要求：
1. 输出必须符合给定 JSON Schema。
2. 只输出 `reply_text`。
3. `reply_text` 必须直接回答当前用户要求，并指出建议如何落实。
4. 不要返回新的 JD，不要返回新的 rubric。
5. 不要输出额外说明，不要输出 markdown。

当前职位描述：
{description_text}

当前 responsibilities：
{serialized_responsibilities}

当前 skills：
{serialized_skills}

当前 rubric：
{serialized_rubric}

最近对话：
{serialized_messages}

当前用户要求：
{user_input}
""".strip()


def build_job_agent_edit_prompt(
    *,
    description_text: str,
    responsibilities: list[str],
    skills: list[str],
    rubric_items: list[dict],
    recent_messages: list[dict],
    user_input: str,
) -> str:
    serialized_rubric = json.dumps(rubric_items, ensure_ascii=False, indent=2)
    serialized_messages = json.dumps(recent_messages, ensure_ascii=False, indent=2)
    serialized_responsibilities = json.dumps(responsibilities, ensure_ascii=False, indent=2)
    serialized_skills = json.dumps(skills, ensure_ascii=False, indent=2)
    return f"""
你是招聘系统中的岗位编辑助手。

请基于当前岗位定义和用户要求，直接输出更新后的职位描述、responsibilities、skills 与 rubric 严格 JSON。

要求：
1. 输出必须符合给定 JSON Schema。
2. 返回新的 `description_text`、完整的 `responsibilities`、完整的 `skills` 和完整的 `rubric_items`。
3. `responsibilities` 与 `skills` 必须是字符串数组，每个元素都是一个清晰条目。
4. `rubric_items` 必须保留完整的名称、说明、criterion_type 和权重。
4. 不要生成 scoring_standard_items、agent_prompt_text、evidence_guidance_text。
5. `weight_input=100` 表示必须满足的硬要求；`1-99` 表示普通加权项。
6. 不要生成 `weight_normalized`，后端会在接收后统一计算。
7. 不要输出额外说明，不要输出 markdown。

当前职位描述：
{description_text}

当前 responsibilities：
{serialized_responsibilities}

当前 skills：
{serialized_skills}

当前 rubric：
{serialized_rubric}

最近对话：
{serialized_messages}

当前用户要求：
{user_input}
""".strip()


def build_job_finalize_prompt(
    *,
    description_text: str,
    responsibilities: list[str],
    skills: list[str],
    rubric_items: list[dict],
) -> str:
    serialized_rubric = json.dumps(rubric_items, ensure_ascii=False, indent=2)
    serialized_responsibilities = json.dumps(responsibilities, ensure_ascii=False, indent=2)
    serialized_skills = json.dumps(skills, ensure_ascii=False, indent=2)
    return f"""
你是招聘系统中的岗位定稿助手。

请只基于当前用户已经编辑好的最新职位描述和最新 rubric，重新生成最终 `title`、最终 `summary`，并为每个 rubric item 补全 `scoring_standard_items`、`agent_prompt_text`、`evidence_guidance_text`，输出严格 JSON。

要求：
1. 输出必须符合给定 JSON Schema。
2. 返回 `title`、`summary` 和 `rubric_items`。
3. `title` 应准确概括当前岗位，不要引用旧版本或过程性措辞。
4. `summary` 应概括岗位定位、关键职责和评估重点，适合用于列表/详情摘要展示。
5. 每个 item 只返回 `sort_order`、`scoring_standard_items`、`agent_prompt_text`、`evidence_guidance_text`。
6. `scoring_standard_items` 必须使用数组形式，每一项都必须是 {{ "key": "...", "value": "..." }}。
7. `hard_requirement` 项应生成三档标准：`满足`、`部分满足`、`不满足`。
8. `weighted` 项应生成五档标准：`5`、`4`、`3`、`2`、`1`。
9. `agent_prompt_text` 必须明确告诉后续 Candidate 分析如何判断该维度。
10. `evidence_guidance_text` 必须明确说明应该优先收集哪些证据。
11. 不要参考任何原始输入、历史输入或旧版本定义，只使用下面提供的当前最新内容。
12. 不要修改或重写 rubric 的其他字段，不要输出额外说明，不要输出 markdown。

当前职位描述：
{description_text}

当前 responsibilities：
{serialized_responsibilities}

当前 skills：
{serialized_skills}

当前 rubric：
{serialized_rubric}
""".strip()
