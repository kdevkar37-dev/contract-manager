import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.permissions import require_authenticated
from backend.app.services.audit.service import AuditLogService
from backend.app.services.decision.contract_comparison_service import (
    ContractComparisonIntegrationService,
)


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/contracts",
    tags=["Contract Comparison"],
)


@router.get("/comparison")
def compare_contracts(
    db: Session = Depends(get_db),
    current_user=Depends(require_authenticated),
):
    """
    Compare all eligible contracts that have stored contract values.

    Accessible to:
        - admin
        - manager
        - viewer
    """

    try:
        service = ContractComparisonIntegrationService(db)

        results = service.compare_all_contracts()

        AuditLogService(db).record(
            user_id=current_user.id,
            action="CONTRACTS_COMPARED",
            resource_type="contract_comparison",
            details="Eligible contracts were compared successfully.",
        )

        return {
            "count": len(results),
            "contracts": [
                {
                    "contract_id": result.contract_id,
                    "contract_value": result.contract_value,
                    "contract_value_score": result.contract_value_score,
                    "rank": result.rank,
                }
                for result in results
            ],
        }

    except Exception:
        logger.exception(
            "Contract comparison failed for user_id=%s",
            current_user.id,
        )

        raise HTTPException(
            status_code=500,
            detail="Contract comparison failed due to an internal server error.",
        )