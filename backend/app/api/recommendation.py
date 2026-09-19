import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.permissions import require_authenticated
from backend.app.services.audit.service import AuditLogService
from backend.app.services.decision.recommendation_service import (
    ContractRecommendationIntegrationService,
)


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/contracts",
    tags=["Contract Recommendation"],
)


@router.get("/recommendation")
def get_contract_recommendations(
    db: Session = Depends(get_db),
    current_user=Depends(require_authenticated),
):
    """
    Return eligible contracts ranked by their persisted final
    decision score.

    Accessible to:
        - admin
        - manager
        - viewer
    """

    try:
        service = ContractRecommendationIntegrationService(db)

        recommendations = service.recommend_all()

        AuditLogService(db).record(
            user_id=current_user.id,
            action="RECOMMENDATIONS_GENERATED",
            resource_type="contract_recommendation",
            details="Contract recommendations were generated successfully.",
        )

        return {
            "count": len(recommendations),
            "recommendations": recommendations,
        }

    except Exception:
        logger.exception(
            "Recommendation generation failed for user_id=%s",
            current_user.id,
        )

        raise HTTPException(
            status_code=500,
            detail="Recommendation generation failed due to an internal server error.",
        )