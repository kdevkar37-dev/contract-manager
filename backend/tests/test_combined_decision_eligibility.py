from decimal import Decimal

from backend.app.models.contract import Contract
from backend.app.models.contract_document import ContractDocument
from backend.app.models.contract_information import ContractInformation
from backend.app.models.financial_analysis import FinancialAnalysis
from backend.app.models.decision_score import DecisionScore
from backend.app.services.decision.combined_decision_service import (
    CombinedDecisionService,
)


def create_contract(
    db_session,
    contract_id,
    contract_value,
):
    contract = Contract(
        contract_id=contract_id,
        name=f"Contract {contract_id}",
        storage_key=f"contracts/{contract_id}.pdf",
        original_filename=f"{contract_id}.pdf",
        mime_type="application/pdf",
        status="completed",
    )

    db_session.add(contract)
    db_session.commit()
    db_session.refresh(contract)

    information = ContractInformation(
        contract_id=contract.id,
        client_name="Test Client",
        vendor_name="Test Vendor",
        contract_value=Decimal(str(contract_value)),
        currency="INR",
    )

    db_session.add(information)
    db_session.commit()

    return contract


def add_document(db_session, contract):
    document = ContractDocument(
        contract_id=contract.id,
        extracted_text="This is a valid contract.",
        processing_status="completed",
    )

    db_session.add(document)
    db_session.commit()

    return document


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

    return financial


def add_decision_score(db_session, contract):
    decision = DecisionScore(
        contract_id=contract.id,
        score=Decimal("80"),
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

    return decision


def make_eligible_contract(
    db_session,
    contract_id,
    contract_value,
):
    contract = create_contract(
        db_session,
        contract_id,
        contract_value,
    )

    add_document(
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


def test_incomplete_contract_is_excluded_from_combined_decision(
    db_session,
):
    eligible_contract = make_eligible_contract(
        db_session,
        "CNT-COMBINED-ELIGIBLE-001",
        100000,
    )

    incomplete_contract = create_contract(
        db_session,
        "CNT-COMBINED-INCOMPLETE-001",
        500000,
    )

    service = CombinedDecisionService(db_session)

    results = service.calculate_for_all_contracts()

    contract_ids = {
        result["contract_id"]
        for result in results
    }

    assert (
        eligible_contract.contract_id
        in contract_ids
    )

    assert (
        incomplete_contract.contract_id
        not in contract_ids
    )


def test_ineligible_high_value_contract_does_not_affect_value_score(
    db_session,
):
    eligible_contract = make_eligible_contract(
        db_session,
        "CNT-COMBINED-ELIGIBLE-002",
        100000,
    )

    high_value_incomplete_contract = create_contract(
        db_session,
        "CNT-COMBINED-HIGH-VALUE-001",
        1000000,
    )

    service = CombinedDecisionService(db_session)

    results = service.calculate_for_all_contracts()

    eligible_result = next(
        result
        for result in results
        if result["contract_id"]
        == eligible_contract.contract_id
    )

    assert (
        high_value_incomplete_contract.contract_id
        not in {
            result["contract_id"]
            for result in results
        }
    )

    assert (
        eligible_result["contract_value_score"]
        == Decimal("100.0000")
    )


def test_only_eligible_contracts_are_used_for_comparison(
    db_session,
):
    first_contract = make_eligible_contract(
        db_session,
        "CNT-COMBINED-ELIGIBLE-003",
        100000,
    )

    second_contract = make_eligible_contract(
        db_session,
        "CNT-COMBINED-ELIGIBLE-004",
        200000,
    )

    incomplete_contract = create_contract(
        db_session,
        "CNT-COMBINED-INCOMPLETE-002",
        1000000,
    )

    service = CombinedDecisionService(db_session)

    results = service.calculate_for_all_contracts()

    result_by_id = {
        result["contract_id"]: result
        for result in results
    }

    assert first_contract.contract_id in result_by_id
    assert second_contract.contract_id in result_by_id
    assert incomplete_contract.contract_id not in result_by_id

    assert (
        result_by_id[
            first_contract.contract_id
        ]["contract_value_score"]
        == Decimal("50.0000")
    )

    assert (
        result_by_id[
            second_contract.contract_id
        ]["contract_value_score"]
        == Decimal("100.0000")
    )