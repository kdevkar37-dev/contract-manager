from sqlalchemy.orm import Session

from backend.app.models.contract import Contract
from backend.app.repositories.contracts import ContractRepository
from backend.app.schemas.contract import ContractCreate, ContractUpdate


class ContractService:
    def __init__(self, db: Session):
        self.repository = ContractRepository(db)

    def get_all_contracts(self) -> list[Contract]:
        return self.repository.get_all()

    def get_contract_by_id(
        self,
        contract_id: str,
    ) -> Contract | None:
        return self.repository.get_by_contract_id(contract_id)

    def create_contract(
        self,
        contract_data: ContractCreate,
    ) -> Contract:
        contract = Contract(
            contract_id=contract_data.contract_id,
            name=contract_data.name,
            description=contract_data.description,
            start_date=contract_data.start_date,
            end_date=contract_data.end_date,
        )

        return self.repository.create(contract)

    def update_contract(
        self,
        contract_id: str,
        contract_data: ContractUpdate,
    ) -> Contract | None:
        contract = self.repository.get_by_contract_id(
            contract_id
        )

        if contract is None:
            return None

        update_data = contract_data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(contract, field, value)

        return self.repository.update(contract)