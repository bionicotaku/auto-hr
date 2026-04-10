"""Replace job rubric scoring JSON objects with scoring item arrays.

Revision ID: 20260410_0004
Revises: 20260409_0003
Create Date: 2026-04-10 01:30:00
"""

from typing import Any, Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260410_0004"
down_revision: Union[str, None] = "20260409_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _to_items(value: Any) -> list[dict[str, str]]:
    if isinstance(value, list):
        return [
            {"key": str(item.get("key", "")), "value": str(item.get("value", ""))}
            for item in value
            if isinstance(item, dict)
        ]
    if isinstance(value, dict):
        return [{"key": str(key), "value": str(item_value)} for key, item_value in value.items()]
    return []


def _to_object(value: Any) -> dict[str, str]:
    if isinstance(value, dict):
        return {str(key): str(item_value) for key, item_value in value.items()}
    if isinstance(value, list):
        converted: dict[str, str] = {}
        for item in value:
            if not isinstance(item, dict):
                continue
            key = item.get("key")
            item_value = item.get("value")
            if key is None or item_value is None:
                continue
            converted[str(key)] = str(item_value)
        return converted
    return {}


def upgrade() -> None:
    connection = op.get_bind()

    with op.batch_alter_table("job_rubric_items") as batch_op:
        batch_op.add_column(sa.Column("scoring_standard_items_json", sa.JSON(), nullable=True))

    rubric_table = sa.table(
        "job_rubric_items",
        sa.column("id", sa.String(length=36)),
        sa.column("scoring_standard_json", sa.JSON()),
        sa.column("scoring_standard_items_json", sa.JSON()),
    )

    rows = connection.execute(
        sa.select(rubric_table.c.id, rubric_table.c.scoring_standard_json)
    ).mappings()
    for row in rows:
        connection.execute(
            rubric_table.update()
            .where(rubric_table.c.id == row["id"])
            .values(scoring_standard_items_json=_to_items(row["scoring_standard_json"]))
        )

    with op.batch_alter_table("job_rubric_items") as batch_op:
        batch_op.drop_column("scoring_standard_json")
        batch_op.alter_column(
            "scoring_standard_items_json",
            existing_type=sa.JSON(),
            nullable=False,
        )


def downgrade() -> None:
    connection = op.get_bind()

    with op.batch_alter_table("job_rubric_items") as batch_op:
        batch_op.add_column(sa.Column("scoring_standard_json", sa.JSON(), nullable=True))

    rubric_table = sa.table(
        "job_rubric_items",
        sa.column("id", sa.String(length=36)),
        sa.column("scoring_standard_json", sa.JSON()),
        sa.column("scoring_standard_items_json", sa.JSON()),
    )

    rows = connection.execute(
        sa.select(rubric_table.c.id, rubric_table.c.scoring_standard_items_json)
    ).mappings()
    for row in rows:
        connection.execute(
            rubric_table.update()
            .where(rubric_table.c.id == row["id"])
            .values(scoring_standard_json=_to_object(row["scoring_standard_items_json"]))
        )

    with op.batch_alter_table("job_rubric_items") as batch_op:
        batch_op.drop_column("scoring_standard_items_json")
        batch_op.alter_column(
            "scoring_standard_json",
            existing_type=sa.JSON(),
            nullable=False,
        )
