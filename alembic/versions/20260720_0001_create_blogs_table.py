"""create blogs table

Revision ID: 20260720_0001
Revises:
Create Date: 2026-07-20 00:01:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260720_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "blogs",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
    )
    op.create_index("ix_blogs_id", "blogs", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_blogs_id", table_name="blogs")
    op.drop_table("blogs")
