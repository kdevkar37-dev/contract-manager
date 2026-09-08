from pathlib import Path

from backend.app.services.documents.base import DocumentProcessor
from backend.app.services.documents.docx_processor import DOCXProcessor
from backend.app.services.documents.pdf_processor import PDFProcessor
from backend.app.services.documents.txt_processor import TXTProcessor


class DocumentProcessorFactory:

    _processors = {
        ".pdf": PDFProcessor,
        ".docx": DOCXProcessor,
        ".txt": TXTProcessor,
    }

    @classmethod
    def create(
        cls,
        filename: str,
    ) -> DocumentProcessor:
        extension = Path(filename).suffix.lower()

        processor_class = cls._processors.get(extension)

        if processor_class is None:
            raise ValueError(
                f"Unsupported document type: {extension}"
            )

        return processor_class()