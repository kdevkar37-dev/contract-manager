import chromadb


class ChromaVectorStore:
    def __init__(
        self,
        persist_directory: str = "chroma_data",
        collection_name: str = "contracts",
    ):
        self.client = chromadb.PersistentClient(
            path=persist_directory,
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
        )

    def add_documents(
        self,
        ids: list[str],
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict],
    ) -> None:
        self.collection.add(
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
        where = None

        if contract_id is not None:
            where = {
                "contract_id": contract_id,
            }

        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
        )