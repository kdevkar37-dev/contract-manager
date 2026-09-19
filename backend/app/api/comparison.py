from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.permissions import require_authenticated
from backend.app.services.decision.contract_comparison_service import (
    ContractComparisonIntegrationService,
)


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

    service = ContractComparisonIntegrationService(db)

    results = service.compare_all_contracts()

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