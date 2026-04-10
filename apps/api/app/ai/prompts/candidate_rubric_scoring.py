import json


def build_weighted_rubric_scoring_prompt(
    *,
    job_title: str,
    job_summary: str,
    rubric_item: dict,
    standardized_candidate: dict,
) -> str:
    serialized_rubric_item = json.dumps(rubric_item, ensure_ascii=False, indent=2)
    serialized_candidate = json.dumps(standardized_candidate, ensure_ascii=False, indent=2)
    return f"""
你是招聘系统中的候选人评分助手。

请针对当前 weighted rubric 项，基于岗位上下文、评分标准和候选人标准化资料，输出一个严格 JSON。

要求：
1. 输出必须符合给定 JSON Schema。
2. 只返回当前 rubric 项的结果。
3. `criterion_type` 必须是 `weighted`。
4. `score_0_to_5` 必须在 0 到 5 之间。
5. `reason_text`、`evidence_points` 必须直接对应当前评分项。
6. 不要输出 markdown，不要输出解释性文字。

岗位标题：
{job_title}

岗位摘要：
{job_summary}

当前 rubric 项：
{serialized_rubric_item}

候选人标准化信息：
{serialized_candidate}
""".strip()


def build_hard_requirement_scoring_prompt(
    *,
    job_title: str,
    job_summary: str,
    rubric_item: dict,
    standardized_candidate: dict,
) -> str:
    serialized_rubric_item = json.dumps(rubric_item, ensure_ascii=False, indent=2)
    serialized_candidate = json.dumps(standardized_candidate, ensure_ascii=False, indent=2)
    return f"""
你是招聘系统中的候选人评分助手。

请针对当前 hard requirement rubric 项，基于岗位上下文、判断标准和候选人标准化资料，输出一个严格 JSON。

要求：
1. 输出必须符合给定 JSON Schema。
2. 只返回当前 rubric 项的结果。
3. `criterion_type` 必须是 `hard_requirement`。
4. `hard_requirement_decision` 只能是 `pass`、`borderline` 或 `fail`。
5. `reason_text`、`evidence_points` 必须直接对应当前门槛项。
6. 不要输出 markdown，不要输出解释性文字。

岗位标题：
{job_title}

岗位摘要：
{job_summary}

当前 rubric 项：
{serialized_rubric_item}

候选人标准化信息：
{serialized_candidate}
""".strip()
