from unittest.mock import MagicMock

from ai.rag.chain import ContractRAGChain


def test_rag_chain_retrieves_context_and_generates_answer():
    retriever = MagicMock()
    llm_service = MagicMock()

    retriever.retrieve.return_value = {
        "documents": [
            [
                "Payment must be completed within 30 days.",
                "Invoices are issued monthly.",
            ]
        ],
        "metadatas": [
            [
                {
                    "document_id": "1",
                    "chunk_index": 0,
                },
                {
                    "document_id": "1",
                    "chunk_index": 1,
                },
            ]
        ],
    }

    llm_service.invoke.return_value = (
        "Payment must be completed within 30 days."
    )

    chain = ContractRAGChain(
        retriever=retriever,
        llm_service=llm_service,
    )

    result = chain.ask(
        contract_id="CNT-001",
        question="What are the payment terms?",
        n_results=3,
    )

    retriever.retrieve.assert_called_once_with(
        question="What are the payment terms?",
        contract_id="CNT-001",
        n_results=3,
    )

    assert result["answer"] == (
        "Payment must be completed within 30 days."
    )

    assert result["sources"] == [
        {
            "document_id": 1,
            "chunk_index": 0,
            "evidence": "Payment must be completed within 30 days.",
        },
        {
            "document_id": 1,
            "chunk_index": 1,
            "evidence": "Invoices are issued monthly.",
        },
    ]


def test_rag_chain_handles_no_documents():
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
        question="What is the termination period?",
    )

    assert result == {
        "answer": (
            "The requested information was not found "
            "in the available contract documents."
        ),
        "sources": [],
    }

    llm_service.invoke.assert_not_called()