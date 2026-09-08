from pathlib import Path
from uuid import uuid4

from sqlalchemy.orm import Session

from backend.app.models.contract import Contract
from backend.app.services.storage.minio_service import MinioStorageService


class IntakeService:
    ALLOWED_EXTENSIONS = {
        ".pdf",
        ".docx",
        ".txt",
    }

    def __init__(self, db: Session | None = None):
        self.db = db
        self.storage = MinioStorageService()

    def validate_file(self, filename: str) -> None:
        extension = Path(filename).suffix.lower()

        if extension not in self.ALLOWED_EXTENSIONS:
            raise ValueError(
                "Unsupported file type. "
                "Only PDF, DOCX, and TXT files are allowed."
            )

    def store_file(
        self,
        filename: str,
        file_data: bytes,
        content_type: str,
    ) -> str:
        extension = Path(filename).suffix.lower()

        object_name = (
            f"contracts/{uuid4()}{extension}"
        )

        return self.storage.upload_file(
            object_name=object_name,
            file_data=file_data,
            content_type=content_type,
        )

    def create_contract_record(
        self,
        filename: str,
        content_type: str,
        storage_key: str,
    ) -> Contract:
        if self.db is None:
            raise RuntimeError(
                "Database session is required "
                "to create a contract record."
            )

        contract = Contract(
            contract_id=f"CNT-{uuid4()}",
            name=Path(filename).stem,
            source_type="manual",
            original_filename=filename,
            mime_type=content_type,
            storage_key=storage_key,
            status="pending",
        )

        self.db.add(contract)
        self.db.commit()
        self.db.refresh(contract)

        return contract