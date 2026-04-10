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
    JobFinalizeScoringResponseSchema,
    JobRubricItemFinalSchema,
    rubric_items_to_json,
)
from app.schemas.jobs import (
    CreateJobFromDescriptionRequest,
    CreateJobFromFormRequest,
    CreateJobDraftResponse,
    JobAgentEditRequest,
    JobCandidateImportContextResponse,
    JobChatRequest,
    JobChatResponse,
    JobEditResponse,
    JobFinalizeRequest,
    JobFinalizeResponse,
    JobGeneratedContentResponse,
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
        finalize_workflow=None,
    ) -> None:
        self.session = session
        self.job_repository = job_repository
        self.draft_workflow = draft_workflow
        self.chat_workflow = chat_workflow
        self.agent_edit_workflow = agent_edit_workflow
        self.finalize_workflow = finalize_workflow

    def create_draft_from_description(
        self, payload: CreateJobFromDescriptionRequest
    ) -> CreateJobDraftResponse:
        try:
            draft = self.draft_workflow.from_description(payload.description_text)
        except ValueError as exc:
            raise DomainValidationError(str(exc)) from exc
        job = self._persist_draft(
            creation_mode="from_description",
            draft=draft,
            original_description_input=payload.description_text,
            original_form_input_json=None,
        )
        return CreateJobDraftResponse(job_id=job.id, lifecycle_status="draft")

    def create_draft_from_form(self, payload: CreateJobFromFormRequest) -> CreateJobDraftResponse:
        try:
            draft = self.draft_workflow.from_form(payload.model_dump(mode="json"))
        except ValueError as exc:
            raise DomainValidationError(str(exc)) from exc
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

    def get_candidate_import_context(self, job_id: str) -> JobCandidateImportContextResponse:
        try:
            job = self.job_repository.get_job(self.session, job_id)
        except LookupError as exc:
            raise NotFoundError(f"Job {job_id} not found.") from exc

        return JobCandidateImportContextResponse(
            job_id=job.id,
            title=job.title,
            summary=job.summary,
            lifecycle_status=job.lifecycle_status,
        )

    def delete_draft_job(self, job_id: str) -> None:
        with self.session.begin():
            deleted = self.job_repository.delete_draft_job(self.session, job_id)
            if not deleted:
                raise NotFoundError(f"Draft job {job_id} not found.")

    def chat_on_draft(self, job_id: str, payload: JobChatRequest) -> JobChatResponse:
        self._get_editable_job(job_id)
        if self.chat_workflow is None:
            raise DomainValidationError("Job chat workflow is not configured.")

        try:
            response = self.chat_workflow.run(
                description_text=payload.description_text,
                responsibilities=payload.responsibilities,
                skills=payload.skills,
                rubric_items=self._coerce_edit_rubric_items(payload.rubric_items),
                recent_messages=[message.model_dump(mode="json") for message in payload.recent_messages],
                user_input=payload.user_input,
            )
        except ValueError as exc:
            raise DomainValidationError(str(exc)) from exc
        return JobChatResponse(reply_text=response.reply_text)

    def agent_edit_draft(self, job_id: str, payload: JobAgentEditRequest) -> JobGeneratedContentResponse:
        job = self._get_editable_job(job_id)
        if self.agent_edit_workflow is None:
            raise DomainValidationError("Job agent edit workflow is not configured.")

        try:
            response = self.agent_edit_workflow.run(
                title=job.title,
                summary=job.summary,
                description_text=payload.description_text,
                structured_info_json=self._merge_structured_info_fields(
                    job.structured_info_json,
                    responsibilities=payload.responsibilities,
                    skills=payload.skills,
                ),
                responsibilities=payload.responsibilities,
                skills=payload.skills,
                rubric_items=self._coerce_edit_rubric_items(payload.rubric_items),
                recent_messages=[message.model_dump(mode="json") for message in payload.recent_messages],
                user_input=payload.user_input,
            )
        except ValueError as exc:
            raise DomainValidationError(str(exc)) from exc
        return self._to_generated_content_response(response)

    def finalize_draft(self, job_id: str, payload: JobFinalizeRequest) -> JobFinalizeResponse:
        job = self._get_editable_job(job_id)
        if self.finalize_workflow is None:
            raise DomainValidationError("Job finalize workflow is not configured.")

        try:
            response = self.finalize_workflow.run(
                description_text=payload.description_text,
                responsibilities=payload.responsibilities,
                skills=payload.skills,
                rubric_items=self._coerce_edit_rubric_items(payload.rubric_items),
            )
            merged_items = self._merge_finalize_enrichment(payload.rubric_items, response)
            normalized_items = self._normalize_finalize_rubric_items(merged_items)
        except DomainValidationError:
            raise
        except ValueError as exc:
            raise DomainValidationError(str(exc)) from exc
        except Exception as exc:
            raise DomainValidationError("Failed to finalize job.") from exc

        rubric_items = [
            JobRubricItemCreateData(**item.model_dump(mode="json", exclude={"id"}))
            for item in normalized_items
        ]

        try:
            self.job_repository.finalize_job(
                self.session,
                job,
                title=response.title,
                summary=response.summary,
                description_text=payload.description_text,
                structured_info_json=self._merge_structured_info_fields(
                    job.structured_info_json,
                    responsibilities=payload.responsibilities,
                    skills=payload.skills,
                ),
                rubric_items=rubric_items,
            )
            self.session.commit()
        except DomainValidationError:
            self.session.rollback()
            raise
        except ValueError as exc:
            self.session.rollback()
            raise DomainValidationError(str(exc)) from exc
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
        normalized_rubric_items = self._normalize_generated_rubric_items(draft.rubric_items)
        rubric_items = [JobRubricItemCreateData(**item) for item in normalized_rubric_items]

        try:
            with self.session.begin():
                return self.job_repository.create_job_with_rubric_items(
                    self.session,
                    job_data=job_data,
                    rubric_items=rubric_items,
                )
        except DomainValidationError:
            raise
        except ValueError as exc:
            raise DomainValidationError(str(exc)) from exc
        except Exception as exc:
            raise DomainValidationError("Failed to create job draft.") from exc

    def _get_draft_job(self, job_id: str) -> Job:
        job = self._get_editable_job(job_id)
        if job.lifecycle_status != "draft":
            raise ConflictError(f"Job {job_id} is not a draft.")
        return job

    def _get_editable_job(self, job_id: str) -> Job:
        try:
            job = self.job_repository.get_job_for_edit(self.session, job_id)
        except LookupError as exc:
            raise NotFoundError(f"Job {job_id} not found.") from exc
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
            responsibilities=self._get_structured_string_list(job.structured_info_json, "responsibilities"),
            skills=self._get_structured_string_list(job.structured_info_json, "skills"),
            created_at=job.created_at,
            updated_at=job.updated_at,
            finalized_at=job.finalized_at,
            rubric_items=[
                {
                    "sort_order": item.sort_order,
                    "name": item.name,
                    "description": item.description,
                    "criterion_type": item.criterion_type,
                    "weight_input": item.weight_input,
                }
                for item in sorted(job.rubric_items, key=lambda rubric: rubric.sort_order)
            ],
        )

    def _to_generated_content_response(
        self, response: JobAgentEditResponseSchema
    ) -> JobGeneratedContentResponse:
        normalized_items = self._normalize_generated_rubric_items(response.rubric_items)
        structured_info_json = response.structured_info_json.model_dump(mode="json")
        return JobGeneratedContentResponse(
            title=response.title,
            summary=response.summary,
            description_text=response.description_text,
            structured_info_json=structured_info_json,
            responsibilities=self._get_structured_string_list(structured_info_json, "responsibilities"),
            skills=self._get_structured_string_list(structured_info_json, "skills"),
            rubric_items=[self._to_draft_rubric_item_response(item) for item in normalized_items],
        )

    def _normalize_generated_rubric_items(self, rubric_items) -> list[dict]:
        serialized_items = rubric_items_to_json(rubric_items)
        for item in serialized_items:
            item["criterion_type"] = self._criterion_type_from_weight(item["weight_input"])

        weighted_items = [item for item in serialized_items if item["criterion_type"] == "weighted"]
        hard_requirement_items = [item for item in serialized_items if item["criterion_type"] == "hard_requirement"]

        if not weighted_items:
            raise DomainValidationError("Generated rubric items must include at least one weighted item.")

        total_weight = sum(item["weight_input"] for item in weighted_items)
        if total_weight <= 0:
            raise DomainValidationError("Weighted rubric items must have a positive total weight.")

        for item in weighted_items:
            item["weight_normalized"] = round(item["weight_input"] / total_weight, 4)
            item["scoring_standard_items"] = []
            item["agent_prompt_text"] = ""
            item["evidence_guidance_text"] = ""

        for item in hard_requirement_items:
            item["weight_normalized"] = None
            item["scoring_standard_items"] = []
            item["agent_prompt_text"] = ""
            item["evidence_guidance_text"] = ""

        if len(weighted_items) + len(hard_requirement_items) != len(serialized_items):
            raise DomainValidationError("Invalid rubric items generated by LLM.")

        return serialized_items

    def _coerce_edit_rubric_items(self, rubric_items) -> list[dict[str, object]]:
        coerced_items: list[dict[str, object]] = []
        for item in rubric_items:
            criterion_type = self._criterion_type_from_edit_item(
                item.criterion_type,
                item.weight_input,
            )
            coerced_items.append(
                {
                    "sort_order": item.sort_order,
                    "name": item.name,
                    "description": item.description,
                    "criterion_type": criterion_type,
                    "weight_input": item.weight_input,
                }
            )
        return coerced_items

    def _criterion_type_from_weight(self, weight_input: float) -> str:
        if weight_input == 100:
            return "hard_requirement"
        if 0 < weight_input < 100:
            return "weighted"
        raise DomainValidationError("weight_input must be between 1 and 100, and 100 represents a hard requirement.")

    def _criterion_type_from_edit_item(self, criterion_type: str, weight_input: float) -> str:
        if criterion_type == "hard_requirement":
            if weight_input != 100:
                raise DomainValidationError(
                    "Hard requirement items must use weight_input 100."
                )
            return "hard_requirement"

        if criterion_type == "weighted":
            if 0 < weight_input <= 100:
                return "weighted"
            raise DomainValidationError("Weighted rubric items must use weight_input between 1 and 100.")

        raise DomainValidationError("Invalid rubric item criterion_type.")

    def _merge_structured_info_fields(
        self,
        structured_info_json: dict,
        *,
        responsibilities: list[str],
        skills: list[str],
    ) -> dict:
        merged = dict(structured_info_json)
        merged["responsibilities"] = responsibilities
        merged["skills"] = skills
        return merged

    def _get_structured_string_list(self, structured_info_json: dict, key: str) -> list[str]:
        value = structured_info_json.get(key)
        if not isinstance(value, list):
            return []
        return [item.strip() for item in value if isinstance(item, str) and item.strip()]

    def _to_draft_rubric_item_response(self, item: dict[str, object]) -> dict[str, object]:
        return {
            "sort_order": item["sort_order"],
            "name": item["name"],
            "description": item["description"],
            "criterion_type": item["criterion_type"],
            "weight_input": item["weight_input"],
        }

    def _merge_finalize_enrichment(
        self,
        rubric_items,
        enrichment_response: JobFinalizeScoringResponseSchema,
    ):
        enrichment_by_sort_order = {
            item.sort_order: {
                "scoring_standard_items": item.scoring_standard_items,
                "agent_prompt_text": item.agent_prompt_text,
                "evidence_guidance_text": item.evidence_guidance_text,
            }
            for item in enrichment_response.rubric_items
        }

        if len(enrichment_by_sort_order) != len(enrichment_response.rubric_items):
            raise DomainValidationError("Finalize enrichment contains duplicate rubric sort_order values.")

        merged_items = []
        for item in rubric_items:
            enrichment = enrichment_by_sort_order.get(item.sort_order)
            if enrichment is None:
                raise DomainValidationError(
                    f"Finalize enrichment is missing rubric item {item.sort_order}."
                )

            merged_items.append(
                JobRubricItemFinalSchema.model_validate(
                    {
                        "sort_order": item.sort_order,
                        "name": item.name,
                        "description": item.description,
                        "criterion_type": self._criterion_type_from_edit_item(
                            item.criterion_type,
                            item.weight_input,
                        ),
                        "weight_input": item.weight_input,
                        "weight_normalized": None,
                        **enrichment,
                    }
                )
            )

        if len(merged_items) != len(enrichment_response.rubric_items):
            raise DomainValidationError("Finalize enrichment returned unexpected rubric items.")

        return merged_items

    def _normalize_finalize_rubric_items(self, rubric_items):
        weighted_items = [item for item in rubric_items if item.criterion_type == "weighted"]
        hard_requirement_items = [
            item for item in rubric_items if item.criterion_type == "hard_requirement"
        ]

        if weighted_items:
            if len(weighted_items) == 1:
                weighted_items[0].weight_input = 99.0
                weighted_items[0].weight_normalized = 1.0
                return rubric_items

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
