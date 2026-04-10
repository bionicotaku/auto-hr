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


class JobRubricItemSchema(BaseModel):
    sort_order: int = Field(ge=1)
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=2000)
    criterion_type: Literal["weighted", "hard_requirement"]
    weight_input: float = Field(ge=0)
    weight_normalized: float | None = Field(default=None, ge=0, le=1)
    scoring_standard_json: dict[str, str]
    agent_prompt_text: str = Field(min_length=1, max_length=4000)
    evidence_guidance_text: str = Field(min_length=1, max_length=2000)

    @model_validator(mode="after")
    def validate_weight_rules(self) -> "JobRubricItemSchema":
        if self.criterion_type == "weighted" and self.weight_normalized is None:
            raise ValueError("weighted rubric items require weight_normalized.")

        if self.criterion_type == "hard_requirement":
            if self.weight_normalized is not None:
                raise ValueError("hard_requirement rubric items must not set weight_normalized.")
            if self.weight_input != 100:
                raise ValueError("hard_requirement rubric items must use weight_input=100.")

        return self


class JobDraftSchema(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    summary: str = Field(min_length=1, max_length=2000)
    description_text: str = Field(min_length=1, max_length=12000)
    structured_info_json: JobStructuredInfoSchema
    rubric_items: list[JobRubricItemSchema] = Field(min_length=1, max_length=12)


class JobChatResponseSchema(BaseModel):
    reply_text: str = Field(min_length=1, max_length=4000)


class JobAgentEditResponseSchema(BaseModel):
    description_text: str = Field(min_length=1, max_length=12000)
    rubric_items: list[JobRubricItemSchema] = Field(min_length=1, max_length=12)


class JobFinalizeResponseSchema(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    summary: str = Field(min_length=1, max_length=2000)
    description_text: str = Field(min_length=1, max_length=12000)
    structured_info_json: JobStructuredInfoSchema
    rubric_items: list[JobRubricItemSchema] = Field(min_length=1, max_length=12)


def rubric_items_to_json(items: list[JobRubricItemSchema | dict[str, Any]]) -> list[dict[str, Any]]:
    serialized: list[dict[str, Any]] = []
    for item in items:
        if isinstance(item, JobRubricItemSchema):
            serialized.append(item.model_dump(mode="json"))
        else:
            serialized.append(item)
    return serialized
