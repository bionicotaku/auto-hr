import logging

from sqlalchemy.orm import Session, sessionmaker

from app.core.exceptions import ConflictError, DomainValidationError, NotFoundError
from app.repositories.analysis_run_repository import AnalysisRunCreateData, AnalysisRunRepository
from app.repositories.job_repository import JobRepository
from app.schemas.analysis_runs import AnalysisRunStartResponse
from app.schemas.jobs import JobFinalizeRequest
from app.services.analysis_run_service import AnalysisRunProgressReporter
from app.services.job_service import JobService
from app.workflows.job_definition.finalize import JobDefinitionFinalizeWorkflow

logger = logging.getLogger(__name__)


class JobFinalizeRunService:
    def __init__(
        self,
        *,
        session_factory: sessionmaker[Session],
        analysis_run_repository: AnalysisRunRepository,
        job_repository: JobRepository,
        finalize_workflow: JobDefinitionFinalizeWorkflow,
    ) -> None:
        self.session_factory = session_factory
        self.analysis_run_repository = analysis_run_repository
        self.job_repository = job_repository
        self.finalize_workflow = finalize_workflow

    def start_run(self, *, job_id: str, payload: JobFinalizeRequest) -> AnalysisRunStartResponse:
        with self.session_factory.begin() as session:
            try:
                self.job_repository.get_job_for_edit(session, job_id)
            except LookupError as exc:
                raise NotFoundError(f"Job {job_id} not found.") from exc

            run = self.analysis_run_repository.create_run(
                session,
                AnalysisRunCreateData(
                    run_type="job_finalize",
                    resource_id=job_id,
                    current_stage="preparing",
                    total_ai_steps=1,
                    payload_json=payload.model_dump(mode="json"),
                ),
            )
            return AnalysisRunStartResponse(
                run_id=run.id,
                run_type="job_finalize",
                status="queued",
                total_ai_steps=run.total_ai_steps,
            )

    async def execute_run(self, run_id: str) -> None:
        reporter = AnalysisRunProgressReporter(
            session_factory=self.session_factory,
            repository=self.analysis_run_repository,
            run_id=run_id,
        )
        reporter.set_stage("preparing", "正在准备岗位定稿任务")

        try:
            with self.session_factory() as session:
                run = self.analysis_run_repository.get_run(session, run_id)
                payload = JobFinalizeRequest.model_validate(run.payload_json)
                job_id = run.resource_id

            reporter.set_stage("finalizing_definition", "正在生成最终岗位定义")
            with self.session_factory() as session:
                job_service = JobService(
                    session=session,
                    job_repository=self.job_repository,
                    finalize_workflow=self.finalize_workflow,
                )
                response = await job_service.finalize_draft(job_id, payload)

            reporter.record_ai_step("finalizing_definition", "AI 已完成岗位定稿分析")
            reporter.set_stage("persisting", "正在写入岗位档案")
            reporter.mark_completed(result_resource_type="job", result_resource_id=response.job_id)
        except (NotFoundError, ConflictError, DomainValidationError) as exc:
            logger.warning(
                "Analysis run failed: run_id=%s run_type=job_finalize reason=%s",
                run_id,
                exc,
            )
            reporter.mark_failed(str(exc))
        except Exception as exc:
            logger.exception(
                "Analysis run failed: run_id=%s run_type=job_finalize reason=%s",
                run_id,
                exc,
            )
            reporter.mark_failed("岗位分析失败，请稍后重试。")
