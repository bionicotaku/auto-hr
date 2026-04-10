from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    candidate_id: Mapped[str] = mapped_column(
        ForeignKey("candidates.id", ondelete="CASCADE"),
        primary_key=True,
    )
    work_experiences_json: Mapped[str] = mapped_column(Text, nullable=False)
    educations_json: Mapped[str] = mapped_column(Text, nullable=False)
    skills_json: Mapped[str] = mapped_column(Text, nullable=False)
    employment_preferences_json: Mapped[str] = mapped_column(Text, nullable=False)
    application_answers_json: Mapped[str] = mapped_column(Text, nullable=False)
    additional_information_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    candidate = relationship("Candidate", back_populates="profile")
