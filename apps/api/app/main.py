from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)
    register_exception_handlers(app)
    return app


app = create_app()
