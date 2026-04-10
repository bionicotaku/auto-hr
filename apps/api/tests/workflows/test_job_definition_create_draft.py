import pytest

from app.schemas.ai.job_definition import JobDraftSchema
from app.workflows.job_definition.create_draft import JobDefinitionCreateDraftWorkflow


class FakeClient:
    def __init__(self, payload):
        self.payload = payload
        self.calls: list[dict] = []

    def generate_structured_output(self, **kwargs):
        self.calls.append(kwargs)
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
            }
        ],
    }


def test_create_draft_workflow_returns_valid_schema() -> None:
    client = FakeClient(valid_payload())
    workflow = JobDefinitionCreateDraftWorkflow(client)
    draft = workflow.from_description("Example description")

    assert isinstance(draft, JobDraftSchema)
    assert draft.title == "Staff AI Recruiter"
    assert "weight_normalized" not in client.calls[0]["schema"]["$defs"]["JobRubricItemDraftSchema"]["properties"]
    assert "scoring_standard_items" not in client.calls[0]["schema"]["$defs"]["JobRubricItemDraftSchema"]["properties"]
    assert "agent_prompt_text" not in client.calls[0]["schema"]["$defs"]["JobRubricItemDraftSchema"]["properties"]
    assert "evidence_guidance_text" not in client.calls[0]["schema"]["$defs"]["JobRubricItemDraftSchema"]["properties"]


def test_create_draft_workflow_rejects_invalid_schema() -> None:
    invalid = valid_payload()
    invalid["rubric_items"][0]["criterion_type"] = "hard_requirement"
    invalid["rubric_items"][0]["weight_input"] = 70

    workflow = JobDefinitionCreateDraftWorkflow(FakeClient(invalid))

    with pytest.raises(ValueError):
        workflow.from_description("Example description")
