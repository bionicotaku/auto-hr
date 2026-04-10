import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, DomainValidationError, NotFoundError
from app.repositories.job_repository import JobRepository
from app.schemas.ai.candidate_rubric_result import CandidateRubricScoreItemsResult
from app.schemas.ai.candidate_standardization import (
    CandidateStandardizationSchema,
    PreparedCandidateImportInput,
)
from app.schemas.ai.candidate_supervisor import CandidateSupervisorSchema
from app.workflows.candidate_analysis.import_prepare import CandidateImportPrepareWorkflow
from app.workflows.candidate_analysis.score_items import (
    CandidateScoreItemsWorkflow,
    PreparedRubricScoringInput,
)
from app.workflows.candidate_analysis.standardize import CandidateStandardizeWorkflow
from app.workflows.candidate_analysis.summarize import CandidateSummarizeWorkflow


@dataclass(frozen=True)
class CandidateAnalysisBundle:
    prepared_input: PreparedCandidateImportInput
    standardized_candidate: CandidateStandardizationSchema
    rubric_score_items: CandidateRubricScoreItemsResult
    supervisor_summary: CandidateSupervisorSchema


class CandidateAnalysisService:
    def __init__(
        self,
        session: Session,
        job_repository: JobRepository,
        import_prepare_workflow: CandidateImportPrepareWorkflow,
        standardize_workflow: CandidateStandardizeWorkflow,
        score_items_workflow: CandidateScoreItemsWorkflow,
        summarize_workflow: CandidateSummarizeWorkflow,
        temp_upload_dir_path: Path | None = None,
    ) -> None:
        self.session = session
        self.job_repository = job_repository
        self.import_prepare_workflow = import_prepare_workflow
        self.standardize_workflow = standardize_workflow
        self.score_items_workflow = score_items_workflow
        self.summarize_workflow = summarize_workflow
        self.temp_upload_dir_path = temp_upload_dir_path

    async def analyze_candidate(
        self,
        *,
        job_id: str,
        raw_text_input: str | None,
        files: list[UploadFile],
    ) -> CandidateAnalysisBundle:
        job = self._get_active_job(job_id)
        prepared_input = await self.import_prepare_workflow.run(
            session=self.session,
            job_id=job_id,
            raw_text_input=raw_text_input,
            files=files,
        )
        try:
            standardized_candidate = self.standardize_workflow.run(prepared_input)
            rubric_items = [self._serialize_rubric_item(item) for item in job.rubric_items]
            rubric_score_items = await self.score_items_workflow.run(
                PreparedRubricScoringInput(
                    prepared_input=prepared_input,
                    standardized_candidate=standardized_candidate,
                    rubric_items=rubric_items,
                )
            )
            hard_requirement_overall = self._compute_hard_requirement_overall(rubric_score_items)
            overall_score_5 = self._compute_overall_score_5(rubric_score_items, rubric_items)
            overall_score_percent = round(overall_score_5 / 5 * 100, 2)
            supervisor_summary = self.summarize_workflow.run(
                job_title=job.title,
                job_summary=job.summary,
                standardized_candidate=standardized_candidate,
                rubric_score_items=rubric_score_items,
                hard_requirement_overall=hard_requirement_overall,
                overall_score_5=overall_score_5,
                overall_score_percent=overall_score_percent,
            )
            return CandidateAnalysisBundle(
                prepared_input=prepared_input,
                standardized_candidate=standardized_candidate,
                rubric_score_items=rubric_score_items,
                supervisor_summary=supervisor_summary,
            )
        except Exception:
            self._cleanup_temp_request(prepared_input.temp_request_id)
            raise

    def _get_active_job(self, job_id: str):
        try:
            job = self.job_repository.get_job_for_edit(self.session, job_id)
        except LookupError as exc:
            raise NotFoundError(f"Job {job_id} not found.") from exc

        if job.lifecycle_status != "active":
            raise ConflictError(f"Job {job_id} is not ready for candidate analysis.")
        return job

    def _compute_hard_requirement_overall(
        self,
        rubric_score_items: CandidateRubricScoreItemsResult,
    ) -> str:
        decisions = [item.hard_requirement_decision for item in rubric_score_items.hard_requirement_results]
        if any(decision == "fail" for decision in decisions):
            return "has_fail"
        if any(decision == "borderline" for decision in decisions):
            return "has_borderline"
        return "all_pass"

    def _compute_overall_score_5(
        self,
        rubric_score_items: CandidateRubricScoreItemsResult,
        rubric_items: list[dict[str, Any]],
    ) -> float:
        weight_by_id = {
            item["id"]: item["weight_normalized"] or 0
            for item in rubric_items
            if item["criterion_type"] == "weighted"
        }
        total = 0.0
        for result in rubric_score_items.weighted_results:
            weight = weight_by_id.get(result.job_rubric_item_id)
            if weight is None:
                raise DomainValidationError(
                    f"Missing weight for weighted rubric result {result.job_rubric_item_id}."
                )
            total += result.score_0_to_5 * weight
        return round(total, 4)

    def _serialize_rubric_item(self, rubric_item) -> dict[str, Any]:
        return {
            "id": rubric_item.id,
            "sort_order": rubric_item.sort_order,
            "name": rubric_item.name,
            "description": rubric_item.description,
            "criterion_type": rubric_item.criterion_type,
            "weight_input": rubric_item.weight_input,
            "weight_normalized": rubric_item.weight_normalized,
            "scoring_standard_json": rubric_item.scoring_standard_json,
            "agent_prompt_text": rubric_item.agent_prompt_text,
            "evidence_guidance_text": rubric_item.evidence_guidance_text,
        }

    def _cleanup_temp_request(self, request_id: str) -> None:
        if self.temp_upload_dir_path is None:
            return
        shutil.rmtree(self.temp_upload_dir_path / "candidate-imports" / request_id, ignore_errors=True)
