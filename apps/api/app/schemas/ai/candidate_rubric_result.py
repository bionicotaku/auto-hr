from pydantic import BaseModel, Field


class WeightedRubricResultSchema(BaseModel):
    job_rubric_item_id: str = Field(min_length=1, max_length=36)
    criterion_type: str = Field(pattern="^weighted$")
    score_0_to_5: float = Field(ge=0, le=5)
    reason_text: str = Field(min_length=1, max_length=4000)
    evidence_points: list[str] = Field(default_factory=list, max_length=12)
    uncertainty_note: str | None = Field(default=None, max_length=2000)


class HardRequirementRubricResultSchema(BaseModel):
    job_rubric_item_id: str = Field(min_length=1, max_length=36)
    criterion_type: str = Field(pattern="^hard_requirement$")
    hard_requirement_decision: str = Field(pattern="^(pass|borderline|fail)$")
    reason_text: str = Field(min_length=1, max_length=4000)
    evidence_points: list[str] = Field(default_factory=list, max_length=12)
    uncertainty_note: str | None = Field(default=None, max_length=2000)


class CandidateRubricScoreItemsResult(BaseModel):
    weighted_results: list[WeightedRubricResultSchema] = Field(default_factory=list)
    hard_requirement_results: list[HardRequirementRubricResultSchema] = Field(default_factory=list)
