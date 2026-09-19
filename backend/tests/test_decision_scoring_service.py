from decimal import Decimal

import pytest

from backend.app.models.contract import Contract
from backend.app.services.decision.scoring import (
    DecisionInputs,
)
from backend.app.services.decision.service import DecisionScoringService


def create_contract(db_session, contract_id: str) -> Contract:
    contract = Contract(
        contract_id=contract_id,
        name="Decision Service Contract",
        source_type="manual",
        status="completed",
    )

    db_session.add(contract)
    db_session.commit()
    db_session.refresh(contract)

    return contract


def test_calculate_for_contract_creates_score(db_session):
    create_contract(db_session, "DEC-SVC-001")

    service = DecisionScoringService(db_session)

    result = service.calculate_for_contract(
        contract_id="DEC-SVC-001",
        inputs=DecisionInputs(
            financial_score=Decimal("90"),
            risk_score=Decimal("70"),
            contract_value_score=Decimal("80"),
        ),
    )

    assert result.id is not None
    assert result.score == Decimal("82.0000")
    assert result.financial_score == Decimal("90")
    assert result.risk_score == Decimal("70")
    assert result.contract_value_score == Decimal("80")


def test_calculate_for_contract_updates_existing_score(db_session):
    create_contract(db_session, "DEC-SVC-002")

    service = DecisionScoringService(db_session)

    first = service.calculate_for_contract(
        contract_id="DEC-SVC-002",
        inputs=DecisionInputs(
            financial_score=Decimal("80"),
            risk_score=Decimal("60"),
            contract_value_score=Decimal("70"),
        ),
    )

    # Store the original value before SQLAlchemy updates
    # the same database object during the second calculation.
    first_score = first.score

    second = service.calculate_for_contract(
        contract_id="DEC-SVC-002",
        inputs=DecisionInputs(
            financial_score=Decimal("95"),
            risk_score=Decimal("80"),
            contract_value_score=Decimal("90"),
        ),
    )

    assert second.id == first.id
    assert first_score == Decimal("72.0000")
    assert second.score == Decimal("89.5000")
    assert second.score != first_score


def test_get_for_contract(db_session):
    create_contract(db_session, "DEC-SVC-003")

    service = DecisionScoringService(db_session)

    service.calculate_for_contract(
        contract_id="DEC-SVC-003",
        inputs=DecisionInputs(
            financial_score=Decimal("90"),
        ),
    )

    result = service.get_for_contract("DEC-SVC-003")

    assert result is not None
    assert result.financial_score == Decimal("90")


def test_get_for_contract_returns_none_when_missing(db_session):
    create_contract(db_session, "DEC-SVC-004")

    service = DecisionScoringService(db_session)

    result = service.get_for_contract("DEC-SVC-004")

    assert result is None


def test_calculate_for_missing_contract_raises_error(db_session):
    service = DecisionScoringService(db_session)

    with pytest.raises(ValueError, match="Contract not found"):
        service.calculate_for_contract(
            contract_id="DOES-NOT-EXIST",
            inputs=DecisionInputs(
                financial_score=Decimal("80")
            ),
        )