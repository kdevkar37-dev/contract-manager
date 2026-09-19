from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.permissions import require_authenticated
from backend.app.schemas.risk import RiskAnalysisResponse
from backend.app.services.risk.service import RiskAnalysisService


router = APIRouter(
    prefix="/contracts",
    tags=["Risk Analysis"],
)


@router.get(
    "/{contract_id}/risks",
    response_model=list[RiskAnalysisResponse],
)
def get_contract_risks(
    contract_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_authenticated),
):
    """
    Get all risks identified for a contract.

    Accessible to:
        - admin
        - manager
        - viewer
    """
    service = RiskAnalysisService(db)

    try:
        risks = service.get_risks(
            contract_id=contract_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return [
        RiskAnalysisResponse(
            id=risk.id,
            contract_id=contract_id,
            risk_type=risk.risk_type,
            severity=risk.severity,
            title=risk.title,
            description=risk.description,
            evidence=risk.evidence,
            source=risk.source,
            confidence=risk.confidence,
        )
        for risk in risks
    ]