from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

from backend.app.services.decision.combined_decision_service import (
    CombinedDecisionService,
)


def create_service():
    db = MagicMock()

    service = CombinedDecisionService(db)

    service.automatic_service = MagicMock()

    service.scoring_engine = MagicMock()

    service.decision_repository = MagicMock()

    return service


def configure_automatic_result(service):
    service.automatic_service.calculate_decision.return_value = {
        "contract_id": 101,
        "score": Decimal("60.9245"),
        "financial_score": Decimal("59.1458"),
        "risk_score": Decimal("63.8889"),
        "contract_value_score": None,
        "explanation": (
            "Financial score: 59.15/100. "
            "Risk score: 63.89/100."
        ),
        "decision": SimpleNamespace(
            score=Decimal("60.9245"),
            weights={
                "financial": Decimal("50"),
                "risk": Decimal("30"),
                "contract_value": Decimal("20"),
            },
        ),
    }


def configure_final_scoring(service):
    service.scoring_engine.calculate.return_value = (
        SimpleNamespace(
            score=Decimal("67.7951"),
            weights={
                "financial": Decimal("50"),
                "risk": Decimal("30"),
                "contract_value": Decimal("20"),
            },
        )
    )


def test_calculate_for_contract_combines_all_three_scores():
    service = create_service()

    configure_automatic_result(service)
    configure_final_scoring(service)

    service.decision_repository.get_by_contract_id.return_value = (
        None
    )

    saved_decision = SimpleNamespace(
        id=1,
        contract_id=101,
        score=Decimal("67.7951"),
    )

    service.decision_repository.create.return_value = (
        saved_decision
    )

    result = service.calculate_for_contract(
        contract_id=101,
        public_contract_id="CNT-TEST-001",
        contract_value_score=Decimal("100.0000"),
    )

    service.scoring_engine.calculate.assert_called_once()

    scoring_inputs = (
        service.scoring_engine.calculate.call_args.args[0]
    )

    assert (
        scoring_inputs.financial_score
        == Decimal("59.1458")
    )

    assert (
        scoring_inputs.risk_score
        == Decimal("63.8889")
    )

    assert (
        scoring_inputs.contract_value_score
        == Decimal("100.0000")
    )

    assert result["contract_id"] == "CNT-TEST-001"
    assert result["financial_score"] == Decimal("59.1458")
    assert result["risk_score"] == Decimal("63.8889")
    assert result["contract_value_score"] == Decimal(
        "100.0000"
    )
    assert result["score"] == Decimal("67.7951")


def test_calculate_for_contract_creates_decision_score():
    service = create_service()

    configure_automatic_result(service)
    configure_final_scoring(service)

    service.decision_repository.get_by_contract_id.return_value = (
        None
    )

    saved_decision = SimpleNamespace(
        id=2,
        contract_id=102,
        score=Decimal("67.7951"),
    )

    service.decision_repository.create.return_value = (
        saved_decision
    )

    result = service.calculate_for_contract(
        contract_id=102,
        public_contract_id="CNT-TEST-002",
        contract_value_score=Decimal("100.0000"),
    )

    service.decision_repository.create.assert_called_once()

    created_decision = (
        service.decision_repository.create.call_args.args[0]
    )

    assert created_decision.contract_id == 102
    assert created_decision.score == Decimal("67.7951")

    assert created_decision.financial_score == Decimal(
        "59.1458"
    )

    assert created_decision.risk_score == Decimal(
        "63.8889"
    )

    assert created_decision.contract_value_score == Decimal(
        "100.0000"
    )

    assert created_decision.financial_weight == Decimal(
        "50"
    )

    assert created_decision.risk_weight == Decimal(
        "30"
    )

    assert created_decision.contract_value_weight == Decimal(
        "20"
    )

    assert result["saved"] == saved_decision


def test_calculate_for_contract_updates_existing_decision():
    service = create_service()

    configure_automatic_result(service)
    configure_final_scoring(service)

    existing_decision = SimpleNamespace(
        id=3,
        contract_id=103,
        score=Decimal("60.0000"),
        financial_score=Decimal("50.0000"),
        risk_score=Decimal("55.0000"),
        contract_value_score=None,
        financial_weight=Decimal("50"),
        risk_weight=Decimal("30"),
        contract_value_weight=Decimal("20"),
        assumptions="Old",
        explanation="Old",
    )

    service.decision_repository.get_by_contract_id.return_value = (
        existing_decision
    )

    service.decision_repository.update.return_value = (
        existing_decision
    )

    result = service.calculate_for_contract(
        contract_id=103,
        public_contract_id="CNT-TEST-003",
        contract_value_score=Decimal("100.0000"),
    )

    service.decision_repository.create.assert_not_called()

    service.decision_repository.update.assert_called_once_with(
        existing_decision
    )

    assert existing_decision.score == Decimal(
        "67.7951"
    )

    assert existing_decision.financial_score == Decimal(
        "59.1458"
    )

    assert existing_decision.risk_score == Decimal(
        "63.8889"
    )

    assert existing_decision.contract_value_score == Decimal(
        "100.0000"
    )

    assert existing_decision.explanation is not None

    assert result["saved"] == existing_decision


def test_calculate_for_contract_explanation_contains_all_scores():
    service = create_service()

    configure_automatic_result(service)
    configure_final_scoring(service)

    service.decision_repository.get_by_contract_id.return_value = (
        None
    )

    service.decision_repository.create.return_value = (
        SimpleNamespace(
            id=4,
            contract_id=104,
        )
    )

    result = service.calculate_for_contract(
        contract_id=104,
        public_contract_id="CNT-TEST-004",
        contract_value_score=Decimal("100.0000"),
    )

    explanation = result["explanation"]

    assert "Financial score" in explanation
    assert "Risk score" in explanation
    assert "Contract value score" in explanation
    assert "Final score" in explanation