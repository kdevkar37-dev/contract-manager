from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.permissions import require_contract_manager
from backend.app.models.user import User
from backend.app.schemas.contract_decision import (
    ContractDecisionCreate,
    ContractDecisionHistoryResponse,
    ContractDecisionResponse,
)
from backend.app.services.audit.service import AuditLogService
from backend.app.services.decision.contract_decision_service import (
    ContractDecisionService,
)


router = APIRouter(
    prefix="/contracts",
    tags=["Contract Decision"],
)


@router.post(
    "/{contract_id}/final-decision",
    response_model=ContractDecisionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_final_decision(
    contract_id: str,
    payload: ContractDecisionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_contract_manager),
):
    service = ContractDecisionService(db)
    audit_service = AuditLogService(db)

    try:
        result = service.create_decision(
            contract_id=contract_id,
            decision=payload.decision,
            reason=payload.reason,
            decided_by=current_user.id,
        )

        audit_service.record(
            user_id=current_user.id,
            action="CONTRACT_FINAL_DECISION_CREATED",
            resource_type="contract",
            resource_id=contract_id,
            details=json.dumps(
                {
                    "decision": result.decision,
                    "reason": result.reason,
                }
            ),
        )

        db.commit()

        return result

    except ValueError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/{contract_id}/final-decision",
    response_model=ContractDecisionResponse | None,
)
def get_final_decision(
    contract_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_contract_manager),
):
    service = ContractDecisionService(db)

    try:
        return service.get_latest_decision(contract_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/{contract_id}/final-decision/history",
    response_model=ContractDecisionHistoryResponse,
)
def get_final_decision_history(
    contract_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_contract_manager),
):
    service = ContractDecisionService(db)

    try:
        decisions = service.get_decision_history(contract_id)

        return ContractDecisionHistoryResponse(
            contract_id=contract_id,
            decisions=decisions,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc