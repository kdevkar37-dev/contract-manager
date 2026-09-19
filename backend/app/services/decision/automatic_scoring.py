from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Sequence

from backend.app.models.decision_score import DecisionScore
from backend.app.models.financial_analysis import FinancialAnalysis
from backend.app.models.risk_analysis import RiskAnalysis

from backend.app.repositories.decision_score import DecisionScoreRepository
from backend.app.repositories.financial_analysis import (
    FinancialAnalysisRepository,
)
from backend.app.repositories.risk_analysis import RiskAnalysisRepository

from backend.app.services.decision.scoring import (
    DecisionInputs,
    DecisionScoringEngine,
)


@dataclass(frozen=True)
class AutomaticDecisionInputs:
    financial_score: Decimal | None
    risk_score: Decimal | None
    contract_value_score: Decimal | None
    explanation: str


class AutomaticDecisionScoringService:
    """
    Automatically calculates and persists a contract decision score.

    Responsibilities:
    - Read financial analysis.
    - Read risk analysis.
    - Convert them into deterministic 0-100 scores.
    - Use the existing DecisionScoringEngine.
    - Persist/update the DecisionScore record.

    No LLM is used for scoring.
    """

    def __init__(
        self,
        financial_repository: FinancialAnalysisRepository,
        risk_repository: RiskAnalysisRepository,
        decision_repository: DecisionScoreRepository,
        scoring_engine: DecisionScoringEngine | None = None,
    ):
        self.financial_repository = financial_repository
        self.risk_repository = risk_repository
        self.decision_repository = decision_repository

        self.scoring_engine = (
            scoring_engine
            if scoring_engine is not None
            else DecisionScoringEngine()
        )

    def build_inputs(
        self,
        contract_id: int,
    ) -> AutomaticDecisionInputs:

        financial = self.financial_repository.get_by_contract_id(
            contract_id
        )

        risks = self.risk_repository.get_by_contract_id(
            contract_id
        )

        financial_score = self._calculate_financial_score(
            financial
        )

        risk_score = self._calculate_risk_score(
            risks
        )

        # Contract value scoring will be implemented
        # when contract comparison is added.
        contract_value_score = None

        explanation_parts: list[str] = []

        if financial_score is not None:
            explanation_parts.append(
                f"Financial score: {financial_score:.2f}/100."
            )
        else:
            explanation_parts.append(
                "Financial score unavailable because sufficient "
                "financial analysis data is not available."
            )

        if risk_score is not None:
            explanation_parts.append(
                f"Risk score: {risk_score:.2f}/100."
            )
        else:
            explanation_parts.append(
                "Risk score unavailable because no usable risk "
                "analysis data is available."
            )

        explanation_parts.append(
            "Contract value score is deferred until contracts "
            "are compared against one another."
        )

        return AutomaticDecisionInputs(
            financial_score=financial_score,
            risk_score=risk_score,
            contract_value_score=contract_value_score,
            explanation=" ".join(explanation_parts),
        )

    def calculate_decision(
        self,
        contract_id: int,
    ) -> dict:

        inputs = self.build_inputs(contract_id)

        decision_inputs = DecisionInputs(
            financial_score=inputs.financial_score,
            risk_score=inputs.risk_score,
            contract_value_score=inputs.contract_value_score,
        )

        result = self.scoring_engine.calculate(
            decision_inputs
        )

        return {
            "contract_id": contract_id,
            "score": result.score,
            "financial_score": inputs.financial_score,
            "risk_score": inputs.risk_score,
            "contract_value_score": inputs.contract_value_score,
            "explanation": inputs.explanation,
            "decision": result,
        }

    def calculate_and_persist(
        self,
        contract_id: int,
    ) -> dict:
        """
        Calculate the automatic decision score and
        create/update the corresponding database record.
        """

        result = self.calculate_decision(contract_id)

        decision = result["decision"]

        weights = decision.weights

        financial_weight = self._get_weight(
            weights,
            "financial",
        )

        risk_weight = self._get_weight(
            weights,
            "risk",
        )

        contract_value_weight = self._get_weight(
            weights,
            "contract_value",
        )

        existing = self.decision_repository.get_by_contract_id(
            contract_id
        )

        if existing is None:

            decision_score = DecisionScore(
                contract_id=contract_id,
                score=decision.score,
                financial_score=result["financial_score"],
                risk_score=result["risk_score"],
                contract_value_score=result[
                    "contract_value_score"
                ],
                financial_weight=financial_weight,
                risk_weight=risk_weight,
                contract_value_weight=contract_value_weight,
                assumptions=result["explanation"],
                explanation=result["explanation"],
            )

            saved = self.decision_repository.create(
                decision_score
            )

        else:

            existing.score = decision.score

            existing.financial_score = result[
                "financial_score"
            ]

            existing.risk_score = result[
                "risk_score"
            ]

            existing.contract_value_score = result[
                "contract_value_score"
            ]

            existing.financial_weight = financial_weight

            existing.risk_weight = risk_weight

            existing.contract_value_weight = (
                contract_value_weight
            )

            existing.assumptions = result["explanation"]

            existing.explanation = result["explanation"]

            saved = self.decision_repository.update(
                existing
            )

        result["saved"] = saved

        return result

    @staticmethod
    def _get_weight(
        weights,
        name: str,
    ) -> Decimal | None:
        """
        Supports the existing scoring engine's weight
        representation whether it is a dictionary or
        an object with attributes.
        """

        if weights is None:
            return None

        if isinstance(weights, dict):
            value = weights.get(name)

            if value is None:
                return None

            return Decimal(str(value))

        value = getattr(
            weights,
            name,
            None,
        )

        if value is None:
            return None

        return Decimal(str(value))

    @staticmethod
    def _calculate_financial_score(
        financial: FinancialAnalysis | None,
    ) -> Decimal | None:

        if financial is None:
            return None

        margin = (
            AutomaticDecisionScoringService._decimal_value(
                getattr(
                    financial,
                    "profit_margin",
                    None,
                )
            )
        )

        roi = (
            AutomaticDecisionScoringService._decimal_value(
                getattr(
                    financial,
                    "roi",
                    None,
                )
            )
        )

        components: list[
            tuple[Decimal, Decimal]
        ] = []

        if margin is not None:

            margin_score = (
                AutomaticDecisionScoringService._clamp(
                    margin,
                    Decimal("0"),
                    Decimal("100"),
                )
            )

            components.append(
                (
                    margin_score,
                    Decimal("0.60"),
                )
            )

        if roi is not None:

            roi_score = (
                AutomaticDecisionScoringService._clamp(
                    roi,
                    Decimal("0"),
                    Decimal("100"),
                )
            )

            components.append(
                (
                    roi_score,
                    Decimal("0.40"),
                )
            )

        if not components:
            return None

        total_weight = sum(
            weight
            for _, weight in components
        )

        if total_weight == 0:
            return None

        weighted_score = (
            sum(
                score * weight
                for score, weight in components
            )
            / total_weight
        )

        return weighted_score.quantize(
            Decimal("0.0001")
        )

    @staticmethod
    def _calculate_risk_score(
        risks: Sequence[RiskAnalysis] | None,
    ) -> Decimal | None:

        if not risks:
            return None

        penalties = {
            "low": Decimal("10"),
            "medium": Decimal("25"),
            "high": Decimal("50"),
            "critical": Decimal("80"),
        }

        risk_penalties: list[Decimal] = []

        for risk in risks:

            severity = getattr(
                risk,
                "severity",
                None,
            )

            if severity is None:
                continue

            normalized_severity = (
                str(severity)
                .strip()
                .lower()
            )

            penalty = penalties.get(
                normalized_severity
            )

            if penalty is not None:
                risk_penalties.append(
                    penalty
                )

        if not risk_penalties:
            return None

        average_penalty = (
            sum(risk_penalties)
            / Decimal(len(risk_penalties))
        )

        risk_score = (
            Decimal("100")
            - average_penalty
        )

        risk_score = (
            AutomaticDecisionScoringService._clamp(
                risk_score,
                Decimal("0"),
                Decimal("100"),
            )
        )

        return risk_score.quantize(
            Decimal("0.0001")
        )

    @staticmethod
    def _decimal_value(
        value,
    ) -> Decimal | None:

        if value is None:
            return None

        try:
            return Decimal(str(value))
        except (ValueError, TypeError, ArithmeticError):
            return None

    @staticmethod
    def _clamp(
        value: Decimal,
        minimum: Decimal,
        maximum: Decimal,
    ) -> Decimal:

        return max(
            minimum,
            min(value, maximum),
        )