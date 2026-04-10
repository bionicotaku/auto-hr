import json
from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.repositories.candidate_repository import CandidateRepository
from app.schemas.candidates import (
    CandidateDetailActionContextResponse,
    CandidateDetailEmailDraftResponse,
    CandidateDetailFeedbackResponse,
    CandidateDetailIdentityResponse,
    CandidateDetailJobContextResponse,
    CandidateDetailNormalizedProfileResponse,
    CandidateDetailProfileSummaryResponse,
    CandidateDetailRawDocumentResponse,
    CandidateDetailRawInputResponse,
    CandidateDetailResponse,
    CandidateDetailRubricResultResponse,
    CandidateDetailSupervisorResponse,
    CandidateDetailTagResponse,
)


class CandidateQueryService:
    def __init__(self, session: Session, candidate_repository: CandidateRepository) -> None:
        self.session = session
        self.candidate_repository = candidate_repository

    def get_candidate_detail(self, candidate_id: str) -> CandidateDetailResponse:
        try:
            candidate = self.candidate_repository.get_candidate(self.session, candidate_id)
        except LookupError as exc:
            raise NotFoundError(f"Candidate {candidate_id} not found.") from exc

        if candidate.job is None:
            raise NotFoundError(f"Candidate {candidate_id} is missing job context.")

        profile = candidate.profile
        rubric_items_by_id = {item.id: item for item in candidate.job.rubric_items}
        tags = sorted(candidate.tags, key=lambda item: (item.tag_source, item.tag_name))
        feedbacks = sorted(candidate.feedbacks, key=lambda item: item.created_at, reverse=True)
        email_drafts = sorted(candidate.email_drafts, key=lambda item: item.updated_at, reverse=True)

        return CandidateDetailResponse(
            candidate_id=candidate.id,
            job=CandidateDetailJobContextResponse(
                job_id=candidate.job.id,
                title=candidate.job.title,
            ),
            raw_input=CandidateDetailRawInputResponse(
                raw_text_input=candidate.raw_text_input,
                documents=[
                    CandidateDetailRawDocumentResponse(
                        id=document.id,
                        document_type=document.document_type,
                        filename=document.filename,
                        storage_path=document.storage_path,
                        mime_type=document.mime_type,
                        extracted_text=document.extracted_text,
                        page_count=document.page_count,
                        upload_order=document.upload_order,
                    )
                    for document in candidate.documents
                ],
            ),
            normalized_profile=CandidateDetailNormalizedProfileResponse(
                identity=CandidateDetailIdentityResponse(
                    full_name=candidate.full_name,
                    current_title=candidate.current_title,
                    current_company=candidate.current_company,
                    location_text=candidate.location_text,
                    email=candidate.email,
                    phone=candidate.phone,
                    linkedin_url=candidate.linkedin_url,
                ),
                profile_summary=CandidateDetailProfileSummaryResponse(
                    professional_summary_raw=candidate.professional_summary_raw,
                    professional_summary_normalized=candidate.professional_summary_normalized,
                    years_of_total_experience=candidate.years_of_total_experience,
                    years_of_relevant_experience=candidate.years_of_relevant_experience,
                    seniority_level=candidate.seniority_level,
                ),
                work_experiences=self._load_json(profile.work_experiences_json if profile else "[]", list),
                educations=self._load_json(profile.educations_json if profile else "[]", list),
                skills=self._load_json(profile.skills_json if profile else "{}", dict),
                employment_preferences=self._load_json(
                    profile.employment_preferences_json if profile else "{}",
                    dict,
                ),
                application_answers=self._load_json(
                    profile.application_answers_json if profile else "[]",
                    list,
                ),
                additional_information=self._load_json(
                    profile.additional_information_json if profile else "{}",
                    dict,
                ),
            ),
            rubric_results=[
                CandidateDetailRubricResultResponse(
                    job_rubric_item_id=result.job_rubric_item_id,
                    rubric_name=rubric_items_by_id.get(result.job_rubric_item_id).name
                    if result.job_rubric_item_id in rubric_items_by_id
                    else "未命名评估项",
                    rubric_description=rubric_items_by_id.get(result.job_rubric_item_id).description
                    if result.job_rubric_item_id in rubric_items_by_id
                    else "",
                    criterion_type=result.criterion_type,
                    weight_label=self._build_weight_label(rubric_items_by_id.get(result.job_rubric_item_id)),
                    score_0_to_5=result.score_0_to_5,
                    hard_requirement_decision=result.hard_requirement_decision,
                    reason_text=result.reason_text,
                    evidence_points=self._load_json(result.evidence_points_json, list),
                    uncertainty_note=result.uncertainty_note,
                )
                for result in sorted(
                    candidate.rubric_results,
                    key=lambda item: rubric_items_by_id.get(item.job_rubric_item_id).sort_order
                    if item.job_rubric_item_id in rubric_items_by_id
                    else 999,
                )
            ],
            supervisor_summary=CandidateDetailSupervisorResponse(
                hard_requirement_overall=candidate.hard_requirement_overall,
                overall_score_5=candidate.overall_score_5,
                overall_score_percent=candidate.overall_score_percent,
                ai_summary=candidate.ai_summary,
                evidence_points=self._load_json(candidate.evidence_points_json, list),
                recommendation=candidate.recommendation,
                tags=[
                    CandidateDetailTagResponse(
                        id=tag.id,
                        name=tag.tag_name,
                        source=tag.tag_source,
                    )
                    for tag in tags
                ],
            ),
            action_context=CandidateDetailActionContextResponse(
                current_status=candidate.current_status,
                feedbacks=[
                    CandidateDetailFeedbackResponse(
                        id=feedback.id,
                        author_name=feedback.author_name,
                        note_text=feedback.note_text,
                        created_at=feedback.created_at,
                    )
                    for feedback in feedbacks
                ],
                email_drafts=[
                    CandidateDetailEmailDraftResponse(
                        id=draft.id,
                        draft_type=draft.draft_type,
                        subject=draft.subject,
                        body=draft.body,
                        created_at=draft.created_at,
                        updated_at=draft.updated_at,
                    )
                    for draft in email_drafts
                ],
            ),
        )

    def _load_json(self, value: str, expected_type: type[list] | type[dict]) -> list[Any] | dict[str, Any]:
        try:
            loaded = json.loads(value)
        except (TypeError, json.JSONDecodeError):
            return expected_type()
        if isinstance(loaded, expected_type):
            return loaded
        return expected_type()

    def _build_weight_label(self, rubric_item) -> str:
        if rubric_item is None:
            return "未匹配"
        if rubric_item.criterion_type == "hard_requirement":
            return "硬门槛"
        if rubric_item.weight_input.is_integer():
            return f"{int(rubric_item.weight_input)}%"
        return f"{rubric_item.weight_input:.0f}%"
