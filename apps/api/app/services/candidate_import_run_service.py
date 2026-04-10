import logging
import shutil
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session, sessionmaker

from app.core.exceptions import ConflictError, DomainValidationError, NotFoundError
from app.files.pdf_extract import extract_pdf_text
from app.files.temp_manager import TempImportManager
from app.repositories.analysis_run_repository import AnalysisRunCreateData, AnalysisRunRepository
from app.repositories.job_repository import JobRepository
from app.schemas.ai.candidate_standardization import (
    PreparedCandidateDocumentInput,
    PreparedCandidateImportInput,
)
from app.schemas.analysis_runs import AnalysisRunStartResponse
from app.services.analysis_run_service import AnalysisRunProgressReporter
from app.services.candidate_analysis_service import CandidateAnalysisBundle
from app.workflows.candidate_analysis.persist import CandidatePersistWorkflow
from app.workflows.candidate_analysis.score_items import (
    CandidateScoreItemsWorkflow,
    PreparedRubricScoringInput,
)
from app.workflows.candidate_analysis.standardize import CandidateStandardizeWorkflow
from app.workflows.candidate_analysis.summarize import CandidateSummarizeWorkflow
from app.workflows.candidate_analysis.validity import validate_candidate_for_persistence

logger = logging.getLogger(__name__)


class CandidateImportRunService:
    def __init__(
        self,
        *,
        session_factory: sessionmaker[Session],
        analysis_run_repository: AnalysisRunRepository,
        job_repository: JobRepository,
        temp_import_manager: TempImportManager,
        standardize_workflow: CandidateStandardizeWorkflow,
        score_items_workflow: CandidateScoreItemsWorkflow,
        summarize_workflow: CandidateSummarizeWorkflow,
        persist_workflow: CandidatePersistWorkflow,
        temp_upload_dir_path: Path,
    ) -> None:
        self.session_factory = session_factory
        self.analysis_run_repository = analysis_run_repository
        self.job_repository = job_repository
        self.temp_import_manager = temp_import_manager
        self.standardize_workflow = standardize_workflow
        self.score_items_workflow = score_items_workflow
        self.summarize_workflow = summarize_workflow
        self.persist_workflow = persist_workflow
        self.temp_upload_dir_path = temp_upload_dir_path

    async def start_run(
        self,
        *,
        job_id: str,
        raw_text_input: str | None,
        files: list[UploadFile],
    ) -> AnalysisRunStartResponse:
        normalized_text = raw_text_input.strip() if raw_text_input else None
        if not normalized_text and not files:
            raise DomainValidationError("Candidate import requires text input or at least one PDF.")
        if len(files) > 4:
            raise DomainValidationError("Candidate import accepts at most 4 PDF files.")

        with self.session_factory() as session:
            try:
                job = self.job_repository.get_job_for_edit(session, job_id)
            except LookupError as exc:
                raise NotFoundError(f"Job {job_id} not found.") from exc
            if job.lifecycle_status != "active":
                raise ConflictError(f"Job {job_id} is not ready for candidate analysis.")
            total_ai_steps = len(job.rubric_items) + 2

        context = self.temp_import_manager.create_context()
        try:
            saved_uploads = await self.temp_import_manager.save_uploads(context, files)
            payload_json = {
                "raw_text_input": normalized_text,
                "temp_request_id": context.request_id,
                "documents": [
                    {
                        "filename": item.original_filename,
                        "storage_path": str(item.stored_path),
                        "mime_type": item.mime_type,
                        "upload_order": item.upload_order,
                    }
                    for item in saved_uploads
                ],
            }
            with self.session_factory.begin() as session:
                run = self.analysis_run_repository.create_run(
                    session,
                    AnalysisRunCreateData(
                        run_type="candidate_import",
                        resource_id=job_id,
                        current_stage="preparing",
                        total_ai_steps=total_ai_steps,
                        payload_json=payload_json,
                    ),
                )
                return AnalysisRunStartResponse(
                    run_id=run.id,
                    run_type="candidate_import",
                    status="queued",
                    total_ai_steps=run.total_ai_steps,
                )
        except Exception:
            self.temp_import_manager.cleanup(context)
            raise

    async def execute_run(self, run_id: str) -> None:
        reporter = AnalysisRunProgressReporter(
            session_factory=self.session_factory,
            repository=self.analysis_run_repository,
            run_id=run_id,
        )
        reporter.set_stage("preparing", "正在准备候选人资料")

        temp_request_id: str | None = None
        try:
            with self.session_factory() as session:
                run = self.analysis_run_repository.get_run(session, run_id)
                job = self.job_repository.get_job_for_edit(session, run.resource_id)
                if job.lifecycle_status != "active":
                    raise ConflictError(f"Job {job.id} is not ready for candidate analysis.")
                payload = run.payload_json
                temp_request_id = str(payload["temp_request_id"])
                prepared_input = self._build_prepared_input(
                    job_id=job.id,
                    job_title=job.title,
                    job_summary=job.summary,
                    raw_text_input=payload.get("raw_text_input"),
                    temp_request_id=temp_request_id,
                    documents_payload=payload.get("documents", []),
                )
                rubric_items = [
                    {
                        "id": item.id,
                        "sort_order": item.sort_order,
                        "name": item.name,
                        "description": item.description,
                        "criterion_type": item.criterion_type,
                        "weight_input": item.weight_input,
                        "weight_normalized": item.weight_normalized,
                        "scoring_standard_items": item.scoring_standard_items,
                        "agent_prompt_text": item.agent_prompt_text,
                        "evidence_guidance_text": item.evidence_guidance_text,
                    }
                    for item in job.rubric_items
                ]

            reporter.set_stage("standardizing", "正在标准化候选人信息")
            standardized_candidate = await self.standardize_workflow.run(prepared_input)
            validate_candidate_for_persistence(standardized_candidate)
            reporter.record_ai_step("standardizing", "AI 已完成候选人标准化")

            reporter.set_stage("scoring", "正在逐项分析评估规范")
            rubric_score_items = await self.score_items_workflow.run(
                PreparedRubricScoringInput(
                    prepared_input=prepared_input,
                    standardized_candidate=standardized_candidate,
                    rubric_items=rubric_items,
                ),
                progress_callback=lambda result: self._record_scoring_progress(
                    reporter,
                    result,
                ),
            )

            hard_requirement_overall = self._compute_hard_requirement_overall(rubric_score_items)
            overall_score_5 = self._compute_overall_score_5(rubric_score_items, rubric_items)
            overall_score_percent = round(overall_score_5 / 5 * 100, 2)

            reporter.set_stage("summarizing", "正在生成候选人汇总结论")
            supervisor_summary = await self.summarize_workflow.run(
                job_title=job.title,
                job_summary=job.summary,
                standardized_candidate=standardized_candidate,
                rubric_score_items=rubric_score_items,
                hard_requirement_overall=hard_requirement_overall,
                overall_score_5=overall_score_5,
                overall_score_percent=overall_score_percent,
            )
            reporter.record_ai_step("summarizing", "AI 已完成候选人汇总")

            reporter.set_stage("persisting", "正在写入候选人档案")
            bundle = CandidateAnalysisBundle(
                prepared_input=prepared_input,
                standardized_candidate=standardized_candidate,
                rubric_score_items=rubric_score_items,
                supervisor_summary=supervisor_summary,
            )
            with self.session_factory() as session:
                persisted = self.persist_workflow.run(session, bundle)
            reporter.mark_completed(result_resource_type="candidate", result_resource_id=persisted.candidate_id)
        except (NotFoundError, ConflictError, DomainValidationError) as exc:
            logger.warning(
                "Analysis run failed: run_id=%s run_type=candidate_import reason=%s",
                run_id,
                exc,
            )
            self._cleanup_temp_request(temp_request_id)
            reporter.mark_failed(str(exc))
        except Exception as exc:
            logger.exception(
                "Analysis run failed: run_id=%s run_type=candidate_import reason=%s",
                run_id,
                exc,
            )
            self._cleanup_temp_request(temp_request_id)
            reporter.mark_failed("候选人分析失败，请稍后重试。")

    def _build_prepared_input(
        self,
        *,
        job_id: str,
        job_title: str,
        job_summary: str,
        raw_text_input: str | None,
        temp_request_id: str,
        documents_payload: list[dict],
    ) -> PreparedCandidateImportInput:
        documents: list[PreparedCandidateDocumentInput] = []
        for item in documents_payload:
            storage_path = str(item["storage_path"])
            extracted = extract_pdf_text(Path(storage_path))
            documents.append(
                PreparedCandidateDocumentInput(
                    filename=str(item["filename"]),
                    storage_path=storage_path,
                    mime_type=str(item["mime_type"]),
                    upload_order=int(item["upload_order"]),
                    extracted_text=extracted.text,
                    page_count=extracted.page_count,
                )
            )
        return PreparedCandidateImportInput(
            raw_text_input=raw_text_input,
            job_id=job_id,
            job_title=job_title,
            job_summary=job_summary,
            temp_request_id=temp_request_id,
            documents=documents,
        )

    async def _record_scoring_progress(self, reporter: AnalysisRunProgressReporter, result) -> None:
        label = getattr(result, "job_rubric_item_id", "")
        reporter.record_ai_step("scoring", f"AI 已完成评估项分析：{label}")

    def _compute_hard_requirement_overall(self, rubric_score_items) -> str:
        decisions = [item.hard_requirement_decision for item in rubric_score_items.hard_requirement_results]
        if any(decision == "fail" for decision in decisions):
            return "has_fail"
        if any(decision == "borderline" for decision in decisions):
            return "has_borderline"
        return "all_pass"

    def _compute_overall_score_5(self, rubric_score_items, rubric_items: list[dict]) -> float:
        weight_by_id = {
            item["id"]: item["weight_normalized"] or 0
            for item in rubric_items
            if item["criterion_type"] == "weighted"
        }
        total = 0.0
        for result in rubric_score_items.weighted_results:
            total += result.score_0_to_5 * weight_by_id.get(result.job_rubric_item_id, 0)
        return round(total, 4)

    def _cleanup_temp_request(self, request_id: str | None) -> None:
        if not request_id:
            return
        shutil.rmtree(self.temp_upload_dir_path / "candidate-imports" / request_id, ignore_errors=True)
