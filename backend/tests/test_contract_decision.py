from datetime import datetime

import pytest

from backend.app.models.contract import Contract
from backend.app.models.user import User
from backend.app.services.decision.contract_decision_service import (
    ContractDecisionService,
)


def create_contract(db_session, contract_id="CONTRACT-001"):
    contract = Contract(
        contract_id=contract_id,
        name="Test Contract",
        source_type="manual",
        status="completed",
    )

    db_session.add(contract)
    db_session.commit()
    db_session.refresh(contract)

    return contract


def create_user(db_session, role="manager"):
    user = User(
        email=f"{role}@example.com",
        password_hash="test-hash",
        role=role,
        is_active=True,
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


def test_create_approved_decision(db_session):
    contract = create_contract(db_session)
    manager = create_user(db_session)

    service = ContractDecisionService(db_session)

    result = service.create_decision(
        contract_id=contract.contract_id,
        decision="approved",
        reason="Financial and risk analysis are acceptable.",
        decided_by=manager.id,
    )

    assert result.contract_id == contract.contract_id
    assert result.decision == "approved"
    assert result.reason == "Financial and risk analysis are acceptable."
    assert result.decided_by == manager.id
    assert isinstance(result.decided_at, datetime)


def test_create_rejected_decision(db_session):
    contract = create_contract(db_session)
    manager = create_user(db_session)

    service = ContractDecisionService(db_session)

    result = service.create_decision(
        contract_id=contract.contract_id,
        decision="rejected",
        reason="Risk exposure is too high.",
        decided_by=manager.id,
    )

    assert result.decision == "rejected"


def test_create_needs_review_decision(db_session):
    contract = create_contract(db_session)
    manager = create_user(db_session)

    service = ContractDecisionService(db_session)

    result = service.create_decision(
        contract_id=contract.contract_id,
        decision="needs_review",
        reason="Additional legal review is required.",
        decided_by=manager.id,
    )

    assert result.decision == "needs_review"


def test_decision_is_normalized(db_session):
    contract = create_contract(db_session)
    manager = create_user(db_session)

    service = ContractDecisionService(db_session)

    result = service.create_decision(
        contract_id=contract.contract_id,
        decision="  APPROVED  ",
        reason="Approved after review.",
        decided_by=manager.id,
    )

    assert result.decision == "approved"


def test_invalid_decision_is_rejected(db_session):
    contract = create_contract(db_session)
    manager = create_user(db_session)

    service = ContractDecisionService(db_session)

    with pytest.raises(ValueError, match="Invalid decision"):
        service.create_decision(
            contract_id=contract.contract_id,
            decision="pending",
            reason="Invalid decision.",
            decided_by=manager.id,
        )


def test_unknown_contract_is_rejected(db_session):
    manager = create_user(db_session)

    service = ContractDecisionService(db_session)

    with pytest.raises(ValueError, match="Contract not found"):
        service.create_decision(
            contract_id="UNKNOWN-CONTRACT",
            decision="approved",
            reason="Test.",
            decided_by=manager.id,
        )


def test_latest_decision_is_returned(db_session):
    contract = create_contract(db_session)
    manager = create_user(db_session)

    service = ContractDecisionService(db_session)

    service.create_decision(
        contract_id=contract.contract_id,
        decision="needs_review",
        reason="Initial review.",
        decided_by=manager.id,
    )

    service.create_decision(
        contract_id=contract.contract_id,
        decision="approved",
        reason="Final review completed.",
        decided_by=manager.id,
    )

    result = service.get_latest_decision(contract.contract_id)

    assert result is not None
    assert result.contract_id == contract.contract_id
    assert result.decision == "approved"


def test_no_decision_returns_none(db_session):
    contract = create_contract(db_session)

    service = ContractDecisionService(db_session)

    result = service.get_latest_decision(contract.contract_id)

    assert result is None


def test_decision_history_is_preserved(db_session):
    contract = create_contract(db_session)
    manager = create_user(db_session)

    service = ContractDecisionService(db_session)

    service.create_decision(
        contract_id=contract.contract_id,
        decision="needs_review",
        reason="Needs legal review.",
        decided_by=manager.id,
    )

    service.create_decision(
        contract_id=contract.contract_id,
        decision="rejected",
        reason="Legal concerns remain.",
        decided_by=manager.id,
    )

    history = service.get_decision_history(contract.contract_id)

    assert len(history) == 2
    assert {item.decision for item in history} == {
        "needs_review",
        "rejected",
    }


def test_decision_history_for_unknown_contract_is_rejected(db_session):
    service = ContractDecisionService(db_session)

    with pytest.raises(ValueError, match="Contract not found"):
        service.get_decision_history("UNKNOWN-CONTRACT")