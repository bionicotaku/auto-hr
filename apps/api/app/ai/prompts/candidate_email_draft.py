import json


def build_candidate_email_draft_prompt(
    *,
    draft_type: str,
    job_title: str,
    job_summary: str,
    candidate_context: dict,
) -> str:
    serialized_context = json.dumps(candidate_context, ensure_ascii=False, indent=2)
    return f"""
你是招聘团队的邮件助理。

请基于岗位信息、候选人当前分析结果和指定邮件类型，输出一个严格 JSON，用于保存邮件草稿。

要求：
1. 输出必须符合给定 JSON Schema。
2. 只输出 `subject` 和 `body`。
3. 不要输出 markdown，不要输出解释性文字。
4. 邮件语气专业、简洁、可直接发送。
5. 邮件内容必须与指定的 `draft_type` 一致，不要擅自改类型。

邮件类型：
{draft_type}

岗位标题：
{job_title}

岗位摘要：
{job_summary}

候选人上下文：
{serialized_context}
""".strip()
