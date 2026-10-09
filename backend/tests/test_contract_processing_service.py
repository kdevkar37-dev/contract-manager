from unittest.mock import MagicMock

from backend.app.models.contract import Contract
from backend.app.models.contract_document import ContractDocument
from backend.app.services.documents.contract_processing_service import (
    ContractProcessingService,
)


def create_contract(
    db_session,
    *,
    contract_id: str = "PROCESS-001",
):
    contract = Contract(
        contract_id=contract_id,
        name="Processing Test Contract",
        source_type="manual",
        status="pending",
        storage_key="contracts/test.pdf",
        original_filename="test.pdf",
        mime_type="application/pdf",
    )

    db_session.add(contract)
    db_session.commit()
    db_session.refresh(contract)

    return contract


def test_contract_processing_extracts_and_indexes_document(
    db_session,
):
    contract = create_contract(db_session)

    service = ContractProcessingService(db_session)

    extracted_text = (
        "This contract has a total value of "
        "500000 INR and a duration of 12 months."
    )

    service.document_service.extract_text = MagicMock(
        return_value=extracted_text
    )

    service.indexing_service.index_contract = MagicMock(
        return_value=1
    )

    service.contract_information_service.extract_and_save = (
        MagicMock()
    )

    service.financial_extraction_service.extract = MagicMock(
        return_value=MagicMock()
    )

    service.financial_analysis_service.calculate_for_contract = (
        MagicMock()
    )

    service.risk_analysis_service.analyze_contract = (
        MagicMock()
    )

    result = service.extract_contract_text(
        contract.contract_id
    )

    assert result == extracted_text

    service.document_service.extract_text.assert_called_once_with(
        filename="test.pdf",
        storage_key="contracts/test.pdf",
    )

    service.indexing_service.index_contract.assert_called_once()

    indexing_call = (
        service.indexing_service.index_contract.call_args
    )

    assert indexing_call.kwargs["contract_id"] == "PROCESS-001"
    assert indexing_call.kwargs["document_id"] > 0
    assert indexing_call.kwargs["extracted_text"] == extracted_text

    service.contract_information_service.extract_and_save.assert_called_once_with(
        contract_id="PROCESS-001",
        contract_text=extracted_text,
    )

    service.financial_extraction_service.extract.assert_called_once_with(
        extracted_text
    )

    service.financial_analysis_service.calculate_for_contract.assert_called_once_with(
        contract_id="PROCESS-001",
        inputs=service.financial_extraction_service.extract.return_value,
    )

    service.risk_analysis_service.analyze_contract.assert_called_once_with(
        contract_id="PROCESS-001",
        contract_text=extracted_text,
    )

    db_session.refresh(contract)

    assert contract.status == "completed"


def test_contract_processing_fails_when_no_text_is_extracted(
    db_session,
):
    contract = create_contract(
        db_session,
        contract_id="PROCESS-002",
    )

    service = ContractProcessingService(db_session)

    service.document_service.extract_text = MagicMock(
        return_value=""
    )

    try:
        service.extract_contract_text(
            contract.contract_id
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert (
            str(exc)
            == "No text could be extracted from the document."
        )

    db_session.refresh(contract)

    assert contract.status == "failed"


def test_contract_processing_fails_when_contract_does_not_exist(
    db_session,
):
    service = ContractProcessingService(db_session)

    try:
        service.extract_contract_text(
            "DOES-NOT-EXIST"
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "Contract not found"