from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile


def sanitize_filename(filename: str | None) -> str:
    if not filename:
        return "upload.pdf"
    return Path(filename).name or "upload.pdf"


async def save_upload_file(upload: UploadFile, destination_dir: Path) -> Path:
    destination_dir.mkdir(parents=True, exist_ok=True)
    safe_name = sanitize_filename(upload.filename)
    destination_path = destination_dir / f"{uuid4()}-{safe_name}"

    await upload.seek(0)
    with destination_path.open("wb") as output:
        while True:
            chunk = await upload.read(1024 * 1024)
            if not chunk:
                break
            output.write(chunk)
    await upload.seek(0)
    return destination_path
