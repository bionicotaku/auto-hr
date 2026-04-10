from fastapi import APIRouter, Response, status

from app.api import service_deps
from app.api.deps import AppSettings, DbSession
from app.schemas.jobs import (
    CreateJobDraftResponse,
    CreateJobFromDescriptionRequest,
    CreateJobFromFormRequest,
    JobEditResponse,
)

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("/from-description", response_model=CreateJobDraftResponse, status_code=status.HTTP_201_CREATED)
def create_job_from_description(
    payload: CreateJobFromDescriptionRequest,
    session: DbSession,
    settings: AppSettings,
) -> CreateJobDraftResponse:
    service = service_deps.get_job_service(session, settings)
    return service.create_draft_from_description(payload)


@router.post("/from-form", response_model=CreateJobDraftResponse, status_code=status.HTTP_201_CREATED)
def create_job_from_form(
    payload: CreateJobFromFormRequest,
    session: DbSession,
    settings: AppSettings,
) -> CreateJobDraftResponse:
    service = service_deps.get_job_service(session, settings)
    return service.create_draft_from_form(payload)


@router.get("/{job_id}/edit", response_model=JobEditResponse)
def get_job_edit(job_id: str, session: DbSession, settings: AppSettings) -> JobEditResponse:
    service = service_deps.get_job_service(session, settings)
    return service.get_job_edit_payload(job_id)


@router.delete("/{job_id}/draft", status_code=status.HTTP_204_NO_CONTENT)
def delete_draft_job(job_id: str, session: DbSession, settings: AppSettings) -> Response:
    service = service_deps.get_job_service(session, settings)
    service.delete_draft_job(job_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
