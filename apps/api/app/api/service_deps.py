from sqlalchemy.orm import Session

from app.ai.client import OpenAIResponsesClient
from app.core.config import Settings
from app.repositories.job_repository import JobRepository
from app.services.job_service import JobService
from app.workflows.job_definition.agent_edit import JobDefinitionAgentEditWorkflow
from app.workflows.job_definition.chat import JobDefinitionChatWorkflow
from app.workflows.job_definition.create_draft import JobDefinitionCreateDraftWorkflow
from app.workflows.job_definition.regenerate import JobDefinitionRegenerateWorkflow


def get_job_service(session: Session, _: Settings) -> JobService:
    repository = JobRepository()
    client = OpenAIResponsesClient()
    return JobService(
        session=session,
        job_repository=repository,
        draft_workflow=JobDefinitionCreateDraftWorkflow(client),
        chat_workflow=JobDefinitionChatWorkflow(client),
        agent_edit_workflow=JobDefinitionAgentEditWorkflow(client),
        regenerate_workflow=JobDefinitionRegenerateWorkflow(client),
    )
