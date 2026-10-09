import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.permissions import require_contract_manager
from backend.app.services.audit.service import AuditLogService
from backend.app.services.decision.combined_decision_service import (
    CombinedDecisionService,
)


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/contracts",
    tags=["Combined Decision"],
)


@router.post("/decision/automatic")
def calculate_combined_decision(
    db: Session = Depends(get_db),
    current_user=Depends(require_contract_manager),
):
    """
    Calculate the complete automatic decision analysis
    for all eligible contracts.

    Includes:
        - Financial score
        - Risk score
        - Contract value score
        - Final decision score
        - Contract rank

    Accessible to:
        - admin
        - manager
    """

    try:
        service = CombinedDecisionService(db)

        results = service.calculate_for_all_contracts()

        AuditLogService(db).record(
            user_id=current_user.id,
            action="COMBINED_DECISION_CALCULATED",
            resource_type="decision_analysis",
            resource_id=None,
            details=(
                f"Automatic combined decision analysis completed "
                f"for {len(results)} eligible contracts."
            ),
        )

        return {
            "count": len(results),
            "contracts": results,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "Combined decision calculation failed for user_id=%s",
            current_user.id,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Combined decision calculation failed "
                "due to an internal server error."
            ),
        ) from exc