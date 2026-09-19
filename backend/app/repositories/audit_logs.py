from __future__ import annotations

from sqlalchemy.orm import Session

from backend.app.models.audit_log import AuditLog


class AuditLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        *,
        user_id: int | None,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        details: str | None = None,
    ) -> AuditLog:
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
        )

        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)

        return audit_log

    def list_by_resource(
        self,
        resource_type: str,
        resource_id: str,
    ) -> list[AuditLog]:
        return (
            self.db.query(AuditLog)
            .filter(
                AuditLog.resource_type == resource_type,
                AuditLog.resource_id == resource_id,
            )
            .order_by(
                AuditLog.created_at.desc(),
                AuditLog.id.desc(),
            )
            .all()
        )

    def list_by_user(self, user_id: int) -> list[AuditLog]:
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.user_id == user_id)
            .order_by(
                AuditLog.created_at.desc(),
                AuditLog.id.desc(),
            )
            .all()
        )