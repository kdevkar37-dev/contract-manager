import pytest

from backend.app.services.intake.service import IntakeService


def test_valid_file_size():
    service = IntakeService()

    service.validate_file(
        filename="contract.pdf",
        file_size=1024,
    )


def test_file_size_limit():
    service = IntakeService()

    max_size = 25 * 1024 * 1024

    service.validate_file(
        filename="contract.pdf",
        file_size=max_size,
    )


def test_file_size_exceeds_limit():
    service = IntakeService()

    max_size = 25 * 1024 * 1024

    with pytest.raises(ValueError, match="File size exceeds"):
        service.validate_file(
            filename="contract.pdf",
            file_size=max_size + 1,
        )