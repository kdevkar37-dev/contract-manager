from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from backend.app.services.financial.engine import FinancialInputs
from backend.app.services.financial.service import FinancialAnalysisService


def test_calculate_for_contract_creates_analysis():
    db = MagicMock()

    contract = MagicMock()
    contract.id = 1
    contract.contract_id = "CNT-001"

    contract_repository = MagicMock()
    contract_repository.get_by_contract_id.return_value = contract

    financial_repository = MagicMock()
    financial_repository.get_by_contract_id.return_value = None

    service = FinancialAnalysisService(db)
    service.contract_repository = contract_repository
    service.financial_repository = financial_repository

    inputs = FinancialInputs(
        revenue=Decimal("100000"),
        initial_investment=Decimal("20000"),
        fixed_costs=Decimal("30000"),
        variable_costs=Decimal("20000"),
        contribution_margin=Decimal("0.5"),
        assumptions=[
            "Revenue estimated from contract value"
        ],
        sources=[
            "Contract Section 5"
        ],
    )

    result = service.calculate_for_contract(
        contract_id="CNT-001",
        inputs=inputs,
    )

    saved_analysis = (
        financial_repository.create.call_args.args[0]
    )

    assert saved_analysis.contract_id == 1
    assert saved_analysis.revenue == Decimal("100000")
    assert saved_analysis.total_cost == Decimal("50000")
    assert saved_analysis.profit == Decimal("50000")
    assert saved_analysis.roi == Decimal("250")
    assert saved_analysis.profit_margin == Decimal("50")
    assert saved_analysis.break_even == Decimal("60000")

    financial_repository.create.assert_called_once()


def test_calculate_for_contract_updates_existing_analysis():
    db = MagicMock()

    contract = MagicMock()
    contract.id = 1
    contract.contract_id = "CNT-001"

    contract_repository = MagicMock()
    contract_repository.get_by_contract_id.return_value = contract

    financial_repository = MagicMock()

    existing_analysis = MagicMock()
    existing_analysis.id = 10
    existing_analysis.contract_id = 1

    financial_repository.get_by_contract_id.return_value = (
        existing_analysis
    )

    service = FinancialAnalysisService(db)
    service.contract_repository = contract_repository
    service.financial_repository = financial_repository

    inputs = FinancialInputs(
        revenue=Decimal("80000"),
        initial_investment=Decimal("10000"),
        fixed_costs=Decimal("20000"),
        variable_costs=Decimal("10000"),
    )

    result = service.calculate_for_contract(
        contract_id="CNT-001",
        inputs=inputs,
    )

    assert existing_analysis.contract_id == 1
    assert existing_analysis.revenue == Decimal("80000")
    assert existing_analysis.total_cost == Decimal("30000")
    assert existing_analysis.profit == Decimal("50000")
    assert existing_analysis.roi == Decimal("500")
    assert existing_analysis.profit_margin == Decimal("62.5")

    financial_repository.update.assert_called_once_with(
        existing_analysis
    )

    assert result is financial_repository.update.return_value


def test_calculate_for_contract_rejects_unknown_contract():
    db = MagicMock()

    contract_repository = MagicMock()
    contract_repository.get_by_contract_id.return_value = None

    service = FinancialAnalysisService(db)
    service.contract_repository = contract_repository

    with pytest.raises(
        ValueError,
        match="Contract not found",
    ):
        service.calculate_for_contract(
            contract_id="CNT-UNKNOWN",
            inputs=FinancialInputs(
                revenue=Decimal("100000"),
            ),
        )