from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.models.contract import Contract
from backend.app.models.contract_document import ContractDocument


def test_get_contract_processing_status(
    db_session,
    authenticated_test_user,
):
    contract = Contract(
        contract_id="STATUS-001",
        name="Status Test Contract",
        source_type="manual",
        status="indexed",
    )

    db_session.add(contract)
    db_session.commit()
    db_session.refresh(contract)

    document = ContractDocument(
        contract_id=contract.id,
        extracted_text="Contract text",
        processing_status="indexed",
    )

    db_session.add(document)
    db_session.commit()

    client = TestClient(app)

    response = client.get(
        f"/contracts/{contract.contract_id}/status"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["contract_id"] == "STATUS-001"
    assert data["contract_status"] == "indexed"
    assert data["document_status"] == "indexed"
    assert data["processed_at"] is None
    assert data["error_message"] is None