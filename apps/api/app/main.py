from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()

    settings.data_dir_path.mkdir(parents=True, exist_ok=True)
    settings.upload_dir_path.mkdir(parents=True, exist_ok=True)
    settings.temp_upload_dir_path.mkdir(parents=True, exist_ok=True)

    yield


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title="auto-hr API",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.include_router(api_router)
    register_exception_handlers(app)
    return app


app = create_app()
