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
