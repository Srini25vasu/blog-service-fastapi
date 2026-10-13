"""Validation tests for the user Pydantic schemas."""

import pytest
from pydantic import ValidationError

from app.database.models import UserModel
from app.models.user import Token, User, UserCreate


def test_user_create_accepts_valid_data():
    payload = UserCreate(username="alice", email="alice@example.com", password="s3cretpass")

    assert payload.username == "alice"
    assert payload.password == "s3cretpass"


def test_user_create_rejects_too_short_password():
    with pytest.raises(ValidationError):
        UserCreate(username="alice", email="alice@example.com", password="short")


def test_user_create_rejects_too_long_password():
    with pytest.raises(ValidationError):
        UserCreate(username="alice", email="alice@example.com", password="x" * 73)


def test_user_create_rejects_too_short_username():
    with pytest.raises(ValidationError):
        UserCreate(username="al", email="alice@example.com", password="s3cretpass")


def test_user_validates_from_orm_model_without_password():
    model = UserModel(
        id=1,
        username="alice",
        email="alice@example.com",
        hashed_password="hashed",
        is_active=True,
    )

    user = User.model_validate(model)

    assert user == User(id=1, username="alice", email="alice@example.com", is_active=True)
    assert "hashed_password" not in user.model_dump()


def test_token_defaults_to_bearer_type():
    token = Token(access_token="abc")

    assert token.token_type == "bearer"
