from langchain_huggingface import HuggingFaceEmbeddings


class ContractEmbeddingService:
    def __init__(
        self,
        model_name: str = "BAAI/bge-small-en-v1.5",
    ):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.embeddings.embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        return self.embeddings.embed_query(text)