import json
from datetime import UTC, datetime

import pytest

from app.core.exceptions import NotFoundError
from app.models.candidate import Candidate
from app.models.candidate_document import CandidateDocument
from app.models.candidate_email_draft import CandidateEmailDraft
from app.models.candidate_feedback import CandidateFeedback
from app.models.candidate_profile import CandidateProfile
from app.models.candidate_rubric_result import CandidateRubricResult
from app.models.candidate_tag import CandidateTag
from app.models.job import Job
from app.models.job_rubric_item import JobRubricItem
from app.repositories.candidate_repository import CandidateRepository
from app.services.candidate_query_service import CandidateQueryService


def create_candidate_detail_graph(db_session) -> Candidate:
    job = Job(
        lifecycle_status="active",
        creation_mode="from_description",
        title="AI Recruiter",
        summary="Own the hiring funnel.",
        description_text="Job description",
        structured_info_json={"location": "Remote"},
        original_description_input="Original JD",
        original_form_input_json=None,
        editor_history_summary=None,
        editor_recent_messages_json=[],
    )
    db_session.add(job)
    db_session.flush()

    weighted_item = JobRubricItem(
        job_id=job.id,
        sort_order=1,
        name="执行力",
        description="能推进招聘流程",
        criterion_type="weighted",
        weight_input=70,
        weight_normalized=0.7,
        scoring_standard_items=[{"key": "5", "value": "Excellent"}],
        agent_prompt_text="Judge execution",
        evidence_guidance_text="Look for execution proof",
    )
    hard_requirement_item = JobRubricItem(
        job_id=job.id,
        sort_order=2,
        name="英文协作",
        description="可跨团队协作",
        criterion_type="hard_requirement",
        weight_input=100,
        weight_normalized=None,
        scoring_standard_items=[{"key": "pass", "value": "Can work in English"}],
        agent_prompt_text="Judge English",
        evidence_guidance_text="Look for global work examples",
    )
    db_session.add_all([weighted_item, hard_requirement_item])
    db_session.flush()

    candidate = Candidate(
        job_id=job.id,
        full_name="Ada Lovelace",
        current_title="Recruiting Lead",
        current_company="Auto HR",
        location_text="Remote",
        email="ada@example.com",
        phone="123456",
        linkedin_url="https://linkedin.example/ada",
        professional_summary_raw="Built hiring systems",
        professional_summary_normalized="Built hiring systems for global teams",
        years_of_total_experience=8,
        years_of_relevant_experience=6,
        seniority_level="Lead",
        raw_text_input="Candidate raw input",
        hard_requirement_overall="all_pass",
        overall_score_percent=90,
        ai_summary="Strong recruiting operator",
        evidence_points_json=json.dumps(["Built structured interview loops"], ensure_ascii=False),
        recommendation="advance",
        current_status="pending",
    )
    db_session.add(candidate)
    db_session.flush()

    db_session.add(
        CandidateProfile(
            candidate_id=candidate.id,
            work_experiences_json=json.dumps(
                [
                    {
                        "company_name": "Auto HR",
                        "title": "Recruiting Lead",
                        "start_date": "2021-01",
                        "end_date": None,
                        "is_current": True,
                        "description_normalized": "Led recruiting operations",
                        "key_achievements": ["Built interview loops"],
                    }
                ],
                ensure_ascii=False,
            ),
            educations_json=json.dumps(
                [
                    {
                        "school_name": "Oxford",
                        "degree": "BSc",
                        "degree_level": "bachelor",
                        "major": "Mathematics",
                        "end_date": "2018-06",
                    }
                ],
                ensure_ascii=False,
            ),
            skills_json=json.dumps(
                {
                    "skills_raw": ["Recruiting", "Ops"],
                    "skills_normalized": ["Recruiting Ops", "Stakeholder Management"],
                },
                ensure_ascii=False,
            ),
            employment_preferences_json=json.dumps(
                {
                    "work_authorization": "Authorized",
                    "requires_sponsorship": False,
                    "willing_to_relocate": True,
                    "preferred_locations": ["New York"],
                    "preferred_work_modes": ["Hybrid"],
                },
                ensure_ascii=False,
            ),
            application_answers_json=json.dumps(
                [{"question_text": "Notice period", "answer_text": "Two weeks"}],
                ensure_ascii=False,
            ),
            additional_information_json=json.dumps(
                {
                    "uncategorized_highlights": ["Built dashboards"],
                    "parser_notes": ["Resume had two formats"],
                },
                ensure_ascii=False,
            ),
        )
    )
    db_session.add(
        CandidateDocument(
            candidate_id=candidate.id,
            document_type="resume",
            filename="Ada-Lovelace-1.pdf",
            storage_path="data/uploads/candidates/ada/resume.pdf",
            mime_type="application/pdf",
            page_count=2,
            upload_order=1,
        )
    )
    db_session.add_all(
        [
            CandidateRubricResult(
                candidate_id=candidate.id,
                job_rubric_item_id=weighted_item.id,
                criterion_type="weighted",
                score_0_to_5=4.0,
                hard_requirement_decision=None,
                reason_text="Strong execution",
                evidence_points_json=json.dumps(["Built hiring workflow"], ensure_ascii=False),
                uncertainty_note="Need one more data point",
            ),
            CandidateRubricResult(
                candidate_id=candidate.id,
                job_rubric_item_id=hard_requirement_item.id,
                criterion_type="hard_requirement",
                score_0_to_5=None,
                hard_requirement_decision="pass",
                reason_text="Collaborated globally",
                evidence_points_json=json.dumps(["Worked with global teams"], ensure_ascii=False),
                uncertainty_note=None,
            ),
        ]
    )
    db_session.add_all(
        [
            CandidateTag(candidate_id=candidate.id, tag_name="高匹配", tag_source="ai"),
            CandidateTag(candidate_id=candidate.id, tag_name="管理经验", tag_source="manual"),
        ]
    )
    db_session.add(
        CandidateFeedback(
            candidate_id=candidate.id,
            author_name="Evan",
            note_text="值得继续跟进",
            created_at=datetime.now(UTC),
        )
    )
    db_session.add(
        CandidateEmailDraft(
            candidate_id=candidate.id,
            draft_type="advance",
            subject="下一轮沟通安排",
            body="我们希望与你继续沟通。",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
    )
    db_session.commit()
    return candidate


def test_candidate_query_service_returns_complete_detail(db_session) -> None:
    candidate = create_candidate_detail_graph(db_session)
    service = CandidateQueryService(db_session, CandidateRepository())

    response = service.get_candidate_detail(
        candidate.id,
        build_document_url=lambda owner_candidate_id, document_id: f"http://testserver/api/candidates/{owner_candidate_id}/documents/{document_id}/file",
    )

    assert response.candidate_id == candidate.id
    assert response.job.title == "AI Recruiter"
    assert response.raw_input.raw_text_input == "Candidate raw input"
    assert response.raw_input.documents[0].filename == "Ada-Lovelace-1.pdf"
    assert response.raw_input.documents[0].file_url.endswith("/documents/" + response.raw_input.documents[0].id + "/file")
    assert response.normalized_profile.identity.full_name == "Ada Lovelace"
    assert response.normalized_profile.work_experiences[0]["company_name"] == "Auto HR"
    assert response.rubric_results[0].rubric_name == "执行力"
    assert response.rubric_results[0].weight_label == "70%"
    assert response.supervisor_summary.ai_summary == "Strong recruiting operator"
    assert [tag.name for tag in response.supervisor_summary.tags] == ["高匹配", "管理经验"]
    assert response.action_context.current_status == "pending"
    assert response.action_context.feedbacks[0].note_text == "值得继续跟进"
    assert response.action_context.email_drafts[0].subject == "下一轮沟通安排"


def test_candidate_query_service_raises_not_found_for_missing_candidate(db_session) -> None:
    service = CandidateQueryService(db_session, CandidateRepository())

    with pytest.raises(NotFoundError):
        service.get_candidate_detail("candidate-missing", build_document_url=lambda *_args: "")
