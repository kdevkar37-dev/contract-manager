from pathlib import Path

from backend.app.services.documents.base import DocumentProcessor


class TXTProcessor(DocumentProcessor):

    def extract_text(self, file_path: str) -> str:
        path = Path(file_path)

        return path.read_text(
            encoding="utf-8"
        )