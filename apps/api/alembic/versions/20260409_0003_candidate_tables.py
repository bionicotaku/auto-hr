"""Add candidate-related tables.

Revision ID: 20260409_0003
Revises: 20260409_0002
Create Date: 2026-04-09 22:45:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260409_0003"
down_revision: Union[str, None] = "20260409_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "candidates",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("job_id", sa.String(length=36), nullable=False),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column("current_title", sa.String(length=200), nullable=True),
        sa.Column("current_company", sa.String(length=200), nullable=True),
        sa.Column("location_text", sa.String(length=200), nullable=True),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("phone", sa.String(length=80), nullable=True),
        sa.Column("linkedin_url", sa.String(length=500), nullable=True),
        sa.Column("professional_summary_raw", sa.Text(), nullable=True),
        sa.Column("professional_summary_normalized", sa.Text(), nullable=True),
        sa.Column("years_of_total_experience", sa.Float(), nullable=True),
        sa.Column("years_of_relevant_experience", sa.Float(), nullable=True),
        sa.Column("seniority_level", sa.String(length=80), nullable=True),
        sa.Column("raw_text_input", sa.Text(), nullable=True),
        sa.Column("hard_requirement_overall", sa.String(length=32), nullable=False),
        sa.Column("overall_score_5", sa.Float(), nullable=True),
        sa.Column("overall_score_percent", sa.Float(), nullable=True),
        sa.Column("ai_summary", sa.Text(), nullable=False),
        sa.Column("evidence_points_json", sa.Text(), nullable=False),
        sa.Column("recommendation", sa.String(length=32), nullable=False),
        sa.Column("current_status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "current_status IN ('pending', 'in_progress', 'rejected', 'offer_sent', 'hired')",
            name="ck_candidates_current_status",
        ),
        sa.CheckConstraint(
            "hard_requirement_overall IN ('all_pass', 'has_borderline', 'has_fail')",
            name="ck_candidates_hard_requirement_overall",
        ),
        sa.CheckConstraint(
            "recommendation IN ('advance', 'manual_review', 'hold', 'reject')",
            name="ck_candidates_recommendation",
        ),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_candidates_job_id", "candidates", ["job_id"], unique=False)

    op.create_table(
        "candidate_profiles",
        sa.Column("candidate_id", sa.String(length=36), nullable=False),
        sa.Column("work_experiences_json", sa.Text(), nullable=False),
        sa.Column("educations_json", sa.Text(), nullable=False),
        sa.Column("skills_json", sa.Text(), nullable=False),
        sa.Column("employment_preferences_json", sa.Text(), nullable=False),
        sa.Column("application_answers_json", sa.Text(), nullable=False),
        sa.Column("additional_information_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("candidate_id"),
    )

    op.create_table(
        "candidate_documents",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("candidate_id", sa.String(length=36), nullable=False),
        sa.Column("document_type", sa.String(length=32), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("storage_path", sa.Text(), nullable=False),
        sa.Column("mime_type", sa.String(length=120), nullable=False),
        sa.Column("extracted_text", sa.Text(), nullable=False),
        sa.Column("page_count", sa.Integer(), nullable=True),
        sa.Column("upload_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "document_type IN ('resume', 'other')",
            name="ck_candidate_documents_document_type",
        ),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_candidate_documents_candidate_id", "candidate_documents", ["candidate_id"], unique=False)

    op.create_table(
        "candidate_rubric_results",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("candidate_id", sa.String(length=36), nullable=False),
        sa.Column("job_rubric_item_id", sa.String(length=36), nullable=False),
        sa.Column("criterion_type", sa.String(length=32), nullable=False),
        sa.Column("score_0_to_5", sa.Float(), nullable=True),
        sa.Column("hard_requirement_decision", sa.String(length=32), nullable=True),
        sa.Column("reason_text", sa.Text(), nullable=False),
        sa.Column("evidence_points_json", sa.Text(), nullable=False),
        sa.Column("uncertainty_note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "criterion_type IN ('weighted', 'hard_requirement')",
            name="ck_candidate_rubric_results_criterion_type",
        ),
        sa.CheckConstraint(
            "hard_requirement_decision IN ('pass', 'borderline', 'fail') OR hard_requirement_decision IS NULL",
            name="ck_candidate_rubric_results_hr_decision",
        ),
        sa.CheckConstraint(
            "("
            "criterion_type = 'weighted' AND score_0_to_5 IS NOT NULL AND hard_requirement_decision IS NULL"
            ") OR ("
            "criterion_type = 'hard_requirement' AND score_0_to_5 IS NULL AND hard_requirement_decision IS NOT NULL"
            ")",
            name="ck_candidate_rubric_results_value_mode",
        ),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_rubric_item_id"], ["job_rubric_items.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_candidate_rubric_results_candidate_id",
        "candidate_rubric_results",
        ["candidate_id"],
        unique=False,
    )
    op.create_index(
        "ix_candidate_rubric_results_job_rubric_item_id",
        "candidate_rubric_results",
        ["job_rubric_item_id"],
        unique=False,
    )

    op.create_table(
        "candidate_tags",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("candidate_id", sa.String(length=36), nullable=False),
        sa.Column("tag_name", sa.String(length=120), nullable=False),
        sa.Column("tag_source", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "tag_source IN ('ai', 'manual')",
            name="ck_candidate_tags_tag_source",
        ),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("candidate_id", "tag_name", name="uq_candidate_tags_candidate_id_tag_name"),
    )
    op.create_index("ix_candidate_tags_candidate_id", "candidate_tags", ["candidate_id"], unique=False)

    op.create_table(
        "candidate_feedbacks",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("candidate_id", sa.String(length=36), nullable=False),
        sa.Column("author_name", sa.String(length=120), nullable=True),
        sa.Column("note_text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_candidate_feedbacks_candidate_id", "candidate_feedbacks", ["candidate_id"], unique=False)

    op.create_table(
        "candidate_email_drafts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("candidate_id", sa.String(length=36), nullable=False),
        sa.Column("draft_type", sa.String(length=32), nullable=False),
        sa.Column("subject", sa.String(length=300), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "draft_type IN ('reject', 'advance', 'offer', 'other')",
            name="ck_candidate_email_drafts_draft_type",
        ),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_candidate_email_drafts_candidate_id",
        "candidate_email_drafts",
        ["candidate_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_candidate_email_drafts_candidate_id", table_name="candidate_email_drafts")
    op.drop_table("candidate_email_drafts")
    op.drop_index("ix_candidate_feedbacks_candidate_id", table_name="candidate_feedbacks")
    op.drop_table("candidate_feedbacks")
    op.drop_index("ix_candidate_tags_candidate_id", table_name="candidate_tags")
    op.drop_table("candidate_tags")
    op.drop_index(
        "ix_candidate_rubric_results_job_rubric_item_id",
        table_name="candidate_rubric_results",
    )
    op.drop_index("ix_candidate_rubric_results_candidate_id", table_name="candidate_rubric_results")
    op.drop_table("candidate_rubric_results")
    op.drop_index("ix_candidate_documents_candidate_id", table_name="candidate_documents")
    op.drop_table("candidate_documents")
    op.drop_table("candidate_profiles")
    op.drop_index("ix_candidates_job_id", table_name="candidates")
    op.drop_table("candidates")
