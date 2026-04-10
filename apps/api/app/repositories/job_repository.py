from dataclasses import dataclass
from datetime import datetime, UTC
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from app.models.job import Job
from app.models.job_rubric_item import JobRubricItem


@dataclass(frozen=True)
class JobRubricItemCreateData:
    sort_order: int
    name: str
    description: str
    criterion_type: str
    weight_input: float
    weight_normalized: float | None
    scoring_standard_items: list[dict[str, Any]]
    agent_prompt_text: str
    evidence_guidance_text: str


@dataclass(frozen=True)
class JobCreateData:
    lifecycle_status: str
    creation_mode: str
    title: str
    summary: str
    description_text: str
    structured_info_json: dict[str, Any]
    original_description_input: str | None
    original_form_input_json: dict[str, Any] | None
    editor_history_summary: str | None
    editor_recent_messages_json: list[dict[str, Any]]
    finalized_at: datetime | None = None


class JobRepository:
    def create_job_with_rubric_items(
        self,
        session: Session,
        job_data: JobCreateData,
        rubric_items: list[JobRubricItemCreateData],
    ) -> Job:
        job = Job(
            lifecycle_status=job_data.lifecycle_status,
            creation_mode=job_data.creation_mode,
            title=job_data.title,
            summary=job_data.summary,
            description_text=job_data.description_text,
            structured_info_json=job_data.structured_info_json,
            original_description_input=job_data.original_description_input,
            original_form_input_json=job_data.original_form_input_json,
            editor_history_summary=job_data.editor_history_summary,
            editor_recent_messages_json=job_data.editor_recent_messages_json,
            finalized_at=job_data.finalized_at,
        )
        session.add(job)
        session.flush()

        for item in rubric_items:
            session.add(
                JobRubricItem(
                    job_id=job.id,
                    sort_order=item.sort_order,
                    name=item.name,
                    description=item.description,
                    criterion_type=item.criterion_type,
                    weight_input=item.weight_input,
                    weight_normalized=item.weight_normalized,
                    scoring_standard_items=item.scoring_standard_items,
                    agent_prompt_text=item.agent_prompt_text,
                    evidence_guidance_text=item.evidence_guidance_text,
                )
            )

        session.flush()
        return self.get_job_for_edit(session, job.id)

    def get_job_for_edit(self, session: Session, job_id: str) -> Job:
        statement = (
            select(Job)
            .options(selectinload(Job.rubric_items))
            .where(Job.id == job_id)
        )
        job = session.scalar(statement)
        if job is None:
            raise LookupError(job_id)
        return job

    def get_job(self, session: Session, job_id: str) -> Job:
        statement = select(Job).where(Job.id == job_id)
        job = session.scalar(statement)
        if job is None:
            raise LookupError(job_id)
        return job

    def list_jobs(self, session: Session) -> list[Job]:
        statement = (
            select(Job)
            .where(Job.lifecycle_status == "active")
            .order_by(Job.updated_at.desc())
        )
        return list(session.scalars(statement).all())

    def delete_draft_job(self, session: Session, job_id: str) -> bool:
        job = session.get(Job, job_id)
        if job is None or job.lifecycle_status != "draft":
            return False

        session.delete(job)
        return True

    def list_expired_drafts(
        self,
        session: Session,
        *,
        older_than: datetime,
        limit: int | None = None,
    ) -> list[Job]:
        statement = (
            select(Job)
            .where(Job.lifecycle_status == "draft", Job.updated_at <= older_than)
            .order_by(Job.updated_at.asc())
        )
        if limit is not None:
            statement = statement.limit(limit)
        return list(session.scalars(statement).all())

    def delete_jobs(self, session: Session, jobs: list[Job]) -> int:
        deleted_count = 0
        for job in jobs:
            session.delete(job)
            deleted_count += 1
        return deleted_count

    def replace_rubric_items(
        self,
        session: Session,
        job_id: str,
        rubric_items: list[JobRubricItemCreateData],
    ) -> None:
        session.execute(delete(JobRubricItem).where(JobRubricItem.job_id == job_id))
        for item in rubric_items:
            session.add(
                JobRubricItem(
                    job_id=job_id,
                    sort_order=item.sort_order,
                    name=item.name,
                    description=item.description,
                    criterion_type=item.criterion_type,
                    weight_input=item.weight_input,
                    weight_normalized=item.weight_normalized,
                    scoring_standard_items=item.scoring_standard_items,
                    agent_prompt_text=item.agent_prompt_text,
                    evidence_guidance_text=item.evidence_guidance_text,
                )
            )

    def touch_updated_at(self, session: Session, job: Job) -> None:
        job.updated_at = datetime.now(UTC)
        session.add(job)

    def finalize_job(
        self,
        session: Session,
        job: Job,
        *,
        title: str,
        summary: str,
        description_text: str,
        structured_info_json: dict[str, Any],
        rubric_items: list[JobRubricItemCreateData],
    ) -> Job:
        job.lifecycle_status = "active"
        job.title = title
        job.summary = summary
        job.description_text = description_text
        job.structured_info_json = structured_info_json
        job.finalized_at = datetime.now(UTC)
        job.updated_at = datetime.now(UTC)
        session.add(job)

        self.replace_rubric_items(session, job.id, rubric_items)
        session.flush()
        return self.get_job_for_edit(session, job.id)
