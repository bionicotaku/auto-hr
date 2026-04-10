import pytest

from app.schemas.ai.job_definition import JobDraftSchema
from app.workflows.job_definition.create_draft import JobDefinitionCreateDraftWorkflow


class FakeClient:
    def __init__(self, payload):
        self.payload = payload

    def generate_structured_output(self, **_kwargs):
        return self.payload


def valid_payload() -> dict:
    return {
        "title": "Staff AI Recruiter",
        "summary": "Own recruiting across AI product teams.",
        "description_text": "A full JD draft",
        "structured_info_json": {
            "department": "Talent",
            "location": "Remote",
            "employment_type": "Full-time",
            "seniority_level": "Staff",
            "responsibilities": ["Lead recruiting"],
            "requirements": ["AI hiring experience"],
            "skills": ["Stakeholder management"],
        },
        "rubric_items": [
            {
                "sort_order": 1,
                "name": "Recruiting depth",
                "description": "Can handle end-to-end hiring",
                "criterion_type": "weighted",
                "weight_input": 70,
                "weight_normalized": 0.7,
                "scoring_standard_json": {"score_5": "Excellent"},
                "agent_prompt_text": "Judge depth",
                "evidence_guidance_text": "Look for ownership",
            }
        ],
    }


def test_create_draft_workflow_returns_valid_schema() -> None:
    workflow = JobDefinitionCreateDraftWorkflow(FakeClient(valid_payload()))
    draft = workflow.from_description("Example description")

    assert isinstance(draft, JobDraftSchema)
    assert draft.title == "Staff AI Recruiter"


def test_create_draft_workflow_rejects_invalid_schema() -> None:
    invalid = valid_payload()
    invalid["rubric_items"][0]["weight_normalized"] = None

    workflow = JobDefinitionCreateDraftWorkflow(FakeClient(invalid))

    with pytest.raises(ValueError):
        workflow.from_description("Example description")
