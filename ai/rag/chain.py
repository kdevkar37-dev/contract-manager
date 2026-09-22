from __future__ import annotations

from ai.rag.llm import ContractLLMService
from ai.rag.prompts import CONTRACT_RAG_PROMPT
from ai.rag.retriever import ContractRetriever


NO_INFORMATION_MESSAGE = (
    "The requested information was not found "
    "in the available contract documents."
)


class ContractRAGChain:
    """
    Coordinates contract-specific retrieval and grounded LLM generation.

    Flow:
        Question
            ↓
        ContractRetriever
            ↓
        Relevant contract chunks
            ↓
        Grounded prompt
            ↓
        Local LLM
            ↓
        Answer + evidence
    """

    def __init__(
        self,
        retriever: ContractRetriever | None = None,
        llm_service: ContractLLMService | None = None,
    ) -> None:
        self.retriever = retriever or ContractRetriever()
        self.llm_service = llm_service or ContractLLMService()

    def ask(
        self,
        contract_id: str,
        question: str,
        n_results: int = 5,
    ) -> dict:
        """
        Ask a question about a specific contract.

        The answer is generated only from chunks retrieved for the
        requested contract.
        """
        if not contract_id or not contract_id.strip():
            raise ValueError("contract_id cannot be empty.")

        if not question or not question.strip():
            raise ValueError("question cannot be empty.")

        if n_results <= 0:
            raise ValueError("n_results must be greater than zero.")

        normalized_contract_id = contract_id.strip()
        normalized_question = question.strip()

        results = self.retriever.retrieve(
            question=normalized_question,
            contract_id=normalized_contract_id,
            n_results=n_results,
        )

        documents = results.get("documents") or [[]]
        metadatas = results.get("metadatas") or [[]]

        documents = documents[0] if documents else []
        metadatas = metadatas[0] if metadatas else []

        if not documents:
            return {
                "answer": NO_INFORMATION_MESSAGE,
                "sources": [],
            }

        context = "\n\n".join(
            document.strip()
            for document in documents
            if document and document.strip()
        )

        if not context:
            return {
                "answer": NO_INFORMATION_MESSAGE,
                "sources": [],
            }

        prompt = CONTRACT_RAG_PROMPT.format(
            context=context,
            question=normalized_question,
        )

        answer = self.llm_service.invoke(prompt)

        sources = []

        for document, metadata in zip(documents, metadatas):
            if not document or not metadata:
                continue

            document_id = metadata.get("document_id")
            chunk_index = metadata.get("chunk_index")

            if document_id is None or chunk_index is None:
                continue

            try:
                document_id = int(document_id)
                chunk_index = int(chunk_index)
            except (TypeError, ValueError):
                continue

            sources.append(
                {
                    "document_id": document_id,
                    "chunk_index": chunk_index,
                    "evidence": document,
                }
            )

        return {
            "answer": answer,
            "sources": sources,
        }