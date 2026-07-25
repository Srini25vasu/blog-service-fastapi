"""move blogs table to configured schema

Revision ID: 20260725_0002
Revises: 20260720_0001
Create Date: 2026-07-25 00:02:00

"""
import os
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260725_0002"
down_revision: Union[str, Sequence[str], None] = "20260720_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


DB_SCHEMA = os.getenv("DB_SCHEMA", "blogs-python")


def _quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def _ensure_index(schema: str | None) -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    indexes = {index["name"] for index in inspector.get_indexes("blogs", schema=schema)}
    if "ix_blogs_id" not in indexes:
        op.create_index("ix_blogs_id", "blogs", ["id"], unique=False, schema=schema)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if DB_SCHEMA:
        op.execute(sa.schema.CreateSchema(DB_SCHEMA, if_not_exists=True))

    target_exists = inspector.has_table("blogs", schema=DB_SCHEMA)
    public_exists = inspector.has_table("blogs", schema="public")

    if not target_exists and public_exists and DB_SCHEMA:
        op.execute(
            sa.text(
                f"ALTER TABLE public.blogs SET SCHEMA {_quote_identifier(DB_SCHEMA)}"
            )
        )
    elif not target_exists:
        op.create_table(
            "blogs",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("content", sa.String(), nullable=False),
            schema=DB_SCHEMA,
        )

    _ensure_index(DB_SCHEMA)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("blogs", schema=DB_SCHEMA):
        return

    indexes = {index["name"] for index in inspector.get_indexes("blogs", schema=DB_SCHEMA)}
    if "ix_blogs_id" in indexes:
        op.drop_index("ix_blogs_id", table_name="blogs", schema=DB_SCHEMA)

    if DB_SCHEMA:
        public_exists = inspector.has_table("blogs", schema="public")
        if not public_exists:
            op.execute(
                sa.text(
                    f"ALTER TABLE {_quote_identifier(DB_SCHEMA)}.blogs SET SCHEMA public"
                )
            )
            op.create_index("ix_blogs_id", "blogs", ["id"], unique=False, schema="public")
            return

    op.drop_table("blogs", schema=DB_SCHEMA)