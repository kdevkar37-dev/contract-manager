from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.contract import Contract
from backend.app.models.contract_document import ContractDocument
from backend.app.models.contract_information import ContractInformation
from backend.app.models.financial_analysis import FinancialAnalysis
from backend.app.models.decision_score import DecisionScore


@dataclass(frozen=True)
class ContractEligibilityResult:
    eligible: bool
    reason: str


class ContractEligibilityService:
    """
    Determines whether a contract is eligible for
    decision analysis and recommendation.

    Eligibility requires:

        1. Original contract document is available
        2. A contract document record exists
        3. Document processing is completed
        4. Contract text has been extracted
        5. Structured contract information exists
        6. Financial analysis exists
        7. Final decision score exists

    A contract may have multiple ContractDocument records.
    Therefore, document queries must not assume that only
    one document record exists.
    """

    COMPLETED_STATUS = "completed"

    def __init__(self, db: Session):
        self.db = db

    def check(
        self,
        contract: Contract,
    ) -> ContractEligibilityResult:

        # ---------------------------------------------------------
        # Contract existence
        # ---------------------------------------------------------

        if contract is None:
            return ContractEligibilityResult(
                eligible=False,
                reason="Contract does not exist.",
            )

        # ---------------------------------------------------------
        # Original document
        # ---------------------------------------------------------

        if not contract.storage_key:
            return ContractEligibilityResult(
                eligible=False,
                reason="Original contract document is not available.",
            )

        # ---------------------------------------------------------
        # Contract document records
        #
        # Do not use scalar_one_or_none() because a contract
        # can have multiple document records.
        # ---------------------------------------------------------

        document_statement = (
            select(ContractDocument)
            .where(
                ContractDocument.contract_id == contract.id
            )
        )

        documents = (
            self.db.execute(document_statement)
            .scalars()
            .all()
        )

        # No document record at all.
        if not documents:
            return ContractEligibilityResult(
                eligible=False,
                reason="Contract document record does not exist.",
            )

        # ---------------------------------------------------------
        # Find a completed document
        # ---------------------------------------------------------

        completed_documents = [
            document
            for document in documents
            if (document.processing_status or "").lower()
            == self.COMPLETED_STATUS
        ]

        if not completed_documents:
            return ContractEligibilityResult(
                eligible=False,
                reason="Contract document processing is not completed.",
            )

        # Use the first completed document with extracted text.
        document = next(
            (
                item
                for item in completed_documents
                if item.extracted_text
                and item.extracted_text.strip()
            ),
            None,
        )

        # ---------------------------------------------------------
        # Extracted text
        # ---------------------------------------------------------

        if document is None:
            return ContractEligibilityResult(
                eligible=False,
                reason="Contract text has not been extracted.",
            )

        # ---------------------------------------------------------
        # Structured contract information
        #
        # contract_id is unique in this table.
        # ---------------------------------------------------------

        information_statement = select(
            ContractInformation
        ).where(
            ContractInformation.contract_id == contract.id
        )

        contract_information = (
            self.db.execute(information_statement)
            .scalar_one_or_none()
        )

        if contract_information is None:
            return ContractEligibilityResult(
                eligible=False,
                reason="Structured contract information is not available.",
            )

        # ---------------------------------------------------------
        # Financial analysis
        #
        # contract_id is unique in this table.
        # ---------------------------------------------------------

        financial_statement = select(
            FinancialAnalysis
        ).where(
            FinancialAnalysis.contract_id == contract.id
        )

        financial_analysis = (
            self.db.execute(financial_statement)
            .scalar_one_or_none()
        )

        if financial_analysis is None:
            return ContractEligibilityResult(
                eligible=False,
                reason="Financial analysis is not available.",
            )

        # ---------------------------------------------------------
        # Decision score
        #
        # contract_id is unique in this table.
        # ---------------------------------------------------------

        decision_statement = select(
            DecisionScore
        ).where(
            DecisionScore.contract_id == contract.id
        )

        decision_score = (
            self.db.execute(decision_statement)
            .scalar_one_or_none()
        )

        if decision_score is None:
            return ContractEligibilityResult(
                eligible=False,
                reason="Decision score has not been calculated.",
            )

        # ---------------------------------------------------------
        # Final score
        # ---------------------------------------------------------

        if decision_score.score is None:
            return ContractEligibilityResult(
                eligible=False,
                reason="Final decision score is not available.",
            )

        # ---------------------------------------------------------
        # Eligible
        # ---------------------------------------------------------

        return ContractEligibilityResult(
            eligible=True,
            reason="Contract is eligible for decision analysis.",
        )

    def is_eligible(
        self,
        contract: Contract,
    ) -> bool:
        return self.check(contract).eligible