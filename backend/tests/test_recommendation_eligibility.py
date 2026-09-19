from decimal import Decimal

from backend.app.models.contract import Contract
from backend.app.models.contract_document import ContractDocument
from backend.app.models.contract_information import ContractInformation
from backend.app.models.financial_analysis import FinancialAnalysis
from backend.app.models.decision_score import DecisionScore
from backend.app.services.decision.recommendation_service import (
    ContractRecommendationIntegrationService,
)


def create_contract(
    db_session,
    contract_id,
    storage_key="contracts/test.pdf",
):
    contract = Contract(
        contract_id=contract_id,
        name=f"Contract {contract_id}",
        storage_key=storage_key,
        original_filename="test.pdf",
        mime_type="application/pdf",
        status="completed",
    )

    db_session.add(contract)
    db_session.commit()
    db_session.refresh(contract)

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

    return financial


def add_decision_score(
    db_session,
    contract,
    score,
):
    decision = DecisionScore(
        contract_id=contract.id,
        score=Decimal(str(score)),
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
    score,
):
    contract = create_contract(
        db_session,
        contract_id,
    )

    add_document(
        db_session,
        contract,
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
        score,
    )

    return contract


def test_ineligible_contract_is_excluded_from_recommendations(
    db_session,
):
    eligible_contract = make_eligible_contract(
        db_session,
        "CNT-ELIGIBLE-001",
        80,
    )

    ineligible_contract = create_contract(
        db_session,
        "CNT-INELIGIBLE-001",
    )

    # Deliberately do not create the required
    # document/information/financial analysis.

    service = ContractRecommendationIntegrationService(
        db_session
    )

    recommendations = service.recommend_all()

    contract_ids = [
        recommendation["contract_id"]
        for recommendation in recommendations
    ]

    assert (
        eligible_contract.contract_id
        in contract_ids
    )

    assert (
        ineligible_contract.contract_id
        not in contract_ids
    )


def test_only_fully_analyzed_contracts_are_recommended(
    db_session,
):
    eligible_contract = make_eligible_contract(
        db_session,
        "CNT-ELIGIBLE-002",
        90,
    )

    contract_without_financial_analysis = create_contract(
        db_session,
        "CNT-NO-FINANCIAL-001",
    )

    add_document(
        db_session,
        contract_without_financial_analysis,
    )

    add_contract_information(
        db_session,
        contract_without_financial_analysis,
    )

    add_decision_score(
        db_session,
        contract_without_financial_analysis,
        95,
    )

    service = ContractRecommendationIntegrationService(
        db_session
    )

    recommendations = service.recommend_all()

    contract_ids = [
        recommendation["contract_id"]
        for recommendation in recommendations
    ]

    assert (
        eligible_contract.contract_id
        in contract_ids
    )

    assert (
        contract_without_financial_analysis.contract_id
        not in contract_ids
    )


def test_contract_without_storage_is_excluded(
    db_session,
):
    eligible_contract = make_eligible_contract(
        db_session,
        "CNT-ELIGIBLE-003",
        75,
    )

    contract_without_storage = make_eligible_contract(
        db_session,
        "CNT-NO-STORAGE-001",
        100,
    )

    contract_without_storage.storage_key = None
    db_session.commit()

    service = ContractRecommendationIntegrationService(
        db_session
    )

    recommendations = service.recommend_all()

    contract_ids = [
        recommendation["contract_id"]
        for recommendation in recommendations
    ]

    assert (
        eligible_contract.contract_id
        in contract_ids
    )

    assert (
        contract_without_storage.contract_id
        not in contract_ids
    )


def test_recommendation_contains_only_eligible_contracts(
    db_session,
):
    first_contract = make_eligible_contract(
        db_session,
        "CNT-ELIGIBLE-004",
        70,
    )

    second_contract = make_eligible_contract(
        db_session,
        "CNT-ELIGIBLE-005",
        85,
    )

    ineligible_contract = create_contract(
        db_session,
        "CNT-INELIGIBLE-002",
    )

    service = ContractRecommendationIntegrationService(
        db_session
    )

    recommendations = service.recommend_all()

    contract_ids = {
        recommendation["contract_id"]
        for recommendation in recommendations
    }

    assert first_contract.contract_id in contract_ids
    assert second_contract.contract_id in contract_ids
    assert ineligible_contract.contract_id not in contract_ids