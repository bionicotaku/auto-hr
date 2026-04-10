import json
import logging
from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import DomainValidationError, NotFoundError
from app.repositories.candidate_repository import (
    CandidateEmailDraftCreateData,
    CandidateRepository,
)
from app.schemas.candidates import CandidateDetailEmailDraftResponse
from app.workflows.candidate_analysis.email_draft import CandidateEmailDraftWorkflow

logger = logging.getLogger(__name__)


class EmailDraftService:
    def __init__(
        self,
        session: Session,
        candidate_repository: CandidateRepository,
        email_draft_workflow: CandidateEmailDraftWorkflow,
    ) -> None:
        self.session = session
        self.candidate_repository = candidate_repository
        self.email_draft_workflow = email_draft_workflow

    def create_email_draft(self, candidate_id: str, draft_type: str) -> CandidateDetailEmailDraftResponse:
        logger.info(
            "Candidate stage started: stage=candidate_email_draft_create result=start candidate_id=%s draft_type=%s",
            candidate_id,
            draft_type,
        )
        candidate = self._get_candidate(candidate_id)
        if candidate.job is None:
            logger.warning(
                "Candidate stage failed: stage=candidate_email_draft_create result=failure candidate_id=%s reason=missing_job_context",
                candidate_id,
            )
            raise NotFoundError(f"Candidate {candidate_id} is missing job context.")

        try:
            generated = self.email_draft_workflow.run(
                draft_type=draft_type,
                job_title=candidate.job.title,
                job_summary=candidate.job.summary,
                candidate_context=self._build_candidate_context(candidate),
            )
        except ValueError as exc:
            logger.warning(
                "Candidate stage failed: stage=candidate_email_draft_create result=failure candidate_id=%s reason=%s",
                candidate_id,
                exc,
            )
            raise DomainValidationError(str(exc)) from exc

        try:
            created = self.candidate_repository.add_candidate_email_draft(
                self.session,
                candidate,
                CandidateEmailDraftCreateData(
                    draft_type=draft_type,
                    subject=generated.subject.strip(),
                    body=generated.body.strip(),
                ),
            )
            self.session.commit()
        except Exception as exc:
            self.session.rollback()
            logger.exception(
                "Candidate stage failed: stage=candidate_email_draft_create result=failure candidate_id=%s reason=%s",
                candidate_id,
                exc,
            )
            raise

        logger.info(
            "Candidate stage finished: stage=candidate_email_draft_create result=success candidate_id=%s draft_id=%s",
            candidate.id,
            created.id,
        )
        return CandidateDetailEmailDraftResponse(
            id=created.id,
            draft_type=created.draft_type,
            subject=created.subject,
            body=created.body,
            created_at=created.created_at,
            updated_at=created.updated_at,
        )

    def _get_candidate(self, candidate_id: str):
        try:
            return self.candidate_repository.get_candidate(self.session, candidate_id)
        except LookupError as exc:
            raise NotFoundError(f"Candidate {candidate_id} not found.") from exc

    def _build_candidate_context(self, candidate) -> dict[str, Any]:
        profile = candidate.profile
        return {
            "current_status": candidate.current_status,
            "recommendation": candidate.recommendation,
            "hard_requirement_overall": candidate.hard_requirement_overall,
            "overall_score_percent": candidate.overall_score_percent,
            "full_name": candidate.full_name,
            "current_title": candidate.current_title,
            "current_company": candidate.current_company,
            "location_text": candidate.location_text,
            "professional_summary_normalized": candidate.professional_summary_normalized,
            "ai_summary": candidate.ai_summary,
            "evidence_points": self._load_json(candidate.evidence_points_json, list),
            "tags": [tag.tag_name for tag in candidate.tags],
            "work_experiences": self._load_json(profile.work_experiences_json if profile else "[]", list),
            "educations": self._load_json(profile.educations_json if profile else "[]", list),
            "skills": self._load_json(profile.skills_json if profile else "{}", dict),
            "employment_preferences": self._load_json(
                profile.employment_preferences_json if profile else "{}",
                dict,
            ),
            "application_answers": self._load_json(
                profile.application_answers_json if profile else "[]",
                list,
            ),
            "additional_information": self._load_json(
                profile.additional_information_json if profile else "{}",
                dict,
            ),
        }

    def _load_json(self, value: str, expected_type: type[list] | type[dict]) -> list[Any] | dict[str, Any]:
        try:
            loaded = json.loads(value)
        except (TypeError, json.JSONDecodeError):
            return expected_type()
        if isinstance(loaded, expected_type):
            return loaded
        return expected_type()
