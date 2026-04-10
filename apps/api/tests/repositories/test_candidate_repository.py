from app.models.job import Job
from app.models.job_rubric_item import JobRubricItem
from app.repositories.candidate_repository import (
    CandidateCreateData,
    CandidateDocumentCreateData,
    CandidateProfileCreateData,
    CandidateRepository,
    CandidateRubricResultCreateData,
    CandidateTagCreateData,
)


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

    db_session.add_all(
        [
            JobRubricItem(
                job_id=job.id,
                sort_order=1,
                name="Execution",
                description="Owns funnel",
                criterion_type="weighted",
                weight_input=60,
                weight_normalized=0.6,
                scoring_standard_json={"score_5": "Excellent"},
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
                scoring_standard_json={"pass_definition": "Can work in English"},
                agent_prompt_text="Judge English collaboration",
                evidence_guidance_text="Look for global evidence",
            ),
        ]
    )
    db_session.flush()
    return job


def test_candidate_repository_creates_full_candidate_graph(db_session) -> None:
    job = create_active_job(db_session)
    repository = CandidateRepository()

    candidate = repository.create_candidate_graph(
        db_session,
        candidate_data=CandidateCreateData(
            candidate_id="candidate-001",
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
            overall_score_5=4.2,
            overall_score_percent=84.0,
            ai_summary="Strong candidate",
            evidence_points_json=["Built systems"],
            recommendation="advance",
        ),
        profile_data=CandidateProfileCreateData(
            work_experiences_json=[{"company_name": "Auto HR"}],
            educations_json=[{"school_name": "Example University"}],
            skills_json={"skills_raw": ["Recruiting"], "skills_normalized": ["recruiting"]},
            employment_preferences_json={"preferred_locations": ["Remote"]},
            application_answers_json=[{"question_text": "Why?", "answer_text": "Because."}],
            additional_information_json={"parser_notes": ["none"]},
        ),
        document_data=[
            CandidateDocumentCreateData(
                document_type="resume",
                filename="resume.pdf",
                storage_path="/tmp/resume.pdf",
                mime_type="application/pdf",
                extracted_text="resume text",
                page_count=1,
                upload_order=1,
            )
        ],
        rubric_result_data=[
            CandidateRubricResultCreateData(
                job_rubric_item_id=job.rubric_items[0].id,
                criterion_type="weighted",
                score_0_to_5=4.0,
                hard_requirement_decision=None,
                reason_text="Strong execution",
                evidence_points_json=["Led hiring"],
                uncertainty_note=None,
            ),
            CandidateRubricResultCreateData(
                job_rubric_item_id=job.rubric_items[1].id,
                criterion_type="hard_requirement",
                score_0_to_5=None,
                hard_requirement_decision="pass",
                reason_text="Can collaborate globally",
                evidence_points_json=["Worked across regions"],
                uncertainty_note=None,
            ),
        ],
        tag_data=[
            CandidateTagCreateData(tag_name="operator", tag_source="ai"),
            CandidateTagCreateData(tag_name="structured", tag_source="ai"),
        ],
    )
    db_session.commit()

    assert candidate.full_name == "Ada Lovelace"
    assert candidate.profile is not None
    assert len(candidate.documents) == 1
    assert len(candidate.rubric_results) == 2
    assert [item.tag_name for item in candidate.tags] == ["operator", "structured"]
