import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.permissions import require_authenticated
from backend.app.schemas.risk import RiskAnalysisResponse
from backend.app.services.audit.service import AuditLogService
from backend.app.services.risk.service import RiskAnalysisService


logger = logging.getLogger(__name__)


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

    except Exception:
        logger.exception(
            "Risk analysis retrieval failed for "
            "contract_id=%s user_id=%s",
            contract_id,
            current_user.id,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Risk analysis retrieval failed due to an internal server error.",
        )

    AuditLogService(db).record(
        user_id=current_user.id,
        action="RISK_ANALYSIS_VIEWED",
        resource_type="contract",
        resource_id=contract_id,
        details="Risk analysis was viewed.",
    )

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