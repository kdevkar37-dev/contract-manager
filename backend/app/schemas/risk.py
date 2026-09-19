from pydantic import BaseModel, ConfigDict


class RiskAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    contract_id: str
    risk_type: str
    severity: str
    title: str
    description: str
    evidence: str | None = None
    source: str | None = None
    confidence: str | None = None