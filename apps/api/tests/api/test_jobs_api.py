from app.api import service_deps
from app.core.exceptions import ConflictError, DomainValidationError
from app.repositories.job_repository import JobRepository
from app.schemas.ai.job_definition import (
    JobAgentEditResponseSchema,
    JobChatResponseSchema,
    JobDraftSchema,
    JobFinalizeScoringResponseSchema,
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
            responsibilities=["Own funnel", "Publish scorecards"],
            skills=["Hiring ops", "Stakeholder communication"],
            rubric_items=StubWorkflow()._draft().rubric_items,
        )


class StubFinalizeWorkflow:
    def run(self, **_kwargs):
        return JobFinalizeScoringResponseSchema.model_validate(
            {
                "title": "Final AI Recruiting Lead",
                "summary": "Lead recruiting execution and quality calibration.",
                "rubric_items": [
                    {
                        "sort_order": 1,
                        "scoring_standard_items": [{"key": "score_5", "value": "Excellent"}],
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


class StubJobQueryService:
    def list_jobs(self):
        return {
            "items": [
                {
                    "job_id": "job-001",
                    "title": "AI Recruiting Lead",
                    "summary": "Build the recruiting engine.",
                    "lifecycle_status": "active",
                    "candidate_count": 2,
                    "updated_at": "2026-04-09T00:00:00Z",
                }
            ]
        }

    def get_job_detail(self, job_id: str):
        return {
            "job_id": job_id,
            "title": "AI Recruiting Lead",
            "summary": "Build the recruiting engine.",
            "description_text": "JD body",
            "lifecycle_status": "active",
            "candidate_count": 2,
            "rubric_summary": [
                {
                    "name": "Execution",
                    "criterion_type": "weighted",
                    "weight_label": "80%",
                }
            ],
            "structured_info_summary": [
                {
                    "label": "地点",
                    "value": "Remote",
                }
            ],
        }

    def list_job_candidates(self, **_kwargs):
        return {
            "items": [
                {
                    "candidate_id": "candidate-001",
                    "full_name": "Ada Lovelace",
                    "ai_summary": "Strong operator",
                    "overall_score_percent": 92.0,
                    "current_status": "pending",
                    "tags": ["高匹配"],
                    "created_at": "2026-04-09T00:00:00Z",
                }
            ],
            "available_tags": ["高匹配", "需要复核"],
        }


def override_job_service(session, _settings):
    return JobService(
        session,
        JobRepository(),
        StubWorkflow(),
        chat_workflow=StubChatWorkflow(),
        agent_edit_workflow=StubAgentEditWorkflow(),
        finalize_workflow=StubFinalizeWorkflow(),
    )


def override_candidate_import_service(_session, _settings):
    return StubCandidateImportService()


def override_job_query_service(_session, _settings):
    return StubJobQueryService()


def test_create_job_from_description_returns_job_id(client, monkeypatch) -> None:
    monkeypatch.setattr(service_deps, "get_job_service", override_job_service)

    response = client.post(
        "/api/jobs/from-description",
        json={"description_text": "A long enough original job description for testing."},
    )

    assert response.status_code == 201
    assert response.json()["job_id"]
    assert response.json()["lifecycle_status"] == "draft"


def test_create_job_from_description_accepts_short_non_empty_input(client, monkeypatch) -> None:
    monkeypatch.setattr(service_deps, "get_job_service", override_job_service)

    response = client.post(
        "/api/jobs/from-description",
        json={"description_text": "短描述"},
    )

    assert response.status_code == 201
    assert response.json()["job_id"]


def test_create_job_from_form_validates_input(client, monkeypatch) -> None:
    monkeypatch.setattr(service_deps, "get_job_service", override_job_service)

    response = client.post(
        "/api/jobs/from-form",
        json={"job_title": ""},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request"
    assert response.json()["error"]["message"] == "job_title: Value error, job_title must not be empty."


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
            "responsibilities": ["Run kickoff"],
            "skills": ["Recruiting ops"],
            "rubric_items": [
                {
                    "sort_order": 1,
                    "name": "Execution",
                    "description": "Runs hiring funnel",
                    "criterion_type": "weighted",
                    "weight_input": 80,
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
            "responsibilities": ["Run kickoff"],
            "skills": ["Recruiting ops"],
            "rubric_items": [
                {
                    "sort_order": 1,
                    "name": "Execution",
                    "description": "Runs hiring funnel",
                    "criterion_type": "weighted",
                    "weight_input": 80,
                }
            ],
            "recent_messages": [],
            "user_input": "直接改写",
        },
    )

    assert response.status_code == 200
    assert response.json()["description_text"] == "Updated JD body"
    assert response.json()["responsibilities"] == ["Own funnel", "Publish scorecards"]
    assert response.json()["skills"] == ["Hiring ops", "Stakeholder communication"]
    assert len(response.json()["rubric_items"]) == 1


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
            "responsibilities": ["Run kickoff"],
            "skills": ["Recruiting ops"],
            "rubric_items": [
                {
                    "sort_order": 1,
                    "name": "Execution",
                    "description": "Runs hiring funnel",
                    "criterion_type": "weighted",
                    "weight_input": 80,
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


def test_jobs_list_endpoint_returns_items(client, monkeypatch) -> None:
    monkeypatch.setattr(service_deps, "get_job_query_service", override_job_query_service)

    response = client.get("/api/jobs")

    assert response.status_code == 200
    assert response.json()["items"][0]["job_id"] == "job-001"


def test_job_detail_endpoint_returns_summary(client, monkeypatch) -> None:
    monkeypatch.setattr(service_deps, "get_job_query_service", override_job_query_service)

    response = client.get("/api/jobs/job-001")

    assert response.status_code == 200
    assert response.json()["candidate_count"] == 2
    assert response.json()["rubric_summary"][0]["name"] == "Execution"


def test_job_candidates_endpoint_returns_filtered_list_payload(client, monkeypatch) -> None:
    monkeypatch.setattr(service_deps, "get_job_query_service", override_job_query_service)

    response = client.get("/api/jobs/job-001/candidates", params={"sort": "score_desc", "status": "all"})

    assert response.status_code == 200
    assert response.json()["items"][0]["candidate_id"] == "candidate-001"
    assert response.json()["available_tags"] == ["高匹配", "需要复核"]
