from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.models import UserModel


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> UserModel | None:
        return self.db.query(UserModel).filter(UserModel.id == user_id).first()

    def get_by_username(self, username: str) -> UserModel | None:
        return self.db.query(UserModel).filter(UserModel.username == username).first()

    def get_by_email(self, email: str) -> UserModel | None:
        return self.db.query(UserModel).filter(UserModel.email == email).first()

    def create_user(self, username: str, email: str, hashed_password: str) -> UserModel:
        user = UserModel(username=username, email=email, hashed_password=hashed_password, is_active=True)
        self.db.add(user)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise
        self.db.refresh(user)
        return user
