from copy import deepcopy
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


class JobRubricItemSchema(JobRubricItemBaseSchema):
    weight_normalized: float | None = Field(default=None, ge=0, le=1)
    scoring_standard_json: dict[str, str]
    agent_prompt_text: str = Field(min_length=1, max_length=4000)
    evidence_guidance_text: str = Field(min_length=1, max_length=2000)


class JobFinalizeScoringItemSchema(BaseModel):
    sort_order: int = Field(ge=1)
    scoring_standard_json: dict[str, str]
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


class JobAgentEditResponseSchema(BaseModel):
    description_text: str = Field(min_length=1, max_length=12000)
    rubric_items: list[JobRubricItemDraftSchema] = Field(min_length=1, max_length=12)


class JobFinalizeScoringResponseSchema(BaseModel):
    rubric_items: list[JobFinalizeScoringItemSchema] = Field(min_length=1, max_length=12)


def build_job_definition_openai_schema(schema: dict[str, Any]) -> dict[str, Any]:
    transformed = deepcopy(schema)

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            properties = node.get("properties")
            if isinstance(properties, dict) and "scoring_standard_json" in properties:
                properties["scoring_standard_json"] = {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "properties": {
                            "key": {"type": "string", "minLength": 1},
                            "value": {"type": "string", "minLength": 1},
                        },
                        "required": ["key", "value"],
                        "additionalProperties": False,
                    },
                }
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for item in node:
                visit(item)

    visit(transformed)
    return transformed


def normalize_job_definition_payload(payload: dict[str, Any]) -> dict[str, Any]:
    def convert_scoring_standard(value: Any) -> Any:
        if isinstance(value, dict):
            return value
        if not isinstance(value, list):
            raise ValueError("scoring_standard_json must be an object or a list of key/value items.")

        converted: dict[str, str] = {}
        for item in value:
            if not isinstance(item, dict):
                raise ValueError("scoring_standard_json items must be objects.")
            key = item.get("key")
            item_value = item.get("value")
            if not isinstance(key, str) or not key.strip():
                raise ValueError("scoring_standard_json items require a non-empty key.")
            if not isinstance(item_value, str) or not item_value.strip():
                raise ValueError("scoring_standard_json items require a non-empty value.")
            if key in converted:
                raise ValueError("scoring_standard_json items must not contain duplicate keys.")
            converted[key] = item_value
        return converted

    def visit(node: Any) -> Any:
        if isinstance(node, dict):
            converted: dict[str, Any] = {}
            for key, value in node.items():
                if key == "scoring_standard_json":
                    converted[key] = convert_scoring_standard(value)
                else:
                    converted[key] = visit(value)
            return converted
        if isinstance(node, list):
            return [visit(item) for item in node]
        return node

    return visit(payload)


def rubric_items_to_json(
    items: list[JobRubricItemDraftSchema | JobRubricItemSchema | dict[str, Any]],
) -> list[dict[str, Any]]:
    serialized: list[dict[str, Any]] = []
    for item in items:
        if isinstance(item, (JobRubricItemDraftSchema, JobRubricItemSchema)):
            payload = item.model_dump(mode="json")
            payload.setdefault("weight_normalized", None)
            payload.setdefault("scoring_standard_json", {})
            payload.setdefault("agent_prompt_text", "")
            payload.setdefault("evidence_guidance_text", "")
            serialized.append(payload)
        else:
            payload = dict(item)
            payload.setdefault("weight_normalized", None)
            payload.setdefault("scoring_standard_json", {})
            payload.setdefault("agent_prompt_text", "")
            payload.setdefault("evidence_guidance_text", "")
            serialized.append(payload)
    return serialized
