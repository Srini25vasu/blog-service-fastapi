"""Tests for the JWT secret key startup check."""

import pytest

from app.config import settings


@pytest.fixture
def jwt_env(monkeypatch):
    def apply(secret, app_env="development"):
        monkeypatch.setattr(settings, "JWT_SECRET_KEY", secret)
        monkeypatch.setattr(settings, "APP_ENV", app_env)

    return apply


def test_default_secret_warns_outside_production(jwt_env):
    jwt_env(settings.DEFAULT_JWT_SECRET_KEY)

    assert "public default" in settings.check_jwt_secret_key()


def test_default_secret_raises_in_production(jwt_env):
    jwt_env(settings.DEFAULT_JWT_SECRET_KEY, app_env="production")

    with pytest.raises(RuntimeError):
        settings.check_jwt_secret_key()


def test_short_secret_warns(jwt_env):
    jwt_env("too-short", app_env="production")

    assert "32 bytes" in settings.check_jwt_secret_key()


def test_strong_secret_passes(jwt_env):
    jwt_env("x" * 32, app_env="production")

    assert settings.check_jwt_secret_key() is None
