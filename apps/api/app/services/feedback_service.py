import logging

from sqlalchemy.orm import Session

from app.core.exceptions import DomainValidationError, NotFoundError
from app.repositories.candidate_repository import (
    CandidateFeedbackCreateData,
    CandidateRepository,
    CandidateTagCreateData,
)
from app.schemas.candidates import (
    CandidateDetailFeedbackResponse,
    CandidateDetailTagResponse,
    CandidateStatusUpdateResponse,
)

logger = logging.getLogger(__name__)


class FeedbackService:
    def __init__(self, session: Session, candidate_repository: CandidateRepository) -> None:
        self.session = session
        self.candidate_repository = candidate_repository

    def update_status(self, candidate_id: str, current_status: str) -> CandidateStatusUpdateResponse:
        logger.info(
            "Candidate stage started: stage=candidate_status_update result=start candidate_id=%s",
            candidate_id,
        )
        candidate = self._get_candidate(candidate_id)
        try:
            self.candidate_repository.update_candidate_status(
                self.session,
                candidate,
                current_status=current_status,
            )
            self.session.commit()
        except Exception as exc:
            self.session.rollback()
            logger.exception(
                "Candidate stage failed: stage=candidate_status_update result=failure candidate_id=%s reason=%s",
                candidate_id,
                exc,
            )
            raise
        logger.info(
            "Candidate stage finished: stage=candidate_status_update result=success candidate_id=%s current_status=%s",
            candidate.id,
            candidate.current_status,
        )
        return CandidateStatusUpdateResponse(candidate_id=candidate.id, current_status=candidate.current_status)

    def add_tag(self, candidate_id: str, tag_name: str) -> CandidateDetailTagResponse:
        normalized_tag_name = tag_name.strip()
        if not normalized_tag_name:
            raise DomainValidationError("tag_name must not be empty.")

        logger.info("Candidate stage started: stage=candidate_tag_add result=start candidate_id=%s", candidate_id)
        candidate = self._get_candidate(candidate_id)
        existing_tags = {tag.tag_name for tag in candidate.tags}
        if normalized_tag_name in existing_tags:
            logger.warning(
                "Candidate stage failed: stage=candidate_tag_add result=failure candidate_id=%s reason=duplicate_tag",
                candidate_id,
            )
            raise DomainValidationError(f"标签“{normalized_tag_name}”已存在。")

        try:
            created = self.candidate_repository.add_candidate_tag(
                self.session,
                candidate,
                CandidateTagCreateData(tag_name=normalized_tag_name, tag_source="manual"),
            )
            self.session.commit()
        except Exception as exc:
            self.session.rollback()
            logger.exception(
                "Candidate stage failed: stage=candidate_tag_add result=failure candidate_id=%s reason=%s",
                candidate_id,
                exc,
            )
            raise

        logger.info(
            "Candidate stage finished: stage=candidate_tag_add result=success candidate_id=%s tag_name=%s",
            candidate.id,
            created.tag_name,
        )
        return CandidateDetailTagResponse(id=created.id, name=created.tag_name, source=created.tag_source)

    def add_feedback(
        self,
        candidate_id: str,
        *,
        note_text: str,
        author_name: str | None,
    ) -> CandidateDetailFeedbackResponse:
        normalized_note = note_text.strip()
        if not normalized_note:
            raise DomainValidationError("note_text must not be empty.")

        normalized_author = author_name.strip() if author_name else None
        logger.info(
            "Candidate stage started: stage=candidate_feedback_add result=start candidate_id=%s",
            candidate_id,
        )
        candidate = self._get_candidate(candidate_id)
        try:
            created = self.candidate_repository.add_candidate_feedback(
                self.session,
                candidate,
                CandidateFeedbackCreateData(
                    note_text=normalized_note,
                    author_name=normalized_author or None,
                ),
            )
            self.session.commit()
        except Exception as exc:
            self.session.rollback()
            logger.exception(
                "Candidate stage failed: stage=candidate_feedback_add result=failure candidate_id=%s reason=%s",
                candidate_id,
                exc,
            )
            raise

        logger.info(
            "Candidate stage finished: stage=candidate_feedback_add result=success candidate_id=%s feedback_id=%s",
            candidate.id,
            created.id,
        )
        return CandidateDetailFeedbackResponse(
            id=created.id,
            author_name=created.author_name,
            note_text=created.note_text,
            created_at=created.created_at,
        )

    def _get_candidate(self, candidate_id: str):
        try:
            return self.candidate_repository.get_candidate(self.session, candidate_id)
        except LookupError as exc:
            raise NotFoundError(f"Candidate {candidate_id} not found.") from exc
