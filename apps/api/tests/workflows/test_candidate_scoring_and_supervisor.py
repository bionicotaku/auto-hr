import re
import threading
import time
from collections import defaultdict

import pytest
from pydantic import ValidationError

from app.ai.prompts.candidate_supervisor import build_candidate_supervisor_prompt
from app.core.exceptions import DomainValidationError
from app.schemas.ai.candidate_rubric_result import (
    CandidateRubricScoreItemsResult,
    HardRequirementRubricResultSchema,
    WeightedRubricResultSchema,
)
from app.schemas.ai.candidate_standardization import (
    CandidateStandardizationSchema,
    PreparedCandidateImportInput,
)
from app.schemas.ai.candidate_supervisor import CandidateSupervisorSchema
from app.workflows.candidate_analysis.score_items import (
    CandidateScoreItemsWorkflow,
    PreparedRubricScoringInput,
)
from app.workflows.candidate_analysis.summarize import CandidateSummarizeWorkflow


def build_standardized_candidate() -> CandidateStandardizationSchema:
    return CandidateStandardizationSchema.model_validate(
        {
            "identity": {
                "full_name": "Ada Lovelace",
                "current_title": "Recruiting Lead",
                "current_company": "Auto HR",
                "location_text": "Remote",
                "email": "ada@example.com",
                "phone": "123456",
                "linkedin_url": "https://linkedin.example/ada",
            },
            "profile_summary": {
                "professional_summary_raw": "Built hiring systems",
                "professional_summary_normalized": "Built hiring systems",
                "years_of_total_experience": 8,
                "years_of_relevant_experience": 6,
                "seniority_level": "Lead",
            },
            "work_experiences": [
                {
                    "company_name": "Auto HR",
                    "title": "Recruiting Lead",
                    "start_date": "2020-01",
                    "end_date": None,
                    "is_current": True,
                    "description_raw": "Built recruiting systems",
                    "description_normalized": "Built recruiting systems",
                    "key_achievements": ["Designed workflows"],
                }
            ],
            "educations": [
                {
                    "school_name": "Example University",
                    "degree": "BS",
                    "degree_level": "Bachelor",
                    "major": "Business",
                    "end_date": "2018-06",
                }
            ],
            "skills": {
                "skills_raw": ["Recruiting", "Operations"],
                "skills_normalized": ["recruiting", "operations"],
            },
            "employment_preferences": {
                "work_authorization": "US",
                "requires_sponsorship": False,
                "willing_to_relocate": None,
                "preferred_locations": ["Remote"],
                "preferred_work_modes": ["remote"],
            },
            "application_answers": [
                {
                    "question_text": "Why this role?",
                    "answer_text": "I like recruiting systems.",
                }
            ],
            "documents": [
                {
                    "document_type": "resume",
                    "filename": "resume.pdf",
                    "storage_path": "/tmp/resume.pdf",
                    "text_extracted": "resume text",
                }
            ],
            "additional_information": {
                "uncategorized_highlights": ["Built global process"],
                "parser_notes": ["Some dates missing"],
            },
        }
    )


def build_prepared_input() -> PreparedCandidateImportInput:
    return PreparedCandidateImportInput(
        raw_text_input="Candidate raw text",
        job_id="job-001",
        job_title="AI Recruiter",
        job_summary="Own hiring for AI teams.",
        temp_request_id="temp-001",
        documents=[],
    )


def build_rubric_items(count: int = 3) -> list[dict]:
    items: list[dict] = []
    for index in range(count):
        criterion_type = "hard_requirement" if index == count - 1 and count > 1 else "weighted"
        items.append(
            {
                "id": f"rubric-{index + 1}",
                "sort_order": index + 1,
                "name": f"Criterion {index + 1}",
                "description": f"Description {index + 1}",
                "criterion_type": criterion_type,
                "weight_input": 100 if criterion_type == "hard_requirement" else 100 / max(count - 1, 1),
                "weight_normalized": None if criterion_type == "hard_requirement" else round(1 / max(count - 1, 1), 4),
                "scoring_standard_items": [{"key": "score_5", "value": "Excellent"}],
                "agent_prompt_text": f"Judge criterion {index + 1}",
                "evidence_guidance_text": "Look for examples",
            }
        )
    return items


def build_weighted_result(job_rubric_item_id: str, score: float) -> dict:
    return {
        "job_rubric_item_id": job_rubric_item_id,
        "criterion_type": "weighted",
        "score_0_to_5": score,
        "reason_text": f"Reason for {job_rubric_item_id}",
        "evidence_points": [f"Evidence for {job_rubric_item_id}"],
        "uncertainty_note": None,
    }


def build_hard_requirement_result(job_rubric_item_id: str, decision: str) -> dict:
    return {
        "job_rubric_item_id": job_rubric_item_id,
        "criterion_type": "hard_requirement",
        "hard_requirement_decision": decision,
        "reason_text": f"Reason for {job_rubric_item_id}",
        "evidence_points": [f"Evidence for {job_rubric_item_id}"],
        "uncertainty_note": None,
    }


class FakeScoringClient:
    def __init__(self, plans: dict[str, list[dict | Exception]], delay_seconds: float = 0.02) -> None:
        self.plans = plans
        self.delay_seconds = delay_seconds
        self.calls: list[dict] = []
        self.attempts: defaultdict[str, int] = defaultdict(int)
        self._lock = threading.Lock()
        self._active_calls = 0
        self.max_active_calls = 0

    def generate_structured_output(self, *, prompt: str, schema_name: str, schema: dict) -> dict:
        match = re.search(r'"id":\s*"([^"]+)"', prompt)
        assert match is not None
        rubric_item_id = match.group(1)

        with self._lock:
            self._active_calls += 1
            self.max_active_calls = max(self.max_active_calls, self._active_calls)

        try:
            time.sleep(self.delay_seconds)
            self.calls.append(
                {
                    "rubric_item_id": rubric_item_id,
                    "schema_name": schema_name,
                    "schema": schema,
                }
            )
            attempt_index = self.attempts[rubric_item_id]
            self.attempts[rubric_item_id] += 1
            planned = self.plans[rubric_item_id][attempt_index]
            if isinstance(planned, Exception):
                raise planned
            return planned
        finally:
            with self._lock:
                self._active_calls -= 1


class FakeSupervisorClient:
    def __init__(self, payload: dict) -> None:
        self.payload = payload
        self.calls: list[dict] = []

    def generate_structured_output(self, **kwargs) -> dict:
        self.calls.append(kwargs)
        return self.payload


def build_supervisor_payload(
    *,
    hard_requirement_overall: str = "all_pass",
    overall_score_5: float = 4.0,
    overall_score_percent: float = 80.0,
    recommendation: str = "advance",
) -> dict:
    return {
        "hard_requirement_overall": hard_requirement_overall,
        "overall_score_5": overall_score_5,
        "overall_score_percent": overall_score_percent,
        "ai_summary": "Strong recruiter with evidence across core criteria.",
        "evidence_points": ["Built systems", "Improved funnel speed"],
        "tags": ["operator", "recruiting"],
        "recommendation": recommendation,
    }


def build_score_items_result() -> CandidateRubricScoreItemsResult:
    return CandidateRubricScoreItemsResult.model_validate(
        {
            "weighted_results": [
                build_weighted_result("rubric-1", 4.0),
                build_weighted_result("rubric-2", 3.0),
            ],
            "hard_requirement_results": [
                build_hard_requirement_result("rubric-3", "borderline"),
            ],
        }
    )


def test_candidate_rubric_score_schema_validates() -> None:
    result = WeightedRubricResultSchema.model_validate(build_weighted_result("rubric-1", 4.5))
    assert result.score_0_to_5 == 4.5

    hard_result = HardRequirementRubricResultSchema.model_validate(
        build_hard_requirement_result("rubric-2", "pass")
    )
    assert hard_result.hard_requirement_decision == "pass"


def test_candidate_supervisor_schema_rejects_invalid_recommendation() -> None:
    with pytest.raises(ValidationError):
        CandidateSupervisorSchema.model_validate(
            build_supervisor_payload(recommendation="promote")
        )


@pytest.mark.anyio
async def test_score_items_workflow_scores_mixed_rubric_items() -> None:
    rubric_items = build_rubric_items()
    client = FakeScoringClient(
        {
            "rubric-1": [build_weighted_result("rubric-1", 4.0)],
            "rubric-2": [build_weighted_result("rubric-2", 3.0)],
            "rubric-3": [build_hard_requirement_result("rubric-3", "pass")],
        }
    )
    workflow = CandidateScoreItemsWorkflow(client)

    result = await workflow.run(
        PreparedRubricScoringInput(
            prepared_input=build_prepared_input(),
            standardized_candidate=build_standardized_candidate(),
            rubric_items=rubric_items,
        )
    )

    assert len(result.weighted_results) == 2
    assert len(result.hard_requirement_results) == 1
    assert {call["schema_name"] for call in client.calls} == {
        "weighted_rubric_result_schema",
        "hard_requirement_rubric_result_schema",
    }


@pytest.mark.anyio
async def test_score_items_workflow_caps_concurrency_at_six() -> None:
    rubric_items = build_rubric_items(count=8)
    client = FakeScoringClient(
        {
            item["id"]: [
                build_hard_requirement_result(item["id"], "pass")
                if item["criterion_type"] == "hard_requirement"
                else build_weighted_result(item["id"], 4.0)
            ]
            for item in rubric_items
        },
        delay_seconds=0.03,
    )
    workflow = CandidateScoreItemsWorkflow(client, concurrency_limit=6)

    result = await workflow.run(
        PreparedRubricScoringInput(
            prepared_input=build_prepared_input(),
            standardized_candidate=build_standardized_candidate(),
            rubric_items=rubric_items,
        )
    )

    assert len(result.weighted_results) + len(result.hard_requirement_results) == 8
    assert 1 < client.max_active_calls <= 6


@pytest.mark.anyio
async def test_score_items_workflow_retries_once_then_succeeds() -> None:
    rubric_items = build_rubric_items()
    client = FakeScoringClient(
        {
            "rubric-1": [
                ValueError("bad payload"),
                build_weighted_result("rubric-1", 4.0),
            ],
            "rubric-2": [build_weighted_result("rubric-2", 3.0)],
            "rubric-3": [build_hard_requirement_result("rubric-3", "pass")],
        }
    )
    workflow = CandidateScoreItemsWorkflow(client, max_retries=1)

    result = await workflow.run(
        PreparedRubricScoringInput(
            prepared_input=build_prepared_input(),
            standardized_candidate=build_standardized_candidate(),
            rubric_items=rubric_items,
        )
    )

    assert len(result.weighted_results) == 2
    assert client.attempts["rubric-1"] == 2


@pytest.mark.anyio
async def test_score_items_workflow_fails_after_second_attempt() -> None:
    rubric_items = build_rubric_items()
    client = FakeScoringClient(
        {
            "rubric-1": [
                ValueError("bad payload"),
                ValueError("still bad"),
            ],
            "rubric-2": [build_weighted_result("rubric-2", 3.0)],
            "rubric-3": [build_hard_requirement_result("rubric-3", "pass")],
        }
    )
    workflow = CandidateScoreItemsWorkflow(client, max_retries=1)

    with pytest.raises(DomainValidationError, match="after retry"):
        await workflow.run(
            PreparedRubricScoringInput(
                prepared_input=build_prepared_input(),
                standardized_candidate=build_standardized_candidate(),
                rubric_items=rubric_items,
            )
        )

    assert client.attempts["rubric-1"] == 2


def test_supervisor_prompt_contains_computed_scores() -> None:
    prompt = build_candidate_supervisor_prompt(
        job_title="AI Recruiter",
        job_summary="Own hiring for AI teams.",
        standardized_candidate=build_standardized_candidate().model_dump(mode="json"),
        rubric_results=build_score_items_result().model_dump(mode="json"),
        hard_requirement_overall="has_borderline",
        overall_score_5=3.4,
        overall_score_percent=68.0,
    )

    assert "AI Recruiter" in prompt
    assert "has_borderline" in prompt
    assert "3.4" in prompt
    assert "68.0" in prompt


def test_summarize_workflow_uses_computed_scores_and_returns_schema() -> None:
    client = FakeSupervisorClient(
        build_supervisor_payload(
            hard_requirement_overall="has_borderline",
            overall_score_5=3.4,
            overall_score_percent=68.0,
            recommendation="manual_review",
        )
    )
    workflow = CandidateSummarizeWorkflow(client)

    result = workflow.run(
        job_title="AI Recruiter",
        job_summary="Own hiring for AI teams.",
        standardized_candidate=build_standardized_candidate(),
        rubric_score_items=build_score_items_result(),
        hard_requirement_overall="has_borderline",
        overall_score_5=3.4,
        overall_score_percent=68.0,
    )

    assert result.recommendation == "manual_review"
    assert "3.4" in client.calls[0]["prompt"]
    assert "68.0" in client.calls[0]["prompt"]


def test_summarize_workflow_rejects_advance_when_hard_requirement_is_not_all_pass() -> None:
    client = FakeSupervisorClient(
        build_supervisor_payload(
            hard_requirement_overall="has_fail",
            overall_score_5=2.2,
            overall_score_percent=44.0,
            recommendation="advance",
        )
    )
    workflow = CandidateSummarizeWorkflow(client)

    with pytest.raises(DomainValidationError, match="cannot advance"):
        workflow.run(
            job_title="AI Recruiter",
            job_summary="Own hiring for AI teams.",
            standardized_candidate=build_standardized_candidate(),
            rubric_score_items=build_score_items_result(),
            hard_requirement_overall="has_fail",
            overall_score_5=2.2,
            overall_score_percent=44.0,
        )
