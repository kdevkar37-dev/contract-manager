from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.models.contract import Contract


def create_contract(
    db_session,
    *,
    contract_id: str,
    status: str,
):
    contract = Contract(
        contract_id=contract_id,
        name="Retry Test Contract",
        source_type="manual",
        status=status,
        storage_key="contracts/test.pdf",
        original_filename="test.pdf",
        mime_type="application/pdf",
    )

    db_session.add(contract)
    db_session.commit()
    db_session.refresh(contract)

    return contract


@patch(
    "backend.app.api.contracts.process_contract_task.delay"
)
def test_failed_contract_can_be_retried(
    mock_delay,
    db_session,
    authenticated_test_user,
):
    contract = create_contract(
        db_session,
        contract_id="RETRY-001",
        status="failed",
    )

    mock_task = MagicMock()
    mock_task.id = "retry-task-001"
    mock_delay.return_value = mock_task

    client = TestClient(app)

    response = client.post(
        f"/contracts/{contract.contract_id}/process"
    )

    assert response.status_code == 202

    data = response.json()

    assert data["contract_id"] == "RETRY-001"
    assert data["status"] == "queued"
    assert data["task_id"] == "retry-task-001"
    assert "retry" in data["message"].lower()

    mock_delay.assert_called_once_with(
        "RETRY-001"
    )


@patch(
    "backend.app.api.contracts.process_contract_task.delay"
)
def test_completed_contract_cannot_be_reprocessed(
    mock_delay,
    db_session,
    authenticated_test_user,
):
    contract = create_contract(
        db_session,
        contract_id="RETRY-002",
        status="completed",
    )

    client = TestClient(app)

    response = client.post(
        f"/contracts/{contract.contract_id}/process"
    )

    assert response.status_code == 409

    assert response.json() == {
        "detail": (
            "Contract processing has already completed."
        )
    }

    mock_delay.assert_not_called()


@patch(
    "backend.app.api.contracts.process_contract_task.delay"
)
def test_processing_contract_cannot_be_queued_again(
    mock_delay,
    db_session,
    authenticated_test_user,
):
    contract = create_contract(
        db_session,
        contract_id="RETRY-003",
        status="processing",
    )

    client = TestClient(app)

    response = client.post(
        f"/contracts/{contract.contract_id}/process"
    )

    assert response.status_code == 409

    assert response.json() == {
        "detail": (
            "Contract processing is already in progress."
        )
    }

    mock_delay.assert_not_called()


@patch(
    "backend.app.api.contracts.process_contract_task.delay"
)
def test_pending_contract_can_be_queued(
    mock_delay,
    db_session,
    authenticated_test_user,
):
    contract = create_contract(
        db_session,
        contract_id="RETRY-004",
        status="pending",
    )

    mock_task = MagicMock()
    mock_task.id = "processing-task-001"
    mock_delay.return_value = mock_task

    client = TestClient(app)

    response = client.post(
        f"/contracts/{contract.contract_id}/process"
    )

    assert response.status_code == 202

    data = response.json()

    assert data["contract_id"] == "RETRY-004"
    assert data["status"] == "queued"
    assert data["task_id"] == "processing-task-001"

    mock_delay.assert_called_once_with(
        "RETRY-004"
    )