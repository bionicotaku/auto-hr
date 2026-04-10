from sqlalchemy.orm import Session

from app.ai.client import OpenAIResponsesClient
from app.core.config import Settings
from app.core.db import get_session_factory
from app.files.temp_manager import TempImportManager
from app.repositories.analysis_run_repository import AnalysisRunRepository
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.job_repository import JobRepository
from app.services.analysis_run_service import AnalysisRunService
from app.services.candidate_import_run_service import CandidateImportRunService
from app.services.candidate_query_service import CandidateQueryService
from app.services.email_draft_service import EmailDraftService
from app.services.feedback_service import FeedbackService
from app.services.job_finalize_run_service import JobFinalizeRunService
from app.services.job_query_service import JobQueryService
from app.services.job_service import JobService
from app.workflows.candidate_analysis.email_draft import CandidateEmailDraftWorkflow
from app.workflows.candidate_analysis.persist import CandidatePersistWorkflow
from app.workflows.candidate_analysis.score_items import CandidateScoreItemsWorkflow
from app.workflows.candidate_analysis.standardize import CandidateStandardizeWorkflow
from app.workflows.candidate_analysis.summarize import CandidateSummarizeWorkflow
from app.workflows.job_definition.agent_edit import JobDefinitionAgentEditWorkflow
from app.workflows.job_definition.chat import JobDefinitionChatWorkflow
from app.workflows.job_definition.create_draft import JobDefinitionCreateDraftWorkflow
from app.workflows.job_definition.finalize import JobDefinitionFinalizeWorkflow
from app.workflows.job_definition.finalize_rubric_items import (
    JobDefinitionFinalizeRubricItemsWorkflow,
)
from app.workflows.job_definition.finalize_title_summary import (
    JobDefinitionFinalizeTitleSummaryWorkflow,
)


def _build_job_finalize_workflow() -> JobDefinitionFinalizeWorkflow:
    client = OpenAIResponsesClient()
    return JobDefinitionFinalizeWorkflow(
        title_summary_workflow=JobDefinitionFinalizeTitleSummaryWorkflow(client),
        rubric_items_workflow=JobDefinitionFinalizeRubricItemsWorkflow(
            client,
            concurrency_limit=6,
            max_retries=1,
        ),
    )


def get_job_service(session: Session, _: Settings) -> JobService:
    repository = JobRepository()
    client = OpenAIResponsesClient()
    return JobService(
        session=session,
        job_repository=repository,
        draft_workflow=JobDefinitionCreateDraftWorkflow(client),
        chat_workflow=JobDefinitionChatWorkflow(client),
        agent_edit_workflow=JobDefinitionAgentEditWorkflow(client),
        finalize_workflow=_build_job_finalize_workflow(),
    )


def get_analysis_run_service(_settings: Settings) -> AnalysisRunService:
    return AnalysisRunService(
        session_factory=get_session_factory(),
        repository=AnalysisRunRepository(),
    )


def get_job_finalize_run_service(_settings: Settings) -> JobFinalizeRunService:
    return JobFinalizeRunService(
        session_factory=get_session_factory(),
        analysis_run_repository=AnalysisRunRepository(),
        job_repository=JobRepository(),
        finalize_workflow=_build_job_finalize_workflow(),
    )


def get_candidate_import_run_service(settings: Settings) -> CandidateImportRunService:
    client = OpenAIResponsesClient()
    return CandidateImportRunService(
        session_factory=get_session_factory(),
        analysis_run_repository=AnalysisRunRepository(),
        job_repository=JobRepository(),
        temp_import_manager=TempImportManager(settings),
        standardize_workflow=CandidateStandardizeWorkflow(client),
        score_items_workflow=CandidateScoreItemsWorkflow(client, concurrency_limit=6, max_retries=1),
        summarize_workflow=CandidateSummarizeWorkflow(client),
        persist_workflow=CandidatePersistWorkflow(
            settings=settings,
            candidate_repository=CandidateRepository(),
        ),
        temp_upload_dir_path=settings.temp_upload_dir_path,
    )


def get_job_query_service(session: Session, _settings: Settings) -> JobQueryService:
    return JobQueryService(
        session=session,
        job_repository=JobRepository(),
        candidate_repository=CandidateRepository(),
    )


def get_candidate_query_service(session: Session, _settings: Settings) -> CandidateQueryService:
    return CandidateQueryService(
        session=session,
        candidate_repository=CandidateRepository(),
    )


def get_feedback_service(session: Session, _settings: Settings) -> FeedbackService:
    return FeedbackService(
        session=session,
        candidate_repository=CandidateRepository(),
    )


def get_email_draft_service(session: Session, _settings: Settings) -> EmailDraftService:
    return EmailDraftService(
        session=session,
        candidate_repository=CandidateRepository(),
        email_draft_workflow=CandidateEmailDraftWorkflow(OpenAIResponsesClient()),
    )
