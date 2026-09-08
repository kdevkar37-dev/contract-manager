from datetime import date

from pydantic import BaseModel


class ContractCreate(BaseModel):
    contract_id: str
    name: str
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class ContractUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class ContractAskRequest(BaseModel):
    question: str


class ContractSource(BaseModel):
    document_id: int
    chunk_index: int
    evidence: str


class ContractAskResponse(BaseModel):
    contract_id: str
    question: str
    answer: str
    sources: list[ContractSource] = []


class ContractResponse(BaseModel):
    id: int
    contract_id: str
    name: str
    description: str | None
    start_date: date | None
    end_date: date | None
    source_type: str
    original_filename: str | None
    mime_type: str | None
    storage_key: str | None
    status: str

    model_config = {"from_attributes": True}