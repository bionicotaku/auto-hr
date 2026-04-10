import json
from dataclasses import dataclass

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.candidate import Candidate
from app.models.candidate_document import CandidateDocument
from app.models.candidate_email_draft import CandidateEmailDraft
from app.models.candidate_feedback import CandidateFeedback
from app.models.candidate_profile import CandidateProfile
from app.models.candidate_rubric_result import CandidateRubricResult
from app.models.candidate_tag import CandidateTag
from app.models.job import Job


@dataclass(frozen=True)
class CandidateCreateData:
    candidate_id: str
    job_id: str
    full_name: str
    current_title: str | None
    current_company: str | None
    location_text: str | None
    email: str | None
    phone: str | None
    linkedin_url: str | None
    professional_summary_raw: str | None
    professional_summary_normalized: str | None
    years_of_total_experience: float | None
    years_of_relevant_experience: float | None
    seniority_level: str | None
    raw_text_input: str | None
    hard_requirement_overall: str
    overall_score_5: float | None
    overall_score_percent: float | None
    ai_summary: str
    evidence_points_json: list[str]
    recommendation: str
    current_status: str = "pending"


@dataclass(frozen=True)
class CandidateProfileCreateData:
    work_experiences_json: list[dict]
    educations_json: list[dict]
    skills_json: dict
    employment_preferences_json: dict
    application_answers_json: list[dict]
    additional_information_json: dict


@dataclass(frozen=True)
class CandidateDocumentCreateData:
    document_type: str
    filename: str
    storage_path: str
    mime_type: str
    extracted_text: str
    page_count: int | None
    upload_order: int


@dataclass(frozen=True)
class CandidateRubricResultCreateData:
    job_rubric_item_id: str
    criterion_type: str
    score_0_to_5: float | None
    hard_requirement_decision: str | None
    reason_text: str
    evidence_points_json: list[str]
    uncertainty_note: str | None


@dataclass(frozen=True)
class CandidateTagCreateData:
    tag_name: str
    tag_source: str


@dataclass(frozen=True)
class CandidateFeedbackCreateData:
    note_text: str
    author_name: str | None


@dataclass(frozen=True)
class CandidateEmailDraftCreateData:
    draft_type: str
    subject: str
    body: str


class CandidateRepository:
    def create_candidate_graph(
        self,
        session: Session,
        *,
        candidate_data: CandidateCreateData,
        profile_data: CandidateProfileCreateData,
        document_data: list[CandidateDocumentCreateData],
        rubric_result_data: list[CandidateRubricResultCreateData],
        tag_data: list[CandidateTagCreateData],
    ) -> Candidate:
        candidate = Candidate(
            id=candidate_data.candidate_id,
            job_id=candidate_data.job_id,
            full_name=candidate_data.full_name,
            current_title=candidate_data.current_title,
            current_company=candidate_data.current_company,
            location_text=candidate_data.location_text,
            email=candidate_data.email,
            phone=candidate_data.phone,
            linkedin_url=candidate_data.linkedin_url,
            professional_summary_raw=candidate_data.professional_summary_raw,
            professional_summary_normalized=candidate_data.professional_summary_normalized,
            years_of_total_experience=candidate_data.years_of_total_experience,
            years_of_relevant_experience=candidate_data.years_of_relevant_experience,
            seniority_level=candidate_data.seniority_level,
            raw_text_input=candidate_data.raw_text_input,
            hard_requirement_overall=candidate_data.hard_requirement_overall,
            overall_score_5=candidate_data.overall_score_5,
            overall_score_percent=candidate_data.overall_score_percent,
            ai_summary=candidate_data.ai_summary,
            evidence_points_json=json.dumps(candidate_data.evidence_points_json, ensure_ascii=False),
            recommendation=candidate_data.recommendation,
            current_status=candidate_data.current_status,
        )
        session.add(candidate)
        session.flush()

        session.add(
            CandidateProfile(
                candidate_id=candidate.id,
                work_experiences_json=json.dumps(profile_data.work_experiences_json, ensure_ascii=False),
                educations_json=json.dumps(profile_data.educations_json, ensure_ascii=False),
                skills_json=json.dumps(profile_data.skills_json, ensure_ascii=False),
                employment_preferences_json=json.dumps(
                    profile_data.employment_preferences_json, ensure_ascii=False
                ),
                application_answers_json=json.dumps(
                    profile_data.application_answers_json, ensure_ascii=False
                ),
                additional_information_json=json.dumps(
                    profile_data.additional_information_json, ensure_ascii=False
                ),
            )
        )

        for item in document_data:
            session.add(
                CandidateDocument(
                    candidate_id=candidate.id,
                    document_type=item.document_type,
                    filename=item.filename,
                    storage_path=item.storage_path,
                    mime_type=item.mime_type,
                    extracted_text=item.extracted_text,
                    page_count=item.page_count,
                    upload_order=item.upload_order,
                )
            )

        for item in rubric_result_data:
            session.add(
                CandidateRubricResult(
                    candidate_id=candidate.id,
                    job_rubric_item_id=item.job_rubric_item_id,
                    criterion_type=item.criterion_type,
                    score_0_to_5=item.score_0_to_5,
                    hard_requirement_decision=item.hard_requirement_decision,
                    reason_text=item.reason_text,
                    evidence_points_json=json.dumps(item.evidence_points_json, ensure_ascii=False),
                    uncertainty_note=item.uncertainty_note,
                )
            )

        for item in tag_data:
            session.add(
                CandidateTag(
                    candidate_id=candidate.id,
                    tag_name=item.tag_name,
                    tag_source=item.tag_source,
                )
            )

        session.flush()
        return self.get_candidate(session, candidate.id)

    def get_candidate(self, session: Session, candidate_id: str) -> Candidate:
        statement = (
            select(Candidate)
            .options(
                selectinload(Candidate.job).selectinload(Job.rubric_items),
                selectinload(Candidate.profile),
                selectinload(Candidate.documents),
                selectinload(Candidate.rubric_results),
                selectinload(Candidate.tags),
                selectinload(Candidate.feedbacks),
                selectinload(Candidate.email_drafts),
            )
            .where(Candidate.id == candidate_id)
        )
        candidate = session.scalar(statement)
        if candidate is None:
            raise LookupError(candidate_id)
        return candidate

    def update_candidate_status(self, session: Session, candidate: Candidate, current_status: str) -> Candidate:
        candidate.current_status = current_status
        session.flush()
        return candidate

    def add_candidate_tag(
        self,
        session: Session,
        candidate: Candidate,
        tag_data: CandidateTagCreateData,
    ) -> CandidateTag:
        tag = CandidateTag(
            candidate_id=candidate.id,
            tag_name=tag_data.tag_name,
            tag_source=tag_data.tag_source,
        )
        session.add(tag)
        session.flush()
        return tag

    def add_candidate_feedback(
        self,
        session: Session,
        candidate: Candidate,
        feedback_data: CandidateFeedbackCreateData,
    ) -> CandidateFeedback:
        feedback = CandidateFeedback(
            candidate_id=candidate.id,
            note_text=feedback_data.note_text,
            author_name=feedback_data.author_name,
        )
        session.add(feedback)
        session.flush()
        return feedback

    def add_candidate_email_draft(
        self,
        session: Session,
        candidate: Candidate,
        draft_data: CandidateEmailDraftCreateData,
    ) -> CandidateEmailDraft:
        draft = CandidateEmailDraft(
            candidate_id=candidate.id,
            draft_type=draft_data.draft_type,
            subject=draft_data.subject,
            body=draft_data.body,
        )
        session.add(draft)
        session.flush()
        return draft

    def count_candidates_by_job_ids(self, session: Session, job_ids: list[str]) -> dict[str, int]:
        if not job_ids:
            return {}

        statement = (
            select(Candidate.job_id, func.count(Candidate.id))
            .where(Candidate.job_id.in_(job_ids))
            .group_by(Candidate.job_id)
        )
        return {job_id: count for job_id, count in session.execute(statement).all()}

    def list_candidates_for_job(
        self,
        session: Session,
        *,
        job_id: str,
        sort: str,
        status: str,
        tags: list[str],
        query: str | None,
    ) -> list[Candidate]:
        statement = select(Candidate).options(selectinload(Candidate.tags)).where(Candidate.job_id == job_id)

        if status != "all":
            statement = statement.where(Candidate.current_status == status)

        normalized_query = query.strip() if query else None
        if normalized_query:
            like = f"%{normalized_query}%"
            statement = statement.where(
                or_(Candidate.full_name.ilike(like), Candidate.ai_summary.ilike(like))
            )

        if tags:
            statement = (
                statement.join(CandidateTag)
                .where(CandidateTag.tag_name.in_(tags))
                .distinct()
            )

        if sort == "score_asc":
            statement = statement.order_by(
                Candidate.overall_score_percent.is_(None),
                Candidate.overall_score_percent.asc(),
                Candidate.created_at.desc(),
            )
        elif sort == "created_at_asc":
            statement = statement.order_by(Candidate.created_at.asc())
        elif sort == "created_at_desc":
            statement = statement.order_by(Candidate.created_at.desc())
        else:
            statement = statement.order_by(
                Candidate.overall_score_percent.is_(None),
                Candidate.overall_score_percent.desc(),
                Candidate.created_at.desc(),
            )

        return list(session.scalars(statement).all())

    def list_available_tags_for_job(self, session: Session, job_id: str) -> list[str]:
        statement = (
            select(CandidateTag.tag_name)
            .join(Candidate, Candidate.id == CandidateTag.candidate_id)
            .where(Candidate.job_id == job_id)
            .distinct()
            .order_by(CandidateTag.tag_name.asc())
        )
        return list(session.scalars(statement).all())
