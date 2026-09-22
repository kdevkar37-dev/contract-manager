from __future__ import annotations

from langchain_huggingface import HuggingFaceEmbeddings


DEFAULT_EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"


class ContractEmbeddingService:
    """
    Generates local embeddings for contract documents and queries.

    The service uses a Hugging Face BGE model locally, so no external
    embedding API or API key is required.
    """

    def __init__(
        self,
        model_name: str = DEFAULT_EMBEDDING_MODEL,
    ) -> None:
        if not model_name.strip():
            raise ValueError("Embedding model name cannot be empty.")

        self.model_name = model_name

        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            encode_kwargs={
                "normalize_embeddings": True,
            },
        )

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Convert multiple document chunks into normalized embeddings.
        """
        if not texts:
            return []

        cleaned_texts = [
            text.strip()
            for text in texts
            if text and text.strip()
        ]

        if not cleaned_texts:
            return []

        return self.embeddings.embed_documents(cleaned_texts)

    def embed_query(
        self,
        text: str,
    ) -> list[float]:
        """
        Convert a user query into a normalized embedding.
        """
        if not text or not text.strip():
            raise ValueError("Query text cannot be empty.")

        return self.embeddings.embed_query(text.strip())