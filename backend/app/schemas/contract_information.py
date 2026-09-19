from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ContractInformationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    contract_id: str
    client_name: str | None
    vendor_name: str | None
    contract_value: Decimal | None
    currency: str | None
    payment_terms: str | None
    renewal_terms: str | None
    termination_terms: str | None
    obligations: list[str]
    dependencies: list[str]