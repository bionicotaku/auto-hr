from dataclasses import dataclass
from datetime import datetime, UTC
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.analysis_run import AnalysisRun
from app.models.analysis_run_event import AnalysisRunEvent


@dataclass(frozen=True)
class AnalysisRunCreateData:
    run_type: str
    resource_id: str
    current_stage: str
    total_ai_steps: int
    payload_json: dict[str, Any]


class AnalysisRunRepository:
    def create_run(self, session: Session, data: AnalysisRunCreateData) -> AnalysisRun:
        run = AnalysisRun(
            run_type=data.run_type,
            resource_id=data.resource_id,
            status="queued",
            current_stage=data.current_stage,
            current_ai_step=0,
            total_ai_steps=data.total_ai_steps,
            payload_json=data.payload_json,
        )
        session.add(run)
        session.flush()
        return run

    def get_run(self, session: Session, run_id: str) -> AnalysisRun:
        run = session.get(AnalysisRun, run_id)
        if run is None:
            raise LookupError(run_id)
        return run

    def update_run(
        self,
        session: Session,
        run: AnalysisRun,
        *,
        status: str | None = None,
        current_stage: str | None = None,
        current_ai_step: int | None = None,
        result_resource_type: str | None = None,
        result_resource_id: str | None = None,
        error_message: str | None = None,
    ) -> AnalysisRun:
        if status is not None:
            run.status = status
        if current_stage is not None:
            run.current_stage = current_stage
        if current_ai_step is not None:
            run.current_ai_step = current_ai_step
        if result_resource_type is not None:
            run.result_resource_type = result_resource_type
        if result_resource_id is not None:
            run.result_resource_id = result_resource_id
        run.error_message = error_message
        run.updated_at = datetime.now(UTC)
        session.add(run)
        session.flush()
        return run

    def append_event(
        self,
        session: Session,
        run: AnalysisRun,
        *,
        event_type: str,
        payload_json: dict[str, Any],
    ) -> AnalysisRunEvent:
        run.last_event_index += 1
        run.updated_at = datetime.now(UTC)
        event = AnalysisRunEvent(
            run_id=run.id,
            event_index=run.last_event_index,
            event_type=event_type,
            payload_json=payload_json,
        )
        session.add(run)
        session.add(event)
        session.flush()
        return event

    def list_events_after(
        self,
        session: Session,
        *,
        run_id: str,
        after_event_index: int,
    ) -> list[AnalysisRunEvent]:
        statement = (
            select(AnalysisRunEvent)
            .where(
                AnalysisRunEvent.run_id == run_id,
                AnalysisRunEvent.event_index > after_event_index,
            )
            .order_by(AnalysisRunEvent.event_index.asc())
        )
        return list(session.scalars(statement).all())
