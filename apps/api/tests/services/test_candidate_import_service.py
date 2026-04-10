from io import BytesIO
from pathlib import Path

import pytest
from pypdf import PdfWriter
from sqlalchemy import func, select

from app.core.config import get_settings
from app.core.exceptions import DomainValidationError
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.job_rubric_item import JobRubricItem
from app.repositories.candidate_repository import CandidateRepository
from app.schemas.ai.candidate_rubric_result import CandidateRubricScoreItemsResult
from app.schemas.ai.candidate_standardization import (
    CandidateStandardizationSchema,
    PreparedCandidateDocumentInput,
    PreparedCandidateImportInput,
)
from app.schemas.ai.candidate_supervisor import CandidateSupervisorSchema
from app.services.candidate_analysis_service import CandidateAnalysisBundle
from app.services.candidate_import_service import CandidateImportService
from app.workflows.candidate_analysis.persist import CandidatePersistWorkflow


def build_pdf_bytes() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    buffer = BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def create_active_job(db_session) -> Job:
    job = Job(
        lifecycle_status="active",
        creation_mode="from_description",
        title="AI Recruiter",
        summary="Own hiring.",
        description_text="JD body",
        structured_info_json={"location": "Remote"},
        original_description_input="Original JD",
        original_form_input_json=None,
        editor_history_summary=None,
        editor_recent_messages_json=[],
    )
    db_session.add(job)
    db_session.flush()
    db_session.add_all(
        [
            JobRubricItem(
                job_id=job.id,
                sort_order=1,
                name="Execution",
                description="Owns funnel",
                criterion_type="weighted",
                weight_input=60,
                weight_normalized=0.6,
                scoring_standard_items=[{"key": "score_5", "value": "Excellent"}],
                agent_prompt_text="Judge execution",
                evidence_guidance_text="Look for examples",
            ),
            JobRubricItem(
                job_id=job.id,
                sort_order=2,
                name="Stakeholder management",
                description="Aligns teams",
                criterion_type="weighted",
                weight_input=40,
                weight_normalized=0.4,
                scoring_standard_items=[{"key": "score_5", "value": "Excellent"}],
                agent_prompt_text="Judge stakeholder management",
                evidence_guidance_text="Look for alignment",
            ),
            JobRubricItem(
                job_id=job.id,
                sort_order=3,
                name="English",
                description="Can collaborate globally",
                criterion_type="hard_requirement",
                weight_input=100,
                weight_normalized=None,
                scoring_standard_items=[{"key": "pass_definition", "value": "Can work in English"}],
                agent_prompt_text="Judge English collaboration",
                evidence_guidance_text="Look for global evidence",
            ),
        ]
    )
    db_session.commit()
    db_session.refresh(job)
    return job


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
            "work_experiences": [{"company_name": "Auto HR"}],
            "educations": [{"school_name": "Example University"}],
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
            "application_answers": [{"question_text": "Why?", "answer_text": "Because."}],
            "documents": [],
            "additional_information": {
                "uncategorized_highlights": [],
                "parser_notes": [],
            },
        }
    )


def build_rubric_result(job: Job) -> CandidateRubricScoreItemsResult:
    return CandidateRubricScoreItemsResult.model_validate(
        {
            "weighted_results": [
                {
                    "job_rubric_item_id": job.rubric_items[0].id,
                    "criterion_type": "weighted",
                    "score_0_to_5": 4.0,
                    "reason_text": "Strong execution",
                    "evidence_points": ["Led hiring"],
                    "uncertainty_note": None,
                },
                {
                    "job_rubric_item_id": job.rubric_items[1].id,
                    "criterion_type": "weighted",
                    "score_0_to_5": 3.0,
                    "reason_text": "Good alignment",
                    "evidence_points": ["Worked with stakeholders"],
                    "uncertainty_note": None,
                },
            ],
            "hard_requirement_results": [
                {
                    "job_rubric_item_id": job.rubric_items[2].id,
                    "criterion_type": "hard_requirement",
                    "hard_requirement_decision": "pass",
                    "reason_text": "Has global collaboration evidence",
                    "evidence_points": ["Global meetings"],
                    "uncertainty_note": None,
                }
            ],
        }
    )


def build_supervisor_summary() -> CandidateSupervisorSchema:
    return CandidateSupervisorSchema.model_validate(
        {
            "hard_requirement_overall": "all_pass",
            "overall_score_5": 3.6,
            "overall_score_percent": 72.0,
            "ai_summary": "Strong candidate with clear execution examples.",
            "evidence_points": ["Led hiring", "Worked with stakeholders"],
            "tags": ["operator", "operator", "recruiting"],
            "recommendation": "advance",
        }
    )


def create_temp_document(tmp_dir: Path, request_id: str, filename: str = "resume.pdf") -> Path:
    input_dir = tmp_dir / "candidate-imports" / request_id / "input"
    input_dir.mkdir(parents=True, exist_ok=True)
    path = input_dir / filename
    path.write_bytes(build_pdf_bytes())
    return path


def build_bundle(job: Job, temp_path: Path) -> CandidateAnalysisBundle:
    return CandidateAnalysisBundle(
        prepared_input=PreparedCandidateImportInput(
            raw_text_input="Candidate raw text",
            job_id=job.id,
            job_title=job.title,
            job_summary=job.summary,
            temp_request_id="request-001",
            documents=[
                PreparedCandidateDocumentInput(
                    filename="resume.pdf",
                    storage_path=str(temp_path),
                    mime_type="application/pdf",
                    upload_order=1,
                    extracted_text="resume text",
                    page_count=1,
                )
            ],
        ),
        standardized_candidate=build_standardized_candidate(),
        rubric_score_items=build_rubric_result(job),
        supervisor_summary=build_supervisor_summary(),
    )


class StubCandidateAnalysisService:
    def __init__(
        self,
        *,
        bundle: CandidateAnalysisBundle | None = None,
        error: Exception | None = None,
    ) -> None:
        self.bundle = bundle
        self.error = error

    async def analyze_candidate(self, **_kwargs) -> CandidateAnalysisBundle:
        if self.error:
            raise self.error
        assert self.bundle is not None
        return self.bundle


class FailingCandidateRepository:
    def create_candidate_graph(self, *args, **kwargs):
        raise RuntimeError("db failed")


@pytest.mark.anyio
async def test_candidate_import_service_persists_candidate_and_moves_files(db_session) -> None:
    settings = get_settings()
    job = create_active_job(db_session)
    temp_path = create_temp_document(settings.temp_upload_dir_path, "request-001")
    bundle = build_bundle(job, temp_path)
    service = CandidateImportService(
        db_session,
        StubCandidateAnalysisService(bundle=bundle),
        CandidatePersistWorkflow(settings=settings, candidate_repository=CandidateRepository()),
    )

    response = await service.import_candidate(
        job_id=job.id,
        raw_text_input="Candidate raw text",
        files=[],
    )

    candidate = db_session.get(Candidate, response.candidate_id)
    assert candidate is not None
    assert response.job_id == job.id
    assert len(candidate.documents) == 1
    assert Path(candidate.documents[0].storage_path).exists()
    assert not temp_path.exists()
    assert not (settings.temp_upload_dir_path / "candidate-imports" / "request-001").exists()


@pytest.mark.anyio
async def test_candidate_import_service_cleans_files_when_persist_fails(db_session) -> None:
    settings = get_settings()
    job = create_active_job(db_session)
    temp_path = create_temp_document(settings.temp_upload_dir_path, "request-001")
    bundle = build_bundle(job, temp_path)
    service = CandidateImportService(
        db_session,
        StubCandidateAnalysisService(bundle=bundle),
        CandidatePersistWorkflow(settings=settings, candidate_repository=FailingCandidateRepository()),
    )

    with pytest.raises(DomainValidationError, match="persist candidate import"):
        await service.import_candidate(job_id=job.id, raw_text_input="Candidate raw text", files=[])

    assert db_session.scalar(select(func.count()).select_from(Candidate)) == 0
    candidates_dir = settings.upload_dir_path / "candidates"
    assert not candidates_dir.exists() or list(candidates_dir.iterdir()) == []
    assert not (settings.temp_upload_dir_path / "candidate-imports" / "request-001").exists()


@pytest.mark.anyio
async def test_candidate_import_service_propagates_analysis_failure(db_session) -> None:
    settings = get_settings()
    job = create_active_job(db_session)
    service = CandidateImportService(
        db_session,
        StubCandidateAnalysisService(error=DomainValidationError("analysis failed")),
        CandidatePersistWorkflow(settings=settings, candidate_repository=CandidateRepository()),
    )

    with pytest.raises(DomainValidationError, match="analysis failed"):
        await service.import_candidate(job_id=job.id, raw_text_input="Candidate raw text", files=[])


@pytest.mark.anyio
async def test_candidate_import_service_surfaces_value_error_message(db_session) -> None:
    settings = get_settings()
    job = create_active_job(db_session)
    service = CandidateImportService(
        db_session,
        StubCandidateAnalysisService(error=ValueError("pdf parse failed")),
        CandidatePersistWorkflow(settings=settings, candidate_repository=CandidateRepository()),
    )

    with pytest.raises(DomainValidationError, match="pdf parse failed"):
        await service.import_candidate(job_id=job.id, raw_text_input="Candidate raw text", files=[])
