from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.permissions import require_authenticated
from backend.app.repositories.contract_information import (
    ContractInformationRepository,
)
from backend.app.repositories.contracts import ContractRepository


router = APIRouter(
    prefix="/contracts",
    tags=["Contract Information"],
)


@router.get("/{contract_id}/information")
def get_contract_information(
    contract_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_authenticated),
):
    """
    Get structured information extracted from a contract.

    Accessible to:
        - admin
        - manager
        - viewer
    """

    contract_repository = ContractRepository(db)

    information_repository = ContractInformationRepository(db)

    contract = contract_repository.get_by_contract_id(
        contract_id
    )

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found",
        )

    information = information_repository.get_by_contract_id(
        contract.id
    )

    if information is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract information not found",
        )

    return {
        "contract_id": contract.contract_id,
        "client_name": information.client_name,
        "vendor_name": information.vendor_name,
        "contract_value": (
            float(information.contract_value)
            if information.contract_value is not None
            else None
        ),
        "currency": information.currency,
        "payment_terms": information.payment_terms,
        "renewal_terms": information.renewal_terms,
        "termination_terms": information.termination_terms,
        "obligations": (
            information.obligations.splitlines()
            if information.obligations
            else []
        ),
        "dependencies": (
            information.dependencies.splitlines()
            if information.dependencies
            else []
        ),
        "created_at": information.created_at,
        "updated_at": information.updated_at,
    }