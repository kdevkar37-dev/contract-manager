from ai.rag.ingestion import ContractRAGIngestionService


class ContractIndexingService:
    def __init__(
        self,
        ingestion_service: ContractRAGIngestionService | None = None,
    ):
        self.ingestion_service = (
            ingestion_service or ContractRAGIngestionService()
        )

    def index_contract(
        self,
        contract_id: str,
        document_id: int,
        extracted_text: str,
    ) -> int:
        return self.ingestion_service.ingest(
            contract_id=contract_id,
            document_id=document_id,
            text=extracted_text,
        )