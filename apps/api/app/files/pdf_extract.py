from pathlib import Path

from pypdf import PdfReader


def read_pdf_page_count(file_path: Path) -> int:
    reader = PdfReader(str(file_path))
    return len(reader.pages)
