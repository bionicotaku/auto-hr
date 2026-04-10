import pytest

from app.schemas.ai.job_definition import (
    JobAgentEditResponseSchema,
    JobChatResponseSchema,
    JobFinalizeScoringResponseSchema,
)
from app.workflows.job_definition.agent_edit import JobDefinitionAgentEditWorkflow
from app.workflows.job_definition.chat import JobDefinitionChatWorkflow
from app.workflows.job_definition.finalize import JobDefinitionFinalizeWorkflow
from app.workflows.job_definition.regenerate import JobDefinitionRegenerateWorkflow


class FakeClient:
    def __init__(self, payload):
        self.payload = payload
        self.calls: list[dict] = []

    def generate_structured_output(self, **kwargs):
        self.calls.append(kwargs)
        return self.payload


def valid_rubric_items() -> list[dict]:
    return [
        {
            "sort_order": 1,
            "name": "Execution",
            "description": "Can lead hiring",
            "criterion_type": "weighted",
            "weight_input": 70,
        }
    ]


def valid_finalize_scoring_items() -> list[dict]:
    return [
        {
            "sort_order": 1,
            "scoring_standard_json": [
                {"key": "score_5", "value": "Excellent"},
                {"key": "score_3", "value": "Acceptable"},
            ],
            "agent_prompt_text": "Judge execution in real project work.",
            "evidence_guidance_text": "Look for shipped outcomes and concrete ownership.",
        }
    ]


def test_chat_workflow_returns_valid_schema() -> None:
    client = FakeClient({"reply_text": "建议把必须项拆开写。"})
    workflow = JobDefinitionChatWorkflow(client)

    response = workflow.run(
        description_text="Current JD",
        rubric_items=valid_rubric_items(),
        recent_messages=[{"role": "user", "content": "请增强要求"}],
        user_input="把必须项单独列出来。",
    )

    assert isinstance(response, JobChatResponseSchema)
    assert response.reply_text == "建议把必须项拆开写。"


def test_agent_edit_workflow_rejects_invalid_schema() -> None:
    client = FakeClient(
        {
            "description_text": "New JD",
            "rubric_items": [
                {
                    "sort_order": 1,
                    "name": "Execution",
                    "description": "Updated",
                    "criterion_type": "hard_requirement",
                    "weight_input": 70,
                }
            ],
        }
    )
    workflow = JobDefinitionAgentEditWorkflow(client)

    with pytest.raises(ValueError):
        workflow.run(
            description_text="Current JD",
            rubric_items=valid_rubric_items(),
            recent_messages=[],
            user_input="重写这段 JD。",
        )


def test_regenerate_workflow_uses_original_inputs_only() -> None:
    client = FakeClient(
        {
            "description_text": "Regenerated JD",
            "rubric_items": valid_rubric_items(),
        }
    )
    workflow = JobDefinitionRegenerateWorkflow(client)

    response = workflow.run(
        original_description_input="ORIGINAL_DESCRIPTION_SOURCE",
        original_form_input_json={"job_title": "AI Recruiter"},
        title="Recruiter",
        summary="Summary",
        structured_info_json={"department": "Talent"},
        history_summary="Earlier discussion",
        recent_messages=[{"role": "assistant", "content": "此前建议"}],
    )

    assert isinstance(response, JobAgentEditResponseSchema)
    prompt = client.calls[0]["prompt"]
    assert "ORIGINAL_DESCRIPTION_SOURCE" in prompt
    assert "job_title" in prompt
    assert "当前编辑区版本不会提供" in prompt
    assert response.rubric_items[0].name == "Execution"


def test_finalize_workflow_returns_valid_schema() -> None:
    client = FakeClient(
        {
            "rubric_items": valid_finalize_scoring_items(),
        }
    )
    workflow = JobDefinitionFinalizeWorkflow(client)

    response = workflow.run(
        description_text="Current JD",
        rubric_items=valid_rubric_items(),
    )

    assert isinstance(response, JobFinalizeScoringResponseSchema)
    assert response.rubric_items[0].sort_order == 1
    assert response.rubric_items[0].agent_prompt_text == "Judge execution in real project work."
    prompt = client.calls[0]["prompt"]
    assert "Current JD" in prompt
    assert "不要参考任何原始输入" in prompt
