from unittest.mock import MagicMock

import pytest

from backend.app.services.risk.extraction import (
    ExtractedRisk,
    RiskExtractionService,
)


def test_extract_risks():
    llm_service = MagicMock()

    llm_service.invoke.return_value = """
[
    {
        "risk_type": "payment",
        "severity": "high",
        "title": "Delayed payment risk",
        "description": "The client may take a long time to make payment.",
        "evidence": "Payment shall be made within 90 days.",
        "source": "Section 5",
        "confidence": "0.90"
    }
]
"""

    service = RiskExtractionService(
        llm_service=llm_service
    )

    result = service.extract(
        "The client shall make payment within 90 days."
    )

    assert len(result) == 1

    assert isinstance(result[0], ExtractedRisk)

    assert result[0].risk_type == "payment"
    assert result[0].severity == "high"
    assert result[0].title == "Delayed payment risk"

    assert (
        result[0].description
        == "The client may take a long time to make payment."
    )

    assert (
        result[0].evidence
        == "Payment shall be made within 90 days."
    )

    assert result[0].source == "Section 5"
    assert result[0].confidence == "0.90"

    llm_service.invoke.assert_called_once()


def test_empty_contract_returns_no_risks():
    llm_service = MagicMock()

    service = RiskExtractionService(
        llm_service=llm_service
    )

    result = service.extract("")

    assert result == []

    llm_service.invoke.assert_not_called()


def test_whitespace_contract_returns_no_risks():
    llm_service = MagicMock()

    service = RiskExtractionService(
        llm_service=llm_service
    )

    result = service.extract("   ")

    assert result == []

    llm_service.invoke.assert_not_called()


def test_no_risks():
    llm_service = MagicMock()

    llm_service.invoke.return_value = "[]"

    service = RiskExtractionService(
        llm_service=llm_service
    )

    result = service.extract(
        "Simple contract with no identified risks."
    )

    assert result == []

    llm_service.invoke.assert_called_once()


def test_invalid_json_is_rejected():
    llm_service = MagicMock()

    llm_service.invoke.return_value = (
        "This is not valid JSON."
    )

    service = RiskExtractionService(
        llm_service=llm_service
    )

    with pytest.raises(
        ValueError,
        match="invalid JSON",
    ):
        service.extract("Contract text")


def test_response_must_be_json_array():
    llm_service = MagicMock()

    llm_service.invoke.return_value = """
{
    "risk_type": "financial",
    "severity": "high",
    "title": "Financial exposure",
    "description": "Financial risk exists."
}
"""

    service = RiskExtractionService(
        llm_service=llm_service
    )

    with pytest.raises(
        ValueError,
        match="JSON array",
    ):
        service.extract("Contract text")


def test_markdown_json_is_supported():
    llm_service = MagicMock()

    llm_service.invoke.return_value = """
```json
[
    {
        "risk_type": "liability",
        "severity": "medium",
        "title": "Liability exposure",
        "description": "The contract contains broad liability.",
        "evidence": "Unlimited liability clause.",
        "source": "Section 8",
        "confidence": "0.85"
    }
]
"""