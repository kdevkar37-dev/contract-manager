import logging
import time

from sqlalchemy.orm import Session

from ai.extraction.financial import FinancialExtractionService
from ai.rag.contract_indexing import ContractIndexingService

from backend.app.repositories.contract_documents import (
    ContractDocumentRepository,
)
from backend.app.repositories.contracts import ContractRepository

from backend.app.services.contracts.information_service import (
    ContractInformationService,
)
from backend.app.services.documents.contract_document_service import (
    ContractDocumentService,
)
from backend.app.services.financial.service import (
    FinancialAnalysisService,
)
from backend.app.services.risk.service import (
    RiskAnalysisService,
)


logger = logging.getLogger(__name__)


class ContractProcessingService:
    def __init__(self, db: Session):
        self.repository = ContractRepository(db)
        self.document_repository = ContractDocumentRepository(db)

        self.document_service = ContractDocumentService()
        self.indexing_service = ContractIndexingService()

        self.contract_information_service = (
            ContractInformationService(db)
        )

        self.financial_extraction_service = (
            FinancialExtractionService()
        )

        self.financial_analysis_service = (
            FinancialAnalysisService(db)
        )

        self.risk_analysis_service = (
            RiskAnalysisService(db)
        )

    def extract_contract_text(
        self,
        contract_id: str,
    ) -> str:
        total_start = time.perf_counter()

        logger.info(
            "Contract processing started: %s",
            contract_id,
        )

        contract = self.repository.get_by_contract_id(
            contract_id
        )

        if contract is None:
            raise ValueError("Contract not found")

        if not contract.storage_key:
            raise ValueError(
                "Contract does not have a stored document"
            )

        if not contract.original_filename:
            raise ValueError(
                "Contract does not have an original filename"
            )

        self.repository.update_status(
            contract,
            "processing",
        )

        # ---------------------------------------------------------
        # REUSE EXISTING DOCUMENT RECORD
        # ---------------------------------------------------------

        document = self.document_repository.get_by_contract_id(
            contract.id
        )

        if document is None:
            document = self.document_repository.create(
                contract.id
            )

        try:
            # -----------------------------------------------------
            # TEXT EXTRACTION
            # -----------------------------------------------------

            start = time.perf_counter()

            extracted_text = self.document_service.extract_text(
                filename=contract.original_filename,
                storage_key=contract.storage_key,
            )

            logger.info(
                "Text extraction completed in %.2f seconds",
                time.perf_counter() - start,
            )

            if not extracted_text.strip():
                raise ValueError(
                    "No text could be extracted from the document."
                )

            self.document_repository.update_extracted_text(
                document=document,
                extracted_text=extracted_text,
            )

            # -----------------------------------------------------
            # RAG INDEXING
            # -----------------------------------------------------

            start = time.perf_counter()

            self.indexing_service.index_contract(
                contract_id=contract.contract_id,
                document_id=document.id,
                extracted_text=extracted_text,
            )

            logger.info(
                "RAG indexing completed in %.2f seconds",
                time.perf_counter() - start,
            )

            # -----------------------------------------------------
            # STRUCTURED CONTRACT INFORMATION
            # -----------------------------------------------------

            start = time.perf_counter()

            self.contract_information_service.extract_and_save(
                contract_id=contract.contract_id,
                contract_text=extracted_text,
            )

            logger.info(
                "Contract information extraction completed in %.2f seconds",
                time.perf_counter() - start,
            )

            # -----------------------------------------------------
            # FINANCIAL ANALYSIS
            # -----------------------------------------------------

            start = time.perf_counter()

            financial_inputs = (
                self.financial_extraction_service.extract(
                    extracted_text
                )
            )

            logger.info(
                "Financial extraction completed in %.2f seconds",
                time.perf_counter() - start,
            )

            start = time.perf_counter()

            self.financial_analysis_service.calculate_for_contract(
                contract_id=contract.contract_id,
                inputs=financial_inputs,
            )

            logger.info(
                "Financial calculation completed in %.2f seconds",
                time.perf_counter() - start,
            )

            # -----------------------------------------------------
            # RISK ANALYSIS
            # -----------------------------------------------------

            start = time.perf_counter()

            self.risk_analysis_service.analyze_contract(
                contract_id=contract.contract_id,
                contract_text=extracted_text,
            )

            logger.info(
                "Risk analysis completed in %.2f seconds",
                time.perf_counter() - start,
            )

            # -----------------------------------------------------
            # COMPLETE
            # -----------------------------------------------------

            self.repository.update_status(
                contract,
                "completed",
            )

            total_time = time.perf_counter() - total_start

            logger.info(
                "Contract processing completed: %s in %.2f seconds",
                contract_id,
                total_time,
            )

            return extracted_text

        except Exception as exc:
            logger.exception(
                "Contract processing failed: %s",
                contract_id,
            )

            self.document_repository.mark_failed(
                document=document,
                error_message=str(exc),
            )

            self.repository.update_status(
                contract,
                "failed",
            )

            raise