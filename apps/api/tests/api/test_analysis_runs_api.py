from app.api import service_deps


class StubAnalysisRunService:
    def get_run(self, run_id: str):
        return {
            "run_id": run_id,
            "run_type": "candidate_import",
            "resource_id": "job-001",
            "status": "running",
            "current_stage": "scoring",
            "current_ai_step": 3,
            "total_ai_steps": 8,
            "result_resource_type": None,
            "result_resource_id": None,
            "error_message": None,
            "created_at": "2026-04-10T00:00:00Z",
            "updated_at": "2026-04-10T00:05:00Z",
        }

    async def stream_run_events(self, run_id: str):
        yield (
            "event: connected\n"
            f'data: {{"run_id":"{run_id}","run_type":"candidate_import","status":"running","current_stage":"preparing","current_ai_step":0,"total_ai_steps":8}}\n\n'
        )
        yield (
            "event: progress\n"
            f'data: {{"run_id":"{run_id}","run_type":"candidate_import","current_stage":"scoring","current_ai_step":3,"total_ai_steps":8,"message":"正在分析评估项 2 / 6"}}\n\n'
        )


def override_analysis_run_service(_settings):
    return StubAnalysisRunService()


def test_get_analysis_run_returns_snapshot(client, monkeypatch) -> None:
    monkeypatch.setattr(service_deps, "get_analysis_run_service", override_analysis_run_service)

    response = client.get("/api/analysis-runs/run-001")

    assert response.status_code == 200
    assert response.json()["run_id"] == "run-001"
    assert response.json()["current_stage"] == "scoring"
    assert response.json()["current_ai_step"] == 3


def test_stream_analysis_run_events_returns_sse(client, monkeypatch) -> None:
    monkeypatch.setattr(service_deps, "get_analysis_run_service", override_analysis_run_service)

    response = client.get("/api/analysis-runs/run-001/events")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "event: connected" in response.text
    assert "event: progress" in response.text
    assert '"current_ai_step":3' in response.text
