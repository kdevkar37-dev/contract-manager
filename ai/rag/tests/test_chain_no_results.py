from unittest.mock import MagicMock

from ai.rag.chain import ContractRAGChain


def test_chain_returns_not_found_when_no_documents():
    retriever = MagicMock()
    llm_service = MagicMock()

    retriever.retrieve.return_value = {
        "documents": [[]],
        "metadatas": [[]],
    }

    chain = ContractRAGChain(
        retriever=retriever,
        llm_service=llm_service,
    )

    result = chain.ask(
        contract_id="CNT-001",
        question="What is the contract value?",
    )

    assert result == {
        "answer": (
            "The requested information was not found "
            "in the available contract documents."
        ),
        "sources": [],
    }

    retriever.retrieve.assert_called_once_with(
        question="What is the contract value?",
        contract_id="CNT-001",
        n_results=5,
    )

    llm_service.invoke.assert_not_called()