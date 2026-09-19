import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.permissions import require_contract_manager
from backend.app.services.audit.service import AuditLogService
from backend.app.services.decision.decision_workflow import (
    DecisionAnalysisWorkflow,
)


logger = logging.getLogger(__name__)


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
        result = workflow.run()

        AuditLogService(db).record(
            user_id=current_user.id,
            action="DECISION_WORKFLOW_EXECUTED",
            resource_type="decision_workflow",
            details="Contract decision-analysis workflow executed successfully.",
        )

        return result

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:
        logger.exception(
            "Decision workflow failed for user_id=%s",
            current_user.id,
        )

        raise HTTPException(
            status_code=500,
            detail="Decision workflow failed due to an internal server error.",
        )