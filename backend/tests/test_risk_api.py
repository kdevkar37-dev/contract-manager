from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_get_contract_risks():
    mock_risk = MagicMock()

    mock_risk.id = 1
    mock_risk.risk_type = "payment"
    mock_risk.severity = "high"
    mock_risk.title = "Delayed payment risk"
    mock_risk.description = "Payment may be delayed."
    mock_risk.evidence = "Payment shall be made within 90 days."
    mock_risk.source = "Section 5"
    mock_risk.confidence = "0.90"

    mock_service = MagicMock()

    mock_service.get_risks.return_value = [
        mock_risk
    ]

    with patch(
        "backend.app.api.risk.RiskAnalysisService",
        return_value=mock_service,
    ):
        response = client.get(
            "/contracts/CNT-001/risks"
        )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert data[0]["id"] == 1
    assert data[0]["contract_id"] == "CNT-001"
    assert data[0]["risk_type"] == "payment"
    assert data[0]["severity"] == "high"
    assert data[0]["title"] == "Delayed payment risk"
    assert data[0]["description"] == "Payment may be delayed."
    assert (
        data[0]["evidence"]
        == "Payment shall be made within 90 days."
    )
    assert data[0]["source"] == "Section 5"
    assert data[0]["confidence"] == "0.90"


def test_get_contract_risks_returns_empty_list():
    mock_service = MagicMock()

    mock_service.get_risks.return_value = []

    with patch(
        "backend.app.api.risk.RiskAnalysisService",
        return_value=mock_service,
    ):
        response = client.get(
            "/contracts/CNT-001/risks"
        )

    assert response.status_code == 200

    assert response.json() == []


def test_get_contract_risks_contract_not_found():
    mock_service = MagicMock()

    mock_service.get_risks.side_effect = ValueError(
        "Contract not found"
    )

    with patch(
        "backend.app.api.risk.RiskAnalysisService",
        return_value=mock_service,
    ):
        response = client.get(
            "/contracts/CNT-404/risks"
        )

    assert response.status_code == 404

    assert response.json()["detail"] == "Contract not found"