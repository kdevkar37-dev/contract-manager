from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ai.rag.chain import ContractRAGChain
from backend.app.core.database import get_db
from backend.app.schemas.contract import (
    ContractAskRequest,
    ContractAskResponse,
    ContractCreate,
    ContractResponse,
    ContractUpdate,
)
from backend.app.services.contracts.service import ContractService
from backend.app.services.documents.contract_processing_service import (
    ContractProcessingService,
)


router = APIRouter(
    prefix="/contracts",
    tags=["Contracts"],
)


@router.get(
    "/",
    response_model=list[ContractResponse],
)
def get_contracts(
    db: Session = Depends(get_db),
):
    service = ContractService(db)

    contracts = service.get_all_contracts()

    return contracts


@router.get(
    "/{contract_id}",
    response_model=ContractResponse,
)
def get_contract(
    contract_id: str,
    db: Session = Depends(get_db),
):
    service = ContractService(db)

    contract = service.get_contract_by_id(contract_id)

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found",
        )

    return contract


@router.post(
    "/",
    response_model=ContractResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_contract(
    contract_data: ContractCreate,
    db: Session = Depends(get_db),
):
    service = ContractService(db)

    try:
        return service.create_contract(contract_data)

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contract ID already exists",
        )


@router.patch(
    "/{contract_id}",
    response_model=ContractResponse,
)
def update_contract(
    contract_id: str,
    contract_data: ContractUpdate,
    db: Session = Depends(get_db),
):
    service = ContractService(db)

    try:
        contract = service.update_contract(
            contract_id,
            contract_data,
        )

        if contract is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contract not found",
            )

        return contract

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contract update failed",
        )


@router.post(
    "/{contract_id}/process",
)
def process_contract(
    contract_id: str,
    db: Session = Depends(get_db),
):
    service = ContractProcessingService(db)

    try:
        text = service.extract_contract_text(contract_id)

        return {
            "contract_id": contract_id,
            "status": "processed",
            "text": text,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.post(
    "/{contract_id}/ask",
    response_model=ContractAskResponse,
)
def ask_contract(
    contract_id: str,
    request: ContractAskRequest,
):
    rag_chain = ContractRAGChain()

    try:
        result = rag_chain.ask(
            contract_id=contract_id,
            question=request.question,
        )

        return ContractAskResponse(
            contract_id=contract_id,
            question=request.question,
            answer=result["answer"],
            sources=result["sources"],
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG query failed: {exc}",
        )