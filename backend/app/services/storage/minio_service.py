from pathlib import Path

from minio import Minio

from backend.app.core.config import settings


class MinioStorageService:
    def __init__(self):
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )

        self.bucket = settings.minio_bucket

    def ensure_bucket_exists(self) -> None:
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def upload_file(
        self,
        object_name: str,
        file_data: bytes,
        content_type: str,
    ) -> str:
        self.ensure_bucket_exists()

        from io import BytesIO

        self.client.put_object(
            self.bucket,
            object_name,
            BytesIO(file_data),
            length=len(file_data),
            content_type=content_type,
        )

        return object_name

    def download_file(
        self,
        object_name: str,
        destination: str,
    ) -> str:
        response = self.client.get_object(
            self.bucket,
            object_name,
        )

        try:
            destination_path = Path(destination)

            destination_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            with destination_path.open("wb") as file:
                for chunk in response.stream(32 * 1024):
                    file.write(chunk)

        finally:
            response.close()
            response.release_conn()

        return str(destination_path)