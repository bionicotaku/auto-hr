"""Repository layer."""

from app.repositories.candidate_repository import CandidateRepository
from app.repositories.job_repository import JobRepository

__all__ = ["CandidateRepository", "JobRepository"]
