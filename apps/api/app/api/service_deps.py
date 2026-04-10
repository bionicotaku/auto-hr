from sqlalchemy.orm import Session

from app.ai.client import OpenAIResponsesClient
from app.core.config import Settings
from app.repositories.job_repository import JobRepository
from app.services.job_service import JobService
from app.workflows.job_definition.create_draft import JobDefinitionCreateDraftWorkflow


def get_job_service(session: Session, _: Settings) -> JobService:
    repository = JobRepository()
    workflow = JobDefinitionCreateDraftWorkflow(OpenAIResponsesClient())
    return JobService(session=session, job_repository=repository, draft_workflow=workflow)
