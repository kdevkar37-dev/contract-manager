from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.contract import Contract
from backend.app.models.contract_information import ContractInformation
from backend.app.services.decision.comparison import (
    ContractComparisonInput,
    ContractComparisonService,
)


class ContractComparisonIntegrationService:
    """
    Loads contracts and their stored contract values from PostgreSQL
    and passes them to the deterministic comparison engine.
    """

    def __init__(self, db: Session):
        self.db = db
        self.comparison_service = ContractComparisonService()

    def compare_all_contracts(self):
        rows = self.db.execute(
            select(
                Contract.contract_id,
                ContractInformation.contract_value,
            )
            .join(
                ContractInformation,
                ContractInformation.contract_id == Contract.id,
            )
        ).all()

        contracts = [
            ContractComparisonInput(
                contract_id=contract_id,
                contract_value=(
                    Decimal(str(contract_value))
                    if contract_value is not None
                    else None
                ),
            )
            for contract_id, contract_value in rows
        ]

        return self.comparison_service.compare(contracts)