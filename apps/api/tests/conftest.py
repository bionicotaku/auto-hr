from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_engine, get_session_factory, reset_db_caches
from app.main import create_app
from app.models import Base


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    database_url = f"sqlite:///{(tmp_path / 'test.db').as_posix()}"

    monkeypatch.setenv("DATABASE_URL", database_url)
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "data" / "uploads"))
    monkeypatch.setenv("TEMP_UPLOAD_DIR", str(tmp_path / "data" / "tmp"))

    get_settings.cache_clear()
    reset_db_caches()

    engine = get_engine()
    Base.metadata.create_all(bind=engine)

    app = create_app()
    with TestClient(app) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=engine)
    reset_db_caches()
    get_settings.cache_clear()


@pytest.fixture
def db_session(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Session:
    database_url = f"sqlite:///{(tmp_path / 'test.db').as_posix()}"

    monkeypatch.setenv("DATABASE_URL", database_url)
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "data" / "uploads"))
    monkeypatch.setenv("TEMP_UPLOAD_DIR", str(tmp_path / "data" / "tmp"))

    get_settings.cache_clear()
    reset_db_caches()

    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    session = get_session_factory()()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        reset_db_caches()
        get_settings.cache_clear()
