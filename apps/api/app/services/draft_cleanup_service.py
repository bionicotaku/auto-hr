import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.repositories.job_repository import JobRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DraftCleanupItem:
    job_id: str
    updated_at: datetime


@dataclass(frozen=True)
class DraftCleanupResult:
    dry_run: bool
    older_than_hours: int
    limit: int | None
    matched_items: list[DraftCleanupItem]
    deleted_count: int


class DraftCleanupService:
    def __init__(self, session: Session, job_repository: JobRepository) -> None:
        self.session = session
        self.job_repository = job_repository

    def cleanup_expired_drafts(
        self,
        *,
        older_than_hours: int = 48,
        apply: bool = False,
        limit: int | None = None,
    ) -> DraftCleanupResult:
        cutoff = datetime.now(UTC) - timedelta(hours=older_than_hours)
        logger.info(
            "Draft cleanup started: stage=draft_cleanup result=start apply=%s older_than_hours=%s limit=%s",
            apply,
            older_than_hours,
            limit,
        )
        jobs = self.job_repository.list_expired_drafts(
            self.session,
            older_than=cutoff,
            limit=limit,
        )
        items = [DraftCleanupItem(job_id=job.id, updated_at=job.updated_at) for job in jobs]

        if not apply:
            logger.info(
                "Draft cleanup finished: stage=draft_cleanup result=success apply=%s matched_count=%s deleted_count=0",
                apply,
                len(items),
            )
            return DraftCleanupResult(
                dry_run=True,
                older_than_hours=older_than_hours,
                limit=limit,
                matched_items=items,
                deleted_count=0,
            )

        try:
            deleted_count = self.job_repository.delete_jobs(self.session, jobs)
            self.session.commit()
        except Exception as exc:
            self.session.rollback()
            logger.exception(
                "Draft cleanup failed: stage=draft_cleanup result=failure apply=%s matched_count=%s reason=%s",
                apply,
                len(items),
                exc,
            )
            raise

        logger.info(
            "Draft cleanup finished: stage=draft_cleanup result=success apply=%s matched_count=%s deleted_count=%s",
            apply,
            len(items),
            deleted_count,
        )
        return DraftCleanupResult(
            dry_run=False,
            older_than_hours=older_than_hours,
            limit=limit,
            matched_items=items,
            deleted_count=deleted_count,
        )
