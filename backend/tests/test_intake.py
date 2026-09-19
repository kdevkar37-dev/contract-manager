import pytest

from backend.app.core.config import settings
from backend.app.services.intake.service import IntakeService


def test_validate_pdf_file():
    service = IntakeService()

    service.validate_file(
        "contract.pdf",
        file_size=1024,
        file_header=b"%PDF-1.7",
    )


def test_validate_docx_file():
    service = IntakeService()

    service.validate_file(
        "contract.docx",
        file_size=1024,
        file_header=b"PK\x03\x04",
    )


def test_validate_txt_file():
    service = IntakeService()

    service.validate_file(
        "contract.txt",
        file_size=1024,
        file_header=b"This is a contract.",
    )


def test_reject_unsupported_file():
    service = IntakeService()

    with pytest.raises(ValueError, match="Unsupported file type"):
        service.validate_file(
            "contract.exe",
            file_size=1024,
            file_header=b"MZ",
        )


def test_reject_file_with_wrong_pdf_signature():
    service = IntakeService()

    with pytest.raises(
        ValueError,
        match="does not match the PDF format",
    ):
        service.validate_file(
            "contract.pdf",
            file_size=1024,
            file_header=b"NOT-A-PDF",
        )


def test_reject_file_with_wrong_docx_signature():
    service = IntakeService()

    with pytest.raises(
        ValueError,
        match="does not match the DOCX format",
    ):
        service.validate_file(
            "contract.docx",
            file_size=1024,
            file_header=b"NOT-A-DOCX",
        )


def test_reject_invalid_txt_encoding():
    service = IntakeService()

    with pytest.raises(
        ValueError,
        match="valid text file",
    ):
        service.validate_file(
            "contract.txt",
            file_size=1024,
            file_header=b"\xff\xfe\xfd",
        )


def test_reject_file_above_maximum_size():
    service = IntakeService()

    max_size = settings.max_upload_size_mb * 1024 * 1024

    with pytest.raises(
        ValueError,
        match="File size exceeds",
    ):
        service.validate_file(
            "contract.pdf",
            file_size=max_size + 1,
            file_header=b"%PDF-1.7",
        )