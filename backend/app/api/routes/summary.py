from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.exception import ExceptionRecord


router = APIRouter(
    prefix="/summary",
    tags=["Summary"],
)


@router.get("")
def get_summary(
    db: Session = Depends(get_db),
):
    total = db.scalar(
        select(func.count(ExceptionRecord.id))
    ) or 0

    open_count = db.scalar(
        select(func.count(ExceptionRecord.id)).where(
            ExceptionRecord.status == "OPEN"
        )
    ) or 0

    approved = db.scalar(
        select(func.count(ExceptionRecord.id)).where(
            ExceptionRecord.status == "APPROVED"
        )
    ) or 0

    rejected = db.scalar(
        select(func.count(ExceptionRecord.id)).where(
            ExceptionRecord.status == "REJECTED"
        )
    ) or 0

    overridden = db.scalar(
        select(func.count(ExceptionRecord.id)).where(
            ExceptionRecord.status == "OVERRIDDEN"
        )
    ) or 0

    return {
        "total_exceptions": total,
        "open": open_count,
        "approved": approved,
        "rejected": rejected,
        "overridden": overridden,
    }