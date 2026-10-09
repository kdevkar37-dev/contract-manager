from decimal import Decimal
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api import combined_decision


client = TestClient(app)


def test_combined_decision_api_success(monkeypatch):
    mock_service = MagicMock()

    mock_service.calculate_for_all_contracts.return_value = [
        {
            "contract_id": "CNT-001",
            "contract_value": Decimal("500000"),
            "financial_score": Decimal("85.0000"),
            "risk_score": Decimal("80.0000"),
            "contract_value_score": Decimal("90.0000"),
            "score": Decimal("84.0000"),
            "rank": 1,
            "explanation": (
                "Strong financial performance with acceptable risk."
            ),
        }
    ]

    monkeypatch.setattr(
        combined_decision,
        "CombinedDecisionService",
        lambda db: mock_service,
    )

    response = client.post(
        "/contracts/decision/automatic"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 1
    assert len(data["contracts"]) == 1

    contract = data["contracts"][0]

    assert contract["contract_id"] == "CNT-001"
    assert Decimal(str(contract["contract_value"])) == Decimal("500000")
    assert Decimal(str(contract["financial_score"])) == Decimal("85.0000")
    assert Decimal(str(contract["risk_score"])) == Decimal("80.0000")
    assert Decimal(str(contract["contract_value_score"])) == Decimal("90.0000")
    assert Decimal(str(contract["score"])) == Decimal("84.0000")
    assert contract["rank"] == 1

    mock_service.calculate_for_all_contracts.assert_called_once()


def test_combined_decision_api_handles_no_eligible_contracts(
    monkeypatch,
):
    mock_service = MagicMock()

    mock_service.calculate_for_all_contracts.return_value = []

    monkeypatch.setattr(
        combined_decision,
        "CombinedDecisionService",
        lambda db: mock_service,
    )

    response = client.post(
        "/contracts/decision/automatic"
    )

    assert response.status_code == 200

    assert response.json() == {
        "count": 0,
        "contracts": [],
    }

    mock_service.calculate_for_all_contracts.assert_called_once()


def test_combined_decision_api_handles_service_error(
    monkeypatch,
):
    mock_service = MagicMock()

    mock_service.calculate_for_all_contracts.side_effect = RuntimeError(
        "Decision calculation failed"
    )

    monkeypatch.setattr(
        combined_decision,
        "CombinedDecisionService",
        lambda db: mock_service,
    )

    response = client.post(
        "/contracts/decision/automatic"
    )

    assert response.status_code == 500

    assert response.json() == {
        "detail": (
            "Combined decision calculation failed "
            "due to an internal server error."
        )
    }

    mock_service.calculate_for_all_contracts.assert_called_once()