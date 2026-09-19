from decimal import Decimal

from backend.app.models.contract import Contract
from backend.app.models.decision_score import DecisionScore
from backend.app.repositories.decision_score import DecisionScoreRepository


def test_create_and_get_decision_score(db_session):
    contract = Contract(
        contract_id="DEC-001",
        name="Decision Test Contract",
        source_type="manual",
        status="completed",
    )

    db_session.add(contract)
    db_session.commit()
    db_session.refresh(contract)

    repository = DecisionScoreRepository(db_session)

    score = DecisionScore(
        contract_id=contract.id,
        score=Decimal("82.5000"),
        financial_score=Decimal("90"),
        risk_score=Decimal("70"),
        contract_value_score=Decimal("80"),
        financial_weight=Decimal("50"),
        risk_weight=Decimal("30"),
        contract_value_weight=Decimal("20"),
        assumptions='["Scores normalized to 0-100"]',
        explanation='["Financial score contributed strongly"]',
    )

    created = repository.create(score)

    assert created.id is not None
    assert created.contract_id == contract.id
    assert created.score == Decimal("82.5000")

    fetched = repository.get_by_contract_id(contract.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.score == Decimal("82.5000")


def test_update_decision_score(db_session):
    contract = Contract(
        contract_id="DEC-002",
        name="Decision Update Contract",
        source_type="manual",
        status="completed",
    )

    db_session.add(contract)
    db_session.commit()
    db_session.refresh(contract)

    repository = DecisionScoreRepository(db_session)

    score = DecisionScore(
        contract_id=contract.id,
        score=Decimal("70"),
        financial_weight=Decimal("50"),
        risk_weight=Decimal("30"),
        contract_value_weight=Decimal("20"),
    )

    repository.create(score)

    score.score = Decimal("85.0000")

    updated = repository.update(score)

    assert updated.score == Decimal("85.0000")


def test_get_missing_decision_score_returns_none(db_session):
    repository = DecisionScoreRepository(db_session)

    result = repository.get_by_contract_id(999999)

    assert result is None