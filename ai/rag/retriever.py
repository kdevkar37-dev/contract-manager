from ai.rag.embeddings import ContractEmbeddingService
from ai.rag.vectorstore import ChromaVectorStore


class ContractRetriever:
    def __init__(
        self,
        embedding_service: ContractEmbeddingService | None = None,
        vector_store: ChromaVectorStore | None = None,
    ):
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
        query_embedding = self.embedding_service.embed_query(
            question
        )

        return self.vector_store.search(
            query_embedding=query_embedding,
            n_results=n_results,
            contract_id=contract_id,
        )