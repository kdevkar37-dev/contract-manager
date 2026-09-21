import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ai.rag.chain import ContractRAGChain

from backend.app.core.database import get_db
from backend.app.core.permissions import (
    require_authenticated,
    require_contract_manager,
)
from backend.app.repositories.contract_documents import (
    ContractDocumentRepository,
)
from backend.app.repositories.contracts import ContractRepository
from backend.app.schemas.contract import (
    ContractAskRequest,
    ContractAskResponse,
    ContractCreate,
    ContractResponse,
    ContractUpdate,
)
from backend.app.services.audit.service import AuditLogService
from backend.app.services.contracts.service import ContractService
from backend.app.workers.tasks import process_contract_task


logger = logging.getLogger(__name__)


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

    return service.get_all_contracts()


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
    Get a single contract.

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
# GET PROCESSING STATUS
# ============================================================

@router.get(
    "/{contract_id}/status",
)
def get_contract_processing_status(
    contract_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_authenticated),
):
    """
    Get the current processing status of a contract.

    Accessible to:
        - admin
        - manager
        - viewer
    """

    repository = ContractRepository(db)

    contract = repository.get_by_contract_id(
        contract_id
    )

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found",
        )

    document_repository = ContractDocumentRepository(db)

    document = document_repository.get_by_contract_id(
        contract.id
    )

    return {
        "contract_id": contract.contract_id,
        "contract_status": contract.status,
        "document_status": (
            document.processing_status
            if document is not None
            else "pending"
        ),
        "processed_at": (
            document.processed_at
            if document is not None
            else None
        ),
        "error_message": (
            document.error_message
            if document is not None
            else None
        ),
    }


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
# PROCESS / RETRY CONTRACT
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

    Failed contracts can be retried.

    Accessible to:
        - admin
        - manager
    """

    repository = ContractRepository(db)

    contract = repository.get_by_contract_id(
        contract_id
    )

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

    if contract.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contract processing has already completed.",
        )

    if contract.status == "processing":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contract processing is already in progress.",
        )

    try:
        task = process_contract_task.delay(
            contract_id
        )

        is_retry = contract.status == "failed"

        AuditLogService(db).record(
            user_id=current_user.id,
            action=(
                "CONTRACT_PROCESSING_RETRY"
                if is_retry
                else "CONTRACT_PROCESSING_QUEUED"
            ),
            resource_type="contract",
            resource_id=contract.contract_id,
            details=(
                "Failed contract processing queued for retry."
                if is_retry
                else "Contract processing queued."
            ),
        )

        return {
            "contract_id": contract_id,
            "status": "queued",
            "task_id": task.id,
            "message": (
                "Failed contract processing has been "
                "queued for retry."
                if is_retry
                else "Contract processing has been queued."
            ),
        }

    except Exception:
        logger.exception(
            "Failed to queue contract processing: %s",
            contract_id,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Contract processing could not be queued "
                "due to an internal server error."
            ),
        )


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
    Ask a question about a contract using RAG.

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

    except Exception:
        logger.exception(
            "RAG query failed for contract: %s",
            contract_id,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="RAG query failed due to an internal server error.",
        )