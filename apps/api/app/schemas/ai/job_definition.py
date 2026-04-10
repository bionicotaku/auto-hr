from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class JobStructuredInfoSchema(BaseModel):
    department: str | None = None
    location: str | None = None
    employment_type: str | None = None
    seniority_level: str | None = None
    responsibilities: list[str] = Field(default_factory=list)
    requirements: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)


class JobRubricItemBaseSchema(BaseModel):
    sort_order: int = Field(ge=1)
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=2000)
    criterion_type: Literal["weighted", "hard_requirement"]
    weight_input: float = Field(ge=0)

    @model_validator(mode="after")
    def validate_weight_rules(self) -> "JobRubricItemBaseSchema":
        if self.criterion_type == "hard_requirement":
            if self.weight_input != 100:
                raise ValueError("hard_requirement rubric items must use weight_input=100.")

        return self


class JobRubricItemDraftSchema(JobRubricItemBaseSchema):
    pass


class ScoringStandardItemSchema(BaseModel):
    key: str = Field(min_length=1, max_length=80)
    value: str = Field(min_length=1, max_length=4000)


class JobRubricItemFinalSchema(JobRubricItemBaseSchema):
    weight_normalized: float | None = Field(default=None, ge=0, le=1)
    scoring_standard_items: list[ScoringStandardItemSchema] = Field(min_length=1, max_length=10)
    agent_prompt_text: str = Field(min_length=1, max_length=4000)
    evidence_guidance_text: str = Field(min_length=1, max_length=2000)


class JobFinalizeTitleSummarySchema(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    summary: str = Field(min_length=1, max_length=2000)


class JobFinalizeRubricItemEnrichmentSchema(BaseModel):
    sort_order: int = Field(ge=1)
    scoring_standard_items: list[ScoringStandardItemSchema] = Field(min_length=1, max_length=10)
    agent_prompt_text: str = Field(min_length=1, max_length=4000)
    evidence_guidance_text: str = Field(min_length=1, max_length=2000)


class JobDraftSchema(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    summary: str = Field(min_length=1, max_length=2000)
    description_text: str = Field(min_length=1, max_length=12000)
    structured_info_json: JobStructuredInfoSchema
    rubric_items: list[JobRubricItemDraftSchema] = Field(min_length=1, max_length=12)


class JobChatResponseSchema(BaseModel):
    reply_text: str = Field(min_length=1, max_length=4000)


class JobAgentEditResponseSchema(JobDraftSchema):
    pass


class JobFinalizeScoringResponseSchema(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    summary: str = Field(min_length=1, max_length=2000)
    rubric_items: list[JobFinalizeRubricItemEnrichmentSchema] = Field(min_length=1, max_length=12)


def rubric_items_to_json(
    items: list[JobRubricItemDraftSchema | JobRubricItemFinalSchema | dict[str, Any]],
) -> list[dict[str, Any]]:
    serialized: list[dict[str, Any]] = []
    for item in items:
        if isinstance(item, (JobRubricItemDraftSchema, JobRubricItemFinalSchema)):
            payload = item.model_dump(mode="json")
            serialized.append(payload)
        else:
            serialized.append(dict(item))
    return serialized
