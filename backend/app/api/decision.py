import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.permissions import (
    require_authenticated,
    require_contract_manager,
)
from backend.app.schemas.decision import (
    DecisionScoreRequest,
    DecisionScoreResponse,
)
from backend.app.services.decision.scoring import (
    DecisionInputs,
    DecisionWeights,
)
from backend.app.services.decision.service import DecisionScoringService


router = APIRouter(
    prefix="/contracts",
    tags=["Decision Scoring"],
)


# ============================================================
# CALCULATE DECISION SCORE
# ============================================================

@router.post(
    "/{contract_id}/decision-score",
    response_model=DecisionScoreResponse,
)
def calculate_decision_score(
    contract_id: str,
    request: DecisionScoreRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_contract_manager),
):
    """
    Calculate and persist a decision score for a contract.

    Accessible to:
        - admin
        - manager

    Not accessible to:
        - viewer
    """
    service = DecisionScoringService(db)

    inputs = DecisionInputs(
        financial_score=request.financial_score,
        risk_score=request.risk_score,
        contract_value_score=request.contract_value_score,
    )

    weights = None

    if request.weights is not None:
        weights = DecisionWeights(
            financial=request.weights.financial,
            risk=request.weights.risk,
            contract_value=request.weights.contract_value,
        )

    try:
        result = service.calculate_for_contract(
            contract_id=contract_id,
            inputs=inputs,
            weights=weights,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return DecisionScoreResponse(
        id=result.id,
        contract_id=contract_id,
        score=result.score,
        financial_score=result.financial_score,
        risk_score=result.risk_score,
        contract_value_score=result.contract_value_score,
        financial_weight=result.financial_weight,
        risk_weight=result.risk_weight,
        contract_value_weight=result.contract_value_weight,
        assumptions=_parse_json_list(result.assumptions),
        explanation=_parse_json_list(result.explanation),
    )


# ============================================================
# GET DECISION SCORE
# ============================================================

@router.get(
    "/{contract_id}/decision-score",
    response_model=DecisionScoreResponse | None,
)
def get_decision_score(
    contract_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_authenticated),
):
    """
    Get the existing decision score for a contract.

    Accessible to:
        - admin
        - manager
        - viewer
    """
    service = DecisionScoringService(db)

    try:
        result = service.get_for_contract(contract_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    if result is None:
        return None

    return DecisionScoreResponse(
        id=result.id,
        contract_id=contract_id,
        score=result.score,
        financial_score=result.financial_score,
        risk_score=result.risk_score,
        contract_value_score=result.contract_value_score,
        financial_weight=result.financial_weight,
        risk_weight=result.risk_weight,
        contract_value_weight=result.contract_value_weight,
        assumptions=_parse_json_list(result.assumptions),
        explanation=_parse_json_list(result.explanation),
    )


# ============================================================
# JSON LIST PARSER
# ============================================================

def _parse_json_list(value: str | None) -> list[str]:
    if not value:
        return []

    try:
        parsed = json.loads(value)

    except json.JSONDecodeError:
        return [value]

    if isinstance(parsed, list):
        return [str(item) for item in parsed]

    return [str(parsed)]