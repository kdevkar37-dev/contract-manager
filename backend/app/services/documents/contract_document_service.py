import tempfile
from pathlib import Path

from backend.app.services.documents.service import DocumentService
from backend.app.services.storage.minio_service import (
    MinioStorageService,
)


class ContractDocumentService:
    def __init__(self):
        self.storage = MinioStorageService()
        self.document_service = DocumentService()

    def extract_text(
        self,
        filename: str,
        storage_key: str,
    ) -> str:
        extension = Path(filename).suffix.lower()

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / f"document{extension}"

            self.storage.download_file(
                object_name=storage_key,
                destination=str(file_path),
            )

            return self.document_service.extract_text(
                filename=filename,
                file_path=str(file_path),
            )