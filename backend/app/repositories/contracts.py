from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.contract import Contract


class ContractRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Contract]:
        result = self.db.execute(
            select(Contract)
        )

        return list(result.scalars().all())

    def get_by_contract_id(
        self,
        contract_id: str,
    ) -> Contract | None:
        result = self.db.execute(
            select(Contract).where(
                Contract.contract_id == contract_id
            )
        )

        return result.scalar_one_or_none()

    def create(self, contract: Contract) -> Contract:
        try:
            self.db.add(contract)
            self.db.commit()
            self.db.refresh(contract)

            return contract

        except IntegrityError:
            self.db.rollback()
            raise

    def update(self, contract: Contract) -> Contract:
        try:
            self.db.commit()
            self.db.refresh(contract)

            return contract

        except IntegrityError:
            self.db.rollback()
            raise