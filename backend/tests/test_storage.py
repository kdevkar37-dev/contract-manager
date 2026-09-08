from pathlib import Path

from backend.app.services.storage.minio_service import (
    MinioStorageService,
)


def test_minio_upload_and_download(tmp_path: Path):
    service = MinioStorageService()

    filename = "test-contract.txt"

    file_data = b"This is a MinIO storage test."

    object_name = "tests/test-contract.txt"

    uploaded_object = service.upload_file(
        object_name=object_name,
        file_data=file_data,
        content_type="text/plain",
    )

    assert uploaded_object == object_name

    destination = tmp_path / filename

    downloaded_file = service.download_file(
        object_name=object_name,
        destination=str(destination),
    )

    assert downloaded_file == str(destination)

    assert destination.read_bytes() == file_data