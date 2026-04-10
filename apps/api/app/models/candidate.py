import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.candidate_document import CandidateDocument
    from app.models.candidate_email_draft import CandidateEmailDraft
    from app.models.candidate_feedback import CandidateFeedback
    from app.models.candidate_profile import CandidateProfile
    from app.models.candidate_rubric_result import CandidateRubricResult
    from app.models.candidate_tag import CandidateTag
    from app.models.job import Job


class Candidate(Base):
    __tablename__ = "candidates"
    __table_args__ = (
        CheckConstraint(
            "hard_requirement_overall IN ('all_pass', 'has_borderline', 'has_fail')",
            name="ck_candidates_hard_requirement_overall",
        ),
        CheckConstraint(
            "recommendation IN ('advance', 'manual_review', 'hold', 'reject')",
            name="ck_candidates_recommendation",
        ),
        CheckConstraint(
            "current_status IN ('pending', 'in_progress', 'rejected', 'offer_sent', 'hired')",
            name="ck_candidates_current_status",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    current_title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    current_company: Mapped[str | None] = mapped_column(String(200), nullable=True)
    location_text: Mapped[str | None] = mapped_column(String(200), nullable=True)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(80), nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    professional_summary_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    professional_summary_normalized: Mapped[str | None] = mapped_column(Text, nullable=True)
    years_of_total_experience: Mapped[float | None] = mapped_column(Float, nullable=True)
    years_of_relevant_experience: Mapped[float | None] = mapped_column(Float, nullable=True)
    seniority_level: Mapped[str | None] = mapped_column(String(80), nullable=True)
    raw_text_input: Mapped[str | None] = mapped_column(Text, nullable=True)
    hard_requirement_overall: Mapped[str] = mapped_column(String(32), nullable=False)
    overall_score_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_summary: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_points_json: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation: Mapped[str] = mapped_column(String(32), nullable=False)
    current_status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    job: Mapped["Job"] = relationship(back_populates="candidates")
    profile: Mapped["CandidateProfile | None"] = relationship(
        back_populates="candidate",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )
    documents: Mapped[list["CandidateDocument"]] = relationship(
        back_populates="candidate",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="CandidateDocument.upload_order",
    )
    rubric_results: Mapped[list["CandidateRubricResult"]] = relationship(
        back_populates="candidate",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    tags: Mapped[list["CandidateTag"]] = relationship(
        back_populates="candidate",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    feedbacks: Mapped[list["CandidateFeedback"]] = relationship(
        back_populates="candidate",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    email_drafts: Mapped[list["CandidateEmailDraft"]] = relationship(
        back_populates="candidate",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
