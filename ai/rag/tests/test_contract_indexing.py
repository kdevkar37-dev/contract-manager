from unittest.mock import MagicMock

from ai.rag.contract_indexing import ContractIndexingService


def test_index_contract_delegates_to_ingestion_service():
    ingestion_service = MagicMock()

    ingestion_service.ingest.return_value = 4

    service = ContractIndexingService(
        ingestion_service=ingestion_service,
    )

    chunk_count = service.index_contract(
        contract_id="CNT-001",
        document_id=1,
        extracted_text="Contract text",
    )

    ingestion_service.ingest.assert_called_once_with(
        contract_id="CNT-001",
        document_id=1,
        text="Contract text",
    )

    assert chunk_count == 4