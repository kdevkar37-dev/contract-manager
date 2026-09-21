from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.models.contract import Contract


client = TestClient(app)


def create_contract(db_session) -> Contract:
    contract = Contract(
        contract_id="CNT-001",
        name="Test Contract",
        source_type="manual",
        status="completed",
    )

    db_session.add(contract)
    db_session.commit()
    db_session.refresh(contract)

    return contract


def test_get_contracts(
    db_session,
    authenticated_test_user,
):
    response = client.get("/contracts/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_existing_contract(
    db_session,
    authenticated_test_user,
):
    create_contract(db_session)

    response = client.get("/contracts/CNT-001")

    assert response.status_code == 200

    data = response.json()

    assert data["contract_id"] == "CNT-001"


def test_get_non_existing_contract(
    db_session,
    authenticated_test_user,
):
    response = client.get("/contracts/CNT-999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Contract not found"


def test_update_contract(
    db_session,
    authenticated_test_user,
):
    create_contract(db_session)

    response = client.patch(
        "/contracts/CNT-001",
        json={
            "name": "Updated Contract Name",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["contract_id"] == "CNT-001"
    assert data["name"] == "Updated Contract Name"


def test_update_non_existing_contract(
    db_session,
    authenticated_test_user,
):
    response = client.patch(
        "/contracts/CNT-999",
        json={
            "name": "Test",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Contract not found"