from math import floor

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, DomainValidationError, NotFoundError
from app.models.job import Job
from app.repositories.job_repository import (
    JobCreateData,
    JobRepository,
    JobRubricItemCreateData,
)
from app.schemas.ai.job_definition import (
    JobAgentEditResponseSchema,
    JobChatResponseSchema,
    JobDraftSchema,
    JobFinalizeResponseSchema,
)
from app.schemas.jobs import (
    CreateJobFromDescriptionRequest,
    CreateJobFromFormRequest,
    CreateJobDraftResponse,
    JobAgentEditRequest,
    JobChatRequest,
    JobChatResponse,
    JobEditResponse,
    JobFinalizeRequest,
    JobFinalizeResponse,
    JobGeneratedContentResponse,
    JobRegenerateRequest,
)
from app.workflows.job_definition.create_draft import JobDefinitionCreateDraftWorkflow


class JobService:
    def __init__(
        self,
        session: Session,
        job_repository: JobRepository,
        draft_workflow: JobDefinitionCreateDraftWorkflow,
        chat_workflow=None,
        agent_edit_workflow=None,
        regenerate_workflow=None,
        finalize_workflow=None,
    ) -> None:
        self.session = session
        self.job_repository = job_repository
        self.draft_workflow = draft_workflow
        self.chat_workflow = chat_workflow
        self.agent_edit_workflow = agent_edit_workflow
        self.regenerate_workflow = regenerate_workflow
        self.finalize_workflow = finalize_workflow

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

    def chat_on_draft(self, job_id: str, payload: JobChatRequest) -> JobChatResponse:
        job = self._get_draft_job(job_id)
        if self.chat_workflow is None:
            raise RuntimeError("Job chat workflow is not configured.")

        response = self.chat_workflow.run(
            description_text=payload.description_text,
            rubric_items=[item.model_dump(mode="json", exclude={"id"}) for item in payload.rubric_items],
            recent_messages=[message.model_dump(mode="json") for message in payload.recent_messages],
            user_input=payload.user_input,
        )
        return JobChatResponse(reply_text=response.reply_text)

    def agent_edit_draft(self, job_id: str, payload: JobAgentEditRequest) -> JobGeneratedContentResponse:
        job = self._get_draft_job(job_id)
        if self.agent_edit_workflow is None:
            raise RuntimeError("Job agent edit workflow is not configured.")

        response = self.agent_edit_workflow.run(
            description_text=payload.description_text,
            rubric_items=[item.model_dump(mode="json", exclude={"id"}) for item in payload.rubric_items],
            recent_messages=[message.model_dump(mode="json") for message in payload.recent_messages],
            user_input=payload.user_input,
        )
        return self._to_generated_content_response(response)

    def regenerate_draft(self, job_id: str, payload: JobRegenerateRequest) -> JobGeneratedContentResponse:
        job = self._get_draft_job(job_id)
        if self.regenerate_workflow is None:
            raise RuntimeError("Job regenerate workflow is not configured.")

        response = self.regenerate_workflow.run(
            original_description_input=job.original_description_input,
            original_form_input_json=job.original_form_input_json,
            title=job.title,
            summary=job.summary,
            structured_info_json=job.structured_info_json,
            history_summary=payload.history_summary,
            recent_messages=[message.model_dump(mode="json") for message in payload.recent_messages],
        )
        return self._to_generated_content_response(response)

    def finalize_draft(self, job_id: str, payload: JobFinalizeRequest) -> JobFinalizeResponse:
        job = self._get_draft_job(job_id)
        if self.finalize_workflow is None:
            raise RuntimeError("Job finalize workflow is not configured.")

        try:
            response = self.finalize_workflow.run(
                title=job.title,
                summary=job.summary,
                description_text=payload.description_text,
                rubric_items=[item.model_dump(mode="json", exclude={"id"}) for item in payload.rubric_items],
                structured_info_json=job.structured_info_json,
                original_description_input=job.original_description_input,
                original_form_input_json=job.original_form_input_json,
            )
            normalized_items = self._normalize_finalize_rubric_items(response.rubric_items)
        except DomainValidationError:
            raise
        except Exception as exc:
            raise DomainValidationError("Failed to finalize job.") from exc

        rubric_items = [
            JobRubricItemCreateData(**item.model_dump(mode="json"))
            for item in normalized_items
        ]

        try:
            self.job_repository.finalize_job(
                self.session,
                job,
                title=response.title,
                summary=response.summary,
                description_text=response.description_text,
                structured_info_json=response.structured_info_json.model_dump(mode="json"),
                rubric_items=rubric_items,
            )
            self.session.commit()
        except DomainValidationError:
            self.session.rollback()
            raise
        except Exception as exc:
            self.session.rollback()
            raise DomainValidationError("Failed to finalize job.") from exc

        return JobFinalizeResponse(job_id=job.id, lifecycle_status="active")

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

    def _get_draft_job(self, job_id: str) -> Job:
        try:
            job = self.job_repository.get_job_for_edit(self.session, job_id)
        except LookupError as exc:
            raise NotFoundError(f"Job {job_id} not found.") from exc

        if job.lifecycle_status != "draft":
            raise ConflictError(f"Job {job_id} is not editable.")
        return job

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

    def _to_generated_content_response(
        self, response: JobAgentEditResponseSchema
    ) -> JobGeneratedContentResponse:
        return JobGeneratedContentResponse(
            description_text=response.description_text,
            rubric_items=[
                {
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
                for item in response.rubric_items
            ],
        )

    def _normalize_finalize_rubric_items(self, rubric_items):
        weighted_items = [item for item in rubric_items if item.criterion_type == "weighted"]
        hard_requirement_items = [
            item for item in rubric_items if item.criterion_type == "hard_requirement"
        ]

        if weighted_items:
            total_weight = sum(item.weight_input for item in weighted_items)
            if total_weight <= 0:
                raise DomainValidationError("Weighted rubric items must have a positive total weight.")

            normalized_inputs = []
            remainders = []

            for index, item in enumerate(weighted_items):
                normalized = item.weight_input / total_weight * 100
                floored = floor(normalized)
                normalized_inputs.append(floored)
                remainders.append((normalized - floored, index))

            remaining_points = 100 - sum(normalized_inputs)
            for _, index in sorted(remainders, reverse=True)[:remaining_points]:
                normalized_inputs[index] += 1

            for item, normalized_input in zip(weighted_items, normalized_inputs, strict=True):
                item.weight_input = float(normalized_input)
                item.weight_normalized = round(normalized_input / 100, 4)
        elif len(hard_requirement_items) != len(rubric_items):
            raise DomainValidationError("Invalid rubric items for finalize.")
        else:
            raise DomainValidationError("Weighted rubric items must not total zero.")

        return rubric_items
