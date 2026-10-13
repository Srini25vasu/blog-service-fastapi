"""Unit tests for the ``UserModel`` ORM mapping.

The metadata tests only inspect the mapped ``Table``; the SQLite test creates
the table in an in-memory database. SQLite has no schemas, so the configured
schema is translated to ``None`` via ``schema_translate_map``.
"""

import pytest
from sqlalchemy import Boolean, Integer, String, create_engine, inspect
from sqlalchemy.orm import Session

from app.database.models import UserModel


@pytest.fixture
def table():
    return UserModel.__table__


@pytest.fixture
def engine(table):
    engine = create_engine("sqlite://").execution_options(
        schema_translate_map={table.schema: None}
    )
    table.create(engine)
    yield engine
    engine.dispose()


def test_table_name(table):
    assert table.name == "users"


def test_columns_and_types(table):
    assert set(table.columns.keys()) == {
        "id",
        "username",
        "email",
        "hashed_password",
        "is_active",
    }
    assert isinstance(table.c.id.type, Integer)
    assert isinstance(table.c.username.type, String)
    assert table.c.username.type.length == 50
    assert table.c.email.type.length == 255
    assert table.c.hashed_password.type.length == 255
    assert isinstance(table.c.is_active.type, Boolean)


def test_primary_key(table):
    assert [column.name for column in table.primary_key.columns] == ["id"]


def test_nullability(table):
    for name in ("username", "email", "hashed_password", "is_active"):
        assert table.c[name].nullable is False


def test_is_active_defaults_to_true(table):
    assert table.c.is_active.default.arg is True


def test_indexes(table):
    # Index names depend on the configured schema, so match by column instead.
    indexes = {
        tuple(column.name for column in index.columns): bool(index.unique)
        for index in table.indexes
    }

    assert indexes == {("id",): False, ("username",): True, ("email",): True}


def test_create_table_on_sqlite(engine):
    inspector = inspect(engine)

    assert "users" in inspector.get_table_names()
    unique_columns = {
        tuple(index["column_names"])
        for index in inspector.get_indexes("users")
        if index["unique"]
    }
    assert unique_columns == {("username",), ("email",)}


def test_insert_applies_is_active_default(engine):
    with Session(engine) as session:
        user = UserModel(username="alice", email="alice@example.com", hashed_password="hash")
        session.add(user)
        session.commit()
        session.refresh(user)

        assert user.id is not None
        assert user.is_active is True
