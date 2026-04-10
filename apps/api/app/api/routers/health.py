from fastapi import APIRouter

from app.api.deps import AppSettings, DbSession
from app.core.db import ping_database

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check(session: DbSession, settings: AppSettings) -> dict[str, str]:
    ping_database(session)
    return {
        "status": "ok",
        "environment": settings.app_env,
        "database": "ok",
    }
