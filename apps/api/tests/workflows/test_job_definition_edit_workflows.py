import asyncio
import threading
import time

import pytest

from app.schemas.ai.job_definition import (
    JobAgentEditResponseSchema,
    JobChatResponseSchema,
    JobFinalizeRubricItemEnrichmentSchema,
    JobFinalizeScoringResponseSchema,
    JobFinalizeTitleSummarySchema,
)
from app.workflows.job_definition.agent_edit import JobDefinitionAgentEditWorkflow
from app.workflows.job_definition.chat import JobDefinitionChatWorkflow
from app.workflows.job_definition.finalize import JobDefinitionFinalizeWorkflow
from app.workflows.job_definition.finalize_rubric_items import (
    JobDefinitionFinalizeRubricItemsWorkflow,
)
from app.workflows.job_definition.finalize_title_summary import (
    JobDefinitionFinalizeTitleSummaryWorkflow,
)


class FakeClient:
    def __init__(self, payload):
        self.payload = payload
        self.calls: list[dict] = []

    def generate_structured_output(self, **kwargs):
        self.calls.append(kwargs)
        return self.payload


class FakeFinalizeOrchestratorClient:
    def __init__(self):
        self.calls: list[dict] = []

    def generate_structured_output(self, **kwargs):
        self.calls.append(kwargs)
        schema_name = kwargs["schema_name"]
        if schema_name == "job_finalize_title_summary_schema":
            return {
                "title": "Senior Recruiting Operator",
                "summary": "Own the recruiting funnel and maintain a clear hiring quality bar.",
            }
        return {
            "sort_order": 1,
            "scoring_standard_items": [
                {"key": "score_5", "value": "Excellent"},
                {"key": "score_3", "value": "Acceptable"},
            ],
            "agent_prompt_text": "Judge execution in real project work.",
            "evidence_guidance_text": "Look for shipped outcomes and concrete ownership.",
        }


class RetryClient:
    def __init__(self):
        self.calls: list[dict] = []
        self.attempts_by_sort_order: dict[int, int] = {}

    def generate_structured_output(self, **kwargs):
        self.calls.append(kwargs)
        prompt = kwargs["prompt"]
        sort_order = self._extract_current_sort_order(prompt)
        self.attempts_by_sort_order[sort_order] = self.attempts_by_sort_order.get(sort_order, 0) + 1
        if sort_order == 1 and self.attempts_by_sort_order[sort_order] == 1:
            raise ValueError("transient failure")
        return {
            "sort_order": sort_order,
            "scoring_standard_items": [{"key": "5", "value": "Excellent"}],
            "agent_prompt_text": f"Judge item {sort_order}",
            "evidence_guidance_text": f"Evidence item {sort_order}",
        }

    def _extract_current_sort_order(self, prompt: str) -> int:
        section = prompt.split("当前 rubric item：", 1)[1]
        return int(section.split('"sort_order": ')[1].split(",")[0])


class AlwaysFailClient:
    def __init__(self):
        self.calls: list[dict] = []

    def generate_structured_output(self, **kwargs):
        self.calls.append(kwargs)
        raise ValueError("always fail")


class ConcurrencyTrackingClient:
    def __init__(self):
        self.calls: list[dict] = []
        self.active = 0
        self.max_active = 0
        self.lock = threading.Lock()

    def generate_structured_output(self, **kwargs):
        self.calls.append(kwargs)
        with self.lock:
            self.active += 1
            self.max_active = max(self.max_active, self.active)
        time.sleep(0.05)
        prompt = kwargs["prompt"]
        section = prompt.split("当前 rubric item：", 1)[1]
        sort_order = int(section.split('"sort_order": ')[1].split(",")[0])
        with self.lock:
            self.active -= 1
        return {
            "sort_order": sort_order,
            "scoring_standard_items": [{"key": "5", "value": "Excellent"}],
            "agent_prompt_text": f"Judge item {sort_order}",
            "evidence_guidance_text": f"Evidence item {sort_order}",
        }


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
            "scoring_standard_items": [
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
        responsibilities=["Run kickoff"],
        skills=["Recruiting ops"],
        rubric_items=valid_rubric_items(),
        recent_messages=[{"role": "user", "content": "请增强要求"}],
        user_input="把必须项单独列出来。",
    )

    assert isinstance(response, JobChatResponseSchema)
    assert response.reply_text == "建议把必须项拆开写。"


def test_agent_edit_workflow_rejects_invalid_schema() -> None:
    client = FakeClient(
        {
            "title": "Updated Recruiter",
            "summary": "Updated hiring owner summary.",
            "description_text": "New JD",
            "structured_info_json": {
                "department": "Talent",
                "location": "Remote",
                "employment_type": "Full-time",
                "seniority_level": "Lead",
                "responsibilities": ["Own funnel"],
                "requirements": ["Recruiting depth"],
                "skills": ["Communication"],
            },
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
            title="Current title",
            summary="Current summary",
            description_text="Current JD",
            structured_info_json={
                "department": "Talent",
                "location": "Remote",
                "employment_type": "Full-time",
                "seniority_level": "Lead",
                "responsibilities": ["Run kickoff"],
                "requirements": ["Recruiting depth"],
                "skills": ["Recruiting ops"],
            },
            responsibilities=["Run kickoff"],
            skills=["Recruiting ops"],
            rubric_items=valid_rubric_items(),
            recent_messages=[],
            user_input="重写这段 JD。",
        )

def test_finalize_title_summary_workflow_returns_valid_schema() -> None:
    client = FakeClient(
        {
            "title": "Senior Recruiting Operator",
            "summary": "Own the recruiting funnel and maintain a clear hiring quality bar.",
        }
    )
    workflow = JobDefinitionFinalizeTitleSummaryWorkflow(client)

    response = workflow.run(
        description_text="Current JD",
        responsibilities=["Run kickoff"],
        skills=["Recruiting ops"],
        rubric_items=valid_rubric_items(),
    )

    assert isinstance(response, JobFinalizeTitleSummarySchema)
    assert response.title == "Senior Recruiting Operator"
    assert response.summary == "Own the recruiting funnel and maintain a clear hiring quality bar."
    prompt = client.calls[0]["prompt"]
    assert "Current JD" in prompt
    assert "Run kickoff" in prompt
    assert "Recruiting ops" in prompt


def test_finalize_rubric_items_workflow_retries_single_item_and_succeeds() -> None:
    client = RetryClient()
    workflow = JobDefinitionFinalizeRubricItemsWorkflow(client, concurrency_limit=6, max_retries=1)

    results = asyncio.run(
        workflow.run(
            description_text="Current JD",
            responsibilities=["Run kickoff"],
            skills=["Recruiting ops"],
            rubric_items=[
                {
                    "sort_order": 1,
                    "name": "Execution",
                    "description": "Can lead hiring",
                    "criterion_type": "weighted",
                    "weight_input": 70,
                },
                {
                    "sort_order": 2,
                    "name": "Stakeholder calibration",
                    "description": "Aligns the team",
                    "criterion_type": "hard_requirement",
                    "weight_input": 100,
                },
            ],
        )
    )

    assert len(results) == 2
    assert client.attempts_by_sort_order[1] == 2
    assert client.attempts_by_sort_order[2] == 1
    assert isinstance(results[0], JobFinalizeRubricItemEnrichmentSchema)


def test_finalize_rubric_items_workflow_fails_after_retry() -> None:
    workflow = JobDefinitionFinalizeRubricItemsWorkflow(
        AlwaysFailClient(),
        concurrency_limit=6,
        max_retries=1,
    )

    with pytest.raises(Exception, match="after retry"):
        asyncio.run(
            workflow.run(
                description_text="Current JD",
                responsibilities=["Run kickoff"],
                skills=["Recruiting ops"],
                rubric_items=valid_rubric_items(),
            )
        )


def test_finalize_rubric_items_workflow_respects_concurrency_limit() -> None:
    client = ConcurrencyTrackingClient()
    workflow = JobDefinitionFinalizeRubricItemsWorkflow(client, concurrency_limit=6, max_retries=1)
    rubric_items = [
        {
            "sort_order": index,
            "name": f"Item {index}",
            "description": "Criterion",
            "criterion_type": "weighted",
            "weight_input": 10,
        }
        for index in range(1, 9)
    ]

    results = asyncio.run(
        workflow.run(
            description_text="Current JD",
            responsibilities=["Run kickoff"],
            skills=["Recruiting ops"],
            rubric_items=rubric_items,
        )
    )

    assert len(results) == 8
    assert client.max_active <= 6


def test_finalize_workflow_returns_valid_schema() -> None:
    client = FakeFinalizeOrchestratorClient()
    workflow = JobDefinitionFinalizeWorkflow(client)

    response = workflow.run(
        description_text="Current JD",
        responsibilities=["Run kickoff"],
        skills=["Recruiting ops"],
        rubric_items=valid_rubric_items(),
    )

    assert isinstance(response, JobFinalizeScoringResponseSchema)
    assert response.title == "Senior Recruiting Operator"
    assert response.summary == "Own the recruiting funnel and maintain a clear hiring quality bar."
    assert response.rubric_items[0].sort_order == 1
    assert response.rubric_items[0].agent_prompt_text == "Judge execution in real project work."
    schema_names = [call["schema_name"] for call in client.calls]
    assert "job_finalize_title_summary_schema" in schema_names
    assert "job_finalize_rubric_item_enrichment_schema" in schema_names


def test_finalize_workflow_rejects_missing_rubric_item_enrichment() -> None:
    class MissingRubricWorkflow:
        async def run(self, **_kwargs):
            return []

    class TitleSummaryWorkflow:
        def run(self, **_kwargs):
            return JobFinalizeTitleSummarySchema(
                title="Senior Recruiting Operator",
                summary="Own the recruiting funnel and maintain a clear hiring quality bar.",
            )

    workflow = JobDefinitionFinalizeWorkflow(
        title_summary_workflow=TitleSummaryWorkflow(),
        rubric_items_workflow=MissingRubricWorkflow(),
    )

    with pytest.raises(Exception, match="did not match the requested rubric items"):
        workflow.run(
            description_text="Current JD",
            responsibilities=["Run kickoff"],
            skills=["Recruiting ops"],
            rubric_items=valid_rubric_items(),
        )
