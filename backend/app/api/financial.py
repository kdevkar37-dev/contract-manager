import json
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.permissions import (
    require_authenticated,
    require_contract_manager,
)
from backend.app.schemas.financial import (
    FinancialAnalysisRequest,
    FinancialAnalysisResponse,
)
from backend.app.services.audit.service import AuditLogService
from backend.app.services.financial.engine import FinancialInputs
from backend.app.services.financial.service import FinancialAnalysisService


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/contracts",
    tags=["Financial Analysis"],
)


def _parse_json_list(value):
    if isinstance(value, list):
        return value

    if isinstance(value, str):
        try:
            parsed = json.loads(value)

            if isinstance(parsed, list):
                return parsed

        except json.JSONDecodeError:
            pass

    return []


def _build_response(contract_id: str, result):
    return FinancialAnalysisResponse(
        contract_id=contract_id,
        revenue=(
            result.revenue
            if not isinstance(result.revenue, str)
            else None
        ),
        initial_investment=(
            result.initial_investment
            if not isinstance(result.initial_investment, str)
            else None
        ),
        fixed_costs=(
            result.fixed_costs
            if not isinstance(result.fixed_costs, str)
            else None
        ),
        variable_costs=(
            result.variable_costs
            if not isinstance(result.variable_costs, str)
            else None
        ),
        total_cost=(
            result.total_cost
            if not isinstance(result.total_cost, str)
            else None
        ),
        profit=(
            result.profit
            if not isinstance(result.profit, str)
            else None
        ),
        roi=(
            result.roi
            if not isinstance(result.roi, str)
            else None
        ),
        profit_margin=(
            result.profit_margin
            if not isinstance(result.profit_margin, str)
            else None
        ),
        break_even=(
            result.break_even
            if not isinstance(result.break_even, str)
            else None
        ),
        assumptions=_parse_json_list(result.assumptions),
        sources=_parse_json_list(result.sources),
    )


# ============================================================
# CALCULATE FINANCIAL ANALYSIS
# ============================================================

@router.post(
    "/{contract_id}/financial-analysis",
    response_model=FinancialAnalysisResponse,
)
def calculate_financial_analysis(
    contract_id: str,
    request: FinancialAnalysisRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_contract_manager),
):
    """
    Calculate and persist financial analysis.

    Accessible to:
        - admin
        - manager

    Not accessible to:
        - viewer
    """

    service = FinancialAnalysisService(db)

    inputs = FinancialInputs(
        revenue=request.revenue,
        initial_investment=request.initial_investment,
        fixed_costs=request.fixed_costs,
        variable_costs=request.variable_costs,
        contribution_margin=request.contribution_margin,
        assumptions=request.assumptions,
        sources=request.sources,
    )

    try:
        result = service.calculate_for_contract(
            contract_id=contract_id,
            inputs=inputs,
        )

        AuditLogService(db).record(
            user_id=current_user.id,
            action="FINANCIAL_ANALYSIS_CALCULATED",
            resource_type="contract",
            resource_id=contract_id,
            details="Financial analysis calculated and persisted.",
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except Exception:
        logger.exception(
            "Financial analysis calculation failed for "
            "contract_id=%s user_id=%s",
            contract_id,
            current_user.id,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Financial analysis failed due to an internal server error.",
        )

    return _build_response(
        contract_id=contract_id,
        result=result,
    )


# ============================================================
# GET FINANCIAL ANALYSIS
# ============================================================

@router.get(
    "/{contract_id}/financial-analysis",
    response_model=FinancialAnalysisResponse,
)
def get_financial_analysis(
    contract_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_authenticated),
):
    """
    Get existing financial analysis.

    Accessible to:
        - admin
        - manager
        - viewer
    """

    service = FinancialAnalysisService(db)

    try:
        result = service.get_for_contract(
            contract_id=contract_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except Exception:
        logger.exception(
            "Financial analysis retrieval failed for "
            "contract_id=%s user_id=%s",
            contract_id,
            current_user.id,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Financial analysis retrieval failed due to an internal server error.",
        )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financial analysis not found",
        )

    AuditLogService(db).record(
        user_id=current_user.id,
        action="FINANCIAL_ANALYSIS_VIEWED",
        resource_type="contract",
        resource_id=contract_id,
        details="Financial analysis was viewed.",
    )

    return _build_response(
        contract_id=contract_id,
        result=result,
    )