from __future__ import annotations

from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.repositories.users import UserRepository
from backend.app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)


class AuthenticationService:
    """
    Handles user registration and authentication.

    Database operations are delegated to UserRepository.
    Password hashing and JWT handling are delegated to security utilities.
    """

    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)

    def register(
        self,
        email: str,
        password: str,
        role: str = "viewer",
    ) -> User:
        normalized_email = email.strip().lower()

        existing_user = self.user_repository.get_by_email(
            normalized_email
        )

        if existing_user is not None:
            raise ValueError("A user with this email already exists.")

        user = User(
            email=normalized_email,
            password_hash=hash_password(password),
            role=role,
            is_active=True,
        )

        return self.user_repository.create(user)

    def authenticate(
        self,
        email: str,
        password: str,
    ) -> User | None:
        normalized_email = email.strip().lower()

        user = self.user_repository.get_by_email(
            normalized_email
        )

        if user is None:
            return None

        if not user.is_active:
            return None

        if not verify_password(
            password,
            user.password_hash,
        ):
            return None

        return user

    def create_token(self, user: User) -> str:
        return create_access_token(
            subject=str(user.id)
        )