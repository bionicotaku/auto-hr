import shutil
import uuid
from dataclasses import dataclass
from pathlib import Path

from fastapi import UploadFile

from app.core.config import Settings
from app.files.storage import save_upload_file


@dataclass(frozen=True)
class TempImportContext:
    request_id: str
    root_dir: Path
    input_dir: Path
    extracted_dir: Path


@dataclass(frozen=True)
class SavedTempUpload:
    original_filename: str
    stored_path: Path
    mime_type: str
    upload_order: int


class TempImportManager:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def create_context(self) -> TempImportContext:
        request_id = str(uuid.uuid4())
        root_dir = self.settings.temp_upload_dir_path / "candidate-imports" / request_id
        input_dir = root_dir / "input"
        extracted_dir = root_dir / "extracted"

        input_dir.mkdir(parents=True, exist_ok=True)
        extracted_dir.mkdir(parents=True, exist_ok=True)

        return TempImportContext(
            request_id=request_id,
            root_dir=root_dir,
            input_dir=input_dir,
            extracted_dir=extracted_dir,
        )

    async def save_uploads(
        self,
        context: TempImportContext,
        files: list[UploadFile],
    ) -> list[SavedTempUpload]:
        saved_uploads: list[SavedTempUpload] = []

        for index, file in enumerate(files, start=1):
            mime_type = file.content_type or ""
            filename = file.filename or ""
            if mime_type != "application/pdf" and not filename.lower().endswith(".pdf"):
                raise ValueError("Only PDF files are allowed.")

            stored_path = await save_upload_file(file, context.input_dir)
            saved_uploads.append(
                SavedTempUpload(
                    original_filename=filename or stored_path.name,
                    stored_path=stored_path,
                    mime_type=mime_type or "application/pdf",
                    upload_order=index,
                )
            )

        return saved_uploads

    def cleanup(self, context: TempImportContext) -> None:
        shutil.rmtree(context.root_dir, ignore_errors=True)
