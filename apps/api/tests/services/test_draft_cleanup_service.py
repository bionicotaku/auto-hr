from __future__ import annotations

import importlib.util
from datetime import UTC, datetime, timedelta
from pathlib import Path

from app.repositories.job_repository import JobCreateData, JobRepository, JobRubricItemCreateData
from app.services.draft_cleanup_service import DraftCleanupService


def make_job_create_data(*, lifecycle_status: str = "draft") -> JobCreateData:
    return JobCreateData(
        lifecycle_status=lifecycle_status,
        creation_mode="from_description",
        title="AI Recruiter",
        summary="Own hiring workflows.",
        description_text="Detailed JD",
        structured_info_json={"department": "Talent"},
        original_description_input="original description",
        original_form_input_json=None,
        editor_history_summary=None,
        editor_recent_messages_json=[],
    )


def make_rubric_items() -> list[JobRubricItemCreateData]:
    return [
        JobRubricItemCreateData(
            sort_order=1,
            name="Execution",
            description="Run hiring loops",
            criterion_type="weighted",
            weight_input=60,
            weight_normalized=0.6,
            scoring_standard_items=[{"key": "5", "value": "Excellent"}],
            agent_prompt_text="Judge execution",
            evidence_guidance_text="Look for examples",
        )
    ]


def create_job(db_session, *, lifecycle_status: str, updated_at_hours_ago: int):
    repository = JobRepository()
    job = repository.create_job_with_rubric_items(
        db_session,
        job_data=make_job_create_data(lifecycle_status=lifecycle_status),
        rubric_items=make_rubric_items(),
    )
    job.updated_at = datetime.now(UTC) - timedelta(hours=updated_at_hours_ago)
    db_session.commit()
    return repository.get_job_for_edit(db_session, job.id)


def load_cleanup_script_module():
    module_path = Path(__file__).resolve().parents[4] / "scripts" / "cleanup_drafts.py"
    spec = importlib.util.spec_from_file_location("cleanup_drafts_script", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_draft_cleanup_service_dry_run_and_apply(db_session) -> None:
    old_draft = create_job(db_session, lifecycle_status="draft", updated_at_hours_ago=72)
    recent_draft = create_job(db_session, lifecycle_status="draft", updated_at_hours_ago=12)
    active_job = create_job(db_session, lifecycle_status="active", updated_at_hours_ago=96)

    service = DraftCleanupService(db_session, JobRepository())

    dry_run = service.cleanup_expired_drafts(older_than_hours=48, apply=False)
    assert dry_run.dry_run is True
    assert [item.job_id for item in dry_run.matched_items] == [old_draft.id]
    assert dry_run.deleted_count == 0

    apply_result = service.cleanup_expired_drafts(older_than_hours=48, apply=True)
    assert apply_result.dry_run is False
    assert [item.job_id for item in apply_result.matched_items] == [old_draft.id]
    assert apply_result.deleted_count == 1

    repository = JobRepository()
    assert repository.list_expired_drafts(
        db_session,
        older_than=datetime.now(UTC) - timedelta(hours=48),
    ) == []
    assert repository.get_job_for_edit(db_session, recent_draft.id).id == recent_draft.id
    assert repository.get_job_for_edit(db_session, active_job.id).id == active_job.id


def test_cleanup_drafts_script_supports_dry_run_and_limit(db_session, capsys) -> None:
    first_old_draft = create_job(db_session, lifecycle_status="draft", updated_at_hours_ago=72)
    second_old_draft = create_job(db_session, lifecycle_status="draft", updated_at_hours_ago=96)

    module = load_cleanup_script_module()
    exit_code = module.main(["--older-than-hours", "48", "--limit", "1"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "mode=dry-run" in captured.out
    assert "matched=1" in captured.out
    assert first_old_draft.id in captured.out or second_old_draft.id in captured.out
