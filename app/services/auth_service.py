"""Business logic for user registration and OAuth2 password-flow login.

Routes call the service; the service talks to the database only through
``UserRepository``. Domain errors are raised as exceptions and translated
into HTTP responses by the API layer.
"""

from app.core.security import (
    InvalidTokenError,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.database.models import UserModel
from app.models.user import Token, UserCreate
from app.repositories.user_repository import UserRepository


class UserAlreadyExistsError(Exception):
    """Raised when the username or email is already registered."""

    def __init__(self, field: str) -> None:
        self.field = field
        super().__init__(f"User with this {field} already exists")


class InvalidCredentialsError(Exception):
    """Raised when credentials or an access token cannot be verified."""


class AuthService:
    """Use cases for registering users, logging in and resolving tokens."""

    def __init__(self, repository: UserRepository) -> None:
        """Create the service.

        Args:
            repository: Data access object used to persist users.
        """
        self.repository = repository

    def register(self, payload: UserCreate) -> UserModel:
        """Create a new user with a hashed password.

        Raises:
            UserAlreadyExistsError: If the username or email is taken.
        """
        if self.repository.get_by_username(payload.username) is not None:
            raise UserAlreadyExistsError("username")
        if self.repository.get_by_email(payload.email) is not None:
            raise UserAlreadyExistsError("email")
        return self.repository.create_user(
            username=payload.username,
            email=payload.email,
            hashed_password=hash_password(payload.password),
        )

    def authenticate(self, username: str, password: str) -> UserModel:
        """Return the active user matching the credentials.

        Raises:
            InvalidCredentialsError: If the user is unknown, inactive or the password is wrong.
        """
        user = self.repository.get_by_username(username)
        if user is None or not user.is_active or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()
        return user

    def issue_token(self, user: UserModel) -> Token:
        """Create a bearer access token for ``user``."""
        return Token(access_token=create_access_token(subject=user.username))

    def get_user_from_token(self, token: str) -> UserModel:
        """Resolve the active user an access token was issued for.

        Raises:
            InvalidCredentialsError: If the token is invalid or the user is unknown or inactive.
        """
        try:
            username = decode_access_token(token)
        except InvalidTokenError as exc:
            raise InvalidCredentialsError() from exc
        user = self.repository.get_by_username(username)
        if user is None or not user.is_active:
            raise InvalidCredentialsError()
        return user
