"""Unit tests for the authentication routes in ``app.api.v1.auth``.

The router is mounted on a fresh FastAPI app (instead of ``main.app``) so the
startup DB check does not run, and ``get_auth_service`` is overridden with a
mocked service. These tests cover HTTP status codes, response bodies and the
mapping of auth domain errors to 401/409.
"""

from unittest.mock import create_autospec

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1 import auth
from app.database.models import UserModel
from app.models.user import Token, UserCreate
from app.services.auth_service import AuthService, InvalidCredentialsError, UserAlreadyExistsError


@pytest.fixture
def service():
    return create_autospec(AuthService, instance=True)


@pytest.fixture
def client(service):
    app = FastAPI()
    app.include_router(auth.router, prefix="/api/v1")
    app.dependency_overrides[auth.get_auth_service] = lambda: service
    return TestClient(app)


@pytest.fixture
def user():
    return UserModel(
        id=1,
        username="alice",
        email="alice@example.com",
        hashed_password="$2b$12$hashedvalue",
        is_active=True,
    )


USER_JSON = {"id": 1, "username": "alice", "email": "alice@example.com", "is_active": True}
REGISTER_PAYLOAD = {"username": "alice", "email": "alice@example.com", "password": "secret123"}


def test_register_returns_201_without_password(client, service, user):
    service.register.return_value = user

    response = client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)

    assert response.status_code == 201
    assert response.json() == USER_JSON
    assert "password" not in response.json()
    assert "hashed_password" not in response.json()
    service.register.assert_called_once_with(UserCreate(**REGISTER_PAYLOAD))


def test_register_returns_409_for_duplicate_user(client, service):
    service.register.side_effect = UserAlreadyExistsError("username")

    response = client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)

    assert response.status_code == 409
    assert response.json() == {"detail": "User with this username already exists"}


def test_register_returns_422_for_short_password(client, service):
    response = client.post(
        "/api/v1/auth/register",
        json={"username": "alice", "email": "alice@example.com", "password": "short"},
    )

    assert response.status_code == 422
    service.register.assert_not_called()


def test_token_returns_access_token(client, service, user):
    service.authenticate.return_value = user
    service.issue_token.return_value = Token(access_token="jwt-token")

    response = client.post("/api/v1/auth/token", data={"username": "alice", "password": "secret123"})

    assert response.status_code == 200
    assert response.json() == {"access_token": "jwt-token", "token_type": "bearer"}
    service.authenticate.assert_called_once_with("alice", "secret123")
    service.issue_token.assert_called_once_with(user)


def test_token_returns_401_for_invalid_credentials(client, service):
    service.authenticate.side_effect = InvalidCredentialsError()

    response = client.post("/api/v1/auth/token", data={"username": "alice", "password": "wrong"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}
    assert response.headers["WWW-Authenticate"] == "Bearer"
    service.issue_token.assert_not_called()


def test_me_returns_current_user(client, service, user):
    service.get_user_from_token.return_value = user

    response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer jwt-token"})

    assert response.status_code == 200
    assert response.json() == USER_JSON
    service.get_user_from_token.assert_called_once_with("jwt-token")


def test_me_returns_401_without_token(client, service):
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
    service.get_user_from_token.assert_not_called()


def test_me_returns_401_for_invalid_token(client, service):
    service.get_user_from_token.side_effect = InvalidCredentialsError()

    response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer bad-token"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}
    assert response.headers["WWW-Authenticate"] == "Bearer"
