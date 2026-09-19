from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.permissions import require_contract_manager
from backend.app.services.decision.decision_workflow import (
    DecisionAnalysisWorkflow,
)


router = APIRouter(
    prefix="/contracts",
    tags=["Decision Workflow"],
)


@router.post("/decision/workflow")
def run_decision_workflow(
    db: Session = Depends(get_db),
    current_user=Depends(require_contract_manager),
):
    """
    Run the complete contract decision-analysis workflow.

    Flow:
        Combined Decision Scoring
        -> Persist Decision Scores
        -> Generate Recommendations

    Allowed roles:
        - admin
        - manager
    """

    try:
        workflow = DecisionAnalysisWorkflow(db)
        return workflow.run()

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Decision workflow failed: {exc}",
        ) from exc