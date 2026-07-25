"""create blogs table

Revision ID: 20260720_0001
Revises:
Create Date: 2026-07-20 00:01:00

"""
import os
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260720_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


DB_SCHEMA = os.getenv("DB_SCHEMA", "blogs-python")


def upgrade() -> None:
    if DB_SCHEMA:
        op.execute(sa.schema.CreateSchema(DB_SCHEMA, if_not_exists=True))

    op.create_table(
        "blogs",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        schema=DB_SCHEMA,
    )
    op.create_index("ix_blogs_id", "blogs", ["id"], unique=False, schema=DB_SCHEMA)


def downgrade() -> None:
    op.drop_index("ix_blogs_id", table_name="blogs", schema=DB_SCHEMA)
    op.drop_table("blogs", schema=DB_SCHEMA)
