from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.contract_document import ContractDocument


class ContractDocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, contract_id: int) -> ContractDocument:
        document = ContractDocument(
            contract_id=contract_id,
            processing_status="processing",
        )

        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)

        return document

    def update_status(
        self,
        document: ContractDocument,
        status: str,
    ) -> ContractDocument:
        document.processing_status = status

        if status == "completed":
            document.processed_at = datetime.now(timezone.utc)
            document.error_message = None

        self.db.commit()
        self.db.refresh(document)

        return document

    def update_extracted_text(
        self,
        document: ContractDocument,
        extracted_text: str,
    ) -> ContractDocument:
        document.extracted_text = extracted_text
        document.processing_status = "text_extracted"
        document.processed_at = None
        document.error_message = None

        self.db.commit()
        self.db.refresh(document)

        return document

    def reset_for_retry(
        self,
        document: ContractDocument,
    ) -> ContractDocument:
        document.processing_status = "processing"
        document.processed_at = None
        document.error_message = None

        self.db.commit()
        self.db.refresh(document)

        return document

    def mark_failed(
        self,
        document: ContractDocument,
        error_message: str,
    ) -> ContractDocument:
        document.processing_status = "failed"
        document.error_message = error_message
        document.processed_at = None

        self.db.commit()
        self.db.refresh(document)

        return document

    def get_by_contract_id(
        self,
        contract_id: int,
    ) -> ContractDocument | None:
        result = self.db.execute(
            select(ContractDocument)
            .where(
                ContractDocument.contract_id == contract_id
            )
            .order_by(ContractDocument.id.desc())
        )

        return result.scalars().first()