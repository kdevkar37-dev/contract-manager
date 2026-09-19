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

    service = AutomaticDecisionScoringService(
        financial_repository=financial_repository,
        risk_repository=risk_repository,
        decision_repository=decision_repository,
    )

    return (
        service,
        financial_repository,
        risk_repository,
        decision_repository,
    )


def test_financial_score_is_calculated_from_margin_and_roi():
    (
        service,
        financial_repository,
        risk_repository,
        _,
    ) = create_service()

    financial_repository.get_by_contract_id.return_value = (
        SimpleNamespace(
            profit_margin=Decimal("80"),
            roi=Decimal("30"),
        )
    )

    risk_repository.get_by_contract_id.return_value = []

    result = service.build_inputs("CNT-TEST-001")

    # 80 * 60% + 30 * 40% = 60
    assert result.financial_score == Decimal("60.0000")


def test_financial_score_is_capped_at_100():
    (
        service,
        financial_repository,
        risk_repository,
        _,
    ) = create_service()

    financial_repository.get_by_contract_id.return_value = (
        SimpleNamespace(
            profit_margin=Decimal("120"),
            roi=Decimal("150"),
        )
    )

    risk_repository.get_by_contract_id.return_value = []

    result = service.build_inputs("CNT-TEST-002")

    assert result.financial_score == Decimal("100.0000")


def test_risk_score_calculates_from_severity():
    (
        service,
        financial_repository,
        risk_repository,
        _,
    ) = create_service()

    financial_repository.get_by_contract_id.return_value = None

    risk_repository.get_by_contract_id.return_value = [
        SimpleNamespace(severity="high"),
        SimpleNamespace(severity="medium"),
    ]

    result = service.build_inputs("CNT-TEST-003")

    # high = 50 penalty
    # medium = 25 penalty
    # average penalty = 37.5
    # risk score = 100 - 37.5 = 62.5
    assert result.risk_score == Decimal("62.5000")


def test_critical_risk_produces_low_risk_score():
    (
        service,
        financial_repository,
        risk_repository,
        _,
    ) = create_service()

    financial_repository.get_by_contract_id.return_value = None

    risk_repository.get_by_contract_id.return_value = [
        SimpleNamespace(severity="critical"),
    ]

    result = service.build_inputs("CNT-TEST-004")

    assert result.risk_score == Decimal("20.0000")


def test_missing_financial_analysis_returns_no_financial_score():
    (
        service,
        financial_repository,
        risk_repository,
        _,
    ) = create_service()

    financial_repository.get_by_contract_id.return_value = None
    risk_repository.get_by_contract_id.return_value = []

    result = service.build_inputs("CNT-TEST-005")

    assert result.financial_score is None
    assert result.risk_score is None
    assert result.contract_value_score is None


def test_contract_value_score_is_deferred():
    (
        service,
        financial_repository,
        risk_repository,
        _,
    ) = create_service()

    financial_repository.get_by_contract_id.return_value = (
        SimpleNamespace(
            profit_margin=Decimal("80"),
            roi=Decimal("30"),
        )
    )

    risk_repository.get_by_contract_id.return_value = [
        SimpleNamespace(severity="low"),
    ]

    result = service.build_inputs("CNT-TEST-006")

    assert result.contract_value_score is None


def test_unknown_risk_severity_is_ignored():
    (
        service,
        financial_repository,
        risk_repository,
        _,
    ) = create_service()

    financial_repository.get_by_contract_id.return_value = None

    risk_repository.get_by_contract_id.return_value = [
        SimpleNamespace(severity="unknown"),
        SimpleNamespace(severity="high"),
    ]

    result = service.build_inputs("CNT-TEST-007")

    assert result.risk_score == Decimal("50.0000")


def test_automatic_decision_uses_existing_scoring_engine():
    (
        service,
        financial_repository,
        risk_repository,
        _,
    ) = create_service()

    financial_repository.get_by_contract_id.return_value = (
        SimpleNamespace(
            profit_margin=Decimal("80"),
            roi=Decimal("30"),
        )
    )

    risk_repository.get_by_contract_id.return_value = [
        SimpleNamespace(severity="low"),
    ]

    result = service.calculate_decision("CNT-TEST-008")

    assert result["contract_id"] == "CNT-TEST-008"
    assert result["financial_score"] == Decimal("60.0000")
    assert result["risk_score"] == Decimal("90.0000")
    assert result["contract_value_score"] is None
    assert result["score"] is not None