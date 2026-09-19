from unittest.mock import MagicMock, patch

from backend.app.services.documents.contract_processing_service import (
    ContractProcessingService,
)


@patch(
    "backend.app.services.documents.contract_processing_service."
    "FinancialAnalysisService"
)
@patch(
    "backend.app.services.documents.contract_processing_service."
    "FinancialExtractionService"
)
@patch(
    "backend.app.services.documents.contract_processing_service."
    "ContractIndexingService"
)
@patch(
    "backend.app.services.documents.contract_processing_service."
    "ContractDocumentService"
)
@patch(
    "backend.app.services.documents.contract_processing_service."
    "ContractDocumentRepository"
)
@patch(
    "backend.app.services.documents.contract_processing_service."
    "ContractRepository"
)
def test_contract_processing_runs_financial_analysis(
    mock_contract_repository,
    mock_document_repository,
    mock_document_service,
    mock_indexing_service,
    mock_financial_extraction,
    mock_financial_analysis,
):
    db = MagicMock()

    contract = MagicMock()
    contract.id = 1
    contract.contract_id = "CNT-001"
    contract.storage_key = "contracts/test.pdf"
    contract.original_filename = "test.pdf"

    document = MagicMock()
    document.id = 10

    mock_contract_repository.return_value.get_by_contract_id.return_value = (
        contract
    )

    # No existing document -> service should create one.
    mock_document_repository.return_value.get_by_contract_id.return_value = None

    mock_document_repository.return_value.create.return_value = (
        document
    )

    extracted_text = """
    Contract value is 100000.
    Initial investment is 20000.
    Fixed costs are 30000.
    Variable costs are 20000.
    """

    mock_document_service.return_value.extract_text.return_value = (
        extracted_text
    )

    financial_inputs = MagicMock()

    mock_financial_extraction.return_value.extract.return_value = (
        financial_inputs
    )

    service = ContractProcessingService(db)

    result = service.extract_contract_text("CNT-001")

    assert result == extracted_text

    mock_document_service.return_value.extract_text.assert_called_once_with(
        filename="test.pdf",
        storage_key="contracts/test.pdf",
    )

    mock_indexing_service.return_value.index_contract.assert_called_once_with(
        contract_id="CNT-001",
        document_id=10,
        extracted_text=extracted_text,
    )

    mock_financial_extraction.return_value.extract.assert_called_once_with(
        extracted_text
    )

    mock_financial_analysis.return_value.calculate_for_contract.assert_called_once_with(
        contract_id="CNT-001",
        inputs=financial_inputs,
    )

    mock_contract_repository.return_value.update_status.assert_any_call(
        contract,
        "processing",
    )

    mock_contract_repository.return_value.update_status.assert_any_call(
        contract,
        "completed",
    )


@patch(
    "backend.app.services.documents.contract_processing_service."
    "FinancialAnalysisService"
)
@patch(
    "backend.app.services.documents.contract_processing_service."
    "FinancialExtractionService"
)
@patch(
    "backend.app.services.documents.contract_processing_service."
    "ContractIndexingService"
)
@patch(
    "backend.app.services.documents.contract_processing_service."
    "ContractDocumentService"
)
@patch(
    "backend.app.services.documents.contract_processing_service."
    "ContractDocumentRepository"
)
@patch(
    "backend.app.services.documents.contract_processing_service."
    "ContractRepository"
)
def test_contract_processing_marks_failed_when_financial_analysis_fails(
    mock_contract_repository,
    mock_document_repository,
    mock_document_service,
    mock_indexing_service,
    mock_financial_extraction,
    mock_financial_analysis,
):
    db = MagicMock()

    contract = MagicMock()
    contract.id = 1
    contract.contract_id = "CNT-001"
    contract.storage_key = "contracts/test.pdf"
    contract.original_filename = "test.pdf"

    document = MagicMock()
    document.id = 10

    mock_contract_repository.return_value.get_by_contract_id.return_value = (
        contract
    )

    # No existing document -> service should create one.
    mock_document_repository.return_value.get_by_contract_id.return_value = None

    mock_document_repository.return_value.create.return_value = (
        document
    )

    mock_document_service.return_value.extract_text.return_value = (
        "Contract financial information."
    )

    financial_inputs = MagicMock()

    mock_financial_extraction.return_value.extract.return_value = (
        financial_inputs
    )

    mock_financial_analysis.return_value.calculate_for_contract.side_effect = (
        ValueError("Invalid financial value")
    )

    service = ContractProcessingService(db)

    try:
        service.extract_contract_text("CNT-001")
    except ValueError as exc:
        assert str(exc) == "Invalid financial value"
    else:
        raise AssertionError(
            "Expected financial analysis failure"
        )

    mock_document_repository.return_value.mark_failed.assert_called_once_with(
        document=document,
        error_message="Invalid financial value",
    )

    mock_contract_repository.return_value.update_status.assert_any_call(
        contract,
        "failed",
    )