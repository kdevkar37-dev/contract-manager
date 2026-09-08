from ai.rag.vectorstore import ChromaVectorStore


def test_add_and_search_documents(tmp_path):
    vector_store = ChromaVectorStore(
        persist_directory=str(tmp_path / "chroma"),
        collection_name="test_contracts",
    )

    documents = [
        "Payment must be completed within 30 days.",
        "The contract may be terminated with 60 days notice.",
    ]

    embeddings = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
    ]

    vector_store.add_documents(
        ids=["chunk-1", "chunk-2"],
        documents=documents,
        embeddings=embeddings,
        metadatas=[
            {"contract_id": "CNT-001"},
            {"contract_id": "CNT-001"},
        ],
    )

    results = vector_store.search(
        query_embedding=[1.0, 0.0, 0.0],
        n_results=1,
    )

    assert len(results["documents"]) == 1
    assert results["documents"][0][0] == documents[0]


def test_search_returns_metadata(tmp_path):
    vector_store = ChromaVectorStore(
        persist_directory=str(tmp_path / "chroma"),
        collection_name="test_contracts_metadata",
    )

    vector_store.add_documents(
        ids=["chunk-1"],
        documents=["Payment terms are 30 days."],
        embeddings=[[1.0, 0.0, 0.0]],
        metadatas=[
            {
                "contract_id": "CNT-001",
                "document_id": "DOC-001",
            }
        ],
    )

    results = vector_store.search(
        query_embedding=[1.0, 0.0, 0.0],
        n_results=1,
    )

    metadata = results["metadatas"][0][0]

    assert metadata["contract_id"] == "CNT-001"
    assert metadata["document_id"] == "DOC-001"