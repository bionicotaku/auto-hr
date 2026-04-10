import uuid
from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class CandidateRubricResult(Base):
    __tablename__ = "candidate_rubric_results"
    __table_args__ = (
        CheckConstraint(
            "criterion_type IN ('weighted', 'hard_requirement')",
            name="ck_candidate_rubric_results_criterion_type",
        ),
        CheckConstraint(
            "hard_requirement_decision IN ('pass', 'borderline', 'fail') OR hard_requirement_decision IS NULL",
            name="ck_candidate_rubric_results_hr_decision",
        ),
        CheckConstraint(
            "("
            "criterion_type = 'weighted' AND score_0_to_5 IS NOT NULL AND hard_requirement_decision IS NULL"
            ") OR ("
            "criterion_type = 'hard_requirement' AND score_0_to_5 IS NULL AND hard_requirement_decision IS NOT NULL"
            ")",
            name="ck_candidate_rubric_results_value_mode",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_rubric_item_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("job_rubric_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    criterion_type: Mapped[str] = mapped_column(String(32), nullable=False)
    score_0_to_5: Mapped[float | None] = mapped_column(Float, nullable=True)
    hard_requirement_decision: Mapped[str | None] = mapped_column(String(32), nullable=True)
    reason_text: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_points_json: Mapped[str] = mapped_column(Text, nullable=False)
    uncertainty_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    candidate = relationship("Candidate", back_populates="rubric_results")
