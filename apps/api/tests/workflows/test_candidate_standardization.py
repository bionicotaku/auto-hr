from io import BytesIO

import pytest
from fastapi import UploadFile
from pypdf import PdfWriter

from app.ai.prompts.candidate_standardization import build_candidate_standardization_prompt
from app.core.exceptions import DomainValidationError
from app.files.temp_manager import TempImportManager
from app.repositories.job_repository import JobRepository
from app.schemas.ai.candidate_standardization import (
    CandidateStandardizationSchema,
    PreparedCandidateDocumentInput,
    PreparedCandidateImportInput,
)
from app.services.job_service import JobService
from app.workflows.candidate_analysis.import_prepare import CandidateImportPrepareWorkflow
from app.workflows.candidate_analysis.standardize import CandidateStandardizeWorkflow


class FakeStructuredClient:
    def __init__(self, payload):
        self.payload = payload
        self.calls: list[dict] = []

    def generate_structured_output_from_inputs(self, **kwargs):
        self.calls.append(kwargs)
        return self.payload


class StubDraftWorkflow:
    def from_description(self, _description_text: str):
        from app.schemas.ai.job_definition import JobDraftSchema

        return JobDraftSchema.model_validate(
            {
                "title": "AI Recruiter",
                "summary": "Own hiring for AI teams.",
                "description_text": "Draft JD",
                "structured_info_json": {
                    "department": "Talent",
                    "location": "Remote",
                    "employment_type": "Full-time",
                    "seniority_level": "Lead",
                    "responsibilities": ["Lead hiring"],
                    "requirements": ["Recruiting depth"],
                    "skills": ["Communication"],
                },
                "rubric_items": [
                    {
                        "sort_order": 1,
                        "name": "Execution",
                        "description": "Runs hiring funnel",
                        "criterion_type": "weighted",
                        "weight_input": 100,
                        "weight_normalized": 1.0,
                        "scoring_standard_items": [{"key": "score_5", "value": "Excellent"}],
                        "agent_prompt_text": "Judge execution",
                        "evidence_guidance_text": "Look for examples",
                    }
                ],
            }
        )


def build_standardization_payload() -> dict:
    return {
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


def build_pdf_bytes() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    buffer = BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def make_pdf_upload(tmp_path, filename: str = "resume.pdf") -> UploadFile:
    file_handle = (tmp_path / filename).open("wb+")
    file_handle.write(build_pdf_bytes())
    file_handle.seek(0)
    return UploadFile(filename=filename, file=file_handle, headers={"content-type": "application/pdf"})


def create_job_draft(db_session) -> str:
    from app.schemas.jobs import CreateJobFromDescriptionRequest

    service = JobService(db_session, JobRepository(), StubDraftWorkflow())
    response = service.create_draft_from_description(
        CreateJobFromDescriptionRequest(description_text="A long enough original job description.")
    )
    return response.job_id


def test_candidate_standardization_schema_validates_full_payload() -> None:
    schema = CandidateStandardizationSchema.model_validate(build_standardization_payload())
    assert schema.identity.full_name == "Ada Lovelace"
    assert len(schema.work_experiences) == 1


def test_candidate_standardization_schema_rejects_missing_sections() -> None:
    invalid = build_standardization_payload()
    invalid.pop("identity")

    with pytest.raises(Exception):
        CandidateStandardizationSchema.model_validate(invalid)


def test_candidate_standardization_prompt_contains_required_context() -> None:
    prompt = build_candidate_standardization_prompt(
        job_title="AI Recruiter",
        job_summary="Own hiring for AI teams.",
        raw_text_input="Candidate raw text",
    )

    assert "AI Recruiter" in prompt
    assert "Candidate raw text" in prompt
    assert "JSON Schema" in prompt
    assert "缺失字段也必须保留" in prompt


def test_standardize_workflow_supports_text_only_input() -> None:
    client = FakeStructuredClient(build_standardization_payload())
    workflow = CandidateStandardizeWorkflow(client)
    prepared_input = PreparedCandidateImportInput(
        raw_text_input="Candidate raw text",
        job_id="job-001",
        job_title="AI Recruiter",
        job_summary="Own hiring for AI teams.",
        temp_request_id="temp-001",
        documents=[],
    )

    response = workflow.run(prepared_input)

    assert isinstance(response, CandidateStandardizationSchema)
    content = client.calls[0]["inputs"][0]["content"]
    assert len(content) == 1
    assert content[0]["type"] == "input_text"


def test_standardize_workflow_adds_input_files_when_documents_exist() -> None:
    client = FakeStructuredClient(build_standardization_payload())
    workflow = CandidateStandardizeWorkflow(client)
    prepared_input = PreparedCandidateImportInput(
        raw_text_input=None,
        job_id="job-001",
        job_title="AI Recruiter",
        job_summary="Own hiring for AI teams.",
        temp_request_id="temp-001",
        documents=[
            PreparedCandidateDocumentInput(
                filename="resume.pdf",
                storage_path="/tmp/resume.pdf",
                mime_type="application/pdf",
                upload_order=1,
                extracted_text="resume text",
                page_count=1,
            )
        ],
    )

    workflow.run(prepared_input)

    content = client.calls[0]["inputs"][0]["content"]
    assert any(item["type"] == "input_file" for item in content)


def test_standardize_workflow_rejects_invalid_payload() -> None:
    client = FakeStructuredClient({"identity": {}})
    workflow = CandidateStandardizeWorkflow(client)
    prepared_input = PreparedCandidateImportInput(
        raw_text_input="Candidate raw text",
        job_id="job-001",
        job_title="AI Recruiter",
        job_summary="Own hiring for AI teams.",
        temp_request_id="temp-001",
        documents=[],
    )

    with pytest.raises(ValueError):
        workflow.run(prepared_input)


@pytest.mark.anyio
async def test_import_prepare_workflow_supports_text_only_input(db_session, monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("TEMP_UPLOAD_DIR", str(tmp_path / "tmp"))
    from app.core.config import get_settings

    get_settings.cache_clear()
    job_id = create_job_draft(db_session)
    workflow = CandidateImportPrepareWorkflow(
        job_repository=JobRepository(),
        temp_import_manager=TempImportManager(get_settings()),
    )

    prepared = await workflow.run(
        session=db_session,
        job_id=job_id,
        raw_text_input="Candidate raw text",
        files=[],
    )

    assert prepared.raw_text_input == "Candidate raw text"
    assert prepared.documents == []


@pytest.mark.anyio
async def test_import_prepare_workflow_supports_file_only_input(db_session, monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("TEMP_UPLOAD_DIR", str(tmp_path / "tmp"))
    from app.core.config import get_settings

    get_settings.cache_clear()
    job_id = create_job_draft(db_session)
    workflow = CandidateImportPrepareWorkflow(
        job_repository=JobRepository(),
        temp_import_manager=TempImportManager(get_settings()),
    )
    upload = make_pdf_upload(tmp_path)

    try:
        prepared = await workflow.run(
            session=db_session,
            job_id=job_id,
            raw_text_input=None,
            files=[upload],
        )
    finally:
        upload.file.close()

    assert prepared.raw_text_input is None
    assert len(prepared.documents) == 1
    assert prepared.documents[0].page_count == 1


@pytest.mark.anyio
async def test_import_prepare_workflow_rejects_invalid_input(db_session, monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("TEMP_UPLOAD_DIR", str(tmp_path / "tmp"))
    from app.core.config import get_settings

    get_settings.cache_clear()
    job_id = create_job_draft(db_session)
    workflow = CandidateImportPrepareWorkflow(
        job_repository=JobRepository(),
        temp_import_manager=TempImportManager(get_settings()),
    )

    with pytest.raises(DomainValidationError):
        await workflow.run(
            session=db_session,
            job_id=job_id,
            raw_text_input="   ",
            files=[],
        )
