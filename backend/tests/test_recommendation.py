from decimal import Decimal

from backend.app.services.decision.recommendation import (
    ContractDecisionResult,
    ContractRecommendationService,
)


def test_recommendations_are_sorted_by_final_score():
    service = ContractRecommendationService()

    contracts = [
        ContractDecisionResult(
            contract_id="CNT-A",
            final_score=Decimal("68.0000"),
            financial_score=Decimal("60.0000"),
            risk_score=Decimal("70.0000"),
            contract_value_score=Decimal("80.0000"),
        ),
        ContractDecisionResult(
            contract_id="CNT-B",
            final_score=Decimal("85.0000"),
            financial_score=Decimal("90.0000"),
            risk_score=Decimal("80.0000"),
            contract_value_score=Decimal("85.0000"),
        ),
        ContractDecisionResult(
            contract_id="CNT-C",
            final_score=Decimal("72.0000"),
            financial_score=Decimal("70.0000"),
            risk_score=Decimal("75.0000"),
            contract_value_score=Decimal("70.0000"),
        ),
    ]

    results = service.recommend(contracts)

    assert results[0].contract_id == "CNT-B"
    assert results[1].contract_id == "CNT-C"
    assert results[2].contract_id == "CNT-A"


def test_highest_score_gets_rank_one():
    service = ContractRecommendationService()

    contracts = [
        ContractDecisionResult(
            contract_id="CNT-A",
            final_score=Decimal("70.0000"),
            financial_score=None,
            risk_score=None,
            contract_value_score=None,
        ),
        ContractDecisionResult(
            contract_id="CNT-B",
            final_score=Decimal("90.0000"),
            financial_score=None,
            risk_score=None,
            contract_value_score=None,
        ),
    ]

    results = service.recommend(contracts)

    assert results[0].contract_id == "CNT-B"
    assert results[0].rank == 1
    assert results[1].rank == 2


def test_equal_scores_receive_same_rank():
    service = ContractRecommendationService()

    contracts = [
        ContractDecisionResult(
            contract_id="CNT-A",
            final_score=Decimal("80.0000"),
            financial_score=None,
            risk_score=None,
            contract_value_score=None,
        ),
        ContractDecisionResult(
            contract_id="CNT-B",
            final_score=Decimal("80.0000"),
            financial_score=None,
            risk_score=None,
            contract_value_score=None,
        ),
        ContractDecisionResult(
            contract_id="CNT-C",
            final_score=Decimal("70.0000"),
            financial_score=None,
            risk_score=None,
            contract_value_score=None,
        ),
    ]

    results = service.recommend(contracts)

    assert results[0].rank == 1
    assert results[1].rank == 1
    assert results[2].rank == 3


def test_contract_without_final_score_is_excluded():
    service = ContractRecommendationService()

    contracts = [
        ContractDecisionResult(
            contract_id="CNT-A",
            final_score=Decimal("80.0000"),
            financial_score=None,
            risk_score=None,
            contract_value_score=None,
        ),
        ContractDecisionResult(
            contract_id="CNT-B",
            final_score=None,
            financial_score=None,
            risk_score=None,
            contract_value_score=None,
        ),
    ]

    results = service.recommend(contracts)

    assert len(results) == 1
    assert results[0].contract_id == "CNT-A"


def test_empty_contract_list_returns_empty_result():
    service = ContractRecommendationService()

    assert service.recommend([]) == []


def test_explanation_contains_available_scores():
    service = ContractRecommendationService()

    contracts = [
        ContractDecisionResult(
            contract_id="CNT-A",
            final_score=Decimal("75.0000"),
            financial_score=Decimal("70.0000"),
            risk_score=Decimal("65.0000"),
            contract_value_score=Decimal("90.0000"),
        )
    ]

    results = service.recommend(contracts)

    explanation = results[0].explanation

    assert "Final decision score" in explanation
    assert "Financial score" in explanation
    assert "Risk score" in explanation
    assert "Contract value score" in explanation