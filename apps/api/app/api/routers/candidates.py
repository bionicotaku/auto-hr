from fastapi import APIRouter

from app.api import service_deps
from app.api.deps import AppSettings, DbSession
from app.schemas.candidates import CandidateDetailResponse

router = APIRouter(prefix="/api/candidates", tags=["candidates"])


@router.get("/{candidate_id}", response_model=CandidateDetailResponse)
def get_candidate_detail(
    candidate_id: str,
    session: DbSession,
    settings: AppSettings,
) -> CandidateDetailResponse:
    service = service_deps.get_candidate_query_service(session, settings)
    return service.get_candidate_detail(candidate_id)
