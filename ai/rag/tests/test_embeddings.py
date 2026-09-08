from ai.rag.embeddings import ContractEmbeddingService


def test_embed_documents():
    service = ContractEmbeddingService()

    texts = [
        "Payment must be completed within 30 days.",
        "The supplier must provide the required documents.",
    ]

    embeddings = service.embed_documents(texts)

    assert len(embeddings) == 2
    assert len(embeddings[0]) > 0
    assert len(embeddings[1]) > 0


def test_embed_query():
    service = ContractEmbeddingService()

    embedding = service.embed_query(
        "What are the payment terms?"
    )

    assert len(embedding) > 0


def test_similar_sentences_have_vectors():
    service = ContractEmbeddingService()

    texts = [
        "Payment must be completed within 30 days.",
        "The invoice should be paid within one month.",
    ]

    embeddings = service.embed_documents(texts)

    assert len(embeddings) == 2
    assert embeddings[0] != embeddings[1]