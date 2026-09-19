from backend.app.models.audit_log import AuditLog
from backend.app.models.user import User
from backend.app.services.audit.service import AuditLogService


def create_test_user(db_session, email="audit@example.com"):
    user = User(
        email=email,
        password_hash="test-password-hash",
        role="manager",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_record_creates_audit_log(db_session):
    user = create_test_user(db_session)

    service = AuditLogService(db_session)

    audit_log = service.record(
        user_id=user.id,
        action="CONTRACT_UPLOADED",
        resource_type="contract",
        resource_id="CNT-123",
        details="Uploaded contract.pdf",
    )

    assert audit_log.id is not None
    assert audit_log.user_id == user.id
    assert audit_log.action == "CONTRACT_UPLOADED"
    assert audit_log.resource_type == "contract"
    assert audit_log.resource_id == "CNT-123"
    assert audit_log.details == "Uploaded contract.pdf"


def test_get_resource_history_returns_latest_first(db_session):
    user = create_test_user(db_session)

    service = AuditLogService(db_session)

    service.record(
        user_id=user.id,
        action="CONTRACT_UPLOADED",
        resource_type="contract",
        resource_id="CNT-123",
    )

    service.record(
        user_id=user.id,
        action="CONTRACT_ANALYZED",
        resource_type="contract",
        resource_id="CNT-123",
    )

    history = service.get_resource_history(
        resource_type="contract",
        resource_id="CNT-123",
    )

    assert len(history) == 2
    assert history[0].action == "CONTRACT_ANALYZED"
    assert history[1].action == "CONTRACT_UPLOADED"


def test_get_user_history_returns_user_audit_logs(db_session):
    user = create_test_user(db_session)

    service = AuditLogService(db_session)

    service.record(
        user_id=user.id,
        action="CONTRACT_UPLOADED",
        resource_type="contract",
        resource_id="CNT-123",
    )

    service.record(
        user_id=user.id,
        action="CONTRACT_ANALYZED",
        resource_type="contract",
        resource_id="CNT-123",
    )

    history = service.get_user_history(user_id=user.id)

    assert len(history) == 2
    assert all(log.user_id == user.id for log in history)