from decimal import Decimal

import pytest

from backend.app.services.decision.scoring import (
    DecisionInputs,
    DecisionScoringEngine,
    DecisionWeights,
)


def test_calculate_decision_score():
    inputs = DecisionInputs(
        financial_score=Decimal("80"),
        risk_score=Decimal("70"),
        contract_value_score=Decimal("90"),
    )

    weights = DecisionWeights(
        financial=Decimal("50"),
        risk=Decimal("30"),
        contract_value=Decimal("20"),
    )

    result = DecisionScoringEngine.calculate(
        inputs=inputs,
        weights=weights,
    )

    assert result.score == Decimal("79.0000")

    assert result.component_scores["financial"] == Decimal("80")
    assert result.component_scores["risk"] == Decimal("70")
    assert result.component_scores["contract_value"] == Decimal("90")

    assert result.weighted_scores["financial"] == Decimal("40.0000")
    assert result.weighted_scores["risk"] == Decimal("21.0000")
    assert result.weighted_scores["contract_value"] == Decimal("18.0000")


def test_default_weights():
    inputs = DecisionInputs(
        financial_score=Decimal("80"),
        risk_score=Decimal("70"),
        contract_value_score=Decimal("90"),
    )

    result = DecisionScoringEngine.calculate(
        inputs=inputs
    )

    assert result.score == Decimal("79.0000")


def test_weights_must_total_100():
    weights = DecisionWeights(
        financial=Decimal("40"),
        risk=Decimal("30"),
        contract_value=Decimal("20"),
    )

    with pytest.raises(
        ValueError,
        match="total 100",
    ):
        weights.validate()


def test_negative_weights_are_rejected():
    weights = DecisionWeights(
        financial=Decimal("-10"),
        risk=Decimal("50"),
        contract_value=Decimal("60"),
    )

    with pytest.raises(
        ValueError,
        match="cannot be negative",
    ):
        weights.validate()


def test_score_below_zero_is_rejected():
    inputs = DecisionInputs(
        financial_score=Decimal("-1"),
        risk_score=Decimal("70"),
        contract_value_score=Decimal("90"),
    )

    with pytest.raises(
        ValueError,
        match="between 0 and 100",
    ):
        DecisionScoringEngine.calculate(inputs)


def test_score_above_100_is_rejected():
    inputs = DecisionInputs(
        financial_score=Decimal("101"),
        risk_score=Decimal("70"),
        contract_value_score=Decimal("90"),
    )

    with pytest.raises(
        ValueError,
        match="between 0 and 100",
    ):
        DecisionScoringEngine.calculate(inputs)


def test_missing_component_is_not_treated_as_zero():
    inputs = DecisionInputs(
        financial_score=None,
        risk_score=Decimal("70"),
        contract_value_score=Decimal("90"),
    )

    result = DecisionScoringEngine.calculate(
        inputs=inputs
    )

    assert result.score == Decimal("78.0000")

    assert (
        result.component_scores["financial"]
        == "Insufficient data"
    )

    assert result.weighted_scores["financial"] == (
        "Insufficient data"
    )

    assert result.weighted_scores["risk"] == Decimal(
        "42.0000"
    )

    assert result.weighted_scores["contract_value"] == (
        Decimal("36.0000")
    )


def test_all_components_missing():
    inputs = DecisionInputs()

    result = DecisionScoringEngine.calculate(
        inputs=inputs
    )

    assert result.score == "Insufficient data"

    assert result.component_scores == {
        "financial": "Insufficient data",
        "risk": "Insufficient data",
        "contract_value": "Insufficient data",
    }

    assert result.weighted_scores == {
        "financial": "Insufficient data",
        "risk": "Insufficient data",
        "contract_value": "Insufficient data",
    }


def test_available_component_with_zero_weight_returns_insufficient_data():
    inputs = DecisionInputs(
        financial_score=Decimal("80"),
        risk_score=None,
        contract_value_score=None,
    )

    weights = DecisionWeights(
        financial=Decimal("0"),
        risk=Decimal("50"),
        contract_value=Decimal("50"),
    )

    result = DecisionScoringEngine.calculate(
        inputs=inputs,
        weights=weights,
    )

    assert result.score == "Insufficient data"

    assert result.component_scores["financial"] == Decimal(
        "80"
    )

    assert result.component_scores["risk"] == (
        "Insufficient data"
    )

    assert result.component_scores["contract_value"] == (
        "Insufficient data"
    )

    assert result.weighted_scores["financial"] == (
        "Insufficient data"
    )

    assert result.weighted_scores["risk"] == (
        "Insufficient data"
    )

    assert result.weighted_scores["contract_value"] == (
        "Insufficient data"
    )


def test_only_financial_component():
    inputs = DecisionInputs(
        financial_score=Decimal("85"),
        risk_score=None,
        contract_value_score=None,
    )

    result = DecisionScoringEngine.calculate(
        inputs=inputs
    )

    assert result.score == Decimal("85.0000")

    assert result.component_scores["financial"] == (
        Decimal("85")
    )

    assert result.component_scores["risk"] == (
        "Insufficient data"
    )

    assert result.component_scores["contract_value"] == (
        "Insufficient data"
    )


def test_only_risk_component():
    inputs = DecisionInputs(
        financial_score=None,
        risk_score=Decimal("75"),
        contract_value_score=None,
    )

    result = DecisionScoringEngine.calculate(
        inputs=inputs
    )

    assert result.score == Decimal("75.0000")


def test_only_contract_value_component():
    inputs = DecisionInputs(
        financial_score=None,
        risk_score=None,
        contract_value_score=Decimal("95"),
    )

    result = DecisionScoringEngine.calculate(
        inputs=inputs
    )

    assert result.score == Decimal("95.0000")


def test_scores_accept_numeric_values():
    inputs = DecisionInputs(
        financial_score=80,
        risk_score=70,
        contract_value_score=90,
    )

    result = DecisionScoringEngine.calculate(
        inputs=inputs
    )

    assert result.score == Decimal("79.0000")


def test_invalid_score_value_is_rejected():
    inputs = DecisionInputs(
        financial_score="invalid",
        risk_score=Decimal("70"),
        contract_value_score=Decimal("90"),
    )

    with pytest.raises(
        ValueError,
        match="Invalid decision score",
    ):
        DecisionScoringEngine.calculate(inputs)


def test_explanation_is_generated():
    inputs = DecisionInputs(
        financial_score=Decimal("80"),
        risk_score=Decimal("70"),
        contract_value_score=Decimal("90"),
    )

    result = DecisionScoringEngine.calculate(
        inputs=inputs
    )

    assert len(result.explanation) > 0

    assert any(
        "Financial performance score: 80"
        in item
        for item in result.explanation
    )

    assert any(
        "Risk score: 70"
        in item
        for item in result.explanation
    )

    assert any(
        "Contract value score: 90"
        in item
        for item in result.explanation
    )

    assert any(
        "Final decision score: 79.0000 out of 100."
        in item
        for item in result.explanation
    )


def test_custom_weights_change_score():
    inputs = DecisionInputs(
        financial_score=Decimal("90"),
        risk_score=Decimal("50"),
        contract_value_score=Decimal("50"),
    )

    weights = DecisionWeights(
        financial=Decimal("70"),
        risk=Decimal("20"),
        contract_value=Decimal("10"),
    )

    result = DecisionScoringEngine.calculate(
        inputs=inputs,
        weights=weights,
    )

    assert result.score == Decimal("78.0000")


def test_weights_are_returned_in_result():
    weights = DecisionWeights(
        financial=Decimal("60"),
        risk=Decimal("25"),
        contract_value=Decimal("15"),
    )

    inputs = DecisionInputs(
        financial_score=Decimal("80"),
        risk_score=Decimal("80"),
        contract_value_score=Decimal("80"),
    )

    result = DecisionScoringEngine.calculate(
        inputs=inputs,
        weights=weights,
    )

    assert result.weights == {
        "financial": Decimal("60"),
        "risk": Decimal("25"),
        "contract_value": Decimal("15"),
    }