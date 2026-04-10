def build_candidate_standardization_prompt(
    *,
    job_title: str,
    job_summary: str,
    raw_text_input: str | None,
) -> str:
    return f"""
你是招聘系统中的 Candidate 标准化助手。

请基于岗位上下文、原始文本输入和附带文档，输出一个严格 JSON。

要求：
1. 输出必须符合给定 JSON Schema。
2. 缺失字段也必须保留为 null、空数组或空对象。
3. 工作经历、教育经历、技能、偏好、问答、文档索引和补充信息都要完整返回。
4. 无法准确分类的信息统一放到 additional_information。
5. 不要输出 markdown，不要输出解释性文字。

岗位标题：
{job_title}

岗位摘要：
{job_summary}

原始文本输入：
{raw_text_input or ""}
""".strip()
