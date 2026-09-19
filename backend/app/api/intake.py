from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.permissions import require_contract_manager
from backend.app.services.audit.service import AuditLogService
from backend.app.services.intake.service import IntakeService
from backend.app.workers.tasks import process_contract_task


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
    current_user=Depends(require_contract_manager),
):
    """
    Upload a contract and queue it for background processing.

    Allowed roles:
        - admin
        - manager
    """

    service = IntakeService(db)

    filename = file.filename or ""
    content_type = file.content_type or "application/octet-stream"

    try:
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)

        file_header = await file.read(512)
        file.file.seek(0)

        service.validate_file(
            filename=filename,
            file_size=file_size,
            file_header=file_header,
        )

        storage_key = service.store_file(
            filename=filename,
            file_data=file.file,
            file_size=file_size,
            content_type=content_type,
        )

        contract = service.create_contract_record(
            filename=filename,
            content_type=content_type,
            storage_key=storage_key,
        )

        AuditLogService(db).record(
            user_id=current_user.id,
            action="CONTRACT_UPLOADED",
            resource_type="contract",
            resource_id=contract.contract_id,
            details=f"Uploaded contract file: {filename}",
        )

        process_contract_task.delay(contract.contract_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return {
        "message": "Contract uploaded successfully",
        "contract_id": contract.contract_id,
        "name": contract.name,
        "filename": contract.original_filename,
        "content_type": contract.mime_type,
        "storage_key": contract.storage_key,
        "status": "processing",
    }