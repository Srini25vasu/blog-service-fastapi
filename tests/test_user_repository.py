"""Tests for ``UserRepository``.

These run real SQL against an in-memory SQLite database. SQLite has no schemas,
so the configured ``DB_SCHEMA`` is translated away via ``schema_translate_map``.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config.settings import DB_SCHEMA
from app.database.models import UserModel
from app.database.session import Base
from app.repositories.user_repository import UserRepository


@pytest.fixture
def engine():
    """Fresh in-memory SQLite engine with only the users table created."""
    engine = create_engine(
        "sqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        execution_options={"schema_translate_map": {DB_SCHEMA: None}},
    )
    Base.metadata.create_all(engine, tables=[UserModel.__table__])
    yield engine
    engine.dispose()


@pytest.fixture
def db(engine):
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def repository(db):
    return UserRepository(db)


@pytest.fixture
def user(repository):
    return repository.create_user("alice", "alice@example.com", "hashed-secret")


def test_create_user_persists_user_with_id_and_active_flag(repository, db):
    created = repository.create_user("bob", "bob@example.com", "hashed-pw")

    assert created.id is not None
    assert created.username == "bob"
    assert created.email == "bob@example.com"
    assert created.hashed_password == "hashed-pw"
    assert created.is_active is True

    db.expire_all()
    stored = db.query(UserModel).filter(UserModel.id == created.id).one()
    assert stored.username == "bob"
    assert stored.is_active is True


def test_get_by_id_returns_user(repository, user):
    found = repository.get_by_id(user.id)

    assert found is not None
    assert found.id == user.id
    assert found.username == "alice"


def test_get_by_id_returns_none_when_missing(repository, user):
    assert repository.get_by_id(user.id + 999) is None


def test_get_by_username_returns_user(repository, user):
    found = repository.get_by_username("alice")

    assert found is not None
    assert found.id == user.id


def test_get_by_username_returns_none_when_missing(repository, user):
    assert repository.get_by_username("nobody") is None


def test_get_by_email_returns_user(repository, user):
    found = repository.get_by_email("alice@example.com")

    assert found is not None
    assert found.id == user.id


def test_get_by_email_returns_none_when_missing(repository, user):
    assert repository.get_by_email("nobody@example.com") is None


def test_create_user_with_duplicate_username_raises_integrity_error(repository, db, user):
    with pytest.raises(IntegrityError):
        repository.create_user("alice", "other@example.com", "hashed-pw")
    db.rollback()


def test_create_user_with_duplicate_email_raises_integrity_error(repository, db, user):
    with pytest.raises(IntegrityError):
        repository.create_user("other", "alice@example.com", "hashed-pw")
    db.rollback()
