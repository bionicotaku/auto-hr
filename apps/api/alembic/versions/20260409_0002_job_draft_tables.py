"""Add job and job_rubric_items tables.

Revision ID: 20260409_0002
Revises: 20260409_0001
Create Date: 2026-04-09 21:05:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260409_0002"
down_revision: Union[str, None] = "20260409_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "jobs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("lifecycle_status", sa.String(length=20), nullable=False),
        sa.Column("creation_mode", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("description_text", sa.Text(), nullable=False),
        sa.Column("structured_info_json", sa.JSON(), nullable=False),
        sa.Column("original_description_input", sa.Text(), nullable=True),
        sa.Column("original_form_input_json", sa.JSON(), nullable=True),
        sa.Column("editor_history_summary", sa.Text(), nullable=True),
        sa.Column("editor_recent_messages_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finalized_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "creation_mode IN ('from_description', 'from_form')",
            name="ck_jobs_creation_mode",
        ),
        sa.CheckConstraint(
            "lifecycle_status IN ('draft', 'active')",
            name="ck_jobs_lifecycle_status",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "job_rubric_items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("job_id", sa.String(length=36), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("criterion_type", sa.String(length=32), nullable=False),
        sa.Column("weight_input", sa.Float(), nullable=False),
        sa.Column("weight_normalized", sa.Float(), nullable=True),
        sa.Column("scoring_standard_json", sa.JSON(), nullable=False),
        sa.Column("agent_prompt_text", sa.Text(), nullable=False),
        sa.Column("evidence_guidance_text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "criterion_type IN ('weighted', 'hard_requirement')",
            name="ck_job_rubric_items_criterion_type",
        ),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_job_rubric_items_job_id",
        "job_rubric_items",
        ["job_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_job_rubric_items_job_id", table_name="job_rubric_items")
    op.drop_table("job_rubric_items")
    op.drop_table("jobs")
