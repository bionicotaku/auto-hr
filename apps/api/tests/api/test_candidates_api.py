from app.api import service_deps


class StubCandidateQueryService:
    def get_candidate_detail(self, candidate_id: str, *, build_document_url):
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
                        "filename": "Ada-Lovelace-1.pdf",
                        "file_url": build_document_url(candidate_id, "doc-001"),
                        "mime_type": "application/pdf",
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

    def get_candidate_document(self, *, candidate_id: str, document_id: str):
        return type(
            "StubDocument",
            (),
            {
                "storage_path": __file__,
                "mime_type": "application/pdf",
                "filename": "Ada-Lovelace-1.pdf",
            },
        )()


def override_candidate_query_service(_session, _settings):
    return StubCandidateQueryService()


class StubFeedbackService:
    def update_status(self, candidate_id: str, current_status: str):
        return {
            "candidate_id": candidate_id,
            "current_status": current_status,
        }

    def add_tag(self, candidate_id: str, tag_name: str):
        return {
            "id": "tag-manual-001",
            "name": tag_name,
            "source": "manual",
        }

    def add_feedback(self, candidate_id: str, *, note_text: str, author_name: str | None):
        return {
            "id": "feedback-002",
            "author_name": author_name,
            "note_text": note_text,
            "created_at": "2026-04-10T01:00:00Z",
        }


class StubEmailDraftService:
    def create_email_draft(self, candidate_id: str, draft_type: str):
        return {
            "id": "draft-002",
            "draft_type": draft_type,
            "subject": f"{draft_type} subject",
            "body": f"{draft_type} body",
            "created_at": "2026-04-10T01:00:00Z",
            "updated_at": "2026-04-10T01:00:00Z",
        }


def override_feedback_service(_session, _settings):
    return StubFeedbackService()


def override_email_draft_service(_session, _settings):
    return StubEmailDraftService()


def test_get_candidate_detail_returns_complete_payload(client, monkeypatch) -> None:
    monkeypatch.setattr(service_deps, "get_candidate_query_service", override_candidate_query_service)

    response = client.get("/api/candidates/candidate-001")

    assert response.status_code == 200
    body = response.json()
    assert body["candidate_id"] == "candidate-001"
    assert body["job"]["title"] == "AI Recruiter"
    assert body["raw_input"]["documents"][0]["filename"] == "Ada-Lovelace-1.pdf"
    assert body["raw_input"]["documents"][0]["file_url"].endswith("/api/candidates/candidate-001/documents/doc-001/file")
    assert body["normalized_profile"]["identity"]["full_name"] == "Ada Lovelace"
    assert body["rubric_results"][0]["rubric_name"] == "执行力"
    assert body["supervisor_summary"]["recommendation"] == "advance"
    assert body["action_context"]["feedbacks"][0]["note_text"] == "值得继续跟进"


def test_get_candidate_document_file_returns_pdf(client, monkeypatch) -> None:
    monkeypatch.setattr(service_deps, "get_candidate_query_service", override_candidate_query_service)

    response = client.get("/api/candidates/candidate-001/documents/doc-001/file")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/pdf")


def test_update_candidate_status(client, monkeypatch) -> None:
    monkeypatch.setattr(service_deps, "get_feedback_service", override_feedback_service)

    response = client.patch("/api/candidates/candidate-001/status", json={"current_status": "in_progress"})

    assert response.status_code == 200
    assert response.json() == {
        "candidate_id": "candidate-001",
        "current_status": "in_progress",
    }


def test_create_candidate_tag(client, monkeypatch) -> None:
    monkeypatch.setattr(service_deps, "get_feedback_service", override_feedback_service)

    response = client.post("/api/candidates/candidate-001/tags", json={"tag_name": "优先跟进"})

    assert response.status_code == 200
    assert response.json()["name"] == "优先跟进"
    assert response.json()["source"] == "manual"


def test_create_candidate_feedback(client, monkeypatch) -> None:
    monkeypatch.setattr(service_deps, "get_feedback_service", override_feedback_service)

    response = client.post(
        "/api/candidates/candidate-001/feedbacks",
        json={"note_text": "安排下一轮", "author_name": "Evan"},
    )

    assert response.status_code == 200
    assert response.json()["note_text"] == "安排下一轮"
    assert response.json()["author_name"] == "Evan"


def test_create_candidate_email_draft(client, monkeypatch) -> None:
    monkeypatch.setattr(service_deps, "get_email_draft_service", override_email_draft_service)

    response = client.post(
        "/api/candidates/candidate-001/email-drafts",
        json={"draft_type": "advance"},
    )

    assert response.status_code == 200
    assert response.json()["draft_type"] == "advance"
    assert response.json()["subject"] == "advance subject"
