from sqlalchemy.orm import Session

from backend.app.models.audit import AuditLog


def create_audit_log(
    db: Session,
    *,
    entity_type: str,
    entity_id: str,
    action: str,
    old_status: str | None = None,
    new_status: str | None = None,
    actor: str,
    comment: str | None = None,
) -> AuditLog:
    audit = AuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        old_status=old_status,
        new_status=new_status,
        actor=actor,
        comment=comment,
    )

    db.add(audit)

    return audit