import json


def build_create_draft_from_description_prompt(description_text: str) -> str:
    return f"""
你是招聘系统中的 Job 定义助手。

请基于用户提供的原始职位描述，输出一个可直接用于创建 Job draft 的严格 JSON。

要求：
1. 输出必须符合给定 JSON Schema。
2. 生成 title、summary、structured_info_json、description_text、rubric_items。
3. rubric_items 必须同时包含 weighted 和 hard_requirement 的合理划分。
4. hard_requirement 项必须设置 weight_input=100，weight_normalized=null。
5. weighted 项必须设置 0-1 之间的 weight_normalized。
6. scoring_standard_json 必须完整、可读、可直接用于后续 Candidate 分析。
7. agent_prompt_text 与 evidence_guidance_text 必须明确，不允许空泛。
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
5. hard_requirement 项必须设置 weight_input=100，weight_normalized=null。
6. weighted 项必须设置 0-1 之间的 weight_normalized。
7. scoring_standard_json、agent_prompt_text、evidence_guidance_text 需要完整且可执行。
8. 不要输出额外说明，不要输出 markdown。

岗位基础信息如下：
{serialized}
""".strip()


def build_job_chat_prompt(
    *,
    description_text: str,
    rubric_items: list[dict],
    recent_messages: list[dict],
    user_input: str,
) -> str:
    serialized_rubric = json.dumps(rubric_items, ensure_ascii=False, indent=2)
    serialized_messages = json.dumps(recent_messages, ensure_ascii=False, indent=2)
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
    rubric_items: list[dict],
    recent_messages: list[dict],
    user_input: str,
) -> str:
    serialized_rubric = json.dumps(rubric_items, ensure_ascii=False, indent=2)
    serialized_messages = json.dumps(recent_messages, ensure_ascii=False, indent=2)
    return f"""
你是招聘系统中的岗位编辑助手。

请基于当前岗位定义和用户要求，直接输出更新后的职位描述与 rubric 严格 JSON。

要求：
1. 输出必须符合给定 JSON Schema。
2. 返回新的 `description_text` 和完整的 `rubric_items`。
3. `rubric_items` 必须保留完整评分标准、子 agent 提示词和证据提取说明。
4. hard_requirement 项必须设置 `weight_input=100` 且 `weight_normalized=null`。
5. weighted 项必须设置合法的 `weight_normalized`。
6. 不要输出额外说明，不要输出 markdown。

当前职位描述：
{description_text}

当前 rubric：
{serialized_rubric}

最近对话：
{serialized_messages}

当前用户要求：
{user_input}
""".strip()


def build_job_regenerate_prompt(
    *,
    original_description_input: str | None,
    original_form_input_json: dict | None,
    title: str,
    summary: str,
    structured_info_json: dict,
    history_summary: str | None,
    recent_messages: list[dict],
) -> str:
    serialized_form = json.dumps(original_form_input_json, ensure_ascii=False, indent=2)
    serialized_structured_info = json.dumps(structured_info_json, ensure_ascii=False, indent=2)
    serialized_messages = json.dumps(recent_messages, ensure_ascii=False, indent=2)
    original_text = original_description_input or ""
    return f"""
你是招聘系统中的岗位编辑助手。

请基于原始输入和历史上下文，重新生成一版新的职位描述与 rubric 严格 JSON。

要求：
1. 输出必须符合给定 JSON Schema。
2. 只基于原始输入、历史摘要、最近对话和必要上下文重新生成。
3. 当前编辑区版本不会提供，请不要假设你已经看过当前编辑中的 JD 或 rubric。
4. 返回新的 `description_text` 和完整的 `rubric_items`。
5. rubric_items 仍需满足 hard_requirement 与 weighted 的权重规则。
6. 不要输出额外说明，不要输出 markdown。

原始职位描述输入：
{original_text}

原始表单输入：
{serialized_form}

当前岗位基础上下文：
title: {title}
summary: {summary}
structured_info_json:
{serialized_structured_info}

历史摘要：
{history_summary or ""}

最近对话：
{serialized_messages}
""".strip()
