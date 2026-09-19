from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.financial_analysis import FinancialAnalysis


class FinancialAnalysisRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_contract_id(
        self,
        contract_id: int,
    ) -> FinancialAnalysis | None:
        result = self.db.execute(
            select(FinancialAnalysis).where(
                FinancialAnalysis.contract_id == contract_id
            )
        )

        return result.scalar_one_or_none()

    def create(
        self,
        analysis: FinancialAnalysis,
    ) -> FinancialAnalysis:
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)

        return analysis

    def update(
        self,
        analysis: FinancialAnalysis,
    ) -> FinancialAnalysis:
        self.db.commit()
        self.db.refresh(analysis)

        return analysis