from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.permissions import require_contract_manager
from backend.app.repositories.contracts import ContractRepository
from backend.app.repositories.financial_analysis import (
    FinancialAnalysisRepository,
)
from backend.app.repositories.risk_analysis import (
    RiskAnalysisRepository,
)
from backend.app.repositories.decision_score import (
    DecisionScoreRepository,
)
from backend.app.services.decision.automatic_scoring import (
    AutomaticDecisionScoringService,
)


router = APIRouter(
    prefix="/contracts",
    tags=["Automatic Decision Scoring"],
)


@router.post("/{contract_id}/decision-score/automatic")
def calculate_automatic_decision_score(
    contract_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_contract_manager),
):
    """
    Calculate and persist an automatic decision score
    for a contract.

    The public contract_id is resolved to the internal
    database contract.id before querying related analysis.

    Allowed roles:
        - admin
        - manager
    """

    # ---------------------------------------------------------
    # 1. Find contract using the public Contract ID
    # ---------------------------------------------------------

    contract_repository = ContractRepository(db)

    contract = contract_repository.get_by_contract_id(
        contract_id
    )

    if contract is None:
        raise HTTPException(
            status_code=404,
            detail="Contract not found",
        )

    # ---------------------------------------------------------
    # 2. Create repositories
    # ---------------------------------------------------------

    financial_repository = FinancialAnalysisRepository(db)

    risk_repository = RiskAnalysisRepository(db)

    decision_repository = DecisionScoreRepository(db)

    # ---------------------------------------------------------
    # 3. Create automatic decision scoring service
    # ---------------------------------------------------------

    service = AutomaticDecisionScoringService(
        financial_repository=financial_repository,
        risk_repository=risk_repository,
        decision_repository=decision_repository,
    )

    # ---------------------------------------------------------
    # 4. Calculate and persist decision score
    # ---------------------------------------------------------

    try:
        result = service.calculate_and_persist(
            contract.id
        )

        decision = result["decision"]

        # -----------------------------------------------------
        # 5. Return API response
        # -----------------------------------------------------

        return {
            "contract_id": contract_id,
            "score": decision.score,
            "financial_score": result["financial_score"],
            "risk_score": result["risk_score"],
            "contract_value_score": result[
                "contract_value_score"
            ],
            "explanation": result["explanation"],
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Automatic decision scoring failed: {exc}"
            ),
        ) from exc