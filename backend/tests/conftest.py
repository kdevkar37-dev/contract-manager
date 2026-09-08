

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.app.models.base import Base
from backend.app.models.contract import Contract
from backend.app.models.contract_document import ContractDocument


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