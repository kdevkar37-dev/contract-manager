from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any


INSUFFICIENT_DATA = "Insufficient data"


@dataclass
class FinancialInputs:
    revenue: Decimal | None = None
    initial_investment: Decimal | None = None
    fixed_costs: Decimal | None = None
    variable_costs: Decimal | None = None
    contribution_margin: Decimal | None = None

    assumptions: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)


@dataclass
class FinancialAnalysis:
    revenue: Decimal | str
    initial_investment: Decimal | str
    fixed_costs: Decimal | str
    variable_costs: Decimal | str
    total_cost: Decimal | str
    profit: Decimal | str
    roi: Decimal | str
    profit_margin: Decimal | str
    break_even: Decimal | str

    assumptions: list[str]
    sources: list[str]


class FinancialCalculationEngine:
    """
    Deterministic financial calculation engine.

    This service performs calculations only.
    It does not use an LLM and does not retrieve data.
    """

    @staticmethod
    def to_decimal(value: Any) -> Decimal | None:
        if value is None:
            return None

        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            raise ValueError(f"Invalid financial value: {value}")

    @staticmethod
    def validate_non_negative(
        value: Decimal | None,
        field_name: str,
    ) -> None:
        if value is not None and value < 0:
            raise ValueError(
                f"{field_name} cannot be negative."
            )

    @staticmethod
    def calculate(
        inputs: FinancialInputs,
    ) -> FinancialAnalysis:

        engine = FinancialCalculationEngine()

        revenue = engine.to_decimal(inputs.revenue)
        investment = engine.to_decimal(
            inputs.initial_investment
        )
        fixed_costs = engine.to_decimal(
            inputs.fixed_costs
        )
        variable_costs = engine.to_decimal(
            inputs.variable_costs
        )
        contribution_margin = engine.to_decimal(
            inputs.contribution_margin
        )

        engine.validate_non_negative(
            revenue,
            "Revenue",
        )
        engine.validate_non_negative(
            investment,
            "Initial investment",
        )
        engine.validate_non_negative(
            fixed_costs,
            "Fixed costs",
        )
        engine.validate_non_negative(
            variable_costs,
            "Variable costs",
        )
        engine.validate_non_negative(
            contribution_margin,
            "Contribution margin",
        )

        total_cost = (
            fixed_costs + variable_costs
            if fixed_costs is not None
            and variable_costs is not None
            else INSUFFICIENT_DATA
        )

        profit = (
            revenue - total_cost
            if revenue is not None
            and isinstance(total_cost, Decimal)
            else INSUFFICIENT_DATA
        )

        roi = (
            (profit / investment) * Decimal("100")
            if isinstance(profit, Decimal)
            and investment is not None
            and investment != 0
            else INSUFFICIENT_DATA
        )

        profit_margin = (
            (profit / revenue) * Decimal("100")
            if isinstance(profit, Decimal)
            and revenue is not None
            and revenue != 0
            else INSUFFICIENT_DATA
        )

        break_even = (
            fixed_costs / contribution_margin
            if fixed_costs is not None
            and contribution_margin is not None
            and contribution_margin != 0
            else INSUFFICIENT_DATA
        )

        return FinancialAnalysis(
            revenue=(
                revenue
                if revenue is not None
                else INSUFFICIENT_DATA
            ),
            initial_investment=(
                investment
                if investment is not None
                else INSUFFICIENT_DATA
            ),
            fixed_costs=(
                fixed_costs
                if fixed_costs is not None
                else INSUFFICIENT_DATA
            ),
            variable_costs=(
                variable_costs
                if variable_costs is not None
                else INSUFFICIENT_DATA
            ),
            total_cost=total_cost,
            profit=profit,
            roi=roi,
            profit_margin=profit_margin,
            break_even=break_even,
            assumptions=list(inputs.assumptions),
            sources=list(inputs.sources),
        )