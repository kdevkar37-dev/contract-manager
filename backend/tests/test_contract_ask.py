from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


@patch("backend.app.api.contracts.ContractRAGChain")
def test_ask_contract(mock_rag_chain):
    mock_chain = MagicMock()

    mock_chain.ask.return_value = {
        "answer": "The contract value is 500000 INR.",
        "sources": [
            {
                "document_id": 1,
                "chunk_index": 0,
                "evidence": "The contract value is 500000 INR.",
            }
        ],
    }

    mock_rag_chain.return_value = mock_chain

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

    mock_chain.ask.assert_called_once_with(
        contract_id="CNT-001",
        question="What is the contract value?",
    )