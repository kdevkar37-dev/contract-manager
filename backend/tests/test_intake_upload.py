from io import BytesIO
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


@patch("backend.app.api.intake.process_contract_task")
@patch("backend.app.api.intake.IntakeService")
def test_upload_contract(mock_intake_service, mock_process_task):
    mock_service = MagicMock()

    mock_service.store_file.return_value = (
        "contracts/test-contract.txt"
    )

    mock_contract = MagicMock()
    mock_contract.contract_id = "CNT-TEST-001"
    mock_contract.name = "test-contract"
    mock_contract.original_filename = "test-contract.txt"
    mock_contract.mime_type = "text/plain"
    mock_contract.storage_key = "contracts/test-contract.txt"
    mock_contract.status = "pending"

    mock_service.create_contract_record.return_value = mock_contract
    mock_intake_service.return_value = mock_service

    response = client.post(
        "/intake/upload",
        files={
            "file": (
                "test-contract.txt",
                BytesIO(b"This is a test contract."),
                "text/plain",
            )
        },
    )

    assert response.status_code == 202

    assert response.json() == {
        "message": "Contract uploaded successfully",
        "contract_id": "CNT-TEST-001",
        "name": "test-contract",
        "filename": "test-contract.txt",
        "content_type": "text/plain",
        "storage_key": "contracts/test-contract.txt",
        "status": "processing",
    }

    mock_process_task.delay.assert_called_once_with(
        "CNT-TEST-001"
    )