from ai.rag.contract_indexing import ContractIndexingService


def test_real_contract_indexing():
    service = ContractIndexingService()

    text = """
    This is a contract between ABC Company and XYZ Company.
    The contract value is 500000 INR.
    The contract duration is 12 months.
    """

    chunk_count = service.index_contract(
        contract_id="TEST-REAL-001",
        document_id=999,
        extracted_text=text,
    )

    assert chunk_count > 0