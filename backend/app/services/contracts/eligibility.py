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
    """
    Result of checking whether a contract is eligible
    for decision analysis.
    """

    eligible: bool
    reason: str


class ContractEligibilityService:
    """
    Determines whether a contract contains enough successfully
    processed information to participate in decision analysis.

    Eligibility flow:

        Contract
            ↓
        Uploaded document
            ↓
        Document processing completed
            ↓
        Contract information exists
            ↓
        Financial analysis exists
            ↓
        Decision score exists
            ↓
        Eligible
    """

    COMPLETED_STATUS = "completed"

    def __init__(self, db: Session):
        self.db = db

    def check(self, contract: Contract) -> ContractEligibilityResult:
        """
        Check whether a contract is eligible for decision analysis.
        """

        if contract is None:
            return ContractEligibilityResult(
                eligible=False,
                reason="Contract does not exist.",
            )

        # ---------------------------------------------------------
        # 1. Original uploaded document must exist
        # ---------------------------------------------------------

        if not contract.storage_key:
            return ContractEligibilityResult(
                eligible=False,
                reason="Original contract document is not available.",
            )

        # ---------------------------------------------------------
        # 2. Document processing must be completed
        # ---------------------------------------------------------

        document = self.db.execute(
            select(ContractDocument).where(
                ContractDocument.contract_id == contract.id
            )
        ).scalar_one_or_none()

        if document is None:
            return ContractEligibilityResult(
                eligible=False,
                reason="Contract document record does not exist.",
            )

        if (
            document.processing_status or ""
        ).lower() != self.COMPLETED_STATUS:
            return ContractEligibilityResult(
                eligible=False,
                reason="Contract document processing is not completed.",
            )

        # ---------------------------------------------------------
        # 3. Extracted text must exist
        # ---------------------------------------------------------

        if not document.extracted_text or not document.extracted_text.strip():
            return ContractEligibilityResult(
                eligible=False,
                reason="Contract text has not been extracted.",
            )

        # ---------------------------------------------------------
        # 4. Structured contract information must exist
        # ---------------------------------------------------------

        contract_information = self.db.execute(
            select(ContractInformation).where(
                ContractInformation.contract_id == contract.id
            )
        ).scalar_one_or_none()

        if contract_information is None:
            return ContractEligibilityResult(
                eligible=False,
                reason="Structured contract information is not available.",
            )

        # ---------------------------------------------------------
        # 5. Financial analysis must exist
        # ---------------------------------------------------------

        financial_analysis = self.db.execute(
            select(FinancialAnalysis).where(
                FinancialAnalysis.contract_id == contract.id
            )
        ).scalar_one_or_none()

        if financial_analysis is None:
            return ContractEligibilityResult(
                eligible=False,
                reason="Financial analysis is not available.",
            )

        # ---------------------------------------------------------
        # 6. Decision score must exist
        # ---------------------------------------------------------

        decision_score = self.db.execute(
            select(DecisionScore).where(
                DecisionScore.contract_id == contract.id
            )
        ).scalar_one_or_none()

        if decision_score is None:
            return ContractEligibilityResult(
                eligible=False,
                reason="Decision score has not been calculated.",
            )

        if decision_score.score is None:
            return ContractEligibilityResult(
                eligible=False,
                reason="Final decision score is not available.",
            )

        # ---------------------------------------------------------
        # Contract is eligible
        # ---------------------------------------------------------

        return ContractEligibilityResult(
            eligible=True,
            reason="Contract is eligible for decision analysis.",
        )

    def is_eligible(self, contract: Contract) -> bool:
        """
        Convenience method returning only the eligibility status.
        """

        return self.check(contract).eligible