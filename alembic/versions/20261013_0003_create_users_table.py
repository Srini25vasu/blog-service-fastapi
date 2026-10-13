"""create users table

Revision ID: 20261013_0003
Revises: 20260725_0002
Create Date: 2026-10-13 00:03:00

"""
import os
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20261013_0003"
down_revision: Union[str, Sequence[str], None] = "20260725_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


DB_SCHEMA = os.getenv("DB_SCHEMA", "blogs-python")


def upgrade() -> None:
    if DB_SCHEMA:
        op.execute(sa.schema.CreateSchema(DB_SCHEMA, if_not_exists=True))

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        schema=DB_SCHEMA,
    )
    op.create_index("ix_users_id", "users", ["id"], unique=False, schema=DB_SCHEMA)
    op.create_index("ix_users_username", "users", ["username"], unique=True, schema=DB_SCHEMA)
    op.create_index("ix_users_email", "users", ["email"], unique=True, schema=DB_SCHEMA)


def downgrade() -> None:
    op.drop_index("ix_users_email", table_name="users", schema=DB_SCHEMA)
    op.drop_index("ix_users_username", table_name="users", schema=DB_SCHEMA)
    op.drop_index("ix_users_id", table_name="users", schema=DB_SCHEMA)
    op.drop_table("users", schema=DB_SCHEMA)
