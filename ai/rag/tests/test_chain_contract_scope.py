from unittest.mock import MagicMock

from ai.rag.chain import ContractRAGChain


def test_chain_retrieves_only_requested_contract():
    retriever = MagicMock()
    llm_service = MagicMock()

    retriever.retrieve.return_value = {
        "documents": [
            [
                "Contract A has a value of 500000 INR.",
            ]
        ],
        "metadatas": [
            [
                {
                    "contract_id": "CNT-A",
                    "document_id": "1",
                    "chunk_index": 0,
                }
            ]
        ],
    }

    llm_service.invoke.return_value = (
        "Contract A has a value of 500000 INR."
    )

    chain = ContractRAGChain(
        retriever=retriever,
        llm_service=llm_service,
    )

    result = chain.ask(
        contract_id="CNT-A",
        question="What is the contract value?",
    )

    assert result == {
        "answer": "Contract A has a value of 500000 INR.",
        "sources": [
            {
                "document_id": 1,
                "chunk_index": 0,
                "evidence": "Contract A has a value of 500000 INR.",
            }
        ],
    }

    retriever.retrieve.assert_called_once_with(
        question="What is the contract value?",
        contract_id="CNT-A",
        n_results=5,
    )