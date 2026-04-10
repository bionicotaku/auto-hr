from app.repositories.job_repository import (
    JobCreateData,
    JobRepository,
    JobRubricItemCreateData,
)


def make_job_create_data() -> JobCreateData:
    return JobCreateData(
        lifecycle_status="draft",
        creation_mode="from_description",
        title="Senior AI Recruiter",
        summary="Lead recruiting workflows for AI teams.",
        description_text="Detailed JD",
        structured_info_json={"department": "Talent"},
        original_description_input="original description",
        original_form_input_json=None,
        editor_history_summary=None,
        editor_recent_messages_json=[],
    )


def make_rubric_items() -> list[JobRubricItemCreateData]:
    return [
        JobRubricItemCreateData(
            sort_order=1,
            name="AI Recruiting",
            description="Hands-on recruiting experience",
            criterion_type="weighted",
            weight_input=50,
            weight_normalized=0.5,
            scoring_standard_json={"score_5": "Excellent"},
            agent_prompt_text="Judge recruiting depth",
            evidence_guidance_text="Look for end-to-end pipeline ownership",
        ),
        JobRubricItemCreateData(
            sort_order=2,
            name="English",
            description="Can collaborate globally",
            criterion_type="hard_requirement",
            weight_input=100,
            weight_normalized=None,
            scoring_standard_json={"pass_definition": "Can work in English"},
            agent_prompt_text="Judge English collaboration fit",
            evidence_guidance_text="Look for cross-border evidence",
        ),
    ]


def test_create_and_delete_draft_job(db_session) -> None:
    repository = JobRepository()
    job = repository.create_job_with_rubric_items(
        db_session,
        job_data=make_job_create_data(),
        rubric_items=make_rubric_items(),
    )
    db_session.commit()

    loaded = repository.get_job_for_edit(db_session, job.id)
    assert loaded.lifecycle_status == "draft"
    assert len(loaded.rubric_items) == 2

    deleted = repository.delete_draft_job(db_session, job.id)
    db_session.commit()
    assert deleted is True
    assert repository.list_jobs(db_session) == []


def test_replace_rubric_items_rewrites_previous_items(db_session) -> None:
    repository = JobRepository()
    job = repository.create_job_with_rubric_items(
        db_session,
        job_data=make_job_create_data(),
        rubric_items=make_rubric_items(),
    )
    db_session.commit()

    repository.replace_rubric_items(
        db_session,
        job.id,
        [
            JobRubricItemCreateData(
                sort_order=1,
                name="System Thinking",
                description="Can define hiring systems",
                criterion_type="weighted",
                weight_input=80,
                weight_normalized=0.8,
                scoring_standard_json={"score_5": "Defines scalable systems"},
                agent_prompt_text="Judge systems thinking",
                evidence_guidance_text="Look for process ownership",
            )
        ],
    )
    db_session.commit()

    loaded = repository.get_job_for_edit(db_session, job.id)
    assert [item.name for item in loaded.rubric_items] == ["System Thinking"]
