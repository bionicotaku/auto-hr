from app.api import service_deps
from app.core.exceptions import ConflictError, DomainValidationError
from app.repositories.job_repository import JobRepository
from app.schemas.ai.job_definition import (
    JobAgentEditResponseSchema,
    JobChatResponseSchema,
    JobDraftSchema,
    JobFinalizeResponseSchema,
)
from app.schemas.jobs import CandidateImportResponse
from app.services.job_service import JobService


class StubWorkflow:
    def from_description(self, _description_text: str):
        return self._draft()

    def from_form(self, _form_payload: dict):
        return self._draft()

    def _draft(self) -> JobDraftSchema:
        return JobDraftSchema.model_validate(
            {
                "title": "AI Recruiting Lead",
                "summary": "Build the recruiting engine.",
                "description_text": "JD body",
                "structured_info_json": {
                    "department": "Talent",
                    "location": "Remote",
                    "employment_type": "Full-time",
                    "seniority_level": "Lead",
                    "responsibilities": ["Run hiring"],
                    "requirements": ["Experience"],
                    "skills": ["Leadership"],
                },
                "rubric_items": [
                    {
                        "sort_order": 1,
                        "name": "Execution",
                        "description": "Runs hiring funnel",
                        "criterion_type": "weighted",
                        "weight_input": 80,
                        "weight_normalized": 0.8,
                        "scoring_standard_json": {"score_5": "Excellent"},
                        "agent_prompt_text": "Judge execution",
                        "evidence_guidance_text": "Look for examples",
                    }
                ],
            }
        )


class StubChatWorkflow:
    def run(self, **_kwargs):
        return JobChatResponseSchema(reply_text="请把必须项单独列出。")


class StubAgentEditWorkflow:
    def run(self, **_kwargs):
        return JobAgentEditResponseSchema(
            description_text="Updated JD body",
            rubric_items=StubWorkflow()._draft().rubric_items,
        )


class StubRegenerateWorkflow:
    def run(self, **_kwargs):
        return JobAgentEditResponseSchema(
            description_text="Regenerated JD body",
            rubric_items=StubWorkflow()._draft().rubric_items,
        )


class StubFinalizeWorkflow:
    def run(self, **_kwargs):
        return JobFinalizeResponseSchema.model_validate(
            {
                "title": "Final Recruiting Lead",
                "summary": "Final summary",
                "description_text": "Final JD body",
                "structured_info_json": {
                    "department": "Talent",
                    "location": "Remote",
                    "employment_type": "Full-time",
                    "seniority_level": "Lead",
                    "responsibilities": ["Run hiring"],
                    "requirements": ["Experience"],
                    "skills": ["Leadership"],
                },
                "rubric_items": [
                    {
                        "sort_order": 1,
                        "name": "Execution",
                        "description": "Runs hiring funnel",
                        "criterion_type": "weighted",
                        "weight_input": 80,
                        "weight_normalized": 0.8,
                        "scoring_standard_json": {"score_5": "Excellent"},
                        "agent_prompt_text": "Judge execution",
                        "evidence_guidance_text": "Look for examples",
                    }
                ],
            }
        )


class StubCandidateImportService:
    def __init__(self, *, error: Exception | None = None):
        self.error = error

    async def import_candidate(self, **_kwargs):
        if self.error:
            raise self.error
        return CandidateImportResponse(candidate_id="candidate-001", job_id="job-001")


def override_job_service(session, _settings):
    return JobService(
        session,
        JobRepository(),
        StubWorkflow(),
        chat_workflow=StubChatWorkflow(),
        agent_edit_workflow=StubAgentEditWorkflow(),
        regenerate_workflow=StubRegenerateWorkflow(),
        finalize_workflow=StubFinalizeWorkflow(),
    )


def override_candidate_import_service(_session, _settings):
    return StubCandidateImportService()


def test_create_job_from_description_returns_job_id(client, monkeypatch) -> None:
    monkeypatch.setattr(service_deps, "get_job_service", override_job_service)

    response = client.post(
        "/api/jobs/from-description",
        json={"description_text": "A long enough original job description for testing."},
    )

    assert response.status_code == 201
    assert response.json()["job_id"]
    assert response.json()["lifecycle_status"] == "draft"


def test_create_job_from_form_validates_input(client, monkeypatch) -> None:
    monkeypatch.setattr(service_deps, "get_job_service", override_job_service)

    response = client.post(
        "/api/jobs/from-form",
        json={"job_title": ""},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request"


def test_delete_job_draft_returns_no_content(client, monkeypatch) -> None:
    monkeypatch.setattr(service_deps, "get_job_service", override_job_service)

    create_response = client.post(
        "/api/jobs/from-description",
        json={"description_text": "A long enough original job description for testing."},
    )
    job_id = create_response.json()["job_id"]

    delete_response = client.delete(f"/api/jobs/{job_id}/draft")
    assert delete_response.status_code == 204


def test_chat_endpoint_returns_reply_text(client, monkeypatch) -> None:
    monkeypatch.setattr(service_deps, "get_job_service", override_job_service)

    create_response = client.post(
        "/api/jobs/from-description",
        json={"description_text": "A long enough original job description for testing."},
    )
    job_id = create_response.json()["job_id"]

    response = client.post(
        f"/api/jobs/{job_id}/chat",
        json={
            "description_text": "Current local description",
            "rubric_items": [
                {
                    "sort_order": 1,
                    "name": "Execution",
                    "description": "Runs hiring funnel",
                    "criterion_type": "weighted",
                    "weight_input": 80,
                    "weight_normalized": 0.8,
                    "scoring_standard_json": {"score_5": "Excellent"},
                    "agent_prompt_text": "Judge execution",
                    "evidence_guidance_text": "Look for examples",
                }
            ],
            "recent_messages": [],
            "user_input": "给我修改建议",
        },
    )

    assert response.status_code == 200
    assert response.json()["reply_text"] == "请把必须项单独列出。"


def test_agent_edit_endpoint_returns_generated_content(client, monkeypatch) -> None:
    monkeypatch.setattr(service_deps, "get_job_service", override_job_service)

    create_response = client.post(
        "/api/jobs/from-description",
        json={"description_text": "A long enough original job description for testing."},
    )
    job_id = create_response.json()["job_id"]

    response = client.post(
        f"/api/jobs/{job_id}/agent-edit",
        json={
            "description_text": "Current local description",
            "rubric_items": [
                {
                    "sort_order": 1,
                    "name": "Execution",
                    "description": "Runs hiring funnel",
                    "criterion_type": "weighted",
                    "weight_input": 80,
                    "weight_normalized": 0.8,
                    "scoring_standard_json": {"score_5": "Excellent"},
                    "agent_prompt_text": "Judge execution",
                    "evidence_guidance_text": "Look for examples",
                }
            ],
            "recent_messages": [],
            "user_input": "直接改写",
        },
    )

    assert response.status_code == 200
    assert response.json()["description_text"] == "Updated JD body"
    assert len(response.json()["rubric_items"]) == 1


def test_regenerate_endpoint_rejects_extra_fields(client, monkeypatch) -> None:
    monkeypatch.setattr(service_deps, "get_job_service", override_job_service)

    create_response = client.post(
        "/api/jobs/from-description",
        json={"description_text": "A long enough original job description for testing."},
    )
    job_id = create_response.json()["job_id"]

    response = client.post(
        f"/api/jobs/{job_id}/regenerate",
        json={
            "recent_messages": [],
            "history_summary": None,
            "description_text": "should not be accepted",
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request"


def test_finalize_endpoint_returns_active_job_id(client, monkeypatch) -> None:
    monkeypatch.setattr(service_deps, "get_job_service", override_job_service)

    create_response = client.post(
        "/api/jobs/from-description",
        json={"description_text": "A long enough original job description for testing."},
    )
    job_id = create_response.json()["job_id"]

    response = client.post(
        f"/api/jobs/{job_id}/finalize",
        json={
            "description_text": "Current finalized description",
            "rubric_items": [
                {
                    "sort_order": 1,
                    "name": "Execution",
                    "description": "Runs hiring funnel",
                    "criterion_type": "weighted",
                    "weight_input": 80,
                    "weight_normalized": 0.8,
                    "scoring_standard_json": {"score_5": "Excellent"},
                    "agent_prompt_text": "Judge execution",
                    "evidence_guidance_text": "Look for examples",
                }
            ],
        },
    )

    assert response.status_code == 200
    assert response.json()["job_id"] == job_id
    assert response.json()["lifecycle_status"] == "active"


def test_candidate_import_context_endpoint_returns_job_context(client, monkeypatch) -> None:
    monkeypatch.setattr(service_deps, "get_job_service", override_job_service)

    create_response = client.post(
        "/api/jobs/from-description",
        json={"description_text": "A long enough original job description for testing."},
    )
    job_id = create_response.json()["job_id"]

    response = client.get(f"/api/jobs/{job_id}/candidate-import-context")

    assert response.status_code == 200
    assert response.json() == {
        "job_id": job_id,
        "title": "AI Recruiting Lead",
        "summary": "Build the recruiting engine.",
        "lifecycle_status": "draft",
    }


def test_candidate_import_context_endpoint_returns_not_found(client, monkeypatch) -> None:
    monkeypatch.setattr(service_deps, "get_job_service", override_job_service)

    response = client.get("/api/jobs/missing-job/candidate-import-context")

    assert response.status_code == 404


def test_candidate_import_endpoint_returns_candidate_id(client, monkeypatch) -> None:
    monkeypatch.setattr(service_deps, "get_candidate_import_service", override_candidate_import_service)

    response = client.post(
        "/api/jobs/job-001/candidates/import",
        data={"raw_text_input": "Candidate raw text"},
    )

    assert response.status_code == 201
    assert response.json() == {"candidate_id": "candidate-001", "job_id": "job-001"}


def test_candidate_import_endpoint_returns_conflict_for_draft_job(client, monkeypatch) -> None:
    monkeypatch.setattr(
        service_deps,
        "get_candidate_import_service",
        lambda _session, _settings: StubCandidateImportService(
            error=ConflictError("Job job-001 is not ready for candidate analysis.")
        ),
    )

    response = client.post(
        "/api/jobs/job-001/candidates/import",
        data={"raw_text_input": "Candidate raw text"},
    )

    assert response.status_code == 409
    assert response.json()["error"]["message"] == "Job job-001 is not ready for candidate analysis."


def test_candidate_import_endpoint_returns_validation_error(client, monkeypatch) -> None:
    monkeypatch.setattr(
        service_deps,
        "get_candidate_import_service",
        lambda _session, _settings: StubCandidateImportService(
            error=DomainValidationError("Candidate import requires text input or at least one PDF.")
        ),
    )

    response = client.post("/api/jobs/job-001/candidates/import")

    assert response.status_code == 422
    assert response.json()["error"]["message"] == "Candidate import requires text input or at least one PDF."
