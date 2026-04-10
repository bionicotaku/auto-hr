import logging

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, DomainValidationError, NotFoundError
from app.schemas.jobs import CandidateImportResponse
from app.services.candidate_analysis_service import CandidateAnalysisService
from app.workflows.candidate_analysis.persist import CandidatePersistWorkflow

logger = logging.getLogger(__name__)


class CandidateImportService:
    def __init__(
        self,
        session: Session,
        candidate_analysis_service: CandidateAnalysisService,
        persist_workflow: CandidatePersistWorkflow,
    ) -> None:
        self.session = session
        self.candidate_analysis_service = candidate_analysis_service
        self.persist_workflow = persist_workflow

    async def import_candidate(
        self,
        *,
        job_id: str,
        raw_text_input: str | None,
        files: list[UploadFile],
    ) -> CandidateImportResponse:
        logger.info(
            "Candidate stage started: stage=candidate_import result=start job_id=%s file_count=%s",
            job_id,
            len(files),
        )
        try:
            bundle = await self.candidate_analysis_service.analyze_candidate(
                job_id=job_id,
                raw_text_input=raw_text_input,
                files=files,
            )
            persisted = self.persist_workflow.run(self.session, bundle)
            logger.info(
                "Candidate stage finished: stage=candidate_import result=success job_id=%s candidate_id=%s",
                persisted.job_id,
                persisted.candidate_id,
            )
            return CandidateImportResponse(
                candidate_id=persisted.candidate_id,
                job_id=persisted.job_id,
            )
        except (NotFoundError, ConflictError, DomainValidationError):
            logger.warning(
                "Candidate stage failed: stage=candidate_import result=failure job_id=%s reason=known_error",
                job_id,
            )
            raise
        except ValueError as exc:
            logger.warning(
                "Candidate stage failed: stage=candidate_import result=failure job_id=%s reason=%s",
                job_id,
                exc,
            )
            raise DomainValidationError(str(exc)) from exc
        except Exception as exc:
            logger.exception(
                "Candidate stage failed: stage=candidate_import result=failure job_id=%s reason=%s",
                job_id,
                exc,
            )
            raise DomainValidationError("Failed to import candidate.") from exc
