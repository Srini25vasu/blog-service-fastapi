"""Unit tests for ``AuthService``.

The repository is replaced by an autospec mock, so these tests run without a
database. Password hashing and JWT handling use the real security helpers.
"""

from datetime import timedelta
from unittest.mock import create_autospec

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.security import create_access_token, decode_access_token, hash_password, verify_password
from app.database.models import UserModel
from app.models.user import Token, UserCreate
from app.repositories.user_repository import UserRepository
from app.services import auth_service
from app.services.auth_service import AuthService, InvalidCredentialsError, UserAlreadyExistsError

PASSWORD = "s3cret-password"


@pytest.fixture
def repository():
    """Mocked repository whose methods enforce the real signatures."""
    return create_autospec(UserRepository, instance=True)


@pytest.fixture
def service(repository):
    return AuthService(repository)


@pytest.fixture(scope="module")
def password_hash():
    return hash_password(PASSWORD)


@pytest.fixture
def user(password_hash):
    return UserModel(id=1, username="alice", email="alice@example.com", hashed_password=password_hash, is_active=True)


@pytest.fixture
def inactive_user(password_hash):
    return UserModel(id=2, username="bob", email="bob@example.com", hashed_password=password_hash, is_active=False)


@pytest.fixture
def payload():
    return UserCreate(username="alice", email="alice@example.com", password=PASSWORD)


# --- register ---------------------------------------------------------------


def test_register_creates_user_with_hashed_password(service, repository, payload, user):
    repository.get_by_username.return_value = None
    repository.get_by_email.return_value = None
    repository.create_user.return_value = user

    assert service.register(payload) is user

    repository.get_by_username.assert_called_once_with("alice")
    repository.get_by_email.assert_called_once_with("alice@example.com")
    repository.create_user.assert_called_once()
    kwargs = repository.create_user.call_args.kwargs
    assert kwargs["username"] == "alice"
    assert kwargs["email"] == "alice@example.com"
    assert kwargs["hashed_password"] != PASSWORD
    assert verify_password(PASSWORD, kwargs["hashed_password"])


def test_register_rejects_duplicate_username(service, repository, payload, user):
    repository.get_by_username.return_value = user

    with pytest.raises(UserAlreadyExistsError) as exc_info:
        service.register(payload)

    assert exc_info.value.field == "username"
    repository.create_user.assert_not_called()


def test_register_rejects_duplicate_email(service, repository, payload, user):
    repository.get_by_username.return_value = None
    repository.get_by_email.return_value = user

    with pytest.raises(UserAlreadyExistsError) as exc_info:
        service.register(payload)

    assert exc_info.value.field == "email"
    repository.create_user.assert_not_called()


@pytest.mark.parametrize(
    ("db_message", "field"),
    [
        ('duplicate key value violates unique constraint "ix_users_email"', "email"),
        ('duplicate key value violates unique constraint "ix_users_username"', "username"),
    ],
)
def test_register_maps_integrity_error_from_concurrent_insert(service, repository, payload, db_message, field):
    repository.get_by_username.return_value = None
    repository.get_by_email.return_value = None
    repository.create_user.side_effect = IntegrityError("INSERT INTO users ...", {}, Exception(db_message))

    with pytest.raises(UserAlreadyExistsError) as exc_info:
        service.register(payload)

    assert exc_info.value.field == field


# --- authenticate -----------------------------------------------------------


def test_authenticate_returns_user_for_valid_credentials(service, repository, user):
    repository.get_by_username.return_value = user

    assert service.authenticate("alice", PASSWORD) is user
    repository.get_by_username.assert_called_once_with("alice")


def test_authenticate_rejects_unknown_user(service, repository, monkeypatch):
    repository.get_by_username.return_value = None
    checked = []
    monkeypatch.setattr(
        auth_service, "verify_password", lambda password, password_hash: checked.append(password) or False
    )

    with pytest.raises(InvalidCredentialsError):
        service.authenticate("nobody", PASSWORD)

    # A dummy bcrypt check still runs so the response time does not reveal unknown usernames.
    assert checked == [PASSWORD]


def test_authenticate_rejects_wrong_password(service, repository, user):
    repository.get_by_username.return_value = user

    with pytest.raises(InvalidCredentialsError):
        service.authenticate("alice", "wrong-password")


def test_authenticate_rejects_inactive_user(service, repository, inactive_user):
    repository.get_by_username.return_value = inactive_user

    with pytest.raises(InvalidCredentialsError):
        service.authenticate("bob", PASSWORD)


# --- issue_token ------------------------------------------------------------


def test_issue_token_returns_bearer_token_for_user(service, user):
    token = service.issue_token(user)

    assert isinstance(token, Token)
    assert token.token_type == "bearer"
    assert decode_access_token(token.access_token) == "alice"


# --- get_user_from_token ----------------------------------------------------


def test_get_user_from_token_returns_user(service, repository, user):
    repository.get_by_username.return_value = user
    token = create_access_token("alice")

    assert service.get_user_from_token(token) is user
    repository.get_by_username.assert_called_once_with("alice")


def test_get_user_from_token_rejects_invalid_token(service, repository):
    with pytest.raises(InvalidCredentialsError):
        service.get_user_from_token("not-a-jwt")

    repository.get_by_username.assert_not_called()


def test_get_user_from_token_rejects_expired_token(service, repository):
    token = create_access_token("alice", expires_delta=timedelta(minutes=-1))

    with pytest.raises(InvalidCredentialsError):
        service.get_user_from_token(token)

    repository.get_by_username.assert_not_called()


def test_get_user_from_token_rejects_unknown_user(service, repository):
    repository.get_by_username.return_value = None
    token = create_access_token("ghost")

    with pytest.raises(InvalidCredentialsError):
        service.get_user_from_token(token)


def test_get_user_from_token_rejects_inactive_user(service, repository, inactive_user):
    repository.get_by_username.return_value = inactive_user
    token = create_access_token("bob")

    with pytest.raises(InvalidCredentialsError):
        service.get_user_from_token(token)
