from typing import Literal

from fastapi import APIRouter, BackgroundTasks, File, Form, Query, Response, UploadFile, status

from app.api import service_deps
from app.api.deps import AppSettings, DbSession
from app.schemas.analysis_runs import AnalysisRunStartResponse
from app.schemas.jobs import (
    CreateJobDraftResponse,
    CreateJobFromDescriptionRequest,
    CreateJobFromFormRequest,
    JobAgentEditRequest,
    JobCandidateImportContextResponse,
    JobCandidateListResponse,
    JobChatRequest,
    JobChatResponse,
    JobDetailResponse,
    JobEditResponse,
    JobFinalizeRequest,
    JobGeneratedContentResponse,
    JobListResponse,
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


@router.get("", response_model=JobListResponse)
def list_jobs(session: DbSession, settings: AppSettings) -> JobListResponse:
    service = service_deps.get_job_query_service(session, settings)
    return service.list_jobs()


@router.get("/{job_id}", response_model=JobDetailResponse)
def get_job_detail(job_id: str, session: DbSession, settings: AppSettings) -> JobDetailResponse:
    service = service_deps.get_job_query_service(session, settings)
    return service.get_job_detail(job_id)


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


@router.get("/{job_id}/candidates", response_model=JobCandidateListResponse)
def list_job_candidates(
    job_id: str,
    session: DbSession,
    settings: AppSettings,
    sort: Literal["score_desc", "score_asc", "created_at_desc", "created_at_asc"] = Query(
        default="score_desc"
    ),
    status_filter: Literal["all", "pending", "in_progress", "rejected", "offer_sent", "hired"] = Query(
        default="all",
        alias="status",
    ),
    tags: list[str] = Query(default_factory=list),
    q: str | None = Query(default=None, max_length=120),
) -> JobCandidateListResponse:
    service = service_deps.get_job_query_service(session, settings)
    return service.list_job_candidates(
        job_id=job_id,
        sort=sort,
        status=status_filter,
        tags=tags,
        query=q,
    )


@router.post(
    "/{job_id}/candidate-import-runs",
    response_model=AnalysisRunStartResponse,
    status_code=status.HTTP_201_CREATED,
)
async def start_candidate_import_run(
    job_id: str,
    background_tasks: BackgroundTasks,
    settings: AppSettings,
    raw_text_input: str | None = Form(default=None),
    files: list[UploadFile] | None = File(default=None),
) -> AnalysisRunStartResponse:
    service = service_deps.get_candidate_import_run_service(settings)
    response = await service.start_run(
        job_id=job_id,
        raw_text_input=raw_text_input,
        files=files or [],
    )
    background_tasks.add_task(service.execute_run, response.run_id)
    return response


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


@router.post("/{job_id}/finalize-runs", response_model=AnalysisRunStartResponse, status_code=status.HTTP_201_CREATED)
def start_job_finalize_run(
    job_id: str,
    payload: JobFinalizeRequest,
    background_tasks: BackgroundTasks,
    settings: AppSettings,
) -> AnalysisRunStartResponse:
    service = service_deps.get_job_finalize_run_service(settings)
    response = service.start_run(job_id=job_id, payload=payload)
    background_tasks.add_task(service.execute_run, response.run_id)
    return response


@router.delete("/{job_id}/draft", status_code=status.HTTP_204_NO_CONTENT)
def delete_draft_job(job_id: str, session: DbSession, settings: AppSettings) -> Response:
    service = service_deps.get_job_service(session, settings)
    service.delete_draft_job(job_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
