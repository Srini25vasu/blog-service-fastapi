"""Unit tests for ``app.core.security``.

Covers bcrypt password hashing/verification and creation/validation of the
JWT access tokens used by the OAuth2 password flow. No database or HTTP layer
is involved.
"""

from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.config.settings import JWT_ALGORITHM, JWT_SECRET_KEY
from app.core.security import (
    InvalidTokenError,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


@pytest.fixture(scope="module")
def password_hash():
    return hash_password("secret123")


def _encode(payload, secret=JWT_SECRET_KEY):
    return jwt.encode(payload, secret, algorithm=JWT_ALGORITHM)


def _future():
    return datetime.now(timezone.utc) + timedelta(minutes=5)


def test_hash_password_does_not_return_plaintext(password_hash):
    assert password_hash != "secret123"
    assert password_hash.startswith("$2")


def test_hash_password_uses_random_salt(password_hash):
    assert hash_password("secret123") != password_hash


def test_verify_password_accepts_correct_password(password_hash):
    assert verify_password("secret123", password_hash) is True


def test_verify_password_rejects_wrong_password(password_hash):
    assert verify_password("wrong-password", password_hash) is False


@pytest.mark.parametrize("malformed", ["", "not-a-bcrypt-hash", "$2b$12$tooshort"])
def test_verify_password_returns_false_for_malformed_hash(malformed):
    assert verify_password("secret123", malformed) is False


def test_create_and_decode_access_token_roundtrip():
    token = create_access_token("alice")

    assert decode_access_token(token) == "alice"


def test_create_access_token_uses_custom_expiry():
    before = datetime.now(timezone.utc)
    token = create_access_token("alice", expires_delta=timedelta(minutes=5))

    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    expires_at = datetime.fromtimestamp(payload["exp"], timezone.utc)
    assert before + timedelta(minutes=4) < expires_at <= before + timedelta(minutes=5, seconds=1)


def test_decode_access_token_rejects_expired_token():
    token = create_access_token("alice", expires_delta=timedelta(minutes=-1))

    with pytest.raises(InvalidTokenError):
        decode_access_token(token)


def test_decode_access_token_rejects_tampered_token():
    token = create_access_token("alice")
    header, payload, signature = token.split(".")
    tampered_signature = ("A" if signature[0] != "A" else "B") + signature[1:]

    with pytest.raises(InvalidTokenError):
        decode_access_token(f"{header}.{payload}.{tampered_signature}")


def test_decode_access_token_rejects_token_signed_with_other_secret():
    token = _encode({"sub": "alice", "exp": _future()}, secret="some-other-secret-key-0123456789")

    with pytest.raises(InvalidTokenError):
        decode_access_token(token)


def test_decode_access_token_rejects_garbage():
    with pytest.raises(InvalidTokenError):
        decode_access_token("not.a.jwt")


def test_decode_access_token_rejects_token_without_subject():
    token = _encode({"exp": _future()})

    with pytest.raises(InvalidTokenError):
        decode_access_token(token)


def test_decode_access_token_rejects_empty_subject():
    token = _encode({"sub": "", "exp": _future()})

    with pytest.raises(InvalidTokenError):
        decode_access_token(token)
