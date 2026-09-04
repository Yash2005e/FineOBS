from sqlalchemy.orm import Session

from backend.app.models.exception import ExceptionRecord
from backend.app.services.reporting.audit import (
    create_audit_log,
)


def create_exception(
    db: Session,
    data: dict,
) -> ExceptionRecord:

    exception = ExceptionRecord(
        payment_id=data["payment_id"],
        order_id=data.get("order_id"),
        settlement_id=data.get("settlement_id"),
        exception_type=data["exception_type"],
        payment_amount=data.get("payment_amount"),
        settlement_amount=data.get("settlement_amount"),
        difference_amount=data.get("difference_amount"),
        confidence=data.get("confidence"),
        explanation=data.get("explanation"),
        status="OPEN",
    )

    db.add(exception)
    db.flush()

    create_audit_log(
        db,
        entity_type="EXCEPTION",
        entity_id=str(exception.id),
        action="CREATED",
        old_status=None,
        new_status="OPEN",
        actor="SYSTEM",
        comment="Exception created by FineOBS.",
    )

    return exception


def update_exception_status(
    db: Session,
    exception: ExceptionRecord,
    *,
    new_status: str,
    reviewer: str,
    comment: str | None = None,
) -> ExceptionRecord:

    old_status = exception.status

    exception.status = new_status
    exception.reviewer = reviewer
    exception.reviewer_comment = comment

    create_audit_log(
        db,
        entity_type="EXCEPTION",
        entity_id=str(exception.id),
        action="STATUS_CHANGED",
        old_status=old_status,
        new_status=new_status,
        actor=reviewer,
        comment=comment,
    )

    db.flush()

    return exception