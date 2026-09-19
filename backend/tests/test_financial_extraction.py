from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from ai.extraction.financial import FinancialExtractionService


def test_extract_financial_information():
    llm_service = MagicMock()

    llm_service.invoke.return_value = """
    {
        "revenue": 100000,
        "initial_investment": 20000,
        "fixed_costs": 30000,
        "variable_costs": 20000,
        "contribution_margin": 0.5,
        "assumptions": [
            "Revenue based on contract value"
        ],
        "sources": [
            "Section 5 - Commercial Terms"
        ]
    }
    """

    service = FinancialExtractionService(
        llm_service=llm_service
    )

    result = service.extract(
        """
        The contract value is 100000.
        Initial investment is 20000.
        Fixed costs are 30000.
        Variable costs are 20000.
        Contribution margin is 0.5.
        """
    )

    assert result.revenue == Decimal("100000")
    assert result.initial_investment == Decimal("20000")
    assert result.fixed_costs == Decimal("30000")
    assert result.variable_costs == Decimal("20000")
    assert result.contribution_margin == Decimal("0.5")

    assert result.assumptions == [
        "Revenue based on contract value"
    ]

    assert result.sources == [
        "Section 5 - Commercial Terms"
    ]

    llm_service.invoke.assert_called_once()


def test_extract_handles_markdown_json():
    llm_service = MagicMock()

    llm_service.invoke.return_value = """
    ```json
    {
        "revenue": 50000,
        "initial_investment": 10000,
        "fixed_costs": 15000,
        "variable_costs": 5000,
        "contribution_margin": 0.4,
        "assumptions": [],
        "sources": ["Section 3"]
    }
    ```
    """

    service = FinancialExtractionService(
        llm_service=llm_service
    )

    result = service.extract(
        "The contract contains financial information."
    )

    assert result.revenue == Decimal("50000")
    assert result.initial_investment == Decimal("10000")
    assert result.fixed_costs == Decimal("15000")
    assert result.variable_costs == Decimal("5000")
    assert result.contribution_margin == Decimal("0.4")


def test_extract_missing_values_as_none():
    llm_service = MagicMock()

    llm_service.invoke.return_value = """
    {
        "revenue": 100000,
        "initial_investment": null,
        "fixed_costs": null,
        "variable_costs": 20000,
        "contribution_margin": null,
        "assumptions": [],
        "sources": []
    }
    """

    service = FinancialExtractionService(
        llm_service=llm_service
    )

    result = service.extract(
        "The contract contains partial financial information."
    )

    assert result.revenue == Decimal("100000")
    assert result.initial_investment is None
    assert result.fixed_costs is None
    assert result.variable_costs == Decimal("20000")
    assert result.contribution_margin is None


def test_extract_rejects_empty_contract_text():
    llm_service = MagicMock()

    service = FinancialExtractionService(
        llm_service=llm_service
    )

    with pytest.raises(
        ValueError,
        match="Contract text cannot be empty",
    ):
        service.extract("")

    llm_service.invoke.assert_not_called()


def test_extract_rejects_invalid_json():
    llm_service = MagicMock()

    llm_service.invoke.return_value = """
    This is not valid JSON.
    """

    service = FinancialExtractionService(
        llm_service=llm_service
    )

    with pytest.raises(
        ValueError,
        match="LLM returned invalid JSON",
    ):
        service.extract(
            "The contract contains financial information."
        )