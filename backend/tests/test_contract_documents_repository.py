from backend.app.models.contract import Contract
from backend.app.repositories.contract_documents import ContractDocumentRepository


def test_create_contract_document(db_session):
    contract = Contract(
        contract_id="TEST-DOC-001",
        name="Test Contract",
        source_type="manual",
        status="pending",
    )

    db_session.add(contract)
    db_session.commit()
    db_session.refresh(contract)

    repository = ContractDocumentRepository(db_session)

    document = repository.create(contract.id)

    assert document.id is not None
    assert document.contract_id == contract.id
    assert document.processing_status == "processing"


def test_update_extracted_text(db_session):
    contract = Contract(
        contract_id="TEST-DOC-002",
        name="Test Contract",
        source_type="manual",
        status="pending",
    )

    db_session.add(contract)
    db_session.commit()
    db_session.refresh(contract)

    repository = ContractDocumentRepository(db_session)

    document = repository.create(contract.id)

    updated_document = repository.update_extracted_text(
        document=document,
        extracted_text="This is extracted contract text.",
    )

    assert updated_document.extracted_text == "This is extracted contract text."
    assert updated_document.processing_status == "completed"
    assert updated_document.processed_at is not None
    assert updated_document.error_message is None


def test_mark_failed(db_session):
    contract = Contract(
        contract_id="TEST-DOC-003",
        name="Test Contract",
        source_type="manual",
        status="pending",
    )

    db_session.add(contract)
    db_session.commit()
    db_session.refresh(contract)

    repository = ContractDocumentRepository(db_session)

    document = repository.create(contract.id)

    failed_document = repository.mark_failed(
        document=document,
        error_message="Text extraction failed.",
    )

    assert failed_document.processing_status == "failed"
    assert failed_document.error_message == "Text extraction failed."


def test_get_by_contract_id(db_session):
    contract = Contract(
        contract_id="TEST-DOC-004",
        name="Test Contract",
        source_type="manual",
        status="pending",
    )

    db_session.add(contract)
    db_session.commit()
    db_session.refresh(contract)

    repository = ContractDocumentRepository(db_session)

    created_document = repository.create(contract.id)

    found_document = repository.get_by_contract_id(contract.id)

    assert found_document is not None
    assert found_document.id == created_document.id
    assert found_document.contract_id == contract.id