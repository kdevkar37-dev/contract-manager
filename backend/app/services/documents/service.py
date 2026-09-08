from backend.app.services.documents.factory import DocumentProcessorFactory


class DocumentService:

    def extract_text(
        self,
        filename: str,
        file_path: str,
    ) -> str:
        processor = DocumentProcessorFactory.create(
            filename
        )

        return processor.extract_text(
            file_path
        )