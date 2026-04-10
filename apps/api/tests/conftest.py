from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.db import reset_db_caches
from app.main import create_app


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    database_url = f"sqlite:///{(tmp_path / 'test.db').as_posix()}"

    monkeypatch.setenv("DATABASE_URL", database_url)
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "data" / "uploads"))
    monkeypatch.setenv("TEMP_UPLOAD_DIR", str(tmp_path / "data" / "tmp"))

    get_settings.cache_clear()
    reset_db_caches()

    app = create_app()
    with TestClient(app) as test_client:
        yield test_client

    reset_db_caches()
    get_settings.cache_clear()
