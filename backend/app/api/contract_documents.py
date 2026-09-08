from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.repositories.contract_documents import ContractDocumentRepository
from backend.app.repositories.contracts import ContractRepository


router = APIRouter(
    prefix="/contracts",
    tags=["Contract Documents"],
)


@router.get("/{contract_id}/document")
def get_contract_document(
    contract_id: str,
    db: Session = Depends(get_db),
):
    contract_repository = ContractRepository(db)

    contract = contract_repository.get_by_contract_id(contract_id)

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found",
        )

    document_repository = ContractDocumentRepository(db)

    document = document_repository.get_by_contract_id(contract.id)

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract document not found",
        )

    return {
        "contract_id": contract.contract_id,
        "document_id": document.id,
        "processing_status": document.processing_status,
        "extracted_text": document.extracted_text,
        "processed_at": document.processed_at,
        "error_message": document.error_message,
    }