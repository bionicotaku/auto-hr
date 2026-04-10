from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CreateJobFromDescriptionRequest(BaseModel):
    description_text: str = Field(max_length=12000)

    model_config = ConfigDict(extra="forbid")

    @field_validator("description_text")
    @classmethod
    def normalize_description_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("description_text must not be empty.")
        return normalized


class CreateJobFromFormRequest(BaseModel):
    job_title: str = Field(max_length=200)
    department: str | None = Field(default=None, max_length=120)
    location: str | None = Field(default=None, max_length=120)
    employment_type: str | None = Field(default=None, max_length=80)
    seniority_level: str | None = Field(default=None, max_length=80)
    business_context: str | None = Field(default=None, max_length=2000)
    responsibilities_summary: str | None = Field(default=None, max_length=3000)
    requirements_summary: str | None = Field(default=None, max_length=3000)

    model_config = ConfigDict(extra="forbid")

    @field_validator(
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

    @field_validator("job_title", mode="before")
    @classmethod
    def normalize_job_title(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("job_title must not be empty.")
        normalized = value.strip()
        if not normalized:
            raise ValueError("job_title must not be empty.")
        return normalized


class JobRubricItemResponse(BaseModel):
    id: str
    sort_order: int
    name: str
    description: str
    criterion_type: Literal["weighted", "hard_requirement"]
    weight_input: float
    weight_normalized: float | None
    scoring_standard_items: list[dict[str, str]]
    agent_prompt_text: str
    evidence_guidance_text: str

    model_config = ConfigDict(from_attributes=True)


class JobEditorMessage(BaseModel):
    role: Literal["user", "assistant", "system"] = Field(default="user")
    content: str = Field(min_length=1, max_length=4000)

    model_config = ConfigDict(extra="forbid")

    @field_validator("content")
    @classmethod
    def normalize_content(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("content must not be empty.")
        return normalized


class JobRubricDraftItemRequest(BaseModel):
    id: str | None = None
    sort_order: int = Field(ge=1)
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=2000)
    criterion_type: Literal["weighted", "hard_requirement"]
    weight_input: float = Field(ge=0)

    model_config = ConfigDict(extra="forbid", from_attributes=True)


class JobRubricDraftItemResponse(BaseModel):
    sort_order: int
    name: str
    description: str
    criterion_type: Literal["weighted", "hard_requirement"]
    weight_input: float


class JobChatRequest(BaseModel):
    description_text: str = Field(min_length=1, max_length=12000)
    rubric_items: list[JobRubricDraftItemRequest] = Field(min_length=1, max_length=12)
    recent_messages: list[JobEditorMessage] = Field(default_factory=list, max_length=5)
    user_input: str = Field(min_length=1, max_length=4000)

    model_config = ConfigDict(extra="forbid")

    @field_validator("description_text", "user_input")
    @classmethod
    def normalize_text_fields(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("text fields must not be empty.")
        return normalized


class JobAgentEditRequest(JobChatRequest):
    pass


class JobRegenerateRequest(BaseModel):
    recent_messages: list[JobEditorMessage] = Field(default_factory=list, max_length=5)
    history_summary: str | None = Field(default=None, max_length=4000)

    model_config = ConfigDict(extra="forbid")

    @field_validator("history_summary")
    @classmethod
    def normalize_history_summary(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class JobChatResponse(BaseModel):
    reply_text: str


class JobGeneratedContentResponse(BaseModel):
    description_text: str
    rubric_items: list[JobRubricDraftItemResponse]


class JobFinalizeRequest(BaseModel):
    description_text: str = Field(min_length=1, max_length=12000)
    rubric_items: list[JobRubricDraftItemRequest] = Field(min_length=1, max_length=12)

    model_config = ConfigDict(extra="forbid")

    @field_validator("description_text")
    @classmethod
    def normalize_finalize_description(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("description_text must not be empty.")
        return normalized


class JobFinalizeResponse(BaseModel):
    job_id: str
    lifecycle_status: Literal["active"]


class JobCandidateImportContextResponse(BaseModel):
    job_id: str
    title: str
    summary: str
    lifecycle_status: Literal["draft", "active"]


class CandidateImportResponse(BaseModel):
    candidate_id: str
    job_id: str


class JobListItemResponse(BaseModel):
    job_id: str
    title: str
    summary: str
    lifecycle_status: Literal["draft", "active"]
    candidate_count: int
    updated_at: datetime


class JobListResponse(BaseModel):
    items: list[JobListItemResponse]


class JobDetailRubricSummaryItemResponse(BaseModel):
    name: str
    criterion_type: Literal["weighted", "hard_requirement"]
    weight_label: str


class JobDetailStructuredInfoItemResponse(BaseModel):
    label: str
    value: str


class JobDetailResponse(BaseModel):
    job_id: str
    title: str
    summary: str
    description_text: str
    lifecycle_status: Literal["draft", "active"]
    candidate_count: int
    rubric_summary: list[JobDetailRubricSummaryItemResponse]
    structured_info_summary: list[JobDetailStructuredInfoItemResponse]


class JobCandidateListItemResponse(BaseModel):
    candidate_id: str
    full_name: str
    ai_summary: str
    overall_score_percent: float | None
    current_status: Literal["pending", "in_progress", "rejected", "offer_sent", "hired"]
    tags: list[str]
    created_at: datetime


class JobCandidateListResponse(BaseModel):
    items: list[JobCandidateListItemResponse]
    available_tags: list[str]


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
    rubric_items: list[JobRubricDraftItemResponse]


class CreateJobDraftResponse(BaseModel):
    job_id: str
    lifecycle_status: Literal["draft"]
