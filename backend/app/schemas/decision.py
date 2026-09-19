

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class DecisionWeightsRequest(BaseModel):
    financial: Decimal = Field(default=Decimal("50"), ge=0)
    risk: Decimal = Field(default=Decimal("30"), ge=0)
    contract_value: Decimal = Field(default=Decimal("20"), ge=0)


class DecisionScoreRequest(BaseModel):
    financial_score: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
    )
    risk_score: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
    )
    contract_value_score: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
    )
    weights: DecisionWeightsRequest | None = None


class DecisionScoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    contract_id: str

    score: Decimal | None

    financial_score: Decimal | None
    risk_score: Decimal | None
    contract_value_score: Decimal | None

    financial_weight: Decimal
    risk_weight: Decimal
    contract_value_weight: Decimal

    assumptions: list[str]
    explanation: list[str]