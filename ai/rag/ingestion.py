from __future__ import annotations

from ai.rag.chunking import ContractTextChunker
from ai.rag.embeddings import ContractEmbeddingService
from ai.rag.vectorstore import ChromaVectorStore


class ContractRAGIngestionService:
    """
    Handles the contract RAG ingestion pipeline.

    Flow:
        Text
          ↓
        Chunking
          ↓
        Embeddings
          ↓
        ChromaDB
    """

    def __init__(
        self,
        chunker: ContractTextChunker | None = None,
        embedding_service: ContractEmbeddingService | None = None,
        vector_store: ChromaVectorStore | None = None,
    ) -> None:
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
        """
        Process and index contract text.

        Returns:
            Number of chunks indexed.

        Empty text is treated as having nothing to index and
        therefore returns 0.
        """
        if not contract_id or not contract_id.strip():
            raise ValueError("contract_id cannot be empty.")

        if document_id <= 0:
            raise ValueError("document_id must be greater than zero.")

        if not text or not text.strip():
            return 0

        normalized_contract_id = contract_id.strip()
        normalized_text = text.strip()

        chunks = self.chunker.split_text(normalized_text)

        if not chunks:
            return 0

        embeddings = self.embedding_service.embed_documents(chunks)

        if len(embeddings) != len(chunks):
            raise ValueError(
                "Number of embeddings must match number of chunks."
            )

        ids = [
            (
                f"{normalized_contract_id}"
                f"-document-{document_id}"
                f"-chunk-{index}"
            )
            for index in range(len(chunks))
        ]

        metadatas = [
            {
                "contract_id": normalized_contract_id,
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