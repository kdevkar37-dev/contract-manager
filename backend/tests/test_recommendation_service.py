from decimal import Decimal
from unittest.mock import MagicMock

from backend.app.services.decision.recommendation_service import (
    ContractRecommendationIntegrationService,
)


def test_recommend_all_loads_contract_metadata_and_scores():
    db = MagicMock()

    db.execute.return_value.all.return_value = [
        (
            "CNT-A",
            "Contract A",
            Decimal("64000000"),
            Decimal("80.0000"),
            Decimal("75.0000"),
            Decimal("85.0000"),
            Decimal("90.0000"),
            "Stored explanation A",
        ),
        (
            "CNT-B",
            "Contract B",
            Decimal("45000000"),
            Decimal("70.0000"),
            Decimal("65.0000"),
            Decimal("75.0000"),
            Decimal("80.0000"),
            "Stored explanation B",
        ),
    ]

    service = ContractRecommendationIntegrationService(db)

    results = service.recommend_all()

    assert len(results) == 2

    assert results[0]["contract_id"] == "CNT-A"
    assert results[0]["contract_name"] == "Contract A"
    assert results[0]["contract_value"] == Decimal(
        "64000000"
    )

    assert results[0]["final_score"] == Decimal(
        "80.0000"
    )

    assert results[0]["financial_score"] == Decimal(
        "75.0000"
    )

    assert results[0]["risk_score"] == Decimal(
        "85.0000"
    )

    assert results[0]["contract_value_score"] == Decimal(
        "90.0000"
    )

    assert results[0]["rank"] == 1

    assert results[1]["contract_id"] == "CNT-B"
    assert results[1]["contract_name"] == "Contract B"
    assert results[1]["rank"] == 2


def test_recommend_all_sorts_by_final_score():
    db = MagicMock()

    db.execute.return_value.all.return_value = [
        (
            "CNT-A",
            "Contract A",
            Decimal("64000000"),
            Decimal("60.0000"),
            Decimal("55.0000"),
            Decimal("65.0000"),
            Decimal("70.0000"),
            "Explanation A",
        ),
        (
            "CNT-B",
            "Contract B",
            Decimal("80000000"),
            Decimal("80.0000"),
            Decimal("75.0000"),
            Decimal("85.0000"),
            Decimal("90.0000"),
            "Explanation B",
        ),
    ]

    service = ContractRecommendationIntegrationService(db)

    results = service.recommend_all()

    assert results[0]["contract_id"] == "CNT-B"
    assert results[0]["rank"] == 1

    assert results[1]["contract_id"] == "CNT-A"
    assert results[1]["rank"] == 2


def test_recommend_all_preserves_missing_scores():
    db = MagicMock()

    db.execute.return_value.all.return_value = [
        (
            "CNT-A",
            "Contract A",
            Decimal("64000000"),
            Decimal("75.0000"),
            Decimal("70.0000"),
            None,
            Decimal("100.0000"),
            "Explanation",
        ),
    ]

    service = ContractRecommendationIntegrationService(db)

    results = service.recommend_all()

    assert len(results) == 1

    assert results[0]["financial_score"] == Decimal(
        "70.0000"
    )

    assert results[0]["risk_score"] is None

    assert results[0]["contract_value_score"] == Decimal(
        "100.0000"
    )