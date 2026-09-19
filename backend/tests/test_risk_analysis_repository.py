from unittest.mock import MagicMock

from backend.app.models.risk_analysis import RiskAnalysis
from backend.app.repositories.risk_analysis import RiskAnalysisRepository


def test_get_by_contract_id():
    db = MagicMock()

    risk = RiskAnalysis(
        contract_id=1,
        risk_type="financial",
        severity="high",
        title="High financial exposure",
        description="Contract has significant financial exposure.",
    )

    db.execute.return_value.scalars.return_value.all.return_value = [
        risk
    ]

    repository = RiskAnalysisRepository(db)

    result = repository.get_by_contract_id(1)

    assert len(result) == 1
    assert result[0].title == "High financial exposure"


def test_create():
    db = MagicMock()

    risk = RiskAnalysis(
        contract_id=1,
        risk_type="payment",
        severity="medium",
        title="Payment delay risk",
        description="Payment terms may create cash-flow risk.",
    )

    repository = RiskAnalysisRepository(db)

    result = repository.create(risk)

    assert result is risk
    db.add.assert_called_once_with(risk)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(risk)


def test_create_many():
    db = MagicMock()

    risks = [
        RiskAnalysis(
            contract_id=1,
            risk_type="financial",
            severity="high",
            title="Financial risk",
            description="Financial exposure identified.",
        ),
        RiskAnalysis(
            contract_id=1,
            risk_type="payment",
            severity="medium",
            title="Payment risk",
            description="Payment terms require review.",
        ),
    ]

    repository = RiskAnalysisRepository(db)

    result = repository.create_many(risks)

    assert result == risks
    db.add_all.assert_called_once_with(risks)
    db.commit.assert_called_once()
    assert db.refresh.call_count == 2


def test_create_many_with_empty_list():
    db = MagicMock()

    repository = RiskAnalysisRepository(db)

    result = repository.create_many([])

    assert result == []
    db.add_all.assert_not_called()
    db.commit.assert_not_called()


def test_delete_by_contract_id():
    db = MagicMock()

    repository = RiskAnalysisRepository(db)

    repository.delete_by_contract_id(1)

    db.execute.assert_called_once()
    db.commit.assert_called_once()