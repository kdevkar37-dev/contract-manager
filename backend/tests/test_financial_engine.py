from decimal import Decimal

import pytest

from backend.app.services.financial.engine import (
    FinancialCalculationEngine,
    FinancialInputs,
    INSUFFICIENT_DATA,
)


def test_financial_calculations():
    inputs = FinancialInputs(
        revenue=Decimal("100000"),
        initial_investment=Decimal("20000"),
        fixed_costs=Decimal("30000"),
        variable_costs=Decimal("20000"),
        contribution_margin=Decimal("50000"),
    )

    result = FinancialCalculationEngine.calculate(inputs)

    assert result.total_cost == Decimal("50000")
    assert result.profit == Decimal("50000")
    assert result.roi == Decimal("250")
    assert result.profit_margin == Decimal("50")
    assert result.break_even == Decimal("0.6")


def test_missing_data_returns_insufficient_data():
    inputs = FinancialInputs(
        revenue=Decimal("100000"),
        fixed_costs=Decimal("30000"),
    )

    result = FinancialCalculationEngine.calculate(inputs)

    assert result.total_cost == INSUFFICIENT_DATA
    assert result.profit == INSUFFICIENT_DATA
    assert result.roi == INSUFFICIENT_DATA
    assert result.profit_margin == INSUFFICIENT_DATA
    assert result.break_even == INSUFFICIENT_DATA


def test_zero_investment_returns_insufficient_roi():
    inputs = FinancialInputs(
        revenue=Decimal("100000"),
        initial_investment=Decimal("0"),
        fixed_costs=Decimal("30000"),
        variable_costs=Decimal("20000"),
    )

    result = FinancialCalculationEngine.calculate(inputs)

    assert result.profit == Decimal("50000")
    assert result.roi == INSUFFICIENT_DATA


def test_zero_revenue_returns_insufficient_margin():
    inputs = FinancialInputs(
        revenue=Decimal("0"),
        fixed_costs=Decimal("30000"),
        variable_costs=Decimal("20000"),
    )

    result = FinancialCalculationEngine.calculate(inputs)

    assert result.profit == Decimal("-50000")
    assert result.profit_margin == INSUFFICIENT_DATA


def test_zero_contribution_margin_returns_insufficient_break_even():
    inputs = FinancialInputs(
        fixed_costs=Decimal("30000"),
        contribution_margin=Decimal("0"),
    )

    result = FinancialCalculationEngine.calculate(inputs)

    assert result.break_even == INSUFFICIENT_DATA


@pytest.mark.parametrize(
    "field_name",
    [
        "revenue",
        "initial_investment",
        "fixed_costs",
        "variable_costs",
        "contribution_margin",
    ],
)
def test_negative_financial_values_are_rejected(field_name):
    inputs = FinancialInputs(
        revenue=Decimal("100000"),
        fixed_costs=Decimal("30000"),
        variable_costs=Decimal("20000"),
        contribution_margin=Decimal("50000"),
    )

    setattr(inputs, field_name, Decimal("-1"))

    with pytest.raises(ValueError):
        FinancialCalculationEngine.calculate(inputs)