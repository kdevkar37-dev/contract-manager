from backend.app.models.user import User
from backend.app.repositories.users import UserRepository


def test_create_and_get_user(db_session):
    repository = UserRepository(db_session)

    user = User(
        email="test@example.com",
        password_hash="hashed-password",
        role="viewer",
    )

    created = repository.create(user)

    assert created.id is not None
    assert created.email == "test@example.com"

    found = repository.get_by_email("test@example.com")

    assert found is not None
    assert found.id == created.id
    assert found.email == "test@example.com"


def test_get_missing_user_returns_none(db_session):
    repository = UserRepository(db_session)

    result = repository.get_by_email("missing@example.com")

    assert result is None