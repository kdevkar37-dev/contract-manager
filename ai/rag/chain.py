from ai.rag.llm import ContractLLMService
from ai.rag.prompts import CONTRACT_RAG_PROMPT
from ai.rag.retriever import ContractRetriever


class ContractRAGChain:
    def __init__(
        self,
        retriever: ContractRetriever | None = None,
        llm_service: ContractLLMService | None = None,
    ):
        self.retriever = retriever or ContractRetriever()
        self.llm_service = llm_service or ContractLLMService()

    def ask(
        self,
        contract_id: str,
        question: str,
        n_results: int = 5,
    ) -> dict:
        results = self.retriever.retrieve(
            question=question,
            contract_id=contract_id,
            n_results=n_results,
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        if not documents:
            return {
                "answer": (
                    "The requested information was not found "
                    "in the available contract documents."
                ),
                "sources": [],
            }

        context = "\n\n".join(documents)

        prompt = CONTRACT_RAG_PROMPT.format(
            context=context,
            question=question,
        )

        answer = self.llm_service.invoke(prompt)

        sources = []

        for document, metadata in zip(documents, metadatas):
            sources.append(
                {
                    "document_id": int(metadata["document_id"]),
                    "chunk_index": int(metadata["chunk_index"]),
                    "evidence": document,
                }
            )

        return {
            "answer": answer,
            "sources": sources,
        }