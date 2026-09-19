from dataclasses import dataclass, field
from decimal import Decimal
from typing import Mapping


@dataclass(frozen=True)
class DecisionWeights:
    """
    Configurable weights used for contract decision scoring.

    All weights must be non-negative and their total must
    equal 100.
    """

    financial: Decimal = Decimal("50")
    risk: Decimal = Decimal("30")
    contract_value: Decimal = Decimal("20")

    def validate(self) -> None:
        weights = (
            self.financial,
            self.risk,
            self.contract_value,
        )

        if any(weight < 0 for weight in weights):
            raise ValueError(
                "Decision weights cannot be negative."
            )

        total = sum(weights)

        if total != Decimal("100"):
            raise ValueError(
                "Decision weights must total 100."
            )


@dataclass(frozen=True)
class DecisionInputs:
    """
    Normalized component scores.

    Every score must be between 0 and 100.

    financial_score:
        Higher score means stronger financial performance.

    risk_score:
        Higher score means lower contract risk.

    contract_value_score:
        Higher score means greater relative contract value.
    """

    financial_score: Decimal | None = None
    risk_score: Decimal | None = None
    contract_value_score: Decimal | None = None


@dataclass(frozen=True)
class DecisionScore:
    """
    Final deterministic decision score.

    score:
        Final score between 0 and 100.

    component_scores:
        Individual normalized component scores.

    weighted_scores:
        Contribution of each component to the final score.

    weights:
        Weights used for the calculation.

    assumptions:
        Information about scoring assumptions.

    explanation:
        Human-readable deterministic explanation.
    """

    score: Decimal | str
    component_scores: Mapping[str, Decimal | str]
    weighted_scores: Mapping[str, Decimal | str]
    weights: Mapping[str, Decimal]
    assumptions: list[str] = field(default_factory=list)
    explanation: list[str] = field(default_factory=list)


class DecisionScoringEngine:
    """
    Deterministic contract decision scoring engine.

    This service:
    - Performs only deterministic calculations.
    - Does not use an LLM.
    - Does not access the database.
    - Does not retrieve documents.
    - Does not make unsupported assumptions.

    Scores are expected to be normalized to 0-100 before
    entering this engine.
    """

    MIN_SCORE = Decimal("0")
    MAX_SCORE = Decimal("100")
    INSUFFICIENT_DATA = "Insufficient data"

    @classmethod
    def to_decimal(
        cls,
        value: Decimal | int | float | str | None,
    ) -> Decimal | None:
        if value is None:
            return None

        try:
            return Decimal(str(value))
        except Exception as exc:
            raise ValueError(
                f"Invalid decision score: {value}"
            ) from exc

    @classmethod
    def validate_score(
        cls,
        value: Decimal | None,
        field_name: str,
    ) -> None:
        if value is None:
            return

        if value < cls.MIN_SCORE or value > cls.MAX_SCORE:
            raise ValueError(
                f"{field_name} must be between 0 and 100."
            )

    @classmethod
    def calculate(
        cls,
        inputs: DecisionInputs,
        weights: DecisionWeights | None = None,
    ) -> DecisionScore:
        """
        Calculate the final decision score.

        If a component is missing, its weight is excluded and
        the remaining available weights are normalized.

        This prevents missing information from automatically
        becoming a score of zero.
        """

        weights = (
            weights
            if weights is not None
            else DecisionWeights()
        )

        weights.validate()

        financial_score = cls.to_decimal(
            inputs.financial_score
        )

        risk_score = cls.to_decimal(
            inputs.risk_score
        )

        contract_value_score = cls.to_decimal(
            inputs.contract_value_score
        )

        cls.validate_score(
            financial_score,
            "Financial score",
        )

        cls.validate_score(
            risk_score,
            "Risk score",
        )

        cls.validate_score(
            contract_value_score,
            "Contract value score",
        )

        available_components: dict[str, tuple[
            Decimal,
            Decimal,
        ]] = {}

        if financial_score is not None:
            available_components["financial"] = (
                financial_score,
                weights.financial,
            )

        if risk_score is not None:
            available_components["risk"] = (
                risk_score,
                weights.risk,
            )

        if contract_value_score is not None:
            available_components["contract_value"] = (
                contract_value_score,
                weights.contract_value,
            )

        if not available_components:
            return DecisionScore(
                score=cls.INSUFFICIENT_DATA,
                component_scores={
                    "financial": cls.INSUFFICIENT_DATA,
                    "risk": cls.INSUFFICIENT_DATA,
                    "contract_value": cls.INSUFFICIENT_DATA,
                },
                weighted_scores={
                    "financial": cls.INSUFFICIENT_DATA,
                    "risk": cls.INSUFFICIENT_DATA,
                    "contract_value": cls.INSUFFICIENT_DATA,
                },
                weights={
                    "financial": weights.financial,
                    "risk": weights.risk,
                    "contract_value": weights.contract_value,
                },
                assumptions=[
                    "No decision-scoring components were available."
                ],
                explanation=[
                    "Decision score cannot be calculated "
                    "because insufficient data is available."
                ],
            )

        available_weight_total = sum(
            weight
            for _, weight in available_components.values()
        )

        if available_weight_total == 0:
            return DecisionScore(
                score=cls.INSUFFICIENT_DATA,
                component_scores={
                    "financial": cls._score_or_insufficient(
                        financial_score
                    ),
                    "risk": cls._score_or_insufficient(
                        risk_score
                    ),
                    "contract_value": cls._score_or_insufficient(
                        contract_value_score
                    ),
                },
                weighted_scores={
                    "financial": cls.INSUFFICIENT_DATA,
                    "risk": cls.INSUFFICIENT_DATA,
                    "contract_value": cls.INSUFFICIENT_DATA,
                },
                weights={
                    "financial": weights.financial,
                    "risk": weights.risk,
                    "contract_value": weights.contract_value,
                },
                assumptions=[
                    "Available scoring components have zero total weight."
                ],
                explanation=[
                    "Decision score cannot be calculated "
                    "because available weights total zero."
                ],
            )

        weighted_scores: dict[str, Decimal | str] = {
            "financial": cls.INSUFFICIENT_DATA,
            "risk": cls.INSUFFICIENT_DATA,
            "contract_value": cls.INSUFFICIENT_DATA,
        }

        component_scores: dict[str, Decimal | str] = {
            "financial": cls._score_or_insufficient(
                financial_score
            ),
            "risk": cls._score_or_insufficient(
                risk_score
            ),
            "contract_value": cls._score_or_insufficient(
                contract_value_score
            ),
        }

        total_score = Decimal("0")

        for component, (
            component_score,
            component_weight,
        ) in available_components.items():
            normalized_weight = (
                component_weight
                / available_weight_total
            )

            contribution = (
                component_score
                * normalized_weight
            )

            weighted_scores[component] = contribution
            total_score += contribution

        total_score = total_score.quantize(
            Decimal("0.0001")
        )

        assumptions = [
            "Component scores are normalized to a 0-100 scale.",
            "Missing components are excluded from the calculation.",
            "Available component weights are re-normalized "
            "to preserve a 0-100 final score.",
        ]

        explanation = cls._build_explanation(
            component_scores=component_scores,
            weighted_scores=weighted_scores,
            final_score=total_score,
        )

        return DecisionScore(
            score=total_score,
            component_scores=component_scores,
            weighted_scores=weighted_scores,
            weights={
                "financial": weights.financial,
                "risk": weights.risk,
                "contract_value": weights.contract_value,
            },
            assumptions=assumptions,
            explanation=explanation,
        )

    @classmethod
    def _build_explanation(
        cls,
        component_scores: Mapping[
            str,
            Decimal | str,
        ],
        weighted_scores: Mapping[
            str,
            Decimal | str,
        ],
        final_score: Decimal,
    ) -> list[str]:
        explanation: list[str] = []

        component_names = {
            "financial": "Financial performance",
            "risk": "Risk",
            "contract_value": "Contract value",
        }

        for component, name in component_names.items():
            score = component_scores[component]
            contribution = weighted_scores[component]

            if isinstance(score, Decimal):
                explanation.append(
                    f"{name} score: {score}."
                )

                if isinstance(contribution, Decimal):
                    explanation.append(
                        f"{name} contribution to final score: "
                        f"{contribution}."
                    )

        explanation.append(
            f"Final decision score: {final_score} out of 100."
        )

        return explanation

    @classmethod
    def _score_or_insufficient(
        cls,
        value: Decimal | None,
    ) -> Decimal | str:
        if value is None:
            return cls.INSUFFICIENT_DATA

        return value