from unittest.mock import MagicMock

from ai.rag.ingestion import ContractRAGIngestionService


def test_ingest_chunks_embeds_and_stores():
    chunker = MagicMock()
    embedding_service = MagicMock()
    vector_store = MagicMock()

    chunker.split_text.return_value = [
        "Payment must be completed within 30 days.",
        "The supplier must provide required documents.",
    ]

    embedding_service.embed_documents.return_value = [
        [0.1, 0.2],
        [0.3, 0.4],
    ]

    service = ContractRAGIngestionService(
        chunker=chunker,
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    chunk_count = service.ingest(
        contract_id="CNT-001",
        document_id=1,
        text="Contract text",
    )

    assert chunk_count == 2

    chunker.split_text.assert_called_once_with("Contract text")

    embedding_service.embed_documents.assert_called_once_with(
        [
            "Payment must be completed within 30 days.",
            "The supplier must provide required documents.",
        ]
    )

    vector_store.add_documents.assert_called_once_with(
        ids=[
            "CNT-001-document-1-chunk-0",
            "CNT-001-document-1-chunk-1",
        ],
        documents=[
            "Payment must be completed within 30 days.",
            "The supplier must provide required documents.",
        ],
        embeddings=[
            [0.1, 0.2],
            [0.3, 0.4],
        ],
        metadatas=[
            {
                "contract_id": "CNT-001",
                "document_id": "1",
                "chunk_index": 0,
            },
            {
                "contract_id": "CNT-001",
                "document_id": "1",
                "chunk_index": 1,
            },
        ],
    )


def test_ingest_empty_text_does_not_create_vectors():
    chunker = MagicMock()
    embedding_service = MagicMock()
    vector_store = MagicMock()

    chunker.split_text.return_value = []

    service = ContractRAGIngestionService(
        chunker=chunker,
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    chunk_count = service.ingest(
        contract_id="CNT-002",
        document_id=2,
        text="",
    )

    assert chunk_count == 0

    embedding_service.embed_documents.assert_not_called()
    vector_store.add_documents.assert_not_called()