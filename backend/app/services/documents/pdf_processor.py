import fitz

from backend.app.services.documents.base import DocumentProcessor


class PDFProcessor(DocumentProcessor):

    def extract_text(self, file_path: str) -> str:
        document = fitz.open(file_path)

        try:
            pages = []

            for page in document:
                pages.append(page.get_text())

            return "\n".join(pages)

        finally:
            document.close()