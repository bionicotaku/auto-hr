import json
from datetime import UTC, datetime, timedelta

from app.models.candidate import Candidate
from app.models.candidate_tag import CandidateTag
from app.models.job import Job
from app.models.job_rubric_item import JobRubricItem
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.job_repository import JobRepository
from app.services.job_query_service import JobQueryService


def create_job(
    db_session,
    *,
    title: str,
    lifecycle_status: str,
    updated_at: datetime,
) -> Job:
    job = Job(
        lifecycle_status=lifecycle_status,
        creation_mode="from_description",
        title=title,
        summary=f"{title} summary",
        description_text=f"{title} description",
        structured_info_json={
            "department": "Talent",
            "location": "Remote",
            "employment_type": "Full-time",
            "seniority_level": "Lead",
        },
        original_description_input="Original JD",
        original_form_input_json=None,
        editor_history_summary=None,
        editor_recent_messages_json=[],
        updated_at=updated_at,
    )
    db_session.add(job)
    db_session.flush()
    db_session.add_all(
        [
            JobRubricItem(
                job_id=job.id,
                sort_order=1,
                name="Execution",
                description="Runs hiring funnel",
                criterion_type="weighted",
                weight_input=70,
                weight_normalized=0.7,
                scoring_standard_items=[{"key": "score_5", "value": "Excellent"}],
                agent_prompt_text="Judge execution",
                evidence_guidance_text="Look for examples",
            ),
            JobRubricItem(
                job_id=job.id,
                sort_order=2,
                name="English",
                description="Can collaborate globally",
                criterion_type="hard_requirement",
                weight_input=100,
                weight_normalized=None,
                scoring_standard_items=[{"key": "pass_definition", "value": "Can work in English"}],
                agent_prompt_text="Judge English collaboration",
                evidence_guidance_text="Look for global evidence",
            ),
        ]
    )
    db_session.flush()
    return job


def create_candidate(
    db_session,
    *,
    job: Job,
    full_name: str,
    score: float,
    status: str,
    ai_summary: str,
    created_at: datetime,
    tags: list[str],
) -> Candidate:
    candidate = Candidate(
        job_id=job.id,
        full_name=full_name,
        current_title="Recruiter",
        current_company="Auto HR",
        location_text="Remote",
        email=f"{full_name}@example.com",
        phone="123456",
        linkedin_url=None,
        professional_summary_raw="Summary",
        professional_summary_normalized="Summary",
        years_of_total_experience=8,
        years_of_relevant_experience=6,
        seniority_level="Lead",
        raw_text_input="Raw text",
        hard_requirement_overall="all_pass",
        overall_score_percent=score,
        ai_summary=ai_summary,
        evidence_points_json=json.dumps(["Evidence"]),
        recommendation="advance",
        current_status=status,
        created_at=created_at,
        updated_at=created_at,
    )
    db_session.add(candidate)
    db_session.flush()

    for tag in tags:
        db_session.add(CandidateTag(candidate_id=candidate.id, tag_name=tag, tag_source="ai"))
    db_session.flush()
    return candidate


def test_job_query_service_lists_jobs_with_candidate_counts(db_session) -> None:
    now = datetime.now(UTC)
    active_job = create_job(db_session, title="AI Recruiter", lifecycle_status="active", updated_at=now)
    draft_job = create_job(
        db_session,
        title="Hiring Ops Lead",
        lifecycle_status="draft",
        updated_at=now - timedelta(hours=1),
    )
    create_candidate(
        db_session,
        job=active_job,
        full_name="Ada",
        score=92,
        status="pending",
        ai_summary="Strong operator",
        created_at=now,
        tags=["高匹配"],
    )
    db_session.commit()

    service = JobQueryService(db_session, JobRepository(), CandidateRepository())
    response = service.list_jobs()

    assert [item.title for item in response.items] == ["AI Recruiter"]
    assert response.items[0].candidate_count == 1


def test_job_query_service_returns_job_detail_summary(db_session) -> None:
    job = create_job(
        db_session,
        title="AI Recruiter",
        lifecycle_status="active",
        updated_at=datetime.now(UTC),
    )
    create_candidate(
        db_session,
        job=job,
        full_name="Ada",
        score=92,
        status="pending",
        ai_summary="Strong operator",
        created_at=datetime.now(UTC),
        tags=["高匹配"],
    )
    db_session.commit()

    service = JobQueryService(db_session, JobRepository(), CandidateRepository())
    response = service.get_job_detail(job.id)

    assert response.job_id == job.id
    assert response.candidate_count == 1
    assert response.rubric_summary[0].weight_label == "70%"
    assert any(item.label == "地点" and item.value == "Remote" for item in response.structured_info_summary)


def test_job_query_service_lists_candidates_with_default_sort_and_filters(db_session) -> None:
    now = datetime.now(UTC)
    job = create_job(db_session, title="AI Recruiter", lifecycle_status="active", updated_at=now)
    create_candidate(
        db_session,
        job=job,
        full_name="Ada",
        score=95,
        status="pending",
        ai_summary="Strong operator",
        created_at=now - timedelta(days=1),
        tags=["高匹配", "管理经验"],
    )
    create_candidate(
        db_session,
        job=job,
        full_name="Grace",
        score=75,
        status="in_progress",
        ai_summary="Needs review for local availability",
        created_at=now,
        tags=["需要复核", "本地候选人"],
    )
    create_candidate(
        db_session,
        job=job,
        full_name="Linus",
        score=80,
        status="rejected",
        ai_summary="Manufacturing experience",
        created_at=now - timedelta(hours=2),
        tags=["制造业经验"],
    )
    db_session.commit()

    service = JobQueryService(db_session, JobRepository(), CandidateRepository())

    default_response = service.list_job_candidates(
        job_id=job.id,
        sort="score_desc",
        status="all",
        tags=[],
        query=None,
    )
    assert [item.full_name for item in default_response.items] == ["Ada", "Linus", "Grace"]
    assert "制造业经验" in default_response.available_tags

    status_response = service.list_job_candidates(
        job_id=job.id,
        sort="score_desc",
        status="in_progress",
        tags=[],
        query=None,
    )
    assert [item.full_name for item in status_response.items] == ["Grace"]

    tag_response = service.list_job_candidates(
        job_id=job.id,
        sort="score_desc",
        status="all",
        tags=["高匹配", "制造业经验"],
        query=None,
    )
    assert [item.full_name for item in tag_response.items] == ["Ada", "Linus"]

    search_response = service.list_job_candidates(
        job_id=job.id,
        sort="score_desc",
        status="all",
        tags=[],
        query="local availability",
    )
    assert [item.full_name for item in search_response.items] == ["Grace"]
