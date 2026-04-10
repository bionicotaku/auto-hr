from fastapi import APIRouter, File, Form, Response, UploadFile, status

from app.api import service_deps
from app.api.deps import AppSettings, DbSession
from app.schemas.jobs import (
    CandidateImportResponse,
    CreateJobDraftResponse,
    CreateJobFromDescriptionRequest,
    CreateJobFromFormRequest,
    JobAgentEditRequest,
    JobCandidateImportContextResponse,
    JobChatRequest,
    JobChatResponse,
    JobEditResponse,
    JobFinalizeRequest,
    JobFinalizeResponse,
    JobGeneratedContentResponse,
    JobRegenerateRequest,
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


@router.get("/{job_id}/candidate-import-context", response_model=JobCandidateImportContextResponse)
def get_job_candidate_import_context(
    job_id: str,
    session: DbSession,
    settings: AppSettings,
) -> JobCandidateImportContextResponse:
    service = service_deps.get_job_service(session, settings)
    return service.get_candidate_import_context(job_id)


@router.post(
    "/{job_id}/candidates/import",
    response_model=CandidateImportResponse,
    status_code=status.HTTP_201_CREATED,
)
async def import_candidate_to_job(
    job_id: str,
    session: DbSession,
    settings: AppSettings,
    raw_text_input: str | None = Form(default=None),
    files: list[UploadFile] | None = File(default=None),
) -> CandidateImportResponse:
    service = service_deps.get_candidate_import_service(session, settings)
    return await service.import_candidate(
        job_id=job_id,
        raw_text_input=raw_text_input,
        files=files or [],
    )


@router.post("/{job_id}/chat", response_model=JobChatResponse)
def chat_on_job_draft(
    job_id: str,
    payload: JobChatRequest,
    session: DbSession,
    settings: AppSettings,
) -> JobChatResponse:
    service = service_deps.get_job_service(session, settings)
    return service.chat_on_draft(job_id, payload)


@router.post("/{job_id}/agent-edit", response_model=JobGeneratedContentResponse)
def agent_edit_job_draft(
    job_id: str,
    payload: JobAgentEditRequest,
    session: DbSession,
    settings: AppSettings,
) -> JobGeneratedContentResponse:
    service = service_deps.get_job_service(session, settings)
    return service.agent_edit_draft(job_id, payload)


@router.post("/{job_id}/regenerate", response_model=JobGeneratedContentResponse)
def regenerate_job_draft(
    job_id: str,
    payload: JobRegenerateRequest,
    session: DbSession,
    settings: AppSettings,
) -> JobGeneratedContentResponse:
    service = service_deps.get_job_service(session, settings)
    return service.regenerate_draft(job_id, payload)


@router.post("/{job_id}/finalize", response_model=JobFinalizeResponse)
def finalize_job_draft(
    job_id: str,
    payload: JobFinalizeRequest,
    session: DbSession,
    settings: AppSettings,
) -> JobFinalizeResponse:
    service = service_deps.get_job_service(session, settings)
    return service.finalize_draft(job_id, payload)


@router.delete("/{job_id}/draft", status_code=status.HTTP_204_NO_CONTENT)
def delete_draft_job(job_id: str, session: DbSession, settings: AppSettings) -> Response:
    service = service_deps.get_job_service(session, settings)
    service.delete_draft_job(job_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
