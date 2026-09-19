import json
from decimal import Decimal

from sqlalchemy.orm import Session

from backend.app.models.decision_score import DecisionScore
from backend.app.repositories.contracts import ContractRepository
from backend.app.repositories.decision_score import DecisionScoreRepository
from backend.app.services.decision.scoring import (
    DecisionInputs,
    DecisionScoringEngine,
    DecisionWeights,
)


class DecisionScoringService:
    def __init__(self, db: Session):
        self.contract_repository = ContractRepository(db)
        self.decision_repository = DecisionScoreRepository(db)
        self.engine = DecisionScoringEngine()

    def calculate_for_contract(
        self,
        contract_id: str,
        inputs: DecisionInputs,
        weights: DecisionWeights | None = None,
    ) -> DecisionScore:
        contract = self.contract_repository.get_by_contract_id(contract_id)

        if contract is None:
            raise ValueError("Contract not found")

        result = self.engine.calculate(
            inputs=inputs,
            weights=weights,
        )

        weights = weights or DecisionWeights()

        score = self.decision_repository.get_by_contract_id(contract.id)

        if score is None:
            score = DecisionScore(contract_id=contract.id)

        score.score = self._decimal_or_none(result.score)

        score.financial_score = self._decimal_or_none(
            result.component_scores["financial"]
        )

        score.risk_score = self._decimal_or_none(
            result.component_scores["risk"]
        )

        score.contract_value_score = self._decimal_or_none(
            result.component_scores["contract_value"]
        )

        score.financial_weight = weights.financial
        score.risk_weight = weights.risk
        score.contract_value_weight = weights.contract_value

        score.assumptions = json.dumps(result.assumptions)
        score.explanation = json.dumps(result.explanation)

        if score.id:
            return self.decision_repository.update(score)

        return self.decision_repository.create(score)

    def get_for_contract(
        self,
        contract_id: str,
    ) -> DecisionScore | None:
        contract = self.contract_repository.get_by_contract_id(contract_id)

        if contract is None:
            raise ValueError("Contract not found")

        return self.decision_repository.get_by_contract_id(contract.id)

    @staticmethod
    def _decimal_or_none(
        value: Decimal | str,
    ) -> Decimal | None:
        if isinstance(value, Decimal):
            return value

        return None