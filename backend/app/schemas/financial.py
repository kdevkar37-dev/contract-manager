from decimal import Decimal

from pydantic import BaseModel, Field


class FinancialAnalysisRequest(BaseModel):
    revenue: Decimal | None = Field(default=None, ge=0)
    initial_investment: Decimal | None = Field(
        default=None,
        ge=0,
    )
    fixed_costs: Decimal | None = Field(
        default=None,
        ge=0,
    )
    variable_costs: Decimal | None = Field(
        default=None,
        ge=0,
    )
    contribution_margin: Decimal | None = Field(
        default=None,
        ge=0,
    )

    assumptions: list[str] = Field(
        default_factory=list
    )

    sources: list[str] = Field(
        default_factory=list
    )


class FinancialAnalysisResponse(BaseModel):
    contract_id: str

    revenue: Decimal | None
    initial_investment: Decimal | None
    fixed_costs: Decimal | None
    variable_costs: Decimal | None
    total_cost: Decimal | None
    profit: Decimal | None
    roi: Decimal | None
    profit_margin: Decimal | None
    break_even: Decimal | None

    assumptions: list[str]
    sources: list[str]