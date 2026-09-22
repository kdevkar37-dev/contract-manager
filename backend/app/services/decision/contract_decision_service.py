from dataclasses import dataclass
from datetime import datetime

from backend.app.repositories.contract_decision import ContractDecisionRepository
from backend.app.repositories.contracts import ContractRepository


ALLOWED_DECISIONS = {
    "approved",
    "rejected",
    "needs_review",
}


@dataclass(frozen=True)
class ContractDecisionResult:
    contract_id: str
    decision: str
    reason: str | None
    decided_by: int
    decided_at: datetime


class ContractDecisionService:
    def __init__(self, db):
        self.db = db
        self.contract_repository = ContractRepository(db)
        self.decision_repository = ContractDecisionRepository(db)

    def create_decision(
        self,
        contract_id: str,
        decision: str,
        reason: str | None,
        decided_by: int,
    ) -> ContractDecisionResult:
        normalized_decision = decision.strip().lower()

        if normalized_decision not in ALLOWED_DECISIONS:
            raise ValueError(
                "Invalid decision. Allowed values: "
                "approved, rejected, needs_review."
            )

        contract = self.contract_repository.get_by_contract_id(contract_id)

        if contract is None:
            raise ValueError("Contract not found.")

        cleaned_reason = reason.strip() if reason else None

        saved_decision = self.decision_repository.create(
            contract_id=contract.id,
            decision=normalized_decision,
            reason=cleaned_reason,
            decided_by=decided_by,
        )

        return ContractDecisionResult(
            contract_id=contract.contract_id,
            decision=saved_decision.decision,
            reason=saved_decision.reason,
            decided_by=saved_decision.decided_by,
            decided_at=saved_decision.decided_at,
        )

    def get_latest_decision(
        self,
        contract_id: str,
    ) -> ContractDecisionResult | None:
        contract = self.contract_repository.get_by_contract_id(contract_id)

        if contract is None:
            raise ValueError("Contract not found.")

        decision = self.decision_repository.get_by_contract_id(contract.id)

        if decision is None:
            return None

        return ContractDecisionResult(
            contract_id=contract.contract_id,
            decision=decision.decision,
            reason=decision.reason,
            decided_by=decision.decided_by,
            decided_at=decision.decided_at,
        )

    def get_decision_history(
        self,
        contract_id: str,
    ) -> list[ContractDecisionResult]:
        contract = self.contract_repository.get_by_contract_id(contract_id)

        if contract is None:
            raise ValueError("Contract not found.")

        decisions = self.decision_repository.get_history(contract.id)

        return [
            ContractDecisionResult(
                contract_id=contract.contract_id,
                decision=decision.decision,
                reason=decision.reason,
                decided_by=decision.decided_by,
                decided_at=decision.decided_at,
            )
            for decision in decisions
        ]