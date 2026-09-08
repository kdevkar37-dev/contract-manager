from unittest.mock import MagicMock

from ai.rag.retriever import ContractRetriever


def test_retrieve_embeds_question_and_searches():
    embedding_service = MagicMock()
    vector_store = MagicMock()

    embedding_service.embed_query.return_value = [
        0.1,
        0.2,
        0.3,
    ]

    vector_store.search.return_value = {
        "documents": [
            ["Payment must be completed within 30 days."]
        ],
        "metadatas": [
            [{"contract_id": "CNT-001"}]
        ],
    }

    retriever = ContractRetriever(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    results = retriever.retrieve(
        question="What are the payment terms?",
        contract_id="CNT-001",
        n_results=3,
    )

    embedding_service.embed_query.assert_called_once_with(
        "What are the payment terms?"
    )

    vector_store.search.assert_called_once_with(
        query_embedding=[0.1, 0.2, 0.3],
        n_results=3,
        contract_id="CNT-001",
    )

    assert results["documents"][0][0] == (
        "Payment must be completed within 30 days."
    )


def test_retrieve_uses_default_result_count():
    embedding_service = MagicMock()
    vector_store = MagicMock()

    embedding_service.embed_query.return_value = [
        0.1,
        0.2,
    ]

    vector_store.search.return_value = {
        "documents": [["Contract information"]],
        "metadatas": [
            [{"contract_id": "CNT-001"}]
        ],
    }

    retriever = ContractRetriever(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    retriever.retrieve(
        question="What is this contract about?",
        contract_id="CNT-001",
    )

    vector_store.search.assert_called_once_with(
        query_embedding=[0.1, 0.2],
        n_results=5,
        contract_id="CNT-001",
    )