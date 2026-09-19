from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

from backend.app.services.decision.automatic_scoring import (
    AutomaticDecisionScoringService,
)


def create_service():
    financial_repository = MagicMock()
    risk_repository = MagicMock()
    decision_repository = MagicMock()
    scoring_engine = MagicMock()

    service = AutomaticDecisionScoringService(
        financial_repository=financial_repository,
        risk_repository=risk_repository,
        decision_repository=decision_repository,
        scoring_engine=scoring_engine,
    )

    return (
        service,
        financial_repository,
        risk_repository,
        decision_repository,
        scoring_engine,
    )


def configure_analysis_repositories(
    financial_repository,
    risk_repository,
):
    financial_repository.get_by_contract_id.return_value = (
        SimpleNamespace(
            profit_margin=Decimal("80"),
            roi=Decimal("30"),
        )
    )

    risk_repository.get_by_contract_id.return_value = [
        SimpleNamespace(severity="low"),
        SimpleNamespace(severity="medium"),
    ]


def configure_scoring_engine(scoring_engine):
    scoring_engine.calculate.return_value = SimpleNamespace(
        score=Decimal("75.0000"),
        weights={
            "financial": Decimal("50"),
            "risk": Decimal("30"),
            "contract_value": Decimal("20"),
        },
    )


def test_calculate_and_persist_creates_new_decision_score():
    (
        service,
        financial_repository,
        risk_repository,
        decision_repository,
        scoring_engine,
    ) = create_service()

    configure_analysis_repositories(
        financial_repository,
        risk_repository,
    )

    configure_scoring_engine(scoring_engine)

    decision_repository.get_by_contract_id.return_value = None

    saved_decision = SimpleNamespace(
        id=1,
        contract_id=101,
        score=Decimal("75.0000"),
    )

    decision_repository.create.return_value = saved_decision

    result = service.calculate_and_persist(101)

    decision_repository.create.assert_called_once()

    created_decision = (
        decision_repository.create.call_args.args[0]
    )

    assert created_decision.contract_id == 101
    assert created_decision.score == Decimal("75.0000")
    assert created_decision.financial_score is not None
    assert created_decision.risk_score is not None
    assert created_decision.contract_value_score is None

    assert created_decision.financial_weight == Decimal("50")
    assert created_decision.risk_weight == Decimal("30")
    assert created_decision.contract_value_weight == Decimal("20")

    assert result["saved"] == saved_decision


def test_calculate_and_persist_updates_existing_decision_score():
    (
        service,
        financial_repository,
        risk_repository,
        decision_repository,
        scoring_engine,
    ) = create_service()

    configure_analysis_repositories(
        financial_repository,
        risk_repository,
    )

    configure_scoring_engine(scoring_engine)

    existing_decision = SimpleNamespace(
        id=10,
        contract_id=102,
        score=Decimal("50.0000"),
        financial_score=Decimal("40.0000"),
        risk_score=Decimal("50.0000"),
        contract_value_score=None,
        financial_weight=Decimal("50"),
        risk_weight=Decimal("30"),
        contract_value_weight=Decimal("20"),
        assumptions="Old assumptions",
        explanation="Old explanation",
    )

    decision_repository.get_by_contract_id.return_value = (
        existing_decision
    )

    updated_decision = SimpleNamespace(
        id=10,
        contract_id=102,
        score=Decimal("75.0000"),
    )

    decision_repository.update.return_value = (
        updated_decision
    )

    result = service.calculate_and_persist(102)

    decision_repository.create.assert_not_called()

    decision_repository.update.assert_called_once_with(
        existing_decision
    )

    assert existing_decision.score == Decimal("75.0000")

    assert existing_decision.financial_weight == Decimal(
        "50"
    )

    assert existing_decision.risk_weight == Decimal(
        "30"
    )

    assert existing_decision.contract_value_weight == Decimal(
        "20"
    )

    assert existing_decision.assumptions is not None
    assert existing_decision.explanation is not None

    assert result["saved"] == updated_decision


def test_existing_decision_is_not_duplicated():
    (
        service,
        financial_repository,
        risk_repository,
        decision_repository,
        scoring_engine,
    ) = create_service()

    configure_analysis_repositories(
        financial_repository,
        risk_repository,
    )

    configure_scoring_engine(scoring_engine)

    existing_decision = SimpleNamespace(
        id=20,
        contract_id=103,
        score=Decimal("60.0000"),
        financial_score=Decimal("55.0000"),
        risk_score=Decimal("65.0000"),
        contract_value_score=None,
        financial_weight=Decimal("50"),
        risk_weight=Decimal("30"),
        contract_value_weight=Decimal("20"),
        assumptions="Existing",
        explanation="Existing",
    )

    decision_repository.get_by_contract_id.return_value = (
        existing_decision
    )

    decision_repository.update.return_value = (
        existing_decision
    )

    service.calculate_and_persist(103)

    decision_repository.create.assert_not_called()
    decision_repository.update.assert_called_once()


def test_persisted_decision_contains_explanation():
    (
        service,
        financial_repository,
        risk_repository,
        decision_repository,
        scoring_engine,
    ) = create_service()

    configure_analysis_repositories(
        financial_repository,
        risk_repository,
    )

    configure_scoring_engine(scoring_engine)

    decision_repository.get_by_contract_id.return_value = None

    decision_repository.create.return_value = SimpleNamespace(
        id=30,
        contract_id=104,
    )

    result = service.calculate_and_persist(104)

    created_decision = (
        decision_repository.create.call_args.args[0]
    )

    assert created_decision.assumptions
    assert created_decision.explanation

    assert (
        "Financial score"
        in created_decision.explanation
    )

    assert (
        "Risk score"
        in created_decision.explanation
    )

    assert result["explanation"] == (
        created_decision.explanation
    )