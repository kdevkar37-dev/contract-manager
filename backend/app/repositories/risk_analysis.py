from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.app.models.risk_analysis import RiskAnalysis


class RiskAnalysisRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_contract_id(
        self,
        contract_id: int,
    ) -> list[RiskAnalysis]:
        result = self.db.execute(
            select(RiskAnalysis)
            .where(
                RiskAnalysis.contract_id == contract_id
            )
            .order_by(RiskAnalysis.id)
        )

        return list(result.scalars().all())

    def create(
        self,
        risk: RiskAnalysis,
    ) -> RiskAnalysis:
        self.db.add(risk)
        self.db.commit()
        self.db.refresh(risk)

        return risk

    def create_many(
        self,
        risks: list[RiskAnalysis],
    ) -> list[RiskAnalysis]:
        if not risks:
            return []

        self.db.add_all(risks)
        self.db.commit()

        for risk in risks:
            self.db.refresh(risk)

        return risks

    def delete_by_contract_id(
        self,
        contract_id: int,
    ) -> None:
        self.db.execute(
            delete(RiskAnalysis).where(
                RiskAnalysis.contract_id == contract_id
            )
        )

        self.db.commit()
        