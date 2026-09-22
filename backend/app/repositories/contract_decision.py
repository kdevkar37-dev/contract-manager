from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.contract_decision import ContractDecision


class ContractDecisionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        contract_id: int,
        decision: str,
        reason: str | None,
        decided_by: int,
    ) -> ContractDecision:
        contract_decision = ContractDecision(
            contract_id=contract_id,
            decision=decision,
            reason=reason,
            decided_by=decided_by,
        )

        self.db.add(contract_decision)
        self.db.flush()
        self.db.refresh(contract_decision)

        return contract_decision

    def get_by_contract_id(
        self,
        contract_id: int,
    ) -> ContractDecision | None:
        statement = (
            select(ContractDecision)
            .where(ContractDecision.contract_id == contract_id)
            .order_by(
                ContractDecision.decided_at.desc(),
                ContractDecision.id.desc(),
            )
        )

        return self.db.execute(statement).scalars().first()

    def get_history(
        self,
        contract_id: int,
    ) -> list[ContractDecision]:
        statement = (
            select(ContractDecision)
            .where(ContractDecision.contract_id == contract_id)
            .order_by(
                ContractDecision.decided_at.desc(),
                ContractDecision.id.desc(),
            )
        )

        return list(self.db.execute(statement).scalars().all())