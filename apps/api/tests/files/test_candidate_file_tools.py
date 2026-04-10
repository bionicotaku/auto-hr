import asyncio
from io import BytesIO
from pathlib import Path

from fastapi import UploadFile
from pypdf import PdfWriter

from app.core.config import get_settings
from app.files.pdf_extract import extract_pdf_text
from app.files.temp_manager import TempImportManager


def build_pdf_bytes() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    buffer = BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def test_temp_import_manager_creates_and_cleans_up_context(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TEMP_UPLOAD_DIR", str(tmp_path / "tmp"))
    get_settings.cache_clear()

    manager = TempImportManager(get_settings())
    context = manager.create_context()

    assert context.input_dir.exists()
    assert context.extracted_dir.exists()

    manager.cleanup(context)

    assert not context.root_dir.exists()


def test_temp_import_manager_saves_pdf_uploads(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TEMP_UPLOAD_DIR", str(tmp_path / "tmp"))
    get_settings.cache_clear()

    manager = TempImportManager(get_settings())
    context = manager.create_context()

    uploads = [
        UploadFile(
            filename="resume-1.pdf",
            file=Path(tmp_path / "resume-1.pdf").open("wb+"),
            headers={"content-type": "application/pdf"},
        ),
        UploadFile(
            filename="resume-2.pdf",
            file=Path(tmp_path / "resume-2.pdf").open("wb+"),
            headers={"content-type": "application/pdf"},
        ),
    ]
    pdf_bytes = build_pdf_bytes()
    for upload in uploads:
        upload.file.write(pdf_bytes)
        upload.file.seek(0)

    saved = asyncio.run(manager.save_uploads(context, uploads))

    assert len(saved) == 2
    assert saved[0].stored_path.exists()
    assert saved[1].stored_path.exists()

    for upload in uploads:
        upload.file.close()


def test_temp_import_manager_rejects_non_pdf(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TEMP_UPLOAD_DIR", str(tmp_path / "tmp"))
    get_settings.cache_clear()

    manager = TempImportManager(get_settings())
    context = manager.create_context()
    upload = UploadFile(
        filename="notes.txt",
        file=Path(tmp_path / "notes.txt").open("wb+"),
        headers={"content-type": "text/plain"},
    )
    upload.file.write(b"not a pdf")
    upload.file.seek(0)

    try:
        try:
            asyncio.run(manager.save_uploads(context, [upload]))
        except ValueError as exc:
            assert str(exc) == "Only PDF files are allowed."
        else:
            raise AssertionError("Expected ValueError for non-PDF upload.")
    finally:
        upload.file.close()


def test_extract_pdf_text_returns_text_and_page_count(tmp_path) -> None:
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(build_pdf_bytes())

    extracted = extract_pdf_text(pdf_path)

    assert extracted.page_count == 1
    assert isinstance(extracted.text, str)
