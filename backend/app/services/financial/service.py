import json
from decimal import Decimal

from sqlalchemy.orm import Session

from backend.app.models.financial_analysis import FinancialAnalysis
from backend.app.repositories.contracts import ContractRepository
from backend.app.repositories.financial_analysis import (
    FinancialAnalysisRepository,
)
from backend.app.services.financial.engine import (
    FinancialCalculationEngine,
    FinancialInputs,
)


class FinancialAnalysisService:
    def __init__(self, db: Session):
        self.contract_repository = ContractRepository(db)
        self.financial_repository = FinancialAnalysisRepository(db)
        self.engine = FinancialCalculationEngine()

    def calculate_for_contract(
        self,
        contract_id: str,
        inputs: FinancialInputs,
    ) -> FinancialAnalysis:
        contract = self.contract_repository.get_by_contract_id(
            contract_id
        )

        if contract is None:
            raise ValueError("Contract not found")

        result = self.engine.calculate(inputs)

        analysis = self.financial_repository.get_by_contract_id(
            contract.id
        )

        if analysis is None:
            analysis = FinancialAnalysis(
                contract_id=contract.id,
            )

        analysis.revenue = self._decimal_or_none(
            result.revenue
        )
        analysis.initial_investment = self._decimal_or_none(
            result.initial_investment
        )
        analysis.fixed_costs = self._decimal_or_none(
            result.fixed_costs
        )
        analysis.variable_costs = self._decimal_or_none(
            result.variable_costs
        )
        analysis.total_cost = self._decimal_or_none(
            result.total_cost
        )
        analysis.profit = self._decimal_or_none(
            result.profit
        )
        analysis.roi = self._decimal_or_none(
            result.roi
        )
        analysis.profit_margin = self._decimal_or_none(
            result.profit_margin
        )
        analysis.break_even = self._decimal_or_none(
            result.break_even
        )

        analysis.assumptions = json.dumps(
            result.assumptions
        )

        analysis.sources = json.dumps(
            result.sources
        )

        if analysis.id:
            return self.financial_repository.update(
                analysis
            )

        return self.financial_repository.create(
            analysis
        )

    def get_for_contract(
        self,
        contract_id: str,
    ) -> FinancialAnalysis | None:
        contract = self.contract_repository.get_by_contract_id(
            contract_id
        )

        if contract is None:
            raise ValueError("Contract not found")

        return self.financial_repository.get_by_contract_id(
            contract.id
        )

    @staticmethod
    def _decimal_or_none(
        value: Decimal | str,
    ) -> Decimal | None:
        if isinstance(value, Decimal):
            return value

        return None