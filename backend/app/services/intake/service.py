from pathlib import Path
from typing import BinaryIO
from uuid import uuid4

from sqlalchemy.orm import Session

from backend.app.core.config import settings
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

    def validate_file(
        self,
        filename: str,
        file_size: int | None = None,
        file_header: bytes | None = None,
    ) -> None:
        extension = Path(filename).suffix.lower()

        if extension not in self.ALLOWED_EXTENSIONS:
            raise ValueError(
                "Unsupported file type. "
                "Only PDF, DOCX, and TXT files are allowed."
            )

        if file_size is not None:
            max_size = settings.max_upload_size_mb * 1024 * 1024

            if file_size > max_size:
                raise ValueError(
                    f"File size exceeds the maximum allowed size "
                    f"of {settings.max_upload_size_mb} MB."
                )

        if file_header is not None:
            self._validate_file_signature(
                extension=extension,
                file_header=file_header,
            )

    def _validate_file_signature(
        self,
        extension: str,
        file_header: bytes,
    ) -> None:
        if extension == ".pdf":
            if not file_header.startswith(b"%PDF"):
                raise ValueError(
                    "File content does not match the PDF format."
                )

        elif extension == ".docx":
            if not file_header.startswith(b"PK"):
                raise ValueError(
                    "File content does not match the DOCX format."
                )

        elif extension == ".txt":
            try:
                file_header.decode("utf-8")
            except UnicodeDecodeError:
                raise ValueError(
                    "File content does not appear to be a valid text file."
                )

    def store_file(
        self,
        filename: str,
        file_data: BinaryIO,
        file_size: int,
        content_type: str,
    ) -> str:
        extension = Path(filename).suffix.lower()

        object_name = f"contracts/{uuid4()}{extension}"

        return self.storage.upload_file(
            object_name=object_name,
            file_data=file_data,
            file_size=file_size,
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