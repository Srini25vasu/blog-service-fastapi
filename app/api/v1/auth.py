"""HTTP routes for user authentication (``/api/v1/auth``).

Implements the OAuth2 password flow: clients register, exchange username and
password for a JWT bearer token at ``/auth/token`` and send it as
``Authorization: Bearer <token>``. ``get_current_user`` can be used by other
routers to protect their endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.config.settings import API_V1_PREFIX
from app.database.models import UserModel
from app.database.session import get_db
from app.models.user import Token, User, UserCreate
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService, InvalidCredentialsError, UserAlreadyExistsError

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{API_V1_PREFIX}/auth/token")


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Build an ``AuthService`` bound to the current request's DB session."""
    repository = UserRepository(db)
    return AuthService(repository)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    service: AuthService = Depends(get_auth_service),
) -> UserModel:
    """Resolve the user for the request's bearer token, or 401 if it is invalid."""
    try:
        return service.get_user_from_token(token)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


@router.post("/auth/register", status_code=status.HTTP_201_CREATED, response_model=User)
def register(payload: UserCreate, service: AuthService = Depends(get_auth_service)):
    """Register a new user, or 409 if the username or email is taken."""
    try:
        return service.register(payload)
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/auth/token", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
):
    """Exchange username and password for a bearer access token, or 401."""
    try:
        user = service.authenticate(form_data.username, form_data.password)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    return service.issue_token(user)


@router.get("/auth/me", response_model=User)
def read_current_user(current_user: UserModel = Depends(get_current_user)):
    """Return the authenticated user."""
    return current_user
