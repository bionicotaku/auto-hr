"""Add analysis run and event tables.

Revision ID: 20260410_0005
Revises: 20260410_0004
Create Date: 2026-04-10 04:30:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260410_0005"
down_revision: Union[str, None] = "20260410_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "analysis_runs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("run_type", sa.String(length=32), nullable=False),
        sa.Column("resource_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("current_stage", sa.String(length=64), nullable=False),
        sa.Column("current_ai_step", sa.Integer(), nullable=False),
        sa.Column("total_ai_steps", sa.Integer(), nullable=False),
        sa.Column("last_event_index", sa.Integer(), nullable=False),
        sa.Column("result_resource_type", sa.String(length=32), nullable=True),
        sa.Column("result_resource_id", sa.String(length=36), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "run_type IN ('job_finalize', 'candidate_import')",
            name="ck_analysis_runs_run_type",
        ),
        sa.CheckConstraint(
            "status IN ('queued', 'running', 'completed', 'failed')",
            name="ck_analysis_runs_status",
        ),
        sa.CheckConstraint(
            "result_resource_type IN ('job', 'candidate') OR result_resource_type IS NULL",
            name="ck_analysis_runs_result_resource_type",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_analysis_runs_resource_id"), "analysis_runs", ["resource_id"], unique=False)
    op.create_index(op.f("ix_analysis_runs_run_type"), "analysis_runs", ["run_type"], unique=False)
    op.create_index(op.f("ix_analysis_runs_status"), "analysis_runs", ["status"], unique=False)

    op.create_table(
        "analysis_run_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("run_id", sa.String(length=36), nullable=False),
        sa.Column("event_index", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=24), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["analysis_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_analysis_run_events_run_id"), "analysis_run_events", ["run_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_analysis_run_events_run_id"), table_name="analysis_run_events")
    op.drop_table("analysis_run_events")

    op.drop_index(op.f("ix_analysis_runs_status"), table_name="analysis_runs")
    op.drop_index(op.f("ix_analysis_runs_run_type"), table_name="analysis_runs")
    op.drop_index(op.f("ix_analysis_runs_resource_id"), table_name="analysis_runs")
    op.drop_table("analysis_runs")
