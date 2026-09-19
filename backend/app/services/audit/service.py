from __future__ import annotations

from sqlalchemy.orm import Session

from backend.app.models.audit_log import AuditLog
from backend.app.repositories.audit_logs import AuditLogRepository


class AuditLogService:
    def __init__(self, db: Session):
        self.repository = AuditLogRepository(db)

    def record(
        self,
        *,
        user_id: int | None,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        details: str | None = None,
    ) -> AuditLog:
        return self.repository.create(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
        )

    def get_resource_history(
        self,
        *,
        resource_type: str,
        resource_id: str,
    ) -> list[AuditLog]:
        return self.repository.list_by_resource(
            resource_type=resource_type,
            resource_id=resource_id,
        )

    def get_user_history(
        self,
        *,
        user_id: int,
    ) -> list[AuditLog]:
        return self.repository.list_by_user(user_id)