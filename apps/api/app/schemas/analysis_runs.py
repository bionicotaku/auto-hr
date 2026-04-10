from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class AnalysisRunStartResponse(BaseModel):
    run_id: str
    run_type: Literal["job_finalize", "candidate_import"]
    status: Literal["queued", "running", "completed", "failed"]
    total_ai_steps: int


class AnalysisRunResponse(BaseModel):
    run_id: str
    run_type: Literal["job_finalize", "candidate_import"]
    resource_id: str
    status: Literal["queued", "running", "completed", "failed"]
    current_stage: str
    current_ai_step: int
    total_ai_steps: int
    result_resource_type: Literal["job", "candidate"] | None
    result_resource_id: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime
