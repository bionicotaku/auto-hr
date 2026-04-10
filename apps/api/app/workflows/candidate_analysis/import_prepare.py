from fastapi import UploadFile

from app.core.exceptions import DomainValidationError, NotFoundError
from app.files.pdf_extract import extract_pdf_text
from app.files.temp_manager import TempImportManager
from app.repositories.job_repository import JobRepository
from app.schemas.ai.candidate_standardization import (
    PreparedCandidateDocumentInput,
    PreparedCandidateImportInput,
)


class CandidateImportPrepareWorkflow:
    def __init__(
        self,
        *,
        job_repository: JobRepository,
        temp_import_manager: TempImportManager,
    ) -> None:
        self.job_repository = job_repository
        self.temp_import_manager = temp_import_manager

    async def run(
        self,
        *,
        session,
        job_id: str,
        raw_text_input: str | None,
        files: list[UploadFile],
    ) -> PreparedCandidateImportInput:
        normalized_text = raw_text_input.strip() if raw_text_input else None
        if not normalized_text and not files:
            raise DomainValidationError("Candidate import requires text input or at least one PDF.")
        if len(files) > 4:
            raise DomainValidationError("Candidate import accepts at most 4 PDF files.")

        try:
            job = self.job_repository.get_job(session, job_id)
        except LookupError as exc:
            raise NotFoundError(f"Job {job_id} not found.") from exc

        context = self.temp_import_manager.create_context()
        try:
            saved_uploads = await self.temp_import_manager.save_uploads(context, files)
            documents: list[PreparedCandidateDocumentInput] = []
            for saved_upload in saved_uploads:
                extracted = extract_pdf_text(saved_upload.stored_path)
                documents.append(
                    PreparedCandidateDocumentInput(
                        filename=saved_upload.original_filename,
                        storage_path=str(saved_upload.stored_path),
                        mime_type=saved_upload.mime_type,
                        upload_order=saved_upload.upload_order,
                        extracted_text=extracted.text,
                        page_count=extracted.page_count,
                    )
                )

            return PreparedCandidateImportInput(
                raw_text_input=normalized_text,
                job_id=job.id,
                job_title=job.title,
                job_summary=job.summary,
                temp_request_id=context.request_id,
                documents=documents,
            )
        except Exception:
            self.temp_import_manager.cleanup(context)
            raise
