from sqlalchemy.orm import Session

from ai.rag.contract_indexing import ContractIndexingService
from backend.app.repositories.contract_documents import ContractDocumentRepository
from backend.app.repositories.contracts import ContractRepository
from backend.app.services.documents.contract_document_service import (
    ContractDocumentService,
)


class ContractProcessingService:
    def __init__(self, db: Session):
        self.repository = ContractRepository(db)
        self.document_repository = ContractDocumentRepository(db)
        self.document_service = ContractDocumentService()
        self.indexing_service = ContractIndexingService()

    def extract_contract_text(self, contract_id: str) -> str:
        contract = self.repository.get_by_contract_id(contract_id)

        if contract is None:
            raise ValueError("Contract not found")

        if not contract.storage_key:
            raise ValueError("Contract does not have a stored document")

        if not contract.original_filename:
            raise ValueError("Contract does not have an original filename")

        self.repository.update_status(contract, "processing")

        document = self.document_repository.create(contract.id)

        try:
            extracted_text = self.document_service.extract_text(
                filename=contract.original_filename,
                storage_key=contract.storage_key,
            )

            self.document_repository.update_extracted_text(
                document=document,
                extracted_text=extracted_text,
            )

            self.indexing_service.index_contract(
                contract_id=contract.contract_id,
                document_id=document.id,
                extracted_text=extracted_text,
            )

            self.repository.update_status(contract, "completed")

            return extracted_text

        except Exception as exc:
            self.document_repository.mark_failed(
                document=document,
                error_message=str(exc),
            )

            self.repository.update_status(contract, "failed")

            raise