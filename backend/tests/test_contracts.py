from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_get_contracts():
    response = client.get("/contracts/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_existing_contract():
    response = client.get("/contracts/CNT-001")

    assert response.status_code == 200

    data = response.json()

    assert data["contract_id"] == "CNT-001"


def test_get_non_existing_contract():
    response = client.get("/contracts/CNT-999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Contract not found"


def test_update_contract():
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


def test_update_non_existing_contract():
    response = client.patch(
        "/contracts/CNT-999",
        json={
            "name": "Test",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Contract not found"