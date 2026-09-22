from __future__ import annotations

from ai.rag.ingestion import ContractRAGIngestionService


class ContractIndexingService:
    """
    Coordinates indexing of a contract into the RAG pipeline.

    The indexing service is responsible for validating the contract
    information and delegating document processing to the ingestion
    service.
    """

    def __init__(
        self,
        ingestion_service: ContractRAGIngestionService | None = None,
    ) -> None:
        self.ingestion_service = (
            ingestion_service or ContractRAGIngestionService()
        )

    def index_contract(
        self,
        contract_id: str,
        document_id: int,
        extracted_text: str,
    ) -> int:
        """
        Index extracted contract text for semantic retrieval.

        Returns:
            Number of chunks indexed.
        """
        if not contract_id or not contract_id.strip():
            raise ValueError("contract_id cannot be empty.")

        if document_id <= 0:
            raise ValueError("document_id must be greater than zero.")

        if not extracted_text or not extracted_text.strip():
            raise ValueError("extracted_text cannot be empty.")

        return self.ingestion_service.ingest(
            contract_id=contract_id.strip(),
            document_id=document_id,
            text=extracted_text.strip(),
        )