import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.app.main import app
from backend.app.core.auth import get_current_user
from backend.app.models.base import Base
from backend.app.models.contract import Contract
from backend.app.models.contract_document import ContractDocument
from backend.app.models.user import User


TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        yield session

    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def authenticated_test_user():
    """
    Provide an authenticated manager user for API tests.

    Real authentication and RBAC remain enabled in the application.
    This override only prevents existing API tests from failing with
    401 before they can test their actual behavior.
    """

    test_user = User(
        id=1,
        email="test-manager@example.com",
        password_hash="test-password-hash",
        role="manager",
        is_active=True,
    )

    app.dependency_overrides[get_current_user] = lambda: test_user

    yield test_user

    app.dependency_overrides.clear()