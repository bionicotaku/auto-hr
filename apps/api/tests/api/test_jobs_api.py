from app.api import service_deps
from app.repositories.job_repository import JobRepository
from app.schemas.ai.job_definition import JobAgentEditResponseSchema, JobChatResponseSchema, JobDraftSchema
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


def override_job_service(session, _settings):
    return JobService(
        session,
        JobRepository(),
        StubWorkflow(),
        chat_workflow=StubChatWorkflow(),
        agent_edit_workflow=StubAgentEditWorkflow(),
        regenerate_workflow=StubRegenerateWorkflow(),
    )


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
