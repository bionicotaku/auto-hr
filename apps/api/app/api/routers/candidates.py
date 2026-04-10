from fastapi import APIRouter

from app.api import service_deps
from app.api.deps import AppSettings, DbSession
from app.schemas.candidates import (
    CandidateDetailEmailDraftResponse,
    CandidateDetailFeedbackResponse,
    CandidateDetailResponse,
    CandidateDetailTagResponse,
    CandidateEmailDraftCreateRequest,
    CandidateFeedbackCreateRequest,
    CandidateStatusUpdateRequest,
    CandidateStatusUpdateResponse,
    CandidateTagCreateRequest,
)

router = APIRouter(prefix="/api/candidates", tags=["candidates"])


@router.get("/{candidate_id}", response_model=CandidateDetailResponse)
def get_candidate_detail(
    candidate_id: str,
    session: DbSession,
    settings: AppSettings,
) -> CandidateDetailResponse:
    service = service_deps.get_candidate_query_service(session, settings)
    return service.get_candidate_detail(candidate_id)


@router.patch("/{candidate_id}/status", response_model=CandidateStatusUpdateResponse)
def update_candidate_status(
    candidate_id: str,
    payload: CandidateStatusUpdateRequest,
    session: DbSession,
    settings: AppSettings,
) -> CandidateStatusUpdateResponse:
    service = service_deps.get_feedback_service(session, settings)
    return service.update_status(candidate_id, payload.current_status)


@router.post("/{candidate_id}/tags", response_model=CandidateDetailTagResponse)
def create_candidate_tag(
    candidate_id: str,
    payload: CandidateTagCreateRequest,
    session: DbSession,
    settings: AppSettings,
) -> CandidateDetailTagResponse:
    service = service_deps.get_feedback_service(session, settings)
    return service.add_tag(candidate_id, payload.tag_name)


@router.post("/{candidate_id}/feedbacks", response_model=CandidateDetailFeedbackResponse)
def create_candidate_feedback(
    candidate_id: str,
    payload: CandidateFeedbackCreateRequest,
    session: DbSession,
    settings: AppSettings,
) -> CandidateDetailFeedbackResponse:
    service = service_deps.get_feedback_service(session, settings)
    return service.add_feedback(
        candidate_id,
        note_text=payload.note_text,
        author_name=payload.author_name,
    )


@router.post("/{candidate_id}/email-drafts", response_model=CandidateDetailEmailDraftResponse)
def create_candidate_email_draft(
    candidate_id: str,
    payload: CandidateEmailDraftCreateRequest,
    session: DbSession,
    settings: AppSettings,
) -> CandidateDetailEmailDraftResponse:
    service = service_deps.get_email_draft_service(session, settings)
    return service.create_email_draft(candidate_id, payload.draft_type)
