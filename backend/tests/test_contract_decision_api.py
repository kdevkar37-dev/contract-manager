from fastapi.testclient import TestClient

from backend.app.core.auth import get_current_user
from backend.app.main import app
from backend.app.models.contract import Contract
from backend.app.models.user import User


client = TestClient(app)


def create_contract(db_session, contract_id="CONTRACT-API-001"):
    contract = Contract(
        contract_id=contract_id,
        name="API Test Contract",
        source_type="manual",
        status="completed",
    )

    db_session.add(contract)
    db_session.commit()
    db_session.refresh(contract)

    return contract


def create_user(db_session, email, role):
    user = User(
        email=email,
        password_hash="test-hash",
        role=role,
        is_active=True,
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


def test_create_final_decision_requires_authentication():
    existing_override = app.dependency_overrides.pop(
        get_current_user,
        None,
    )

    try:
        response = client.post(
            "/contracts/CONTRACT-API-001/final-decision",
            json={
                "decision": "approved",
                "reason": "Approved after review.",
            },
        )
    finally:
        if existing_override is not None:
            app.dependency_overrides[get_current_user] = (
                existing_override
            )

    assert response.status_code in {401, 403}


def test_create_final_decision_manager(
    db_session,
    authenticated_test_user,
):
    contract = create_contract(db_session)

    response = client.post(
        f"/contracts/{contract.contract_id}/final-decision",
        json={
            "decision": "approved",
            "reason": "Financial and risk analysis are acceptable.",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["contract_id"] == contract.contract_id
    assert data["decision"] == "approved"
    assert data["reason"] == (
        "Financial and risk analysis are acceptable."
    )
    assert data["decided_by"] == authenticated_test_user.id
    assert data["decided_at"] is not None


def test_create_final_decision_invalid_value(
    db_session,
    authenticated_test_user,
):
    contract = create_contract(
        db_session,
        contract_id="CONTRACT-API-002",
    )

    response = client.post(
        f"/contracts/{contract.contract_id}/final-decision",
        json={
            "decision": "pending",
            "reason": "Invalid decision.",
        },
    )

    assert response.status_code == 400
    assert "Invalid decision" in response.json()["detail"]


def test_create_final_decision_unknown_contract(
    authenticated_test_user,
):
    response = client.post(
        "/contracts/UNKNOWN-CONTRACT/final-decision",
        json={
            "decision": "approved",
            "reason": "Test.",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Contract not found."


def test_get_latest_final_decision(
    db_session,
    authenticated_test_user,
):
    contract = create_contract(
        db_session,
        contract_id="CONTRACT-API-003",
    )

    create_response = client.post(
        f"/contracts/{contract.contract_id}/final-decision",
        json={
            "decision": "approved",
            "reason": "Approved.",
        },
    )

    assert create_response.status_code == 201

    response = client.get(
        f"/contracts/{contract.contract_id}/final-decision"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["contract_id"] == contract.contract_id
    assert data["decision"] == "approved"


def test_get_final_decision_without_decision(
    db_session,
    authenticated_test_user,
):
    contract = create_contract(
        db_session,
        contract_id="CONTRACT-API-004",
    )

    response = client.get(
        f"/contracts/{contract.contract_id}/final-decision"
    )

    assert response.status_code == 200
    assert response.json() is None


def test_get_final_decision_history(
    db_session,
    authenticated_test_user,
):
    contract = create_contract(
        db_session,
        contract_id="CONTRACT-API-005",
    )

    first_response = client.post(
        f"/contracts/{contract.contract_id}/final-decision",
        json={
            "decision": "needs_review",
            "reason": "Needs legal review.",
        },
    )

    assert first_response.status_code == 201

    second_response = client.post(
        f"/contracts/{contract.contract_id}/final-decision",
        json={
            "decision": "approved",
            "reason": "Legal review completed.",
        },
    )

    assert second_response.status_code == 201

    response = client.get(
        f"/contracts/{contract.contract_id}/final-decision/history"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["contract_id"] == contract.contract_id
    assert len(data["decisions"]) == 2

    decisions = {
        item["decision"]
        for item in data["decisions"]
    }

    assert decisions == {
        "needs_review",
        "approved",
    }


def test_get_final_decision_unknown_contract(
    authenticated_test_user,
):
    response = client.get(
        "/contracts/UNKNOWN-CONTRACT/final-decision"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Contract not found."


def test_get_final_decision_history_unknown_contract(
    authenticated_test_user,
):
    response = client.get(
        "/contracts/UNKNOWN-CONTRACT/final-decision/history"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Contract not found."