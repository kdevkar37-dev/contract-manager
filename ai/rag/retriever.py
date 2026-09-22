from __future__ import annotations

from ai.rag.embeddings import ContractEmbeddingService
from ai.rag.vectorstore import ChromaVectorStore


class ContractRetriever:
    """
    Retrieves relevant chunks from a specific contract using
    semantic similarity.
    """

    def __init__(
        self,
        embedding_service: ContractEmbeddingService | None = None,
        vector_store: ChromaVectorStore | None = None,
    ) -> None:
        self.embedding_service = (
            embedding_service or ContractEmbeddingService()
        )
        self.vector_store = vector_store or ChromaVectorStore()

    def retrieve(
        self,
        question: str,
        contract_id: str,
        n_results: int = 5,
    ) -> dict:
        """
        Retrieve relevant contract chunks for a question.

        Retrieval is always restricted to the requested contract.
        """
        if not question or not question.strip():
            raise ValueError("question cannot be empty.")

        if not contract_id or not contract_id.strip():
            raise ValueError("contract_id cannot be empty.")

        if n_results <= 0:
            raise ValueError("n_results must be greater than zero.")

        query_embedding = self.embedding_service.embed_query(
            question.strip()
        )

        return self.vector_store.search(
            query_embedding=query_embedding,
            n_results=n_results,
            contract_id=contract_id.strip(),
        )