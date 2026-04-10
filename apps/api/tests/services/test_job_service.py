import pytest

from app.repositories.job_repository import JobRepository
from app.schemas.ai.job_definition import JobAgentEditResponseSchema, JobChatResponseSchema, JobDraftSchema
from app.schemas.jobs import (
    CreateJobFromDescriptionRequest,
    CreateJobFromFormRequest,
    JobAgentEditRequest,
    JobChatRequest,
    JobRegenerateRequest,
)
from app.services.job_service import JobService


class StubWorkflow:
    def __init__(self, result=None, error: Exception | None = None):
        self.result = result
        self.error = error

    def from_description(self, _description_text: str):
        if self.error:
            raise self.error
        return self.result

    def from_form(self, _form_payload: dict):
        if self.error:
            raise self.error
        return self.result


class StubChatWorkflow:
    def __init__(self):
        self.calls: list[dict] = []

    def run(self, **kwargs):
        self.calls.append(kwargs)
        return JobChatResponseSchema(reply_text="建议保持职责结构清晰。")


class StubAgentEditWorkflow:
    def __init__(self):
        self.calls: list[dict] = []

    def run(self, **kwargs):
        self.calls.append(kwargs)
        return JobAgentEditResponseSchema(
            description_text="New JD body",
            rubric_items=make_job_draft().rubric_items,
        )


class StubRegenerateWorkflow:
    def __init__(self):
        self.calls: list[dict] = []

    def run(self, **kwargs):
        self.calls.append(kwargs)
        return JobAgentEditResponseSchema(
            description_text="Regenerated JD body",
            rubric_items=make_job_draft().rubric_items,
        )


def make_job_draft() -> JobDraftSchema:
    return JobDraftSchema.model_validate(
        {
            "title": "Recruiting Lead",
            "summary": "Build the recruiting motion.",
            "description_text": "JD body",
            "structured_info_json": {
                "department": "Talent",
                "location": "Remote",
                "employment_type": "Full-time",
                "seniority_level": "Lead",
                "responsibilities": ["Run hiring"],
                "requirements": ["Strong recruiting"],
                "skills": ["Leadership"],
            },
            "rubric_items": [
                {
                    "sort_order": 1,
                    "name": "Recruiting execution",
                    "description": "Can run the funnel",
                    "criterion_type": "weighted",
                    "weight_input": 60,
                    "weight_normalized": 0.6,
                    "scoring_standard_json": {"score_5": "Excellent"},
                    "agent_prompt_text": "Judge execution",
                    "evidence_guidance_text": "Look for hiring throughput",
                },
                {
                    "sort_order": 2,
                    "name": "English collaboration",
                    "description": "Works globally",
                    "criterion_type": "hard_requirement",
                    "weight_input": 100,
                    "weight_normalized": None,
                    "scoring_standard_json": {"pass_definition": "Can collaborate globally"},
                    "agent_prompt_text": "Judge English collaboration",
                    "evidence_guidance_text": "Look for cross-border work",
                },
            ],
        }
    )


def test_create_draft_from_description_persists_job(db_session) -> None:
    service = JobService(db_session, JobRepository(), StubWorkflow(result=make_job_draft()))

    response = service.create_draft_from_description(
        CreateJobFromDescriptionRequest(description_text="A long enough original job description.")
    )

    loaded = service.get_job_edit_payload(response.job_id)
    assert response.lifecycle_status == "draft"
    assert loaded.creation_mode == "from_description"
    assert len(loaded.rubric_items) == 2


def test_create_draft_from_form_persists_job(db_session) -> None:
    service = JobService(db_session, JobRepository(), StubWorkflow(result=make_job_draft()))

    response = service.create_draft_from_form(
        CreateJobFromFormRequest(
            job_title="AI Recruiter",
            department="Talent",
            location="Remote",
            employment_type="Full-time",
        )
    )

    loaded = service.get_job_edit_payload(response.job_id)
    assert loaded.creation_mode == "from_form"
    assert loaded.original_form_input_json["job_title"] == "AI Recruiter"


def test_workflow_failure_does_not_create_dirty_draft(db_session) -> None:
    service = JobService(
        db_session,
        JobRepository(),
        StubWorkflow(error=ValueError("llm failed")),
    )

    with pytest.raises(ValueError):
        service.create_draft_from_description(
            CreateJobFromDescriptionRequest(description_text="A long enough original job description.")
        )

    assert JobRepository().list_jobs(db_session) == []


def test_chat_on_draft_does_not_persist_editor_changes(db_session) -> None:
    chat_workflow = StubChatWorkflow()
    service = JobService(
        db_session,
        JobRepository(),
        StubWorkflow(result=make_job_draft()),
        chat_workflow=chat_workflow,
    )
    created = service.create_draft_from_description(
        CreateJobFromDescriptionRequest(description_text="Original raw description input.")
    )

    response = service.chat_on_draft(
        created.job_id,
        JobChatRequest(
            description_text="Locally edited description",
            rubric_items=service.get_job_edit_payload(created.job_id).rubric_items,
            recent_messages=[{"role": "user", "content": "先给建议"}],
            user_input="请给建议",
        ),
    )

    loaded = service.get_job_edit_payload(created.job_id)
    assert response.reply_text == "建议保持职责结构清晰。"
    assert loaded.description_text == "JD body"
    assert chat_workflow.calls[0]["description_text"] == "Locally edited description"


def test_agent_edit_on_draft_returns_generated_content_without_writing(db_session) -> None:
    agent_workflow = StubAgentEditWorkflow()
    service = JobService(
        db_session,
        JobRepository(),
        StubWorkflow(result=make_job_draft()),
        agent_edit_workflow=agent_workflow,
    )
    created = service.create_draft_from_description(
        CreateJobFromDescriptionRequest(description_text="Original raw description input.")
    )

    response = service.agent_edit_draft(
        created.job_id,
        JobAgentEditRequest(
            description_text="Locally edited description",
            rubric_items=service.get_job_edit_payload(created.job_id).rubric_items,
            recent_messages=[],
            user_input="直接应用新的版本",
        ),
    )

    loaded = service.get_job_edit_payload(created.job_id)
    assert response.description_text == "New JD body"
    assert loaded.description_text == "JD body"
    assert agent_workflow.calls[0]["user_input"] == "直接应用新的版本"


def test_regenerate_uses_original_input_not_current_description(db_session) -> None:
    regenerate_workflow = StubRegenerateWorkflow()
    service = JobService(
        db_session,
        JobRepository(),
        StubWorkflow(result=make_job_draft()),
        regenerate_workflow=regenerate_workflow,
    )
    created = service.create_draft_from_description(
        CreateJobFromDescriptionRequest(description_text="Original raw description input.")
    )

    response = service.regenerate_draft(
        created.job_id,
        JobRegenerateRequest(
            recent_messages=[{"role": "assistant", "content": "此前建议"}],
            history_summary=None,
        ),
    )

    assert response.description_text == "Regenerated JD body"
    assert regenerate_workflow.calls[0]["original_description_input"] == "Original raw description input."
    assert "description_text" not in regenerate_workflow.calls[0]
