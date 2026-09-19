from fastapi.testclient import TestClient

from backend.app.main import app


def test_unexpected_exception_returns_safe_500_response():
    @app.get("/test-unexpected-error")
    def test_unexpected_error():
        raise RuntimeError("Sensitive internal error details")

    client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/test-unexpected-error")

    assert response.status_code == 500
    assert response.json() == {
        "detail": "An unexpected internal server error occurred."
    }
    assert "Sensitive internal error details" not in response.text