from sqlalchemy.orm import Session

from backend.app.models.risk_analysis import RiskAnalysis
from backend.app.repositories.contracts import ContractRepository
from backend.app.repositories.risk_analysis import (
    RiskAnalysisRepository,
)
from backend.app.services.risk.extraction import (
    ExtractedRisk,
    RiskExtractionService,
)


class RiskAnalysisService:
    """
    Coordinates contract risk extraction and persistence.

    Responsibilities:
    - Resolve the public contract ID.
    - Extract risks from contract text.
    - Replace previous risk results.
    - Persist the new risks.

    This service does NOT:
    - Calculate financial values.
    - Calculate decision scores.
    - Generate embeddings.
    """

    def __init__(
        self,
        db: Session,
        extraction_service: RiskExtractionService | None = None,
    ):
        self.contract_repository = ContractRepository(db)

        self.risk_repository = RiskAnalysisRepository(db)

        self.extraction_service = (
            extraction_service
            if extraction_service is not None
            else RiskExtractionService()
        )

    def analyze_contract(
        self,
        contract_id: str,
        contract_text: str,
    ) -> list[RiskAnalysis]:
        """
        Extract and persist risks for a contract.
        """

        contract = self.contract_repository.get_by_contract_id(
            contract_id
        )

        if contract is None:
            raise ValueError("Contract not found")

        extracted_risks = self.extraction_service.extract(
            contract_text
        )

        self.risk_repository.delete_by_contract_id(
            contract.id
        )

        risks = [
            self._to_model(
                contract_id=contract.id,
                risk=risk,
            )
            for risk in extracted_risks
        ]

        return self.risk_repository.create_many(risks)

    def get_risks(
        self,
        contract_id: str,
    ) -> list[RiskAnalysis]:
        """
        Retrieve persisted risks for a contract.
        """

        contract = self.contract_repository.get_by_contract_id(
            contract_id
        )

        if contract is None:
            raise ValueError("Contract not found")

        return self.risk_repository.get_by_contract_id(
            contract.id
        )

    @staticmethod
    def _to_model(
        contract_id: int,
        risk: ExtractedRisk,
    ) -> RiskAnalysis:
        return RiskAnalysis(
            contract_id=contract_id,
            risk_type=risk.risk_type,
            severity=risk.severity,
            title=risk.title,
            description=risk.description,
            evidence=risk.evidence,
            source=risk.source,
            confidence=risk.confidence,
        )