from unittest.mock import MagicMock

from backend.app.services.documents.contract_processing_service import (
    ContractProcessingService,
)


def test_contract_processing_indexes_extracted_text():
    db = MagicMock()

    service = ContractProcessingService(db)

    service.repository.get_by_contract_id = MagicMock()
    service.repository.get_by_contract_id.return_value = MagicMock(
        contract_id="CNT-001",
        id=1,
        storage_key="contracts/test.pdf",
        original_filename="test.pdf",
    )

    service.repository.update_status = MagicMock()

    document = MagicMock(id=10)

    service.document_repository.create = MagicMock(
        return_value=document
    )

    service.document_repository.update_extracted_text = MagicMock()

    service.document_service.extract_text = MagicMock(
        return_value="This is contract text."
    )

    service.indexing_service.index_contract = MagicMock(
        return_value=1
    )

    result = service.extract_contract_text("CNT-001")

    service.indexing_service.index_contract.assert_called_once_with(
        contract_id="CNT-001",
        document_id=10,
        extracted_text="This is contract text.",
    )

    assert result == "This is contract text."