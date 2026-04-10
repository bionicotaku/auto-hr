import asyncio

import pytest
from pydantic import ValidationError

from app.core.exceptions import DomainValidationError
from app.repositories.job_repository import JobRepository
from app.schemas.ai.job_definition import (
    JobAgentEditResponseSchema,
    JobChatResponseSchema,
    JobDraftSchema,
    JobFinalizeScoringResponseSchema,
)
from app.schemas.jobs import (
    CreateJobFromDescriptionRequest,
    CreateJobFromFormRequest,
    JobAgentEditRequest,
    JobChatRequest,
    JobFinalizeRequest,
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
            title="New Recruiting Lead",
            summary="Lead the recruiting motion with stronger hiring discipline.",
            description_text="New JD body",
            structured_info_json={
                "department": "Talent",
                "location": "Hybrid",
                "employment_type": "Full-time",
                "seniority_level": "Lead",
                "responsibilities": ["Own funnel", "Coordinate interview loop"],
                "requirements": ["Recruiting depth"],
                "skills": ["Hiring ops", "Stakeholder management"],
            },
            rubric_items=make_job_draft().rubric_items,
        )


class StubFinalizeWorkflow:
    def __init__(self, result=None, error: Exception | None = None):
        self.calls: list[dict] = []
        self.result = result
        self.error = error

    async def run(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return self.result


def run_finalize(service: JobService, job_id: str, payload: JobFinalizeRequest):
    return asyncio.run(service.finalize_draft(job_id, payload))


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
                },
                {
                    "sort_order": 2,
                    "name": "English collaboration",
                    "description": "Works globally",
                    "criterion_type": "hard_requirement",
                    "weight_input": 100,
                },
            ],
        }
    )


def make_finalize_result(
    weight_input: float = 35,
    secondary_weight_input: float = 15,
) -> JobFinalizeScoringResponseSchema:
    return JobFinalizeScoringResponseSchema.model_validate(
        {
            "title": "Final Recruiting Lead",
            "summary": "Lead the recruiting motion with clear quality standards.",
            "rubric_items": [
                {
                    "sort_order": 1,
                    "scoring_standard_items": [{"key": "score_5", "value": "Excellent"}],
                    "agent_prompt_text": "Judge execution",
                    "evidence_guidance_text": "Look for hiring throughput",
                },
                {
                    "sort_order": 2,
                    "scoring_standard_items": [{"key": "pass_definition", "value": "Can collaborate globally"}],
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
    assert "weight_normalized" not in loaded.rubric_items[0].model_dump()


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


def test_create_draft_logs_stage_success(db_session, caplog) -> None:
    service = JobService(db_session, JobRepository(), StubWorkflow(result=make_job_draft()))

    with caplog.at_level("INFO"):
        response = service.create_draft_from_description(
            CreateJobFromDescriptionRequest(description_text="A long enough original job description.")
        )

    assert response.lifecycle_status == "draft"
    assert f"stage=job_draft_create result=success creation_mode=from_description job_id={response.job_id}" in caplog.text


def test_workflow_failure_does_not_create_dirty_draft(db_session) -> None:
    service = JobService(
        db_session,
        JobRepository(),
        StubWorkflow(error=ValueError("llm failed")),
    )

    with pytest.raises(DomainValidationError, match="llm failed"):
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
            responsibilities=["Run kickoff"],
            skills=["Recruiting ops"],
            rubric_items=service.get_job_edit_payload(created.job_id).rubric_items,
            recent_messages=[{"role": "user", "content": "先给建议"}],
            user_input="请给建议",
        ),
    )

    loaded = service.get_job_edit_payload(created.job_id)
    assert response.reply_text == "建议保持职责结构清晰。"
    assert loaded.description_text == "JD body"
    assert chat_workflow.calls[0]["description_text"] == "Locally edited description"
    assert chat_workflow.calls[0]["responsibilities"] == ["Run kickoff"]
    assert chat_workflow.calls[0]["skills"] == ["Recruiting ops"]


def test_chat_on_active_job_returns_reply_text(db_session) -> None:
    chat_workflow = StubChatWorkflow()
    finalize_workflow = StubFinalizeWorkflow(result=make_finalize_result())
    service = JobService(
        db_session,
        JobRepository(),
        StubWorkflow(result=make_job_draft()),
        chat_workflow=chat_workflow,
        finalize_workflow=finalize_workflow,
    )
    created = service.create_draft_from_description(
        CreateJobFromDescriptionRequest(description_text="Original raw description input.")
    )
    draft_payload = service.get_job_edit_payload(created.job_id)
    run_finalize(
        service,
        created.job_id,
        JobFinalizeRequest(
            description_text="Locally finalized description",
            responsibilities=["Own funnel"],
            skills=["Hiring ops"],
            rubric_items=draft_payload.rubric_items,
        ),
    )

    response = service.chat_on_draft(
        created.job_id,
        JobChatRequest(
            description_text="Active local description",
            responsibilities=["Run kickoff"],
            skills=["Recruiting ops"],
            rubric_items=service.get_job_edit_payload(created.job_id).rubric_items,
            recent_messages=[],
            user_input="请继续给建议",
        ),
    )

    assert response.reply_text == "建议保持职责结构清晰。"
    assert chat_workflow.calls[0]["description_text"] == "Active local description"


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
            responsibilities=["Run kickoff"],
            skills=["Recruiting ops"],
            rubric_items=service.get_job_edit_payload(created.job_id).rubric_items,
            recent_messages=[],
            user_input="直接应用新的版本",
        ),
    )

    loaded = service.get_job_edit_payload(created.job_id)
    assert response.description_text == "New JD body"
    assert response.title == "New Recruiting Lead"
    assert response.summary == "Lead the recruiting motion with stronger hiring discipline."
    assert response.structured_info_json["location"] == "Hybrid"
    assert response.responsibilities == ["Own funnel", "Coordinate interview loop"]
    assert response.skills == ["Hiring ops", "Stakeholder management"]
    assert "weight_normalized" not in response.rubric_items[0].model_dump()
    assert loaded.description_text == "JD body"
    assert agent_workflow.calls[0]["user_input"] == "直接应用新的版本"


def test_agent_edit_on_active_job_returns_generated_content_without_writing(db_session) -> None:
    agent_workflow = StubAgentEditWorkflow()
    finalize_workflow = StubFinalizeWorkflow(result=make_finalize_result())
    service = JobService(
        db_session,
        JobRepository(),
        StubWorkflow(result=make_job_draft()),
        agent_edit_workflow=agent_workflow,
        finalize_workflow=finalize_workflow,
    )
    created = service.create_draft_from_description(
        CreateJobFromDescriptionRequest(description_text="Original raw description input.")
    )
    draft_payload = service.get_job_edit_payload(created.job_id)
    run_finalize(
        service,
        created.job_id,
        JobFinalizeRequest(
            description_text="Locally finalized description",
            responsibilities=["Own funnel"],
            skills=["Hiring ops"],
            rubric_items=draft_payload.rubric_items,
        ),
    )

    response = service.agent_edit_draft(
        created.job_id,
        JobAgentEditRequest(
            description_text="Active local description",
            responsibilities=["Run kickoff"],
            skills=["Recruiting ops"],
            rubric_items=service.get_job_edit_payload(created.job_id).rubric_items,
            recent_messages=[],
            user_input="直接改成新版",
        ),
    )

    assert response.title == "New Recruiting Lead"
    assert response.description_text == "New JD body"
    assert agent_workflow.calls[0]["description_text"] == "Active local description"


def test_finalize_draft_updates_job_to_active_and_replaces_rubric(db_session) -> None:
    finalize_workflow = StubFinalizeWorkflow(result=make_finalize_result())
    service = JobService(
        db_session,
        JobRepository(),
        StubWorkflow(result=make_job_draft()),
        finalize_workflow=finalize_workflow,
    )
    created = service.create_draft_from_description(
        CreateJobFromDescriptionRequest(description_text="Original raw description input.")
    )
    loaded_before = service.get_job_edit_payload(created.job_id)

    response = run_finalize(
        service,
        created.job_id,
        JobFinalizeRequest(
          description_text="Locally finalized description",
          responsibilities=["Own funnel", "Partner hiring managers"],
          skills=["Hiring ops", "Structured interviews"],
          rubric_items=loaded_before.rubric_items,
        ),
    )

    loaded_after = service.get_job_edit_payload(created.job_id)
    assert response.lifecycle_status == "active"
    assert loaded_after.lifecycle_status == "active"
    assert loaded_after.title == "Final Recruiting Lead"
    assert loaded_after.summary == "Lead the recruiting motion with clear quality standards."
    assert loaded_after.description_text == "Locally finalized description"
    assert loaded_after.responsibilities == ["Own funnel", "Partner hiring managers"]
    assert loaded_after.skills == ["Hiring ops", "Structured interviews"]
    assert loaded_after.finalized_at is not None
    assert len(loaded_after.rubric_items) == 2
    final_job = service.job_repository.get_job_for_edit(db_session, created.job_id)
    weighted_items = [item for item in final_job.rubric_items if item.criterion_type == "weighted"]
    assert len(weighted_items) == 1
    assert weighted_items[0].weight_input == 99
    assert weighted_items[0].weight_normalized == 1.0
    assert final_job.rubric_items[0].scoring_standard_items == [{"key": "score_5", "value": "Excellent"}]
    assert final_job.rubric_items[0].agent_prompt_text == "Judge execution"
    assert final_job.rubric_items[0].evidence_guidance_text == "Look for hiring throughput"


def test_finalize_failure_does_not_override_draft(db_session) -> None:
    finalize_workflow = StubFinalizeWorkflow(error=ValueError("finalize failed"))
    service = JobService(
        db_session,
        JobRepository(),
        StubWorkflow(result=make_job_draft()),
        finalize_workflow=finalize_workflow,
    )
    created = service.create_draft_from_description(
        CreateJobFromDescriptionRequest(description_text="Original raw description input.")
    )
    loaded_before = service.get_job_edit_payload(created.job_id)

    with pytest.raises(DomainValidationError):
        run_finalize(
            service,
            created.job_id,
            JobFinalizeRequest(
                description_text="Locally finalized description",
                responsibilities=["Own funnel"],
                skills=["Hiring ops"],
                rubric_items=loaded_before.rubric_items,
            ),
        )

    loaded_after = service.get_job_edit_payload(created.job_id)
    assert loaded_after.lifecycle_status == "draft"
    assert loaded_after.description_text == "JD body"
    assert loaded_after.finalized_at is None


def test_finalize_on_active_job_updates_in_place(db_session) -> None:
    finalize_workflow = StubFinalizeWorkflow(result=make_finalize_result())
    service = JobService(
        db_session,
        JobRepository(),
        StubWorkflow(result=make_job_draft()),
        finalize_workflow=finalize_workflow,
    )
    created = service.create_draft_from_description(
        CreateJobFromDescriptionRequest(description_text="Original raw description input.")
    )
    draft_payload = service.get_job_edit_payload(created.job_id)
    run_finalize(
        service,
        created.job_id,
        JobFinalizeRequest(
            description_text="Locally finalized description",
            responsibilities=["Own funnel"],
            skills=["Hiring ops"],
            rubric_items=draft_payload.rubric_items,
        ),
    )

    second_response = run_finalize(
        service,
        created.job_id,
        JobFinalizeRequest(
            description_text="Second finalize attempt",
            responsibilities=["Own funnel", "Calibrate hiring bar"],
            skills=["Hiring ops", "Structured interviews"],
            rubric_items=service.get_job_edit_payload(created.job_id).rubric_items,
        ),
    )

    loaded_after = service.get_job_edit_payload(created.job_id)
    assert second_response.lifecycle_status == "active"
    assert loaded_after.lifecycle_status == "active"
    assert loaded_after.description_text == "Second finalize attempt"
    assert loaded_after.responsibilities == ["Own funnel", "Calibrate hiring bar"]
    assert loaded_after.skills == ["Hiring ops", "Structured interviews"]
    weighted_items = [item for item in service.job_repository.get_job_for_edit(db_session, created.job_id).rubric_items if item.criterion_type == "weighted"]
    assert len(weighted_items) == 1
    assert weighted_items[0].weight_input == 99
    assert weighted_items[0].weight_normalized == 1.0


def test_finalize_rejects_zero_weighted_total(db_session) -> None:
    finalize_workflow = StubFinalizeWorkflow(result=make_finalize_result())
    service = JobService(
        db_session,
        JobRepository(),
        StubWorkflow(result=make_job_draft()),
        finalize_workflow=finalize_workflow,
    )
    created = service.create_draft_from_description(
        CreateJobFromDescriptionRequest(description_text="Original raw description input.")
    )
    draft_payload = service.get_job_edit_payload(created.job_id)
    zero_weight_items = [
        item.model_copy(update={"weight_input": 0})
        if item.criterion_type == "weighted"
        else item
        for item in draft_payload.rubric_items
    ]

    with pytest.raises(ValidationError):
        JobFinalizeRequest(
            description_text="Locally finalized description",
            responsibilities=["Own funnel"],
            skills=["Hiring ops"],
            rubric_items=zero_weight_items,
        )
