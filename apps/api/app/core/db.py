from functools import lru_cache
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


def _sqlite_connect_args(database_url: str) -> dict[str, bool]:
    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


def _ensure_database_directory(database_url: str) -> None:
    prefix = "sqlite:///"
    if not database_url.startswith(prefix):
        return

    raw_path = database_url[len(prefix) :]
    if raw_path == ":memory:":
        return

    database_path = raw_path
    if database_path.startswith("/"):
        path_parent = database_path.rsplit("/", 1)[0]
    else:
        path_parent = ""

    if path_parent:
        from pathlib import Path

        Path(path_parent).mkdir(parents=True, exist_ok=True)


@lru_cache
def get_engine() -> Engine:
    settings = get_settings()
    database_url = settings.resolved_database_url
    _ensure_database_directory(database_url)

    return create_engine(
        database_url,
        future=True,
        connect_args=_sqlite_connect_args(database_url),
    )


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), autoflush=False, autocommit=False, future=True)


def get_db_session() -> Generator[Session, None, None]:
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()


def ping_database(session: Session) -> None:
    session.execute(text("SELECT 1"))


def reset_db_caches() -> None:
    if get_engine.cache_info().currsize > 0:
        get_engine().dispose()
    get_session_factory.cache_clear()
    get_engine.cache_clear()
