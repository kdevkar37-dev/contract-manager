from unittest.mock import MagicMock

from backend.app.models.contract import Contract
from backend.app.services.risk.extraction import ExtractedRisk
from backend.app.services.risk.service import RiskAnalysisService


def test_analyze_contract_extracts_and_persists_risks():
    db = MagicMock()

    contract = Contract(
        id=1,
        contract_id="CNT-001",
        name="Test Contract",
    )

    contract_repository = MagicMock()
    contract_repository.get_by_contract_id.return_value = contract

    extraction_service = MagicMock()

    extraction_service.extract.return_value = [
        ExtractedRisk(
            risk_type="payment",
            severity="high",
            title="Delayed payment risk",
            description="Payment may be delayed.",
            evidence="Payment shall be made within 90 days.",
            source="Section 5",
            confidence="0.90",
        )
    ]

    risk_repository = MagicMock()

    risk_repository.create_many.return_value = [
        MagicMock(
            contract_id=1,
            risk_type="payment",
            severity="high",
            title="Delayed payment risk",
        )
    ]

    service = RiskAnalysisService(
        db=db,
        extraction_service=extraction_service,
    )

    service.contract_repository = contract_repository
    service.risk_repository = risk_repository

    result = service.analyze_contract(
        contract_id="CNT-001",
        contract_text="Payment shall be made within 90 days.",
    )

    assert len(result) == 1

    extraction_service.extract.assert_called_once_with(
        "Payment shall be made within 90 days."
    )

    risk_repository.delete_by_contract_id.assert_called_once_with(
        1
    )

    risk_repository.create_many.assert_called_once()

    persisted_risks = (
        risk_repository.create_many.call_args.args[0]
    )

    assert len(persisted_risks) == 1

    assert persisted_risks[0].contract_id == 1
    assert persisted_risks[0].risk_type == "payment"
    assert persisted_risks[0].severity == "high"
    assert persisted_risks[0].title == "Delayed payment risk"


def test_analyze_contract_with_no_risks():
    db = MagicMock()

    contract = Contract(
        id=1,
        contract_id="CNT-002",
        name="Safe Contract",
    )

    contract_repository = MagicMock()
    contract_repository.get_by_contract_id.return_value = contract

    extraction_service = MagicMock()
    extraction_service.extract.return_value = []

    risk_repository = MagicMock()
    risk_repository.create_many.return_value = []

    service = RiskAnalysisService(
        db=db,
        extraction_service=extraction_service,
    )

    service.contract_repository = contract_repository
    service.risk_repository = risk_repository

    result = service.analyze_contract(
        contract_id="CNT-002",
        contract_text="Simple contract.",
    )

    assert result == []

    risk_repository.delete_by_contract_id.assert_called_once_with(
        1
    )

    risk_repository.create_many.assert_called_once_with([])


def test_analyze_contract_replaces_existing_risks():
    db = MagicMock()

    contract = Contract(
        id=5,
        contract_id="CNT-003",
        name="Renewable Contract",
    )

    contract_repository = MagicMock()
    contract_repository.get_by_contract_id.return_value = contract

    extraction_service = MagicMock()

    extraction_service.extract.return_value = [
        ExtractedRisk(
            risk_type="termination",
            severity="medium",
            title="Termination risk",
            description="Termination clause may create exposure.",
        )
    ]

    risk_repository = MagicMock()

    risk_repository.create_many.return_value = [
        MagicMock()
    ]

    service = RiskAnalysisService(
        db=db,
        extraction_service=extraction_service,
    )

    service.contract_repository = contract_repository
    service.risk_repository = risk_repository

    service.analyze_contract(
        contract_id="CNT-003",
        contract_text="Termination clause.",
    )

    risk_repository.delete_by_contract_id.assert_called_once_with(
        5
    )

    risk_repository.create_many.assert_called_once()


def test_analyze_contract_contract_not_found():
    db = MagicMock()

    contract_repository = MagicMock()
    contract_repository.get_by_contract_id.return_value = None

    extraction_service = MagicMock()
    risk_repository = MagicMock()

    service = RiskAnalysisService(
        db=db,
        extraction_service=extraction_service,
    )

    service.contract_repository = contract_repository
    service.risk_repository = risk_repository

    try:
        service.analyze_contract(
            contract_id="CNT-404",
            contract_text="Contract text.",
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "Contract not found"

    extraction_service.extract.assert_not_called()
    risk_repository.delete_by_contract_id.assert_not_called()
    risk_repository.create_many.assert_not_called()


def test_get_risks():
    db = MagicMock()

    contract = Contract(
        id=10,
        contract_id="CNT-010",
        name="Test Contract",
    )

    contract_repository = MagicMock()
    contract_repository.get_by_contract_id.return_value = contract

    risk_repository = MagicMock()

    expected_risks = [
        MagicMock(
            contract_id=10,
            risk_type="financial",
            severity="high",
        ),
        MagicMock(
            contract_id=10,
            risk_type="legal",
            severity="medium",
        ),
    ]

    risk_repository.get_by_contract_id.return_value = (
        expected_risks
    )

    service = RiskAnalysisService(
        db=db,
    )

    service.contract_repository = contract_repository
    service.risk_repository = risk_repository

    result = service.get_risks(
        contract_id="CNT-010"
    )

    assert result == expected_risks

    contract_repository.get_by_contract_id.assert_called_once_with(
        "CNT-010"
    )

    risk_repository.get_by_contract_id.assert_called_once_with(
        10
    )


def test_get_risks_contract_not_found():
    db = MagicMock()

    contract_repository = MagicMock()
    contract_repository.get_by_contract_id.return_value = None

    risk_repository = MagicMock()

    service = RiskAnalysisService(
        db=db,
    )

    service.contract_repository = contract_repository
    service.risk_repository = risk_repository

    try:
        service.get_risks(
            contract_id="CNT-404"
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "Contract not found"

    risk_repository.get_by_contract_id.assert_not_called()