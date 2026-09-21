import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.core.auth import get_current_user
from backend.app.core.database import get_db
from backend.app.models.audit_log import AuditLog
from backend.app.models.base import Base
from backend.app.models.contract import Contract
from backend.app.models.contract_document import ContractDocument
from backend.app.models.user import User


TEST_DATABASE_URL = "sqlite://"


engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        yield session

    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def authenticated_test_user(db_session):
    """
    Provide an authenticated manager user for API tests.

    The database dependency is overridden so API requests use
    the same SQLite test database as the test itself.
    """

    test_user = User(
        id=1,
        email="test-manager@example.com",
        password_hash="test-password-hash",
        role="manager",
        is_active=True,
    )

    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    app.dependency_overrides[get_current_user] = (
        lambda: test_user
    )

    yield test_user

    app.dependency_overrides.clear()