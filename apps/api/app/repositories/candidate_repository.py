import json
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.candidate import Candidate
from app.models.candidate_document import CandidateDocument
from app.models.candidate_profile import CandidateProfile
from app.models.candidate_rubric_result import CandidateRubricResult
from app.models.candidate_tag import CandidateTag


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
                selectinload(Candidate.profile),
                selectinload(Candidate.documents),
                selectinload(Candidate.rubric_results),
                selectinload(Candidate.tags),
            )
            .where(Candidate.id == candidate_id)
        )
        candidate = session.scalar(statement)
        if candidate is None:
            raise LookupError(candidate_id)
        return candidate
