from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel


class CandidateDetailJobContextResponse(BaseModel):
    job_id: str
    title: str


class CandidateDetailRawDocumentResponse(BaseModel):
    id: str
    document_type: Literal["resume", "other"]
    filename: str
    storage_path: str
    mime_type: str
    extracted_text: str
    page_count: int | None
    upload_order: int


class CandidateDetailRawInputResponse(BaseModel):
    raw_text_input: str | None
    documents: list[CandidateDetailRawDocumentResponse]


class CandidateDetailIdentityResponse(BaseModel):
    full_name: str
    current_title: str | None
    current_company: str | None
    location_text: str | None
    email: str | None
    phone: str | None
    linkedin_url: str | None


class CandidateDetailProfileSummaryResponse(BaseModel):
    professional_summary_raw: str | None
    professional_summary_normalized: str | None
    years_of_total_experience: float | None
    years_of_relevant_experience: float | None
    seniority_level: str | None


class CandidateDetailNormalizedProfileResponse(BaseModel):
    identity: CandidateDetailIdentityResponse
    profile_summary: CandidateDetailProfileSummaryResponse
    work_experiences: list[dict[str, Any]]
    educations: list[dict[str, Any]]
    skills: dict[str, Any]
    employment_preferences: dict[str, Any]
    application_answers: list[dict[str, Any]]
    additional_information: dict[str, Any]


class CandidateDetailRubricResultResponse(BaseModel):
    job_rubric_item_id: str
    rubric_name: str
    rubric_description: str
    criterion_type: Literal["weighted", "hard_requirement"]
    weight_label: str
    score_0_to_5: float | None
    hard_requirement_decision: Literal["pass", "borderline", "fail"] | None
    reason_text: str
    evidence_points: list[str]
    uncertainty_note: str | None


class CandidateDetailTagResponse(BaseModel):
    id: str
    name: str
    source: Literal["ai", "manual"]


class CandidateDetailSupervisorResponse(BaseModel):
    hard_requirement_overall: Literal["all_pass", "has_borderline", "has_fail"]
    overall_score_5: float | None
    overall_score_percent: float | None
    ai_summary: str
    evidence_points: list[str]
    recommendation: Literal["advance", "manual_review", "hold", "reject"]
    tags: list[CandidateDetailTagResponse]


class CandidateDetailFeedbackResponse(BaseModel):
    id: str
    author_name: str | None
    note_text: str
    created_at: datetime


class CandidateDetailEmailDraftResponse(BaseModel):
    id: str
    draft_type: Literal["reject", "advance", "offer", "other"]
    subject: str
    body: str
    created_at: datetime
    updated_at: datetime


class CandidateDetailActionContextResponse(BaseModel):
    current_status: Literal["pending", "in_progress", "rejected", "offer_sent", "hired"]
    feedbacks: list[CandidateDetailFeedbackResponse]
    email_drafts: list[CandidateDetailEmailDraftResponse]


class CandidateDetailResponse(BaseModel):
    candidate_id: str
    job: CandidateDetailJobContextResponse
    raw_input: CandidateDetailRawInputResponse
    normalized_profile: CandidateDetailNormalizedProfileResponse
    rubric_results: list[CandidateDetailRubricResultResponse]
    supervisor_summary: CandidateDetailSupervisorResponse
    action_context: CandidateDetailActionContextResponse
