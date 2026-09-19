from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ai.rag.chain import ContractRAGChain

from backend.app.core.database import get_db
from backend.app.core.permissions import (
    require_authenticated,
    require_contract_manager,
)
from backend.app.repositories.contracts import ContractRepository
from backend.app.schemas.contract import (
    ContractAskRequest,
    ContractAskResponse,
    ContractCreate,
    ContractResponse,
    ContractUpdate,
)
from backend.app.services.contracts.service import ContractService
from backend.app.workers.tasks import process_contract_task


router = APIRouter(
    prefix="/contracts",
    tags=["Contracts"],
)


# ============================================================
# GET ALL CONTRACTS
# ============================================================

@router.get(
    "/",
    response_model=list[ContractResponse],
)
def get_contracts(
    db: Session = Depends(get_db),
    current_user=Depends(require_authenticated),
):
    """
    Get all contracts.

    Accessible to:
        - admin
        - manager
        - viewer
    """
    service = ContractService(db)

    contracts = service.get_all_contracts()

    return contracts


# ============================================================
# GET SINGLE CONTRACT
# ============================================================

@router.get(
    "/{contract_id}",
    response_model=ContractResponse,
)
def get_contract(
    contract_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_authenticated),
):
    """
    Get a single contract by contract ID.

    Accessible to:
        - admin
        - manager
        - viewer
    """
    service = ContractService(db)

    contract = service.get_contract_by_id(contract_id)

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found",
        )

    return contract


# ============================================================
# CREATE CONTRACT
# ============================================================

@router.post(
    "/",
    response_model=ContractResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_contract(
    contract_data: ContractCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_contract_manager),
):
    """
    Create a new contract.

    Accessible to:
        - admin
        - manager

    Not accessible to:
        - viewer
    """
    service = ContractService(db)

    try:
        return service.create_contract(contract_data)

    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contract ID already exists",
        ) from exc


# ============================================================
# UPDATE CONTRACT
# ============================================================

@router.patch(
    "/{contract_id}",
    response_model=ContractResponse,
)
def update_contract(
    contract_id: str,
    contract_data: ContractUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_contract_manager),
):
    """
    Update an existing contract.

    Accessible to:
        - admin
        - manager

    Not accessible to:
        - viewer
    """
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

    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contract update failed",
        ) from exc


# ============================================================
# PROCESS CONTRACT
# ============================================================

@router.post(
    "/{contract_id}/process",
    status_code=status.HTTP_202_ACCEPTED,
)
def process_contract(
    contract_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_contract_manager),
):
    """
    Queue contract processing using Celery.

    Accessible to:
        - admin
        - manager

    Not accessible to:
        - viewer
    """
    repository = ContractRepository(db)

    contract = repository.get_by_contract_id(contract_id)

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found",
        )

    if not contract.storage_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contract does not have a stored document",
        )

    task = process_contract_task.delay(contract_id)

    return {
        "contract_id": contract_id,
        "status": "queued",
        "task_id": task.id,
        "message": "Contract processing has been queued.",
    }


# ============================================================
# ASK CONTRACT USING RAG
# ============================================================

@router.post(
    "/{contract_id}/ask",
    response_model=ContractAskResponse,
)
def ask_contract(
    contract_id: str,
    request: ContractAskRequest,
    current_user=Depends(require_authenticated),
):
    """
    Ask a question about a contract using the RAG pipeline.

    Accessible to:
        - admin
        - manager
        - viewer
    """
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
        ) from exc