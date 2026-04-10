from fastapi import APIRouter

from app.api.routers.analysis_runs import router as analysis_runs_router
from app.api.routers.candidates import router as candidates_router
from app.api.routers.health import router as health_router
from app.api.routers.jobs import router as jobs_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(jobs_router)
api_router.include_router(candidates_router)
api_router.include_router(analysis_runs_router)
