from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


@dataclass(frozen=True)
class ExtractedPdfContent:
    text: str
    page_count: int


def extract_pdf_text(file_path: Path) -> ExtractedPdfContent:
    reader = PdfReader(str(file_path))
    pages = reader.pages
    text_parts: list[str] = []

    for page in pages:
        extracted = page.extract_text() or ""
        if extracted:
            text_parts.append(extracted)

    return ExtractedPdfContent(text="\n\n".join(text_parts).strip(), page_count=len(pages))
