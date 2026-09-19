from fastapi import HTTPException

from backend.app.core.permissions import (
    require_admin,
    require_authenticated,
    require_contract_manager,
)
from backend.app.models.user import User


def make_user(role: str) -> User:
    return User(
        id=1,
        email=f"{role}@example.com",
        password_hash="hashed-password",
        role=role,
        is_active=True,
    )


def test_authenticated_allows_admin():
    user = make_user("admin")

    result = require_authenticated(current_user=user)

    assert result is user


def test_authenticated_allows_manager():
    user = make_user("manager")

    result = require_authenticated(current_user=user)

    assert result is user


def test_authenticated_allows_viewer():
    user = make_user("viewer")

    result = require_authenticated(current_user=user)

    assert result is user


def test_contract_manager_allows_admin():
    user = make_user("admin")

    result = require_contract_manager(current_user=user)

    assert result is user


def test_contract_manager_allows_manager():
    user = make_user("manager")

    result = require_contract_manager(current_user=user)

    assert result is user


def test_contract_manager_rejects_viewer():
    user = make_user("viewer")

    try:
        require_contract_manager(current_user=user)
        assert False, "Expected HTTPException"
    except HTTPException as exc:
        assert exc.status_code == 403


def test_admin_allows_admin():
    user = make_user("admin")

    result = require_admin(current_user=user)

    assert result is user


def test_admin_rejects_manager():
    user = make_user("manager")

    try:
        require_admin(current_user=user)
        assert False, "Expected HTTPException"
    except HTTPException as exc:
        assert exc.status_code == 403


def test_admin_rejects_viewer():
    user = make_user("viewer")

    try:
        require_admin(current_user=user)
        assert False, "Expected HTTPException"
    except HTTPException as exc:
        assert exc.status_code == 403