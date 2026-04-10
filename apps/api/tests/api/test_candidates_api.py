from app.api import service_deps


class StubCandidateQueryService:
    def get_candidate_detail(self, candidate_id: str):
        return {
            "candidate_id": candidate_id,
            "job": {
                "job_id": "job-001",
                "title": "AI Recruiter",
            },
            "raw_input": {
                "raw_text_input": "Candidate raw input",
                "documents": [
                    {
                        "id": "doc-001",
                        "document_type": "resume",
                        "filename": "resume.pdf",
                        "storage_path": "data/uploads/candidates/candidate-001/resume.pdf",
                        "mime_type": "application/pdf",
                        "extracted_text": "Resume extracted text",
                        "page_count": 2,
                        "upload_order": 1,
                    }
                ],
            },
            "normalized_profile": {
                "identity": {
                    "full_name": "Ada Lovelace",
                    "current_title": "Recruiting Lead",
                    "current_company": "Auto HR",
                    "location_text": "Remote",
                    "email": "ada@example.com",
                    "phone": "123456",
                    "linkedin_url": "https://linkedin.example/ada",
                },
                "profile_summary": {
                    "professional_summary_raw": "Built hiring systems",
                    "professional_summary_normalized": "Built hiring systems for global teams",
                    "years_of_total_experience": 8,
                    "years_of_relevant_experience": 6,
                    "seniority_level": "Lead",
                },
                "work_experiences": [
                    {
                        "company_name": "Auto HR",
                        "title": "Recruiting Lead",
                    }
                ],
                "educations": [],
                "skills": {
                    "skills_raw": ["Recruiting", "Ops"],
                    "skills_normalized": ["Recruiting Ops"],
                },
                "employment_preferences": {
                    "preferred_locations": ["New York"],
                },
                "application_answers": [],
                "additional_information": {
                    "uncategorized_highlights": ["Built dashboards"],
                    "parser_notes": [],
                },
            },
            "rubric_results": [
                {
                    "job_rubric_item_id": "rubric-001",
                    "rubric_name": "执行力",
                    "rubric_description": "推进招聘流程",
                    "criterion_type": "weighted",
                    "weight_label": "70%",
                    "score_0_to_5": 4.0,
                    "hard_requirement_decision": None,
                    "reason_text": "Strong execution",
                    "evidence_points": ["Built hiring workflow"],
                    "uncertainty_note": None,
                }
            ],
            "supervisor_summary": {
                "hard_requirement_overall": "all_pass",
                "overall_score_5": 4.5,
                "overall_score_percent": 90,
                "ai_summary": "Strong recruiting operator",
                "evidence_points": ["Built structured interview loops"],
                "recommendation": "advance",
                "tags": [
                    {
                        "id": "tag-001",
                        "name": "高匹配",
                        "source": "ai",
                    }
                ],
            },
            "action_context": {
                "current_status": "pending",
                "feedbacks": [
                    {
                        "id": "feedback-001",
                        "author_name": "Evan",
                        "note_text": "值得继续跟进",
                        "created_at": "2026-04-10T00:00:00Z",
                    }
                ],
                "email_drafts": [
                    {
                        "id": "draft-001",
                        "draft_type": "advance",
                        "subject": "下一轮沟通安排",
                        "body": "我们希望与你继续沟通。",
                        "created_at": "2026-04-10T00:00:00Z",
                        "updated_at": "2026-04-10T00:00:00Z",
                    }
                ],
            },
        }


def override_candidate_query_service(_session, _settings):
    return StubCandidateQueryService()


def test_get_candidate_detail_returns_complete_payload(client, monkeypatch) -> None:
    monkeypatch.setattr(service_deps, "get_candidate_query_service", override_candidate_query_service)

    response = client.get("/api/candidates/candidate-001")

    assert response.status_code == 200
    body = response.json()
    assert body["candidate_id"] == "candidate-001"
    assert body["job"]["title"] == "AI Recruiter"
    assert body["raw_input"]["documents"][0]["filename"] == "resume.pdf"
    assert body["normalized_profile"]["identity"]["full_name"] == "Ada Lovelace"
    assert body["rubric_results"][0]["rubric_name"] == "执行力"
    assert body["supervisor_summary"]["recommendation"] == "advance"
    assert body["action_context"]["feedbacks"][0]["note_text"] == "值得继续跟进"
