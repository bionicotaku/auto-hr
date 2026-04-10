import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, CheckConstraint, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.candidate import Candidate
    from app.models.job_rubric_item import JobRubricItem


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (
        CheckConstraint(
            "lifecycle_status IN ('draft', 'active')",
            name="ck_jobs_lifecycle_status",
        ),
        CheckConstraint(
            "creation_mode IN ('from_description', 'from_form')",
            name="ck_jobs_creation_mode",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lifecycle_status: Mapped[str] = mapped_column(String(20), nullable=False)
    creation_mode: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    description_text: Mapped[str] = mapped_column(Text, nullable=False)
    structured_info_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    original_description_input: Mapped[str | None] = mapped_column(Text, nullable=True)
    original_form_input_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    editor_history_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    editor_recent_messages_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    finalized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    rubric_items: Mapped[list["JobRubricItem"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="JobRubricItem.sort_order",
    )
    candidates: Mapped[list["Candidate"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
