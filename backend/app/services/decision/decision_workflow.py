from __future__ import annotations

from sqlalchemy.orm import Session

from backend.app.services.decision.combined_decision_service import (
    CombinedDecisionService,
)
from backend.app.services.decision.recommendation_service import (
    ContractRecommendationIntegrationService,
)


class DecisionAnalysisWorkflow:
    """
    Runs the complete contract decision-analysis workflow.

    Flow:
        Compare contracts
        -> Calculate combined decision scores
        -> Persist scores
        -> Generate recommendations
    """

    def __init__(self, db: Session):
        self.db = db

        self.combined_decision_service = (
            CombinedDecisionService(db)
        )

        self.recommendation_service = (
            ContractRecommendationIntegrationService(db)
        )

    def run(self) -> dict:
        """
        Execute the complete decision-analysis workflow.
        """

        # -----------------------------------------------------
        # 1. Calculate combined decision scores
        # -----------------------------------------------------

        decision_results = (
            self.combined_decision_service
            .calculate_for_all_contracts()
        )

        # -----------------------------------------------------
        # 2. Generate recommendations from persisted scores
        # -----------------------------------------------------

        recommendations = (
            self.recommendation_service.recommend_all()
        )

        # -----------------------------------------------------
        # 3. Determine top-ranked contract
        # -----------------------------------------------------

        top_recommendation = (
            recommendations[0]
            if recommendations
            else None
        )

        return {
            "contracts_processed": len(
                decision_results
            ),
            "recommendations_count": len(
                recommendations
            ),
            "top_recommendation": top_recommendation,
            "recommendations": recommendations,
        }