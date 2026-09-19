from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.permissions import require_authenticated
from backend.app.services.decision.recommendation_service import (
    ContractRecommendationIntegrationService,
)


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

        return {
            "count": len(recommendations),
            "recommendations": recommendations,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Recommendation generation failed: {exc}",
        ) from exc