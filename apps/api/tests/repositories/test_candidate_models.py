import json

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.candidate import Candidate
from app.models.candidate_document import CandidateDocument
from app.models.candidate_email_draft import CandidateEmailDraft
from app.models.candidate_feedback import CandidateFeedback
from app.models.candidate_profile import CandidateProfile
from app.models.candidate_rubric_result import CandidateRubricResult
from app.models.candidate_tag import CandidateTag
from app.models.job import Job
from app.models.job_rubric_item import JobRubricItem


def create_active_job(db_session) -> Job:
    job = Job(
        lifecycle_status="active",
        creation_mode="from_description",
        title="AI Recruiter",
        summary="Own hiring.",
        description_text="JD body",
        structured_info_json={"location": "Remote"},
        original_description_input="Original JD",
        original_form_input_json=None,
        editor_history_summary=None,
        editor_recent_messages_json=[],
    )
    db_session.add(job)
    db_session.flush()

    rubric_item = JobRubricItem(
        job_id=job.id,
        sort_order=1,
        name="Execution",
        description="Owns funnel",
        criterion_type="weighted",
        weight_input=80,
        weight_normalized=0.8,
        scoring_standard_items=[{"key": "score_5", "value": "Excellent"}],
        agent_prompt_text="Judge execution",
        evidence_guidance_text="Look for examples",
    )
    db_session.add(rubric_item)
    db_session.flush()
    return job


def create_candidate(db_session) -> tuple[Candidate, JobRubricItem]:
    job = create_active_job(db_session)
    rubric_item = job.rubric_items[0]
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
        professional_summary_normalized="Built hiring systems",
        years_of_total_experience=8,
        years_of_relevant_experience=6,
        seniority_level="Lead",
        raw_text_input="Candidate raw text",
        hard_requirement_overall="all_pass",
        overall_score_percent=90,
        ai_summary="Strong candidate",
        evidence_points_json=json.dumps(["Built teams"]),
        recommendation="advance",
        current_status="pending",
    )
    db_session.add(candidate)
    db_session.flush()
    return candidate, rubric_item


def test_candidate_related_models_support_basic_crud(db_session) -> None:
    candidate, rubric_item = create_candidate(db_session)

    db_session.add(
        CandidateProfile(
            candidate_id=candidate.id,
            work_experiences_json="[]",
            educations_json="[]",
            skills_json="{}",
            employment_preferences_json="{}",
            application_answers_json="[]",
            additional_information_json="{}",
        )
    )
    db_session.add(
        CandidateDocument(
            candidate_id=candidate.id,
            document_type="resume",
            filename="Ada-Lovelace-1.pdf",
            storage_path="data/uploads/candidates/a/resume.pdf",
            mime_type="application/pdf",
            page_count=1,
            upload_order=1,
        )
    )
    db_session.add(
        CandidateRubricResult(
            candidate_id=candidate.id,
            job_rubric_item_id=rubric_item.id,
            criterion_type="weighted",
            score_0_to_5=4.0,
            hard_requirement_decision=None,
            reason_text="Strong execution",
            evidence_points_json='["Led hiring"]',
            uncertainty_note=None,
        )
    )
    db_session.add(
        CandidateTag(
            candidate_id=candidate.id,
            tag_name="执行力强",
            tag_source="ai",
        )
    )
    db_session.add(
        CandidateFeedback(
            candidate_id=candidate.id,
            author_name="HR",
            note_text="值得继续跟进",
        )
    )
    db_session.add(
        CandidateEmailDraft(
            candidate_id=candidate.id,
            draft_type="advance",
            subject="下一轮面试邀请",
            body="请参加下一轮面试。",
        )
    )
    db_session.commit()

    loaded = db_session.get(Candidate, candidate.id)
    assert loaded is not None
    assert loaded.profile is not None
    assert len(loaded.documents) == 1
    assert len(loaded.rubric_results) == 1
    assert len(loaded.tags) == 1
    assert len(loaded.feedbacks) == 1
    assert len(loaded.email_drafts) == 1


def test_candidate_tags_unique_constraint_is_enforced(db_session) -> None:
    candidate, _ = create_candidate(db_session)
    db_session.add(CandidateTag(candidate_id=candidate.id, tag_name="执行力强", tag_source="ai"))
    db_session.commit()

    db_session.add(CandidateTag(candidate_id=candidate.id, tag_name="执行力强", tag_source="manual"))
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_candidate_rubric_results_mode_constraint_is_enforced(db_session) -> None:
    candidate, rubric_item = create_candidate(db_session)
    db_session.add(
        CandidateRubricResult(
            candidate_id=candidate.id,
            job_rubric_item_id=rubric_item.id,
            criterion_type="weighted",
            score_0_to_5=None,
            hard_requirement_decision="pass",
            reason_text="invalid",
            evidence_points_json="[]",
            uncertainty_note=None,
        )
    )

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_candidate_status_constraint_is_enforced(db_session) -> None:
    job = create_active_job(db_session)
    db_session.add(
        Candidate(
            job_id=job.id,
            full_name="Grace Hopper",
            current_title=None,
            current_company=None,
            location_text=None,
            email=None,
            phone=None,
            linkedin_url=None,
            professional_summary_raw=None,
            professional_summary_normalized=None,
            years_of_total_experience=None,
            years_of_relevant_experience=None,
            seniority_level=None,
            raw_text_input=None,
            hard_requirement_overall="all_pass",
            overall_score_percent=None,
            ai_summary="summary",
            evidence_points_json="[]",
            recommendation="advance",
            current_status="invalid_status",
        )
    )

    with pytest.raises(IntegrityError):
        db_session.commit()
