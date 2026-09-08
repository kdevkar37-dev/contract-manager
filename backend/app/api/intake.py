from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.services.intake.service import IntakeService


router = APIRouter(
    prefix="/intake",
    tags=["Contract Intake"],
)


@router.post(
    "/upload",
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_contract(
    file: UploadFile,
    db: Session = Depends(get_db),
):
    service = IntakeService(db)

    filename = file.filename or ""
    content_type = file.content_type or "application/octet-stream"

    try:
        # 1. Validate the file
        service.validate_file(filename)

        # 2. Read the file
        file_data = await file.read()

        # 3. Store the original file in MinIO
        storage_key = service.store_file(
            filename=filename,
            file_data=file_data,
            content_type=content_type,
        )

        # 4. Create contract record in PostgreSQL
        contract = service.create_contract_record(
            filename=filename,
            content_type=content_type,
            storage_key=storage_key,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    return {
        "message": "Contract uploaded successfully",
        "contract_id": contract.contract_id,
        "name": contract.name,
        "filename": contract.original_filename,
        "content_type": contract.mime_type,
        "storage_key": contract.storage_key,
        "status": contract.status,
    }