from decimal import Decimal
from unittest.mock import MagicMock

from backend.app.services.decision.decision_workflow import (
    DecisionAnalysisWorkflow,
)


def test_workflow_runs_complete_decision_analysis():
    db = MagicMock()

    workflow = DecisionAnalysisWorkflow(db)

    workflow.combined_decision_service = MagicMock()
    workflow.recommendation_service = MagicMock()

    workflow.combined_decision_service.calculate_for_all_contracts.return_value = [
        {
            "contract_id": "CNT-A",
            "score": Decimal("80.0000"),
        },
        {
            "contract_id": "CNT-B",
            "score": Decimal("70.0000"),
        },
    ]

    workflow.recommendation_service.recommend_all.return_value = [
        {
            "contract_id": "CNT-A",
            "final_score": Decimal("80.0000"),
            "rank": 1,
        },
        {
            "contract_id": "CNT-B",
            "final_score": Decimal("70.0000"),
            "rank": 2,
        },
    ]

    result = workflow.run()

    workflow.combined_decision_service.calculate_for_all_contracts.assert_called_once()

    workflow.recommendation_service.recommend_all.assert_called_once()

    assert result["contracts_processed"] == 2
    assert result["recommendations_count"] == 2

    assert (
        result["top_recommendation"]["contract_id"]
        == "CNT-A"
    )

    assert (
        result["top_recommendation"]["rank"]
        == 1
    )


def test_workflow_handles_no_contracts():
    db = MagicMock()

    workflow = DecisionAnalysisWorkflow(db)

    workflow.combined_decision_service = MagicMock()
    workflow.recommendation_service = MagicMock()

    workflow.combined_decision_service.calculate_for_all_contracts.return_value = []

    workflow.recommendation_service.recommend_all.return_value = []

    result = workflow.run()

    assert result["contracts_processed"] == 0
    assert result["recommendations_count"] == 0
    assert result["top_recommendation"] is None
    assert result["recommendations"] == []


def test_workflow_uses_recommendations_after_scoring():
    db = MagicMock()

    workflow = DecisionAnalysisWorkflow(db)

    workflow.combined_decision_service = MagicMock()
    workflow.recommendation_service = MagicMock()

    workflow.combined_decision_service.calculate_for_all_contracts.return_value = [
        {
            "contract_id": "CNT-A",
            "score": Decimal("85.0000"),
        }
    ]

    workflow.recommendation_service.recommend_all.return_value = [
        {
            "contract_id": "CNT-A",
            "final_score": Decimal("85.0000"),
            "rank": 1,
        }
    ]

    result = workflow.run()

    assert result["top_recommendation"]["final_score"] == (
        Decimal("85.0000")
    )

    workflow.combined_decision_service.calculate_for_all_contracts.assert_called_once()

    workflow.recommendation_service.recommend_all.assert_called_once()