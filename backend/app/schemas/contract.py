from datetime import date

from pydantic import BaseModel


class ContractCreate(BaseModel):
    contract_id: str
    name: str
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class ContractResponse(BaseModel):
    id: int
    contract_id: str
    name: str
    description: str | None
    start_date: date | None
    end_date: date | None

    model_config = {
        "from_attributes": True
    }