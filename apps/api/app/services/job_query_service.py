from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.job_repository import JobRepository
from app.schemas.jobs import (
    JobCandidateListItemResponse,
    JobCandidateListResponse,
    JobDetailResponse,
    JobListItemResponse,
    JobListResponse,
)

STRUCTURED_INFO_LABELS = {
    "department": "部门",
    "location": "地点",
    "employment_type": "用工类型",
    "seniority_level": "级别",
}


class JobQueryService:
    def __init__(
        self,
        session: Session,
        job_repository: JobRepository,
        candidate_repository: CandidateRepository,
    ) -> None:
        self.session = session
        self.job_repository = job_repository
        self.candidate_repository = candidate_repository

    def list_jobs(self) -> JobListResponse:
        jobs = self.job_repository.list_jobs(self.session)
        counts = self.candidate_repository.count_candidates_by_job_ids(
            self.session,
            [job.id for job in jobs],
        )
        return JobListResponse(
            items=[
                JobListItemResponse(
                    job_id=job.id,
                    title=job.title,
                    summary=job.summary,
                    lifecycle_status=job.lifecycle_status,
                    candidate_count=counts.get(job.id, 0),
                    updated_at=job.updated_at,
                )
                for job in jobs
            ]
        )

    def get_job_detail(self, job_id: str) -> JobDetailResponse:
        try:
            job = self.job_repository.get_job_for_edit(self.session, job_id)
        except LookupError as exc:
            raise NotFoundError(f"Job {job_id} not found.") from exc

        candidate_count = self.candidate_repository.count_candidates_by_job_ids(
            self.session,
            [job.id],
        ).get(job.id, 0)

        rubric_summary = [
            {
                "name": item.name,
                "criterion_type": item.criterion_type,
                "weight_label": "硬门槛" if item.criterion_type == "hard_requirement" else f"{int(item.weight_input)}%",
            }
            for item in job.rubric_items
        ]
        structured_info_summary = []
        for key, label in STRUCTURED_INFO_LABELS.items():
            value = job.structured_info_json.get(key)
            if isinstance(value, str) and value.strip():
                structured_info_summary.append({"label": label, "value": value})

        return JobDetailResponse(
            job_id=job.id,
            title=job.title,
            summary=job.summary,
            description_text=job.description_text,
            lifecycle_status=job.lifecycle_status,
            candidate_count=candidate_count,
            rubric_summary=rubric_summary,
            structured_info_summary=structured_info_summary,
        )

    def list_job_candidates(
        self,
        *,
        job_id: str,
        sort: str,
        status: str,
        tags: list[str],
        query: str | None,
    ) -> JobCandidateListResponse:
        try:
            self.job_repository.get_job(self.session, job_id)
        except LookupError as exc:
            raise NotFoundError(f"Job {job_id} not found.") from exc

        candidates = self.candidate_repository.list_candidates_for_job(
            self.session,
            job_id=job_id,
            sort=sort,
            status=status,
            tags=tags,
            query=query,
        )
        available_tags = self.candidate_repository.list_available_tags_for_job(self.session, job_id)

        return JobCandidateListResponse(
            items=[
                JobCandidateListItemResponse(
                    candidate_id=candidate.id,
                    full_name=candidate.full_name,
                    ai_summary=candidate.ai_summary,
                    overall_score_percent=candidate.overall_score_percent,
                    current_status=candidate.current_status,
                    tags=[tag.tag_name for tag in candidate.tags],
                    created_at=candidate.created_at,
                )
                for candidate in candidates
            ],
            available_tags=available_tags,
        )
