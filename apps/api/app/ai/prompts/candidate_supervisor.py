import json


def build_candidate_supervisor_prompt(
    *,
    job_title: str,
    job_summary: str,
    standardized_candidate: dict,
    rubric_results: dict,
    hard_requirement_overall: str,
    overall_score_5: float,
    overall_score_percent: float,
) -> str:
    serialized_candidate = json.dumps(standardized_candidate, ensure_ascii=False, indent=2)
    serialized_results = json.dumps(rubric_results, ensure_ascii=False, indent=2)
    return f"""
你是招聘系统中的 Candidate supervisor。

请基于岗位上下文、候选人标准化结果、逐项评分结果以及已经计算好的总分与硬门槛总览，输出一个严格 JSON。

要求：
1. 输出必须符合给定 JSON Schema。
2. 不要重新计算总分，也不要重做逐项评分。
3. 只生成汇总层输出：summary、核心证据点、标签、推荐结论。
4. `hard_requirement_overall`、`overall_score_5`、`overall_score_percent` 必须与输入一致。
5. 不要输出 markdown，不要输出解释性文字。

岗位标题：
{job_title}

岗位摘要：
{job_summary}

候选人标准化信息：
{serialized_candidate}

逐项评分结果：
{serialized_results}

已计算硬门槛总览：
{hard_requirement_overall}

已计算总分（0-5）：
{overall_score_5}

已计算总分（百分制）：
{overall_score_percent}
""".strip()
