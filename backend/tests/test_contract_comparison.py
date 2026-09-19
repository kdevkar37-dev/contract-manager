from decimal import Decimal

from backend.app.services.decision.comparison import (
    ContractComparisonInput,
    ContractComparisonService,
)


def test_compare_contracts_calculates_relative_value_scores():
    service = ContractComparisonService()

    contracts = [
        ContractComparisonInput(
            contract_id="CNT-A",
            contract_value=Decimal("64000000"),
        ),
        ContractComparisonInput(
            contract_id="CNT-B",
            contract_value=Decimal("45000000"),
        ),
        ContractComparisonInput(
            contract_id="CNT-C",
            contract_value=Decimal("80000000"),
        ),
    ]

    results = service.compare(contracts)

    result_by_id = {
        result.contract_id: result
        for result in results
    }

    assert (
        result_by_id["CNT-C"].contract_value_score
        == Decimal("100.0000")
    )

    assert (
        result_by_id["CNT-A"].contract_value_score
        == Decimal("80.0000")
    )

    assert (
        result_by_id["CNT-B"].contract_value_score
        == Decimal("56.2500")
    )


def test_highest_contract_value_gets_rank_one():
    service = ContractComparisonService()

    contracts = [
        ContractComparisonInput(
            contract_id="CNT-A",
            contract_value=Decimal("64000000"),
        ),
        ContractComparisonInput(
            contract_id="CNT-B",
            contract_value=Decimal("80000000"),
        ),
    ]

    results = service.compare(contracts)

    result_by_id = {
        result.contract_id: result
        for result in results
    }

    assert result_by_id["CNT-B"].rank == 1
    assert result_by_id["CNT-A"].rank == 2


def test_missing_contract_value_is_not_scored():
    service = ContractComparisonService()

    contracts = [
        ContractComparisonInput(
            contract_id="CNT-A",
            contract_value=Decimal("64000000"),
        ),
        ContractComparisonInput(
            contract_id="CNT-B",
            contract_value=None,
        ),
    ]

    results = service.compare(contracts)

    result_by_id = {
        result.contract_id: result
        for result in results
    }

    assert (
        result_by_id["CNT-A"].contract_value_score
        == Decimal("100.0000")
    )

    assert (
        result_by_id["CNT-B"].contract_value_score
        is None
    )

    assert result_by_id["CNT-A"].rank == 1
    assert result_by_id["CNT-B"].rank is None


def test_empty_contract_list_returns_empty_result():
    service = ContractComparisonService()

    assert service.compare([]) == []


def test_zero_contract_values_are_not_scored():
    service = ContractComparisonService()

    contracts = [
        ContractComparisonInput(
            contract_id="CNT-A",
            contract_value=Decimal("0"),
        ),
        ContractComparisonInput(
            contract_id="CNT-B",
            contract_value=Decimal("0"),
        ),
    ]

    results = service.compare(contracts)

    assert all(
        result.contract_value_score is None
        for result in results
    )


def test_equal_contract_values_receive_equal_scores_and_rank():
    service = ContractComparisonService()

    contracts = [
        ContractComparisonInput(
            contract_id="CNT-A",
            contract_value=Decimal("50000000"),
        ),
        ContractComparisonInput(
            contract_id="CNT-B",
            contract_value=Decimal("50000000"),
        ),
    ]

    results = service.compare(contracts)

    result_by_id = {
        result.contract_id: result
        for result in results
    }

    assert (
        result_by_id["CNT-A"].contract_value_score
        == Decimal("100.0000")
    )

    assert (
        result_by_id["CNT-B"].contract_value_score
        == Decimal("100.0000")
    )

    assert result_by_id["CNT-A"].rank == 1
    assert result_by_id["CNT-B"].rank == 1