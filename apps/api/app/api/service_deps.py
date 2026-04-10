from sqlalchemy.orm import Session

from app.ai.client import OpenAIResponsesClient
from app.core.config import Settings
from app.files.temp_manager import TempImportManager
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.job_repository import JobRepository
from app.services.candidate_analysis_service import CandidateAnalysisService
from app.services.candidate_import_service import CandidateImportService
from app.services.job_query_service import JobQueryService
from app.services.job_service import JobService
from app.workflows.candidate_analysis.import_prepare import CandidateImportPrepareWorkflow
from app.workflows.candidate_analysis.persist import CandidatePersistWorkflow
from app.workflows.candidate_analysis.score_items import CandidateScoreItemsWorkflow
from app.workflows.candidate_analysis.standardize import CandidateStandardizeWorkflow
from app.workflows.candidate_analysis.summarize import CandidateSummarizeWorkflow
from app.workflows.job_definition.agent_edit import JobDefinitionAgentEditWorkflow
from app.workflows.job_definition.chat import JobDefinitionChatWorkflow
from app.workflows.job_definition.create_draft import JobDefinitionCreateDraftWorkflow
from app.workflows.job_definition.finalize import JobDefinitionFinalizeWorkflow


def get_job_service(session: Session, _: Settings) -> JobService:
    repository = JobRepository()
    client = OpenAIResponsesClient()
    return JobService(
        session=session,
        job_repository=repository,
        draft_workflow=JobDefinitionCreateDraftWorkflow(client),
        chat_workflow=JobDefinitionChatWorkflow(client),
        agent_edit_workflow=JobDefinitionAgentEditWorkflow(client),
        finalize_workflow=JobDefinitionFinalizeWorkflow(client),
    )


def get_candidate_import_service(session: Session, settings: Settings) -> CandidateImportService:
    job_repository = JobRepository()
    candidate_repository = CandidateRepository()
    client = OpenAIResponsesClient()
    temp_import_manager = TempImportManager(settings)

    candidate_analysis_service = CandidateAnalysisService(
        session=session,
        job_repository=job_repository,
        import_prepare_workflow=CandidateImportPrepareWorkflow(
            job_repository=job_repository,
            temp_import_manager=temp_import_manager,
        ),
        standardize_workflow=CandidateStandardizeWorkflow(client),
        score_items_workflow=CandidateScoreItemsWorkflow(client, concurrency_limit=6, max_retries=1),
        summarize_workflow=CandidateSummarizeWorkflow(client),
        temp_upload_dir_path=settings.temp_upload_dir_path,
    )
    return CandidateImportService(
        session=session,
        candidate_analysis_service=candidate_analysis_service,
        persist_workflow=CandidatePersistWorkflow(
            settings=settings,
            candidate_repository=candidate_repository,
        ),
    )


def get_job_query_service(session: Session, _settings: Settings) -> JobQueryService:
    return JobQueryService(
        session=session,
        job_repository=JobRepository(),
        candidate_repository=CandidateRepository(),
    )
