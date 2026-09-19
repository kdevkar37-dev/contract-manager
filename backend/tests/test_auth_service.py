from backend.app.models.user import User
from backend.app.services.auth.service import AuthenticationService


def test_register_creates_user(db_session):
    service = AuthenticationService(db_session)

    user = service.register(
        email="newuser@example.com",
        password="Test@123",
    )

    assert user.id is not None
    assert user.email == "newuser@example.com"
    assert user.role == "viewer"
    assert user.is_active is True
    assert user.password_hash != "Test@123"


def test_register_normalizes_email(db_session):
    service = AuthenticationService(db_session)

    user = service.register(
        email="  USER@EXAMPLE.COM  ",
        password="Test@123",
    )

    assert user.email == "user@example.com"


def test_register_rejects_duplicate_email(db_session):
    service = AuthenticationService(db_session)

    service.register(
        email="duplicate@example.com",
        password="Test@123",
    )

    try:
        service.register(
            email="DUPLICATE@example.com",
            password="Test@456",
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "A user with this email already exists."


def test_authenticate_with_correct_password(db_session):
    service = AuthenticationService(db_session)

    service.register(
        email="login@example.com",
        password="Test@123",
    )

    user = service.authenticate(
        email="login@example.com",
        password="Test@123",
    )

    assert user is not None
    assert user.email == "login@example.com"


def test_authenticate_rejects_wrong_password(db_session):
    service = AuthenticationService(db_session)

    service.register(
        email="wrongpassword@example.com",
        password="Test@123",
    )

    user = service.authenticate(
        email="wrongpassword@example.com",
        password="Wrong@123",
    )

    assert user is None


def test_authenticate_rejects_unknown_user(db_session):
    service = AuthenticationService(db_session)

    user = service.authenticate(
        email="unknown@example.com",
        password="Test@123",
    )

    assert user is None


def test_authenticate_rejects_inactive_user(db_session):
    service = AuthenticationService(db_session)

    user = service.register(
        email="inactive@example.com",
        password="Test@123",
    )

    user.is_active = False
    db_session.commit()

    authenticated_user = service.authenticate(
        email="inactive@example.com",
        password="Test@123",
    )

    assert authenticated_user is None


def test_create_token_returns_jwt(db_session):
    service = AuthenticationService(db_session)

    user = service.register(
        email="token@example.com",
        password="Test@123",
    )

    token = service.create_token(user)

    assert isinstance(token, str)
    assert len(token) > 0
    assert token.count(".") == 2