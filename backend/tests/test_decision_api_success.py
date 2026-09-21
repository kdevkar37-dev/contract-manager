import uuid
from decimal import Decimal

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.models.contract import Contract


client = TestClient(app)


def create_contract(db_session) -> str:
    contract_id = f"DEC-API-{uuid.uuid4().hex[:12]}"

    contract = Contract(
        contract_id=contract_id,
        name="Decision API Test Contract",
        source_type="manual",
        status="completed",
    )

    db_session.add(contract)
    db_session.commit()
    db_session.refresh(contract)

    return contract_id


def test_calculate_decision_score_success(
    db_session,
    authenticated_test_user,
):
    contract_id = create_contract(db_session)

    response = client.post(
        f"/contracts/{contract_id}/decision-score",
        json={
            "financial_score": 90,
            "risk_score": 70,
            "contract_value_score": 80,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["contract_id"] == contract_id
    assert Decimal(str(data["score"])) == Decimal("82.0000")

    assert Decimal(str(data["financial_score"])) == Decimal("90")
    assert Decimal(str(data["risk_score"])) == Decimal("70")
    assert Decimal(str(data["contract_value_score"])) == Decimal("80")

    assert Decimal(str(data["financial_weight"])) == Decimal("50")
    assert Decimal(str(data["risk_weight"])) == Decimal("30")
    assert Decimal(str(data["contract_value_weight"])) == Decimal("20")

    assert isinstance(data["assumptions"], list)
    assert isinstance(data["explanation"], list)


def test_get_decision_score_success(
    db_session,
    authenticated_test_user,
):
    contract_id = create_contract(db_session)

    create_response = client.post(
        f"/contracts/{contract_id}/decision-score",
        json={
            "financial_score": 95,
            "risk_score": 75,
            "contract_value_score": 85,
        },
    )

    assert create_response.status_code == 200

    response = client.get(
        f"/contracts/{contract_id}/decision-score"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["contract_id"] == contract_id
    assert Decimal(str(data["score"])) == Decimal("87.0000")


def test_get_decision_score_returns_null_when_not_calculated(
    db_session,
    authenticated_test_user,
):
    contract_id = create_contract(db_session)

    response = client.get(
        f"/contracts/{contract_id}/decision-score"
    )

    assert response.status_code == 200
    assert response.json() is None