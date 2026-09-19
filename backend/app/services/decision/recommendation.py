from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Sequence


@dataclass(frozen=True)
class ContractDecisionResult:
    contract_id: str
    final_score: Decimal | None
    financial_score: Decimal | None
    risk_score: Decimal | None
    contract_value_score: Decimal | None


@dataclass(frozen=True)
class ContractRecommendation:
    contract_id: str
    final_score: Decimal
    rank: int
    financial_score: Decimal | None
    risk_score: Decimal | None
    contract_value_score: Decimal | None
    explanation: str


class ContractRecommendationService:
    """
    Deterministically ranks contracts using their final
    decision scores.

    The service does not make calculations using an LLM.
    """

    def recommend(
        self,
        contracts: Sequence[ContractDecisionResult],
    ) -> list[ContractRecommendation]:

        valid_contracts = [
            contract
            for contract in contracts
            if contract.final_score is not None
        ]

        if not valid_contracts:
            return []

        sorted_contracts = sorted(
            valid_contracts,
            key=lambda contract: contract.final_score,
            reverse=True,
        )

        recommendations: list[ContractRecommendation] = []

        current_rank = 0
        previous_score: Decimal | None = None

        for position, contract in enumerate(
            sorted_contracts,
            start=1,
        ):
            score = contract.final_score

            if score != previous_score:
                current_rank = position
                previous_score = score

            explanation = self._build_explanation(contract)

            recommendations.append(
                ContractRecommendation(
                    contract_id=contract.contract_id,
                    final_score=score,
                    rank=current_rank,
                    financial_score=contract.financial_score,
                    risk_score=contract.risk_score,
                    contract_value_score=contract.contract_value_score,
                    explanation=explanation,
                )
            )

        return recommendations

    @staticmethod
    def _build_explanation(
        contract: ContractDecisionResult,
    ) -> str:
        parts: list[str] = [
            f"Final decision score: "
            f"{contract.final_score:.4f}/100."
        ]

        if contract.financial_score is not None:
            parts.append(
                f"Financial score: "
                f"{contract.financial_score:.4f}/100."
            )

        if contract.risk_score is not None:
            parts.append(
                f"Risk score: "
                f"{contract.risk_score:.4f}/100."
            )

        if contract.contract_value_score is not None:
            parts.append(
                f"Contract value score: "
                f"{contract.contract_value_score:.4f}/100."
            )

        return " ".join(parts)