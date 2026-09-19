from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.services.decision.combined_decision_service import (
    CombinedDecisionService,
)

router = APIRouter(
    prefix="/contracts",
    tags=["Combined Decision"],
)


@router.post("/decision/automatic")
def calculate_combined_decision(
    db: Session = Depends(get_db),
):
    """
    Calculate the complete automatic decision analysis
    for all contracts.

    Includes:
    - Financial score
    - Risk score
    - Contract value score
    - Final decision score
    - Contract rank
    """

    try:
        service = CombinedDecisionService(db)

        results = service.calculate_for_all_contracts()

        return {
            "count": len(results),
            "contracts": results,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Combined decision calculation failed: {exc}",
        ) from exc