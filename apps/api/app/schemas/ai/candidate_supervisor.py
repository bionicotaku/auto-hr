from pydantic import BaseModel, Field


class CandidateSupervisorSchema(BaseModel):
    hard_requirement_overall: str = Field(pattern="^(all_pass|has_borderline|has_fail)$")
    overall_score_percent: float = Field(ge=0, le=100)
    ai_summary: str = Field(min_length=1, max_length=4000)
    evidence_points: list[str] = Field(default_factory=list, max_length=12)
    tags: list[str] = Field(default_factory=list, max_length=12)
    recommendation: str = Field(pattern="^(advance|manual_review|hold|reject)$")
