from datetime import date
from decimal import Decimal

from backend.app.models.contract import Contract
from backend.app.services.contracts.information_service import (
    ContractInformationService,
)


class FakeExtractionService:
    def extract(self, contract_text: str):
        from ai.extraction.contract_information import (
            ExtractedContractInformation,
        )

        return ExtractedContractInformation(
            client_name="ABC Corporation",
            vendor_name="XYZ Technologies",
            contract_value=Decimal("1500000"),
            currency="INR",
            start_date=date(2026, 1, 1),
            end_date=date(2027, 12, 31),
            payment_terms="30 days from invoice",
            renewal_terms="Annual renewal",
            termination_terms="60 days notice",
            penalties=[
                "2% penalty for delayed delivery",
            ],
            liabilities=[
                "Vendor liable for direct damages caused by breach",
            ],
            obligations=[
                "Deliver monthly reports",
                "Provide technical support",
            ],
            dependencies=[
                "Client provides required data",
            ],
        )


def create_contract(db_session):
    contract = Contract(
        contract_id="INFO-001",
        name="Information Test Contract",
        source_type="manual",
        status="completed",
    )

    db_session.add(contract)
    db_session.commit()
    db_session.refresh(contract)

    return contract


def test_extract_and_save_contract_information(
    db_session,
):
    contract = create_contract(db_session)

    service = ContractInformationService(
        db_session,
        extraction_service=FakeExtractionService(),
    )

    information = service.extract_and_save(
        contract_id=contract.contract_id,
        contract_text="Test contract text",
    )

    assert information.client_name == "ABC Corporation"
    assert information.vendor_name == "XYZ Technologies"
    assert information.contract_value == Decimal("1500000")
    assert information.currency == "INR"

    assert information.start_date == date(2026, 1, 1)
    assert information.end_date == date(2027, 12, 31)

    assert information.payment_terms == "30 days from invoice"
    assert information.renewal_terms == "Annual renewal"
    assert information.termination_terms == "60 days notice"

    assert service.parse_list(
        information.penalties
    ) == [
        "2% penalty for delayed delivery",
    ]

    assert service.parse_list(
        information.liabilities
    ) == [
        "Vendor liable for direct damages caused by breach",
    ]

    assert service.parse_list(
        information.obligations
    ) == [
        "Deliver monthly reports",
        "Provide technical support",
    ]

    assert service.parse_list(
        information.dependencies
    ) == [
        "Client provides required data",
    ]


def test_get_contract_information(
    db_session,
):
    contract = create_contract(db_session)

    service = ContractInformationService(
        db_session,
        extraction_service=FakeExtractionService(),
    )

    service.extract_and_save(
        contract_id=contract.contract_id,
        contract_text="Test contract text",
    )

    information = service.get_for_contract(
        contract.contract_id
    )

    assert information is not None
    assert information.client_name == "ABC Corporation"
    assert information.vendor_name == "XYZ Technologies"
    assert information.start_date == date(2026, 1, 1)
    assert information.end_date == date(2027, 12, 31)


def test_extract_and_save_updates_existing_information(
    db_session,
):
    contract = create_contract(db_session)

    service = ContractInformationService(
        db_session,
        extraction_service=FakeExtractionService(),
    )

    first = service.extract_and_save(
        contract_id=contract.contract_id,
        contract_text="Test contract text",
    )

    second = service.extract_and_save(
        contract_id=contract.contract_id,
        contract_text="Updated contract text",
    )

    assert second.id == first.id
    assert second.contract_id == contract.id
    assert second.contract_value == Decimal("1500000")

    assert second.start_date == date(2026, 1, 1)
    assert second.end_date == date(2027, 12, 31)

    assert service.parse_list(
        second.penalties
    ) == [
        "2% penalty for delayed delivery",
    ]

    assert service.parse_list(
        second.liabilities
    ) == [
        "Vendor liable for direct damages caused by breach",
    ]


def test_get_contract_information_for_missing_contract(
    db_session,
):
    service = ContractInformationService(
        db_session,
        extraction_service=FakeExtractionService(),
    )

    try:
        service.get_for_contract("DOES-NOT-EXIST")
        assert False
    except ValueError as exc:
        assert str(exc) == "Contract not found"