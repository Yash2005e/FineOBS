from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.audit import AuditLog


router = APIRouter(
    prefix="/audit",
    tags=["Audit"],
)


@router.get("")
def get_audit_logs(
    db: Session = Depends(get_db),
):
    query = select(AuditLog).order_by(
        AuditLog.created_at.desc()
    )

    logs = list(
        db.scalars(query).all()
    )

    return logs