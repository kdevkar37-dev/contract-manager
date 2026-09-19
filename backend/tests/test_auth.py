from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from backend.app.core.auth import get_current_user, require_roles
from backend.app.core.security import create_access_token
from backend.app.models.user import User
from backend.app.services.auth.service import AuthenticationService


def create_test_user(db_session, email="auth@example.com", role="viewer"):
    service = AuthenticationService(db_session)

    return service.register(
        email=email,
        password="Test@123",
        role=role,
    )


def test_get_current_user_with_valid_token(db_session):
    user = create_test_user(db_session)

    token = create_access_token(str(user.id))

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )

    current_user = get_current_user(
        credentials=credentials,
        db=db_session,
    )

    assert current_user.id == user.id
    assert current_user.email == user.email


def test_get_current_user_rejects_invalid_token(db_session):
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="invalid.token.value",
    )

    try:
        get_current_user(
            credentials=credentials,
            db=db_session,
        )
        assert False, "Expected HTTPException"
    except HTTPException as exc:
        assert exc.status_code == 401


def test_get_current_user_rejects_expired_token(db_session):
    user = create_test_user(
        db_session,
        email="expired@example.com",
    )

    token = create_access_token(
        str(user.id),
        expires_minutes=-1,
    )

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )

    try:
        get_current_user(
            credentials=credentials,
            db=db_session,
        )
        assert False, "Expected HTTPException"
    except HTTPException as exc:
        assert exc.status_code == 401


def test_get_current_user_rejects_unknown_user(db_session):
    token = create_access_token("999999")

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )

    try:
        get_current_user(
            credentials=credentials,
            db=db_session,
        )
        assert False, "Expected HTTPException"
    except HTTPException as exc:
        assert exc.status_code == 401


def test_get_current_user_rejects_inactive_user(db_session):
    user = create_test_user(
        db_session,
        email="inactive@example.com",
    )

    user.is_active = False
    db_session.commit()

    token = create_access_token(str(user.id))

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )

    try:
        get_current_user(
            credentials=credentials,
            db=db_session,
        )
        assert False, "Expected HTTPException"
    except HTTPException as exc:
        assert exc.status_code == 403


def test_require_roles_allows_matching_role(db_session):
    user = create_test_user(
        db_session,
        email="manager@example.com",
        role="manager",
    )

    role_dependency = require_roles("manager")

    result = role_dependency(current_user=user)

    assert result is user


def test_require_roles_rejects_wrong_role(db_session):
    user = create_test_user(
        db_session,
        email="viewer@example.com",
        role="viewer",
    )

    role_dependency = require_roles("manager")

    try:
        role_dependency(current_user=user)
        assert False, "Expected HTTPException"
    except HTTPException as exc:
        assert exc.status_code == 403


def test_require_roles_supports_multiple_roles(db_session):
    user = create_test_user(
        db_session,
        email="admin@example.com",
        role="admin",
    )

    role_dependency = require_roles("admin", "manager")

    result = role_dependency(current_user=user)

    assert result is user