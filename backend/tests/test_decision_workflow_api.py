from decimal import Decimal
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api import decision_workflow


client = TestClient(app)


def test_decision_workflow_api_success(monkeypatch):
    mock_workflow = MagicMock()

    mock_workflow.run.return_value = {
        "contracts_processed": 1,
        "recommendations_count": 1,
        "top_recommendation": {
            "contract_id": "CNT-TEST-001",
            "final_score": Decimal("85.0000"),
            "rank": 1,
        },
        "recommendations": [
            {
                "contract_id": "CNT-TEST-001",
                "final_score": Decimal("85.0000"),
                "rank": 1,
            }
        ],
    }

    monkeypatch.setattr(
        decision_workflow,
        "DecisionAnalysisWorkflow",
        lambda db: mock_workflow,
    )

    response = client.post("/contracts/decision/workflow")

    assert response.status_code == 200

    data = response.json()

    assert data["contracts_processed"] == 1
    assert data["recommendations_count"] == 1
    assert data["top_recommendation"]["contract_id"] == "CNT-TEST-001"
    assert data["top_recommendation"]["rank"] == 1

    mock_workflow.run.assert_called_once()


def test_decision_workflow_api_handles_no_contracts(monkeypatch):
    mock_workflow = MagicMock()

    mock_workflow.run.return_value = {
        "contracts_processed": 0,
        "recommendations_count": 0,
        "top_recommendation": None,
        "recommendations": [],
    }

    monkeypatch.setattr(
        decision_workflow,
        "DecisionAnalysisWorkflow",
        lambda db: mock_workflow,
    )

    response = client.post("/contracts/decision/workflow")

    assert response.status_code == 200

    data = response.json()

    assert data["contracts_processed"] == 0
    assert data["recommendations_count"] == 0
    assert data["top_recommendation"] is None
    assert data["recommendations"] == []

    mock_workflow.run.assert_called_once()