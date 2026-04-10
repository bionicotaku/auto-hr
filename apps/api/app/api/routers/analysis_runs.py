from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.api import service_deps
from app.api.deps import AppSettings
from app.schemas.analysis_runs import AnalysisRunResponse

router = APIRouter(prefix="/api/analysis-runs", tags=["analysis-runs"])


@router.get("/{run_id}", response_model=AnalysisRunResponse)
def get_analysis_run(run_id: str, settings: AppSettings) -> AnalysisRunResponse:
    service = service_deps.get_analysis_run_service(settings)
    return service.get_run(run_id)


@router.get("/{run_id}/events")
async def stream_analysis_run_events(run_id: str, settings: AppSettings) -> StreamingResponse:
    service = service_deps.get_analysis_run_service(settings)
    return StreamingResponse(
        service.stream_run_events(run_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
