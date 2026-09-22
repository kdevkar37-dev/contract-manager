from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ContractDecisionCreate(BaseModel):
    decision: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )

    reason: str | None = Field(
        default=None,
        max_length=5000,
    )


class ContractDecisionResponse(BaseModel):
    contract_id: str
    decision: str
    reason: str | None
    decided_by: int
    decided_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ContractDecisionHistoryResponse(BaseModel):
    contract_id: str
    decisions: list[ContractDecisionResponse]