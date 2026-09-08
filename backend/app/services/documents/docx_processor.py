from docx import Document

from backend.app.services.documents.base import DocumentProcessor


class DOCXProcessor(DocumentProcessor):

    def extract_text(self, file_path: str) -> str:
        document = Document(file_path)

        paragraphs = [
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        return "\n".join(paragraphs)