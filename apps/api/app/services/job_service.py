from sqlalchemy.orm import Session

from app.core.exceptions import DomainValidationError, NotFoundError
from app.models.job import Job
from app.repositories.job_repository import (
    JobCreateData,
    JobRepository,
    JobRubricItemCreateData,
)
from app.schemas.ai.job_definition import JobDraftSchema
from app.schemas.jobs import (
    CreateJobFromDescriptionRequest,
    CreateJobFromFormRequest,
    CreateJobDraftResponse,
    JobEditResponse,
)
from app.workflows.job_definition.create_draft import JobDefinitionCreateDraftWorkflow


class JobService:
    def __init__(
        self,
        session: Session,
        job_repository: JobRepository,
        draft_workflow: JobDefinitionCreateDraftWorkflow,
    ) -> None:
        self.session = session
        self.job_repository = job_repository
        self.draft_workflow = draft_workflow

    def create_draft_from_description(
        self, payload: CreateJobFromDescriptionRequest
    ) -> CreateJobDraftResponse:
        draft = self.draft_workflow.from_description(payload.description_text)
        job = self._persist_draft(
            creation_mode="from_description",
            draft=draft,
            original_description_input=payload.description_text,
            original_form_input_json=None,
        )
        return CreateJobDraftResponse(job_id=job.id, lifecycle_status="draft")

    def create_draft_from_form(self, payload: CreateJobFromFormRequest) -> CreateJobDraftResponse:
        draft = self.draft_workflow.from_form(payload.model_dump(mode="json"))
        job = self._persist_draft(
            creation_mode="from_form",
            draft=draft,
            original_description_input=None,
            original_form_input_json=payload.model_dump(mode="json"),
        )
        return CreateJobDraftResponse(job_id=job.id, lifecycle_status="draft")

    def get_job_edit_payload(self, job_id: str) -> JobEditResponse:
        try:
            job = self.job_repository.get_job_for_edit(self.session, job_id)
        except LookupError as exc:
            raise NotFoundError(f"Job {job_id} not found.") from exc

        return self._to_job_edit_response(job)

    def delete_draft_job(self, job_id: str) -> None:
        with self.session.begin():
            deleted = self.job_repository.delete_draft_job(self.session, job_id)
            if not deleted:
                raise NotFoundError(f"Draft job {job_id} not found.")

    def _persist_draft(
        self,
        *,
        creation_mode: str,
        draft: JobDraftSchema,
        original_description_input: str | None,
        original_form_input_json: dict | None,
    ) -> Job:
        job_data = JobCreateData(
            lifecycle_status="draft",
            creation_mode=creation_mode,
            title=draft.title,
            summary=draft.summary,
            description_text=draft.description_text,
            structured_info_json=draft.structured_info_json.model_dump(mode="json"),
            original_description_input=original_description_input,
            original_form_input_json=original_form_input_json,
            editor_history_summary=None,
            editor_recent_messages_json=[],
        )
        rubric_items = [
            JobRubricItemCreateData(**item.model_dump(mode="json"))
            for item in draft.rubric_items
        ]

        try:
            with self.session.begin():
                return self.job_repository.create_job_with_rubric_items(
                    self.session,
                    job_data=job_data,
                    rubric_items=rubric_items,
                )
        except Exception as exc:
            raise DomainValidationError("Failed to create job draft.") from exc

    def _to_job_edit_response(self, job: Job) -> JobEditResponse:
        return JobEditResponse(
            id=job.id,
            lifecycle_status=job.lifecycle_status,
            creation_mode=job.creation_mode,
            title=job.title,
            summary=job.summary,
            description_text=job.description_text,
            structured_info_json=job.structured_info_json,
            original_description_input=job.original_description_input,
            original_form_input_json=job.original_form_input_json,
            editor_history_summary=job.editor_history_summary,
            editor_recent_messages_json=job.editor_recent_messages_json,
            created_at=job.created_at,
            updated_at=job.updated_at,
            finalized_at=job.finalized_at,
            rubric_items=[
                {
                    "id": item.id,
                    "sort_order": item.sort_order,
                    "name": item.name,
                    "description": item.description,
                    "criterion_type": item.criterion_type,
                    "weight_input": item.weight_input,
                    "weight_normalized": item.weight_normalized,
                    "scoring_standard_json": item.scoring_standard_json,
                    "agent_prompt_text": item.agent_prompt_text,
                    "evidence_guidance_text": item.evidence_guidance_text,
                }
                for item in sorted(job.rubric_items, key=lambda rubric: rubric.sort_order)
            ],
        )
