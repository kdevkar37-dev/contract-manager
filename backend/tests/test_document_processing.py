from pathlib import Path
from shutil import copyfile
from unittest.mock import patch

import fitz
import pytest
from docx import Document

from backend.app.services.documents.contract_document_service import (
    ContractDocumentService,
)
from backend.app.services.documents.docx_processor import DOCXProcessor
from backend.app.services.documents.factory import DocumentProcessorFactory
from backend.app.services.documents.pdf_processor import PDFProcessor
from backend.app.services.documents.service import DocumentService
from backend.app.services.documents.txt_processor import TXTProcessor


def test_txt_processor_extracts_text(tmp_path: Path):
    file_path = tmp_path / "contract.txt"

    file_path.write_text(
        "This is a test contract.",
        encoding="utf-8",
    )

    processor = TXTProcessor()

    text = processor.extract_text(
        str(file_path)
    )

    assert text == "This is a test contract."


def test_pdf_processor_extracts_text(tmp_path: Path):
    file_path = tmp_path / "contract.pdf"

    document = fitz.open()

    page = document.new_page()

    page.insert_text(
        (72, 72),
        "This is a test PDF contract.",
    )

    document.save(file_path)
    document.close()

    processor = PDFProcessor()

    text = processor.extract_text(
        str(file_path)
    )

    assert "This is a test PDF contract." in text


def test_docx_processor_extracts_text(tmp_path: Path):
    file_path = tmp_path / "contract.docx"

    document = Document()

    document.add_paragraph(
        "This is a test DOCX contract."
    )

    document.save(file_path)

    processor = DOCXProcessor()

    text = processor.extract_text(
        str(file_path)
    )

    assert "This is a test DOCX contract." in text


def test_factory_creates_pdf_processor():
    processor = DocumentProcessorFactory.create(
        "contract.pdf"
    )

    assert isinstance(
        processor,
        PDFProcessor,
    )


def test_factory_creates_docx_processor():
    processor = DocumentProcessorFactory.create(
        "contract.docx"
    )

    assert isinstance(
        processor,
        DOCXProcessor,
    )


def test_factory_creates_txt_processor():
    processor = DocumentProcessorFactory.create(
        "contract.txt"
    )

    assert isinstance(
        processor,
        TXTProcessor,
    )


def test_factory_rejects_unsupported_file():
    with pytest.raises(ValueError):
        DocumentProcessorFactory.create(
            "contract.exe"
        )


def test_document_service_extracts_txt(tmp_path: Path):
    file_path = tmp_path / "contract.txt"

    file_path.write_text(
        "This is a service test contract.",
        encoding="utf-8",
    )

    service = DocumentService()

    text = service.extract_text(
        filename="contract.txt",
        file_path=str(file_path),
    )

    assert text == "This is a service test contract."


def test_contract_document_service_extracts_txt(
    tmp_path: Path,
):
    source_file = tmp_path / "source.txt"

    source_file.write_text(
        "This is a stored contract.",
        encoding="utf-8",
    )

    service = ContractDocumentService()

    def mock_download_file(
        object_name: str,
        destination: str,
    ) -> str:
        copyfile(
            source_file,
            destination,
        )

        return destination

    with patch.object(
        service.storage,
        "download_file",
        side_effect=mock_download_file,
    ) as mock_download:

        text = service.extract_text(
            filename="contract.txt",
            storage_key="contracts/test-contract.txt",
        )

    mock_download.assert_called_once()

    assert text == "This is a stored contract."