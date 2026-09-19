from decimal import Decimal

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_calculate_decision_score_for_missing_contract():
    response = client.post(
        "/contracts/DOES-NOT-EXIST/decision-score",
        json={
            "financial_score": 90,
            "risk_score": 70,
            "contract_value_score": 80,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Contract not found"


def test_get_decision_score_for_missing_contract():
    response = client.get(
        "/contracts/DOES-NOT-EXIST/decision-score"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Contract not found"


def test_decision_score_request_rejects_score_above_100():
    response = client.post(
        "/contracts/DEC-API-001/decision-score",
        json={
            "financial_score": 101,
            "risk_score": 70,
            "contract_value_score": 80,
        },
    )

    assert response.status_code == 422


def test_decision_score_request_rejects_negative_score():
    response = client.post(
        "/contracts/DEC-API-001/decision-score",
        json={
            "financial_score": -1,
            "risk_score": 70,
            "contract_value_score": 80,
        },
    )

    assert response.status_code == 422


def test_decision_score_request_accepts_custom_weights():
    response = client.post(
        "/contracts/DEC-API-001/decision-score",
        json={
            "financial_score": 90,
            "risk_score": 70,
            "contract_value_score": 80,
            "weights": {
                "financial": 60,
                "risk": 25,
                "contract_value": 15,
            },
        },
    )

    # Contract does not exist, but request validation should succeed.
    assert response.status_code == 400
    assert response.json()["detail"] == "Contract not found"