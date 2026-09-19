from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.contract import Contract
from backend.app.models.contract_information import ContractInformation
from backend.app.models.decision_score import DecisionScore
from backend.app.repositories.contracts import ContractRepository
from backend.app.repositories.decision_score import DecisionScoreRepository
from backend.app.repositories.financial_analysis import (
    FinancialAnalysisRepository,
)
from backend.app.repositories.risk_analysis import (
    RiskAnalysisRepository,
)
from backend.app.services.decision.automatic_scoring import (
    AutomaticDecisionScoringService,
)
from backend.app.services.decision.comparison import (
    ContractComparisonInput,
    ContractComparisonService,
)
from backend.app.services.decision.eligibility import (
    ContractEligibilityService,
)
from backend.app.services.decision.scoring import (
    DecisionInputs,
    DecisionScoringEngine,
)


class CombinedDecisionService:
    """
    Combines:

        Financial Score
        Risk Score
        Contract Value Score

    into one deterministic final decision score.

    Only eligible contracts participate in the combined
    decision analysis.

    No LLM is used for numerical scoring.
    """

    def __init__(self, db: Session):
        self.db = db

        self.contract_repository = ContractRepository(db)
        self.financial_repository = FinancialAnalysisRepository(db)
        self.risk_repository = RiskAnalysisRepository(db)
        self.decision_repository = DecisionScoreRepository(db)

        self.automatic_service = AutomaticDecisionScoringService(
            financial_repository=self.financial_repository,
            risk_repository=self.risk_repository,
            decision_repository=self.decision_repository,
        )

        self.comparison_service = ContractComparisonService()

        self.scoring_engine = DecisionScoringEngine()

        self.eligibility_service = ContractEligibilityService(db)

    def calculate_for_all_contracts(self) -> list[dict]:
        """
        Calculate final decision scores only for eligible contracts.

        The process is:

            1. Load contracts with structured contract values.
            2. Filter using the eligibility service.
            3. Calculate relative contract-value scores.
            4. Calculate financial and risk scores.
            5. Combine all three scores.
            6. Persist the final DecisionScore.
        """

        comparison_inputs = self._load_contract_values()

        comparison_results = self.comparison_service.compare(
            comparison_inputs
        )

        results: list[dict] = []

        for comparison_result in comparison_results:
            contract = (
                self.contract_repository.get_by_contract_id(
                    comparison_result.contract_id
                )
            )

            if contract is None:
                continue

            if not self.eligibility_service.is_eligible(
                contract
            ):
                continue

            result = self.calculate_for_contract(
                contract_id=contract.id,
                public_contract_id=contract.contract_id,
                contract_value_score=(
                    comparison_result.contract_value_score
                ),
            )

            result["contract_value"] = (
                comparison_result.contract_value
            )

            result["rank"] = comparison_result.rank

            results.append(result)

        return results

    def calculate_for_contract(
        self,
        contract_id: int,
        public_contract_id: str,
        contract_value_score: Decimal | None,
    ) -> dict:
        """
        Calculate and persist the final decision score
        for one contract.
        """

        automatic_result = (
            self.automatic_service.calculate_decision(
                contract_id
            )
        )

        financial_score = automatic_result[
            "financial_score"
        ]

        risk_score = automatic_result[
            "risk_score"
        ]

        decision_inputs = DecisionInputs(
            financial_score=financial_score,
            risk_score=risk_score,
            contract_value_score=contract_value_score,
        )

        decision = self.scoring_engine.calculate(
            decision_inputs
        )

        explanation = self._build_explanation(
            financial_score=financial_score,
            risk_score=risk_score,
            contract_value_score=contract_value_score,
        )

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

        existing = (
            self.decision_repository.get_by_contract_id(
                contract_id
            )
        )

        if existing is None:
            decision_score = DecisionScore(
                contract_id=contract_id,
                score=decision.score,
                financial_score=financial_score,
                risk_score=risk_score,
                contract_value_score=contract_value_score,
                financial_weight=financial_weight,
                risk_weight=risk_weight,
                contract_value_weight=contract_value_weight,
                assumptions=explanation,
                explanation=explanation,
            )

            saved = self.decision_repository.create(
                decision_score
            )

        else:
            existing.score = decision.score
            existing.financial_score = financial_score
            existing.risk_score = risk_score
            existing.contract_value_score = (
                contract_value_score
            )
            existing.financial_weight = financial_weight
            existing.risk_weight = risk_weight
            existing.contract_value_weight = (
                contract_value_weight
            )
            existing.assumptions = explanation
            existing.explanation = explanation

            saved = self.decision_repository.update(
                existing
            )

        return {
            "contract_id": public_contract_id,
            "score": decision.score,
            "financial_score": financial_score,
            "risk_score": risk_score,
            "contract_value_score": contract_value_score,
            "financial_weight": financial_weight,
            "risk_weight": risk_weight,
            "contract_value_weight": contract_value_weight,
            "explanation": explanation,
            "saved": saved,
        }

    def _load_contract_values(
        self,
    ) -> list[ContractComparisonInput]:
        """
        Load contract values only from contracts that are
        eligible for decision analysis.

        This filtering happens BEFORE comparison so that an
        incomplete high-value contract cannot distort the
        relative contract-value scores of eligible contracts.
        """

        rows = self.db.execute(
            select(
                Contract,
                ContractInformation.contract_value,
            )
            .join(
                ContractInformation,
                ContractInformation.contract_id
                == Contract.id,
            )
        ).all()

        comparison_inputs: list[
            ContractComparisonInput
        ] = []

        for contract, contract_value in rows:

            if not self.eligibility_service.is_eligible(
                contract
            ):
                continue

            comparison_inputs.append(
                ContractComparisonInput(
                    contract_id=contract.contract_id,
                    contract_value=(
                        Decimal(str(contract_value))
                        if contract_value is not None
                        else None
                    ),
                )
            )

        return comparison_inputs

    @staticmethod
    def _get_weight(
        weights,
        name: str,
    ) -> Decimal | None:
        """
        Supports both dictionary-based and object-based
        weight representations.
        """

        if weights is None:
            return None

        if isinstance(weights, dict):
            value = weights.get(name)
        else:
            value = getattr(
                weights,
                name,
                None,
            )

        if value is None:
            return None

        return Decimal(str(value))

    @staticmethod
    def _build_explanation(
        financial_score: Decimal | None,
        risk_score: Decimal | None,
        contract_value_score: Decimal | None,
    ) -> str:

        parts: list[str] = []

        if financial_score is not None:
            parts.append(
                f"Financial score: {financial_score:.2f}/100."
            )
        else:
            parts.append(
                "Financial score unavailable."
            )

        if risk_score is not None:
            parts.append(
                f"Risk score: {risk_score:.2f}/100."
            )
        else:
            parts.append(
                "Risk score unavailable."
            )

        if contract_value_score is not None:
            parts.append(
                "Contract value score: "
                f"{contract_value_score:.2f}/100."
            )
        else:
            parts.append(
                "Contract value score unavailable because "
                "contract value could not be compared."
            )

        parts.append(
            "Final score is calculated using the configured "
            "deterministic decision weights."
        )

        return " ".join(parts)