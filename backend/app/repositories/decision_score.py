from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.decision_score import DecisionScore


class DecisionScoreRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_contract_id(self, contract_id: int) -> DecisionScore | None:
        result = self.db.execute(
            select(DecisionScore).where(
                DecisionScore.contract_id == contract_id
            )
        )
        return result.scalar_one_or_none()

    def create(self, score: DecisionScore) -> DecisionScore:
        self.db.add(score)
        self.db.commit()
        self.db.refresh(score)
        return score

    def update(self, score: DecisionScore) -> DecisionScore:
        self.db.commit()
        self.db.refresh(score)
        return score