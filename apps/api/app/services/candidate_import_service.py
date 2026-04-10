from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, DomainValidationError, NotFoundError
from app.schemas.jobs import CandidateImportResponse
from app.services.candidate_analysis_service import CandidateAnalysisService
from app.workflows.candidate_analysis.persist import CandidatePersistWorkflow


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
        try:
            bundle = await self.candidate_analysis_service.analyze_candidate(
                job_id=job_id,
                raw_text_input=raw_text_input,
                files=files,
            )
            persisted = self.persist_workflow.run(self.session, bundle)
            return CandidateImportResponse(
                candidate_id=persisted.candidate_id,
                job_id=persisted.job_id,
            )
        except (NotFoundError, ConflictError, DomainValidationError):
            raise
        except Exception as exc:
            raise DomainValidationError("Failed to import candidate.") from exc
