import pytest

from backend.app.services.intake.service import IntakeService


def test_validate_pdf_file():
    service = IntakeService()

    service.validate_file("contract.pdf")


def test_validate_docx_file():
    service = IntakeService()

    service.validate_file("contract.docx")


def test_validate_txt_file():
    service = IntakeService()

    service.validate_file("contract.txt")


def test_reject_unsupported_file():
    service = IntakeService()

    with pytest.raises(ValueError):
        service.validate_file("contract.exe")