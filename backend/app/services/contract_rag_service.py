from __future__ import annotations

from dataclasses import dataclass

from ai.rag.chain import ContractRAGChain
from backend.app.repositories.contracts import ContractRepository


@dataclass(frozen=True)
class ContractRAGResult:
    contract_id: str
    question: str
    answer: str
    sources: list[dict]


class ContractRAGService:
    """
    Application service for contract-specific RAG questions.

    Responsibilities:
        - Verify that the contract exists.
        - Delegate RAG processing to ContractRAGChain.
        - Return a stable application-level result.
    """

    def __init__(
        self,
        db,
        rag_chain: ContractRAGChain | None = None,
    ) -> None:
        self.contract_repository = ContractRepository(db)
        self.rag_chain = rag_chain or ContractRAGChain()

    def ask(
        self,
        contract_id: str,
        question: str,
    ) -> ContractRAGResult:
        if not contract_id or not contract_id.strip():
            raise ValueError("contract_id cannot be empty.")

        if not question or not question.strip():
            raise ValueError("question cannot be empty.")

        normalized_contract_id = contract_id.strip()
        normalized_question = question.strip()

        contract = self.contract_repository.get_by_contract_id(
            normalized_contract_id
        )

        if contract is None:
            raise LookupError("Contract not found.")

        result = self.rag_chain.ask(
            contract_id=normalized_contract_id,
            question=normalized_question,
        )

        return ContractRAGResult(
            contract_id=normalized_contract_id,
            question=normalized_question,
            answer=result["answer"],
            sources=result.get("sources", []),
        )