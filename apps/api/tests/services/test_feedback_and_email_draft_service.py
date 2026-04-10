import json
from datetime import UTC, datetime

import pytest

from app.core.exceptions import DomainValidationError, NotFoundError
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
from app.services.email_draft_service import EmailDraftService
from app.services.feedback_service import FeedbackService


class StubEmailDraftWorkflow:
    def run(self, *, draft_type: str, job_title: str, job_summary: str, candidate_context: dict):
        assert draft_type in {"reject", "advance", "offer", "other"}
        assert job_title == "AI Recruiter"
        assert job_summary == "Own the hiring funnel."
        assert candidate_context["full_name"] == "Ada Lovelace"
        return type(
            "StubDraft",
            (),
            {
                "subject": f"{draft_type} subject",
                "body": f"{draft_type} body",
            },
        )()


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
    db_session.add(weighted_item)
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
            work_experiences_json=json.dumps([], ensure_ascii=False),
            educations_json=json.dumps([], ensure_ascii=False),
            skills_json=json.dumps({}, ensure_ascii=False),
            employment_preferences_json=json.dumps({}, ensure_ascii=False),
            application_answers_json=json.dumps([], ensure_ascii=False),
            additional_information_json=json.dumps({}, ensure_ascii=False),
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
    db_session.add(
        CandidateRubricResult(
            candidate_id=candidate.id,
            job_rubric_item_id=weighted_item.id,
            criterion_type="weighted",
            score_0_to_5=4.0,
            hard_requirement_decision=None,
            reason_text="Strong execution",
            evidence_points_json=json.dumps(["Built hiring workflow"], ensure_ascii=False),
            uncertainty_note=None,
        )
    )
    db_session.add(CandidateTag(candidate_id=candidate.id, tag_name="管理经验", tag_source="manual"))
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


def test_feedback_service_updates_status_adds_tag_and_feedback(db_session) -> None:
    candidate = create_candidate_detail_graph(db_session)
    service = FeedbackService(db_session, CandidateRepository())

    status_response = service.update_status(candidate.id, "in_progress")
    tag_response = service.add_tag(candidate.id, "优先跟进")
    feedback_response = service.add_feedback(
        candidate.id,
        note_text="安排二轮面试",
        author_name="Evan",
    )

    refreshed = CandidateRepository().get_candidate(db_session, candidate.id)
    assert status_response.current_status == "in_progress"
    assert refreshed.current_status == "in_progress"
    assert tag_response.name == "优先跟进"
    assert any(tag.tag_name == "优先跟进" and tag.tag_source == "manual" for tag in refreshed.tags)
    assert feedback_response.note_text == "安排二轮面试"
    assert refreshed.feedbacks[-1].note_text == "安排二轮面试"


def test_feedback_service_logs_status_update(db_session, caplog) -> None:
    candidate = create_candidate_detail_graph(db_session)
    service = FeedbackService(db_session, CandidateRepository())

    with caplog.at_level("INFO"):
        response = service.update_status(candidate.id, "in_progress")

    assert response.current_status == "in_progress"
    assert f"stage=candidate_status_update result=success candidate_id={candidate.id} current_status=in_progress" in caplog.text


def test_feedback_service_rejects_duplicate_tag(db_session) -> None:
    candidate = create_candidate_detail_graph(db_session)
    service = FeedbackService(db_session, CandidateRepository())

    with pytest.raises(DomainValidationError):
        service.add_tag(candidate.id, "管理经验")


def test_feedback_service_raises_not_found(db_session) -> None:
    service = FeedbackService(db_session, CandidateRepository())

    with pytest.raises(NotFoundError):
        service.update_status("candidate-missing", "pending")


def test_email_draft_service_creates_email_draft(db_session) -> None:
    candidate = create_candidate_detail_graph(db_session)
    service = EmailDraftService(
        db_session,
        CandidateRepository(),
        StubEmailDraftWorkflow(),
    )

    response = service.create_email_draft(candidate.id, "offer")
    refreshed = CandidateRepository().get_candidate(db_session, candidate.id)

    assert response.draft_type == "offer"
    assert response.subject == "offer subject"
    assert refreshed.email_drafts[-1].draft_type == "offer"
    assert refreshed.email_drafts[-1].subject == "offer subject"
