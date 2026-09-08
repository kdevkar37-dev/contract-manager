from ai.rag.chunking import ContractTextChunker
from ai.rag.embeddings import ContractEmbeddingService
from ai.rag.vectorstore import ChromaVectorStore


class ContractRAGIngestionService:
    def __init__(
        self,
        chunker: ContractTextChunker | None = None,
        embedding_service: ContractEmbeddingService | None = None,
        vector_store: ChromaVectorStore | None = None,
    ):
        self.chunker = chunker or ContractTextChunker()
        self.embedding_service = (
            embedding_service or ContractEmbeddingService()
        )
        self.vector_store = vector_store or ChromaVectorStore()

    def ingest(
        self,
        contract_id: str,
        document_id: int,
        text: str,
    ) -> int:
        chunks = self.chunker.split_text(text)

        if not chunks:
            return 0

        embeddings = self.embedding_service.embed_documents(chunks)

        ids = [
            f"{contract_id}-document-{document_id}-chunk-{index}"
            for index in range(len(chunks))
        ]

        metadatas = [
            {
                "contract_id": contract_id,
                "document_id": str(document_id),
                "chunk_index": index,
            }
            for index in range(len(chunks))
        ]

        self.vector_store.add_documents(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        return len(chunks)