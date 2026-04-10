import uuid
from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class CandidateTag(Base):
    __tablename__ = "candidate_tags"
    __table_args__ = (
        CheckConstraint(
            "tag_source IN ('ai', 'manual')",
            name="ck_candidate_tags_tag_source",
        ),
        UniqueConstraint("candidate_id", "tag_name", name="uq_candidate_tags_candidate_id_tag_name"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tag_name: Mapped[str] = mapped_column(String(120), nullable=False)
    tag_source: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    candidate = relationship("Candidate", back_populates="tags")
