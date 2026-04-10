import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, CheckConstraint, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.job import Job


class JobRubricItem(Base):
    __tablename__ = "job_rubric_items"
    __table_args__ = (
        CheckConstraint(
            "criterion_type IN ('weighted', 'hard_requirement')",
            name="ck_job_rubric_items_criterion_type",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    criterion_type: Mapped[str] = mapped_column(String(32), nullable=False)
    weight_input: Mapped[float] = mapped_column(Float, nullable=False)
    weight_normalized: Mapped[float | None] = mapped_column(Float, nullable=True)
    scoring_standard_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    agent_prompt_text: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_guidance_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    job: Mapped["Job"] = relationship(back_populates="rubric_items")
