from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.contract_rag_service import ContractRAGResult


client = TestClient(app)


@patch("backend.app.api.contracts.ContractRAGService")
def test_ask_contract(mock_rag_service):
    mock_service = MagicMock()

    mock_service.ask.return_value = ContractRAGResult(
        contract_id="CNT-001",
        question="What is the contract value?",
        answer="The contract value is 500000 INR.",
        sources=[
            {
                "document_id": 1,
                "chunk_index": 0,
                "evidence": "The contract value is 500000 INR.",
            }
        ],
    )

    mock_rag_service.return_value = mock_service

    response = client.post(
        "/contracts/CNT-001/ask",
        json={
            "question": "What is the contract value?"
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "contract_id": "CNT-001",
        "question": "What is the contract value?",
        "answer": "The contract value is 500000 INR.",
        "sources": [
            {
                "document_id": 1,
                "chunk_index": 0,
                "evidence": "The contract value is 500000 INR.",
            }
        ],
    }

    mock_service.ask.assert_called_once_with(
        contract_id="CNT-001",
        question="What is the contract value?",
    )