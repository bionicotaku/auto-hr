import asyncio
import json
from collections.abc import AsyncIterator

from sqlalchemy.orm import Session, sessionmaker

from app.core.exceptions import NotFoundError
from app.repositories.analysis_run_repository import AnalysisRunRepository
from app.schemas.analysis_runs import AnalysisRunResponse


class AnalysisRunService:
    def __init__(
        self,
        *,
        session_factory: sessionmaker[Session],
        repository: AnalysisRunRepository,
        poll_interval_seconds: float = 0.5,
    ) -> None:
        self.session_factory = session_factory
        self.repository = repository
        self.poll_interval_seconds = poll_interval_seconds

    def get_run(self, run_id: str) -> AnalysisRunResponse:
        with self.session_factory() as session:
            try:
                run = self.repository.get_run(session, run_id)
            except LookupError as exc:
                raise NotFoundError(f"Analysis run {run_id} not found.") from exc
            return self._to_response(run)

    async def stream_run_events(self, run_id: str) -> AsyncIterator[str]:
        current_snapshot = self.get_run(run_id)
        yield self._format_sse(
            "connected",
            {
                "run_id": current_snapshot.run_id,
                "run_type": current_snapshot.run_type,
                "status": current_snapshot.status,
                "current_stage": current_snapshot.current_stage,
                "current_ai_step": current_snapshot.current_ai_step,
                "total_ai_steps": current_snapshot.total_ai_steps,
            },
        )

        last_event_index = 0
        while True:
            with self.session_factory() as session:
                try:
                    run = self.repository.get_run(session, run_id)
                except LookupError as exc:
                    raise NotFoundError(f"Analysis run {run_id} not found.") from exc
                events = self.repository.list_events_after(
                    session,
                    run_id=run_id,
                    after_event_index=last_event_index,
                )

            for event in events:
                yield self._format_sse(event.event_type, event.payload_json)
                last_event_index = event.event_index

            if run.status in {"completed", "failed"} and last_event_index >= run.last_event_index:
                break

            await asyncio.sleep(self.poll_interval_seconds)

    def _to_response(self, run) -> AnalysisRunResponse:
        return AnalysisRunResponse(
            run_id=run.id,
            run_type=run.run_type,
            resource_id=run.resource_id,
            status=run.status,
            current_stage=run.current_stage,
            current_ai_step=run.current_ai_step,
            total_ai_steps=run.total_ai_steps,
            result_resource_type=run.result_resource_type,
            result_resource_id=run.result_resource_id,
            error_message=run.error_message,
            created_at=run.created_at,
            updated_at=run.updated_at,
        )

    def _format_sse(self, event_type: str, payload: dict) -> str:
        return f"event: {event_type}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


class AnalysisRunProgressReporter:
    def __init__(
        self,
        *,
        session_factory: sessionmaker[Session],
        repository: AnalysisRunRepository,
        run_id: str,
    ) -> None:
        self.session_factory = session_factory
        self.repository = repository
        self.run_id = run_id

    def set_stage(self, current_stage: str, message: str) -> None:
        with self.session_factory.begin() as session:
            run = self.repository.get_run(session, self.run_id)
            status = "running" if run.status != "failed" else run.status
            self.repository.update_run(
                session,
                run,
                status=status,
                current_stage=current_stage,
            )
            self.repository.append_event(
                session,
                run,
                event_type="progress",
                payload_json=self._progress_payload(run, current_stage=current_stage, message=message),
            )

    def record_ai_step(self, current_stage: str, message: str) -> None:
        with self.session_factory.begin() as session:
            run = self.repository.get_run(session, self.run_id)
            next_step = min(run.current_ai_step + 1, run.total_ai_steps)
            self.repository.update_run(
                session,
                run,
                status="running",
                current_stage=current_stage,
                current_ai_step=next_step,
            )
            self.repository.append_event(
                session,
                run,
                event_type="progress",
                payload_json=self._progress_payload(
                    run,
                    current_stage=current_stage,
                    current_ai_step=next_step,
                    message=message,
                ),
            )

    def mark_completed(
        self,
        *,
        result_resource_type: Literal["job", "candidate"],
        result_resource_id: str,
    ) -> None:
        with self.session_factory.begin() as session:
            run = self.repository.get_run(session, self.run_id)
            self.repository.update_run(
                session,
                run,
                status="completed",
                current_stage="completed",
                result_resource_type=result_resource_type,
                result_resource_id=result_resource_id,
                error_message=None,
            )
            self.repository.append_event(
                session,
                run,
                event_type="completed",
                payload_json={
                    "run_id": run.id,
                    "run_type": run.run_type,
                    "result_resource_type": result_resource_type,
                    "result_resource_id": result_resource_id,
                },
            )

    def mark_failed(self, message: str) -> None:
        with self.session_factory.begin() as session:
            run = self.repository.get_run(session, self.run_id)
            self.repository.update_run(
                session,
                run,
                status="failed",
                current_stage="failed",
                error_message=message,
            )
            self.repository.append_event(
                session,
                run,
                event_type="failed",
                payload_json={
                    "run_id": run.id,
                    "run_type": run.run_type,
                    "message": message,
                },
            )

    def _progress_payload(
        self,
        run,
        *,
        current_stage: str,
        message: str,
        current_ai_step: int | None = None,
    ) -> dict[str, object]:
        return {
            "run_id": run.id,
            "run_type": run.run_type,
            "current_stage": current_stage,
            "current_ai_step": run.current_ai_step if current_ai_step is None else current_ai_step,
            "total_ai_steps": run.total_ai_steps,
            "message": message,
        }
