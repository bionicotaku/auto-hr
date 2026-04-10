import pytest
from sqlalchemy import func, select

from app.core.exceptions import ConflictError, DomainValidationError
from app.models.candidate import Candidate
from app.repositories.job_repository import JobCreateData, JobRepository, JobRubricItemCreateData
from app.schemas.ai.candidate_rubric_result import CandidateRubricScoreItemsResult
from app.schemas.ai.candidate_standardization import (
    CandidateStandardizationSchema,
    PreparedCandidateImportInput,
)
from app.schemas.ai.candidate_supervisor import CandidateSupervisorSchema
from app.services.candidate_analysis_service import CandidateAnalysisService


class StubImportPrepareWorkflow:
    def __init__(self, result: PreparedCandidateImportInput) -> None:
        self.result = result
        self.calls: list[dict] = []

    async def run(self, **kwargs) -> PreparedCandidateImportInput:
        self.calls.append(kwargs)
        return self.result


class StubStandardizeWorkflow:
    def __init__(self, result: CandidateStandardizationSchema) -> None:
        self.result = result
        self.calls: list[PreparedCandidateImportInput] = []

    def run(self, prepared_input: PreparedCandidateImportInput) -> CandidateStandardizationSchema:
        self.calls.append(prepared_input)
        return self.result


class StubScoreItemsWorkflow:
    def __init__(
        self,
        result: CandidateRubricScoreItemsResult | None = None,
        error: Exception | None = None,
    ) -> None:
        self.result = result
        self.error = error
        self.calls: list = []

    async def run(self, scoring_input):
        self.calls.append(scoring_input)
        if self.error:
            raise self.error
        return self.result


class StubSummarizeWorkflow:
    def __init__(
        self,
        result: CandidateSupervisorSchema | None = None,
        error: Exception | None = None,
    ) -> None:
        self.result = result
        self.error = error
        self.calls: list[dict] = []

    def run(self, **kwargs) -> CandidateSupervisorSchema:
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return self.result


def build_prepared_input() -> PreparedCandidateImportInput:
    return PreparedCandidateImportInput(
        raw_text_input="Candidate raw text",
        job_id="job-001",
        job_title="AI Recruiter",
        job_summary="Own hiring for AI teams.",
        temp_request_id="temp-001",
        documents=[],
    )


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
            "work_experiences": [],
            "educations": [],
            "skills": {
                "skills_raw": ["Recruiting"],
                "skills_normalized": ["recruiting"],
            },
            "employment_preferences": {
                "work_authorization": "US",
                "requires_sponsorship": False,
                "willing_to_relocate": None,
                "preferred_locations": ["Remote"],
                "preferred_work_modes": ["remote"],
            },
            "application_answers": [],
            "documents": [],
            "additional_information": {
                "uncategorized_highlights": [],
                "parser_notes": [],
            },
        }
    )


def build_score_items_result(
    *,
    weighted_result_ids: tuple[str, str],
    hard_requirement_result_id: str,
) -> CandidateRubricScoreItemsResult:
    return CandidateRubricScoreItemsResult.model_validate(
        {
            "weighted_results": [
                {
                    "job_rubric_item_id": weighted_result_ids[0],
                    "criterion_type": "weighted",
                    "score_0_to_5": 4.0,
                    "reason_text": "Strong execution",
                    "evidence_points": ["Built systems"],
                    "uncertainty_note": None,
                },
                {
                    "job_rubric_item_id": weighted_result_ids[1],
                    "criterion_type": "weighted",
                    "score_0_to_5": 2.0,
                    "reason_text": "Mixed signals",
                    "evidence_points": ["Some evidence"],
                    "uncertainty_note": None,
                },
            ],
            "hard_requirement_results": [
                {
                    "job_rubric_item_id": hard_requirement_result_id,
                    "criterion_type": "hard_requirement",
                    "hard_requirement_decision": "borderline",
                    "reason_text": "English evidence is incomplete",
                    "evidence_points": ["Global meetings"],
                    "uncertainty_note": None,
                }
            ],
        }
    )


def build_supervisor_summary() -> CandidateSupervisorSchema:
    return CandidateSupervisorSchema.model_validate(
        {
            "hard_requirement_overall": "has_borderline",
            "overall_score_5": 3.2,
            "overall_score_percent": 64.0,
            "ai_summary": "Promising operator with one borderline requirement.",
            "evidence_points": ["Built systems", "Global meetings"],
            "tags": ["operator", "recruiting"],
            "recommendation": "manual_review",
        }
    )


def create_job(db_session, *, lifecycle_status: str):
    repository = JobRepository()
    job = repository.create_job_with_rubric_items(
        db_session,
        JobCreateData(
            lifecycle_status=lifecycle_status,
            creation_mode="from_description",
            title="AI Recruiter",
            summary="Own hiring for AI teams.",
            description_text="JD body",
            structured_info_json={"department": "Talent"},
            original_description_input="Original description",
            original_form_input_json=None,
            editor_history_summary=None,
            editor_recent_messages_json=[],
        ),
        [
            JobRubricItemCreateData(
                sort_order=1,
                name="Execution",
                description="Can run the funnel",
                criterion_type="weighted",
                weight_input=60,
                weight_normalized=0.6,
                scoring_standard_json={"score_5": "Excellent"},
                agent_prompt_text="Judge execution",
                evidence_guidance_text="Look for outcomes",
            ),
            JobRubricItemCreateData(
                sort_order=2,
                name="Stakeholder management",
                description="Can align hiring managers",
                criterion_type="weighted",
                weight_input=40,
                weight_normalized=0.4,
                scoring_standard_json={"score_5": "Excellent"},
                agent_prompt_text="Judge stakeholder management",
                evidence_guidance_text="Look for alignment",
            ),
            JobRubricItemCreateData(
                sort_order=3,
                name="English collaboration",
                description="Works globally",
                criterion_type="hard_requirement",
                weight_input=100,
                weight_normalized=None,
                scoring_standard_json={"pass_definition": "Can collaborate globally"},
                agent_prompt_text="Judge English collaboration",
                evidence_guidance_text="Look for global work",
            ),
        ],
    )
    db_session.commit()
    return repository.get_job_for_edit(db_session, job.id)


@pytest.mark.anyio
async def test_candidate_analysis_service_returns_bundle_without_writing_candidates(db_session) -> None:
    job = create_job(db_session, lifecycle_status="active")
    weighted_ids = (job.rubric_items[0].id, job.rubric_items[1].id)
    hard_requirement_id = job.rubric_items[2].id
    import_prepare_workflow = StubImportPrepareWorkflow(build_prepared_input())
    standardize_workflow = StubStandardizeWorkflow(build_standardized_candidate())
    score_items_workflow = StubScoreItemsWorkflow(
        result=build_score_items_result(
            weighted_result_ids=weighted_ids,
            hard_requirement_result_id=hard_requirement_id,
        )
    )
    summarize_workflow = StubSummarizeWorkflow(result=build_supervisor_summary())

    service = CandidateAnalysisService(
        db_session,
        JobRepository(),
        import_prepare_workflow,
        standardize_workflow,
        score_items_workflow,
        summarize_workflow,
    )

    bundle = await service.analyze_candidate(
        job_id=job.id,
        raw_text_input="Candidate raw text",
        files=[],
    )

    assert bundle.supervisor_summary.recommendation == "manual_review"
    assert summarize_workflow.calls[0]["hard_requirement_overall"] == "has_borderline"
    assert summarize_workflow.calls[0]["overall_score_5"] == 3.2
    assert summarize_workflow.calls[0]["overall_score_percent"] == 64.0
    assert db_session.scalar(select(func.count()).select_from(Candidate)) == 0


@pytest.mark.anyio
async def test_candidate_analysis_service_rejects_non_active_job(db_session) -> None:
    job = create_job(db_session, lifecycle_status="draft")
    service = CandidateAnalysisService(
        db_session,
        JobRepository(),
        StubImportPrepareWorkflow(build_prepared_input()),
        StubStandardizeWorkflow(build_standardized_candidate()),
        StubScoreItemsWorkflow(
            result=build_score_items_result(
                weighted_result_ids=(job.rubric_items[0].id, job.rubric_items[1].id),
                hard_requirement_result_id=job.rubric_items[2].id,
            )
        ),
        StubSummarizeWorkflow(result=build_supervisor_summary()),
    )

    with pytest.raises(ConflictError):
        await service.analyze_candidate(job_id=job.id, raw_text_input="Candidate raw text", files=[])


@pytest.mark.anyio
async def test_candidate_analysis_service_propagates_score_items_failure(db_session) -> None:
    job = create_job(db_session, lifecycle_status="active")
    summarize_workflow = StubSummarizeWorkflow(result=build_supervisor_summary())
    service = CandidateAnalysisService(
        db_session,
        JobRepository(),
        StubImportPrepareWorkflow(build_prepared_input()),
        StubStandardizeWorkflow(build_standardized_candidate()),
        StubScoreItemsWorkflow(error=DomainValidationError("score failed")),
        summarize_workflow,
    )

    with pytest.raises(DomainValidationError, match="score failed"):
        await service.analyze_candidate(job_id=job.id, raw_text_input="Candidate raw text", files=[])

    assert summarize_workflow.calls == []


@pytest.mark.anyio
async def test_candidate_analysis_service_propagates_summarize_failure(db_session) -> None:
    job = create_job(db_session, lifecycle_status="active")
    service = CandidateAnalysisService(
        db_session,
        JobRepository(),
        StubImportPrepareWorkflow(build_prepared_input()),
        StubStandardizeWorkflow(build_standardized_candidate()),
        StubScoreItemsWorkflow(
            result=build_score_items_result(
                weighted_result_ids=(job.rubric_items[0].id, job.rubric_items[1].id),
                hard_requirement_result_id=job.rubric_items[2].id,
            )
        ),
        StubSummarizeWorkflow(error=DomainValidationError("summary failed")),
    )

    with pytest.raises(DomainValidationError, match="summary failed"):
        await service.analyze_candidate(job_id=job.id, raw_text_input="Candidate raw text", files=[])
