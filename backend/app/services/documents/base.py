from abc import ABC, abstractmethod


class DocumentProcessor(ABC):

    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        """
        Extract text from a document.

        Each document processor must implement
        this method.
        """
        pass