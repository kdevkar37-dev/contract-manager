from decimal import Decimal

from backend.app.models.contract import Contract
from backend.app.models.contract_document import ContractDocument
from backend.app.models.contract_information import ContractInformation
from backend.app.models.financial_analysis import FinancialAnalysis
from backend.app.models.decision_score import DecisionScore
from backend.app.services.decision.eligibility import (
    ContractEligibilityService,
)


def create_contract(db_session):
    contract = Contract(
        contract_id="CNT-ELIGIBILITY-001",
        name="Eligibility Test Contract",
        storage_key="contracts/test.pdf",
        original_filename="test.pdf",
        mime_type="application/pdf",
        status="completed",
    )

    db_session.add(contract)
    db_session.commit()
    db_session.refresh(contract)

    return contract


def add_document(
    db_session,
    contract,
    completed=True,
    extracted_text=True,
):
    document = ContractDocument(
        contract_id=contract.id,
        extracted_text=(
            "This is a valid contract."
            if extracted_text
            else None
        ),
        processing_status=(
            "completed"
            if completed
            else "processing"
        ),
    )

    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)

    return document


def add_contract_information(db_session, contract):
    information = ContractInformation(
        contract_id=contract.id,
        client_name="Test Client",
        vendor_name="Test Vendor",
        contract_value=Decimal("100000"),
        currency="INR",
    )

    db_session.add(information)
    db_session.commit()
    db_session.refresh(information)

    return information


def add_financial_analysis(db_session, contract):
    financial = FinancialAnalysis(
        contract_id=contract.id,
        revenue=Decimal("100000"),
        initial_investment=Decimal("20000"),
        fixed_costs=Decimal("10000"),
        variable_costs=Decimal("10000"),
        total_cost=Decimal("20000"),
        profit=Decimal("80000"),
        roi=Decimal("400"),
        profit_margin=Decimal("80"),
        break_even=Decimal("25000"),
    )

    db_session.add(financial)
    db_session.commit()
    db_session.refresh(financial)

    return financial


def add_decision_score(
    db_session,
    contract,
    score=Decimal("80"),
):
    decision = DecisionScore(
        contract_id=contract.id,
        score=score,
        financial_score=Decimal("85"),
        risk_score=Decimal("75"),
        contract_value_score=Decimal("80"),
        financial_weight=Decimal("50"),
        risk_weight=Decimal("30"),
        contract_value_weight=Decimal("20"),
        explanation="Test decision score",
    )

    db_session.add(decision)
    db_session.commit()
    db_session.refresh(decision)

    return decision


def make_fully_eligible(db_session):
    contract = create_contract(db_session)

    add_document(
        db_session,
        contract,
        completed=True,
        extracted_text=True,
    )

    add_contract_information(
        db_session,
        contract,
    )

    add_financial_analysis(
        db_session,
        contract,
    )

    add_decision_score(
        db_session,
        contract,
    )

    return contract


def test_fully_processed_contract_is_eligible(db_session):
    contract = make_fully_eligible(db_session)

    service = ContractEligibilityService(db_session)

    result = service.check(contract)

    assert result.eligible is True
    assert "eligible" in result.reason.lower()


def test_contract_without_storage_is_not_eligible(db_session):
    contract = make_fully_eligible(db_session)

    contract.storage_key = None
    db_session.commit()

    service = ContractEligibilityService(db_session)

    result = service.check(contract)

    assert result.eligible is False
    assert "document" in result.reason.lower()


def test_contract_without_document_is_not_eligible(db_session):
    contract = create_contract(db_session)

    service = ContractEligibilityService(db_session)

    result = service.check(contract)

    assert result.eligible is False
    assert "document record" in result.reason.lower()


def test_unprocessed_document_is_not_eligible(db_session):
    contract = create_contract(db_session)

    add_document(
        db_session,
        contract,
        completed=False,
        extracted_text=True,
    )

    service = ContractEligibilityService(db_session)

    result = service.check(contract)

    assert result.eligible is False
    assert "processing" in result.reason.lower()


def test_document_without_extracted_text_is_not_eligible(
    db_session,
):
    contract = create_contract(db_session)

    add_document(
        db_session,
        contract,
        completed=True,
        extracted_text=False,
    )

    service = ContractEligibilityService(db_session)

    result = service.check(contract)

    assert result.eligible is False
    assert "text" in result.reason.lower()


def test_missing_contract_information_is_not_eligible(
    db_session,
):
    contract = create_contract(db_session)

    add_document(
        db_session,
        contract,
        completed=True,
        extracted_text=True,
    )

    service = ContractEligibilityService(db_session)

    result = service.check(contract)

    assert result.eligible is False
    assert "contract information" in result.reason.lower()


def test_missing_financial_analysis_is_not_eligible(
    db_session,
):
    contract = create_contract(db_session)

    add_document(
        db_session,
        contract,
        completed=True,
        extracted_text=True,
    )

    add_contract_information(
        db_session,
        contract,
    )

    service = ContractEligibilityService(db_session)

    result = service.check(contract)

    assert result.eligible is False
    assert "financial analysis" in result.reason.lower()


def test_missing_decision_score_is_not_eligible(
    db_session,
):
    contract = create_contract(db_session)

    add_document(
        db_session,
        contract,
        completed=True,
        extracted_text=True,
    )

    add_contract_information(
        db_session,
        contract,
    )

    add_financial_analysis(
        db_session,
        contract,
    )

    service = ContractEligibilityService(db_session)

    result = service.check(contract)

    assert result.eligible is False
    assert "decision score" in result.reason.lower()


def test_decision_score_without_final_score_is_not_eligible(
    db_session,
):
    contract = create_contract(db_session)

    add_document(
        db_session,
        contract,
        completed=True,
        extracted_text=True,
    )

    add_contract_information(
        db_session,
        contract,
    )

    add_financial_analysis(
        db_session,
        contract,
    )

    add_decision_score(
        db_session,
        contract,
        score=None,
    )

    service = ContractEligibilityService(db_session)

    result = service.check(contract)

    assert result.eligible is False
    assert "final decision score" in result.reason.lower()


def test_is_eligible_returns_boolean(db_session):
    contract = make_fully_eligible(db_session)

    service = ContractEligibilityService(db_session)

    result = service.is_eligible(contract)

    assert result is True
    assert isinstance(result, bool)