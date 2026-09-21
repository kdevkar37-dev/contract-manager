import json
from decimal import Decimal

from sqlalchemy.orm import Session

from ai.extraction.contract_information import (
    ContractInformationExtractionService,
)
from backend.app.models.contract_information import ContractInformation
from backend.app.repositories.contract_information import (
    ContractInformationRepository,
)
from backend.app.repositories.contracts import ContractRepository


class ContractInformationService:
    def __init__(
        self,
        db: Session,
        extraction_service: ContractInformationExtractionService | None = None,
    ):
        self.contract_repository = ContractRepository(db)
        self.information_repository = ContractInformationRepository(db)
        self.extraction_service = (
            extraction_service
            if extraction_service is not None
            else ContractInformationExtractionService()
        )

    def extract_and_save(
        self,
        contract_id: str,
        contract_text: str,
    ) -> ContractInformation:
        contract = self.contract_repository.get_by_contract_id(contract_id)

        if contract is None:
            raise ValueError("Contract not found")

        extracted = self.extraction_service.extract(contract_text)

        information = self.information_repository.get_by_contract_id(
            contract.id
        )

        if information is None:
            information = ContractInformation(
                contract_id=contract.id,
            )

        information.client_name = extracted.client_name
        information.vendor_name = extracted.vendor_name

        information.contract_value = (
            Decimal(str(extracted.contract_value))
            if extracted.contract_value is not None
            else None
        )

        information.currency = extracted.currency

        information.start_date = extracted.start_date
        information.end_date = extracted.end_date

        information.payment_terms = extracted.payment_terms
        information.renewal_terms = extracted.renewal_terms
        information.termination_terms = extracted.termination_terms

        information.penalties = json.dumps(
            extracted.penalties
        )

        information.liabilities = json.dumps(
            extracted.liabilities
        )

        information.obligations = json.dumps(
            extracted.obligations
        )

        information.dependencies = json.dumps(
            extracted.dependencies
        )

        if information.id:
            return self.information_repository.update(information)

        return self.information_repository.create(information)

    def get_for_contract(
        self,
        contract_id: str,
    ) -> ContractInformation | None:
        contract = self.contract_repository.get_by_contract_id(contract_id)

        if contract is None:
            raise ValueError("Contract not found")

        return self.information_repository.get_by_contract_id(
            contract.id
        )

    @staticmethod
    def parse_list(value: str | None) -> list[str]:
        if not value:
            return []

        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return [value]

        if not isinstance(parsed, list):
            return [str(parsed)]

        return [str(item) for item in parsed]