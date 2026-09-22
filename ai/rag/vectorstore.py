from __future__ import annotations

import chromadb

from backend.app.core.config import settings


class ChromaVectorStore:
    """
    ChromaDB vector store.

    Production usage:
        Connects to the configured ChromaDB HTTP server.

    Test/local isolated usage:
        Uses PersistentClient when persist_directory is provided.
    """

    def __init__(
        self,
        persist_directory: str | None = None,
        collection_name: str = "contracts",
    ) -> None:
        if not collection_name or not collection_name.strip():
            raise ValueError("collection_name cannot be empty.")

        self.collection_name = collection_name.strip()

        if persist_directory is not None:
            self.client = chromadb.PersistentClient(
                path=persist_directory,
            )
        else:
            self.client = chromadb.HttpClient(
                host=settings.chroma_host,
                port=settings.chroma_port,
            )

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
        )

    def add_documents(
        self,
        ids: list[str],
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict],
    ) -> None:
        """
        Add or update contract document chunks in ChromaDB.
        """
        if not ids:
            return

        if not (
            len(ids)
            == len(documents)
            == len(embeddings)
            == len(metadatas)
        ):
            raise ValueError(
                "ids, documents, embeddings, and metadatas "
                "must have the same length."
            )

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def search(
        self,
        query_embedding: list[float],
        n_results: int = 5,
        contract_id: str | None = None,
    ) -> dict:
        """
        Search contract chunks using semantic similarity.

        When contract_id is supplied, retrieval is restricted to
        that contract.
        """
        if not query_embedding:
            raise ValueError("Query embedding cannot be empty.")

        if n_results <= 0:
            raise ValueError("n_results must be greater than zero.")

        where = None

        if contract_id is not None:
            normalized_contract_id = contract_id.strip()

            if not normalized_contract_id:
                raise ValueError("contract_id cannot be empty.")

            where = {
                "contract_id": normalized_contract_id,
            }

        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
        )