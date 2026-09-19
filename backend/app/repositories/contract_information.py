from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.contract_information import ContractInformation


class ContractInformationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_contract_id(
        self,
        contract_id: int,
    ) -> ContractInformation | None:
        result = self.db.execute(
            select(ContractInformation).where(
                ContractInformation.contract_id == contract_id
            )
        )
        return result.scalar_one_or_none()

    def create(
        self,
        information: ContractInformation,
    ) -> ContractInformation:
        self.db.add(information)
        self.db.commit()
        self.db.refresh(information)
        return information

    def update(
        self,
        information: ContractInformation,
    ) -> ContractInformation:
        self.db.commit()
        self.db.refresh(information)
        return information