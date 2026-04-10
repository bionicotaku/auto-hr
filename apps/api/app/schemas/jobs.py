from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CreateJobFromDescriptionRequest(BaseModel):
    description_text: str = Field(min_length=20, max_length=12000)

    @field_validator("description_text")
    @classmethod
    def normalize_description_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("description_text must not be empty.")
        return normalized


class CreateJobFromFormRequest(BaseModel):
    job_title: str = Field(min_length=2, max_length=200)
    department: str | None = Field(default=None, max_length=120)
    location: str | None = Field(default=None, max_length=120)
    employment_type: str | None = Field(default=None, max_length=80)
    seniority_level: str | None = Field(default=None, max_length=80)
    business_context: str | None = Field(default=None, max_length=2000)
    responsibilities_summary: str | None = Field(default=None, max_length=3000)
    requirements_summary: str | None = Field(default=None, max_length=3000)

    @field_validator(
        "job_title",
        "department",
        "location",
        "employment_type",
        "seniority_level",
        "business_context",
        "responsibilities_summary",
        "requirements_summary",
        mode="before",
    )
    @classmethod
    def strip_strings(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class JobRubricItemResponse(BaseModel):
    id: str
    sort_order: int
    name: str
    description: str
    criterion_type: Literal["weighted", "hard_requirement"]
    weight_input: float
    weight_normalized: float | None
    scoring_standard_json: dict[str, Any]
    agent_prompt_text: str
    evidence_guidance_text: str

    model_config = ConfigDict(from_attributes=True)


class JobEditResponse(BaseModel):
    id: str
    lifecycle_status: Literal["draft", "active"]
    creation_mode: Literal["from_description", "from_form"]
    title: str
    summary: str
    description_text: str
    structured_info_json: dict[str, Any]
    original_description_input: str | None
    original_form_input_json: dict[str, Any] | None
    editor_history_summary: str | None
    editor_recent_messages_json: list[dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    finalized_at: datetime | None
    rubric_items: list[JobRubricItemResponse]


class CreateJobDraftResponse(BaseModel):
    job_id: str
    lifecycle_status: Literal["draft"]
