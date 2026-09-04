from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.exception import ExceptionRecord
from backend.app.schemas.exception import (
    ExceptionActionRequest,
    ExceptionResponse,
)
from backend.app.services.reporting.exceptions import (
    update_exception_status,
)


router = APIRouter(
    prefix="/exceptions",
    tags=["Exceptions"],
)


@router.get(
    "",
    response_model=list[ExceptionResponse],
)
def get_exceptions(
    status: str | None = None,
    db: Session = Depends(get_db),
):
    query = select(ExceptionRecord)

    if status:
        query = query.where(
            ExceptionRecord.status == status.upper()
        )

    query = query.order_by(
        ExceptionRecord.created_at.desc()
    )

    return list(
        db.scalars(query).all()
    )


@router.get(
    "/{exception_id}",
    response_model=ExceptionResponse,
)
def get_exception(
    exception_id: int,
    db: Session = Depends(get_db),
):
    exception = db.get(
        ExceptionRecord,
        exception_id,
    )

    if exception is None:
        raise HTTPException(
            status_code=404,
            detail="Exception not found.",
        )

    return exception


@router.post(
    "/{exception_id}/approve",
    response_model=ExceptionResponse,
)
def approve_exception(
    exception_id: int,
    request: ExceptionActionRequest,
    db: Session = Depends(get_db),
):
    exception = db.get(
        ExceptionRecord,
        exception_id,
    )

    if exception is None:
        raise HTTPException(
            status_code=404,
            detail="Exception not found.",
        )

    if exception.status != "OPEN":
        raise HTTPException(
            status_code=409,
            detail="Only OPEN exceptions can be approved.",
        )

    update_exception_status(
        db,
        exception,
        new_status="APPROVED",
        reviewer=request.reviewer,
        comment=request.comment,
    )

    db.commit()
    db.refresh(exception)

    return exception


@router.post(
    "/{exception_id}/reject",
    response_model=ExceptionResponse,
)
def reject_exception(
    exception_id: int,
    request: ExceptionActionRequest,
    db: Session = Depends(get_db),
):
    exception = db.get(
        ExceptionRecord,
        exception_id,
    )

    if exception is None:
        raise HTTPException(
            status_code=404,
            detail="Exception not found.",
        )

    if exception.status != "OPEN":
        raise HTTPException(
            status_code=409,
            detail="Only OPEN exceptions can be rejected.",
        )

    update_exception_status(
        db,
        exception,
        new_status="REJECTED",
        reviewer=request.reviewer,
        comment=request.comment,
    )

    db.commit()
    db.refresh(exception)

    return exception


@router.post(
    "/{exception_id}/override",
    response_model=ExceptionResponse,
)
def override_exception(
    exception_id: int,
    request: ExceptionActionRequest,
    db: Session = Depends(get_db),
):
    exception = db.get(
        ExceptionRecord,
        exception_id,
    )

    if exception is None:
        raise HTTPException(
            status_code=404,
            detail="Exception not found.",
        )

    if exception.status != "OPEN":
        raise HTTPException(
            status_code=409,
            detail="Only OPEN exceptions can be overridden.",
        )

    update_exception_status(
        db,
        exception,
        new_status="OVERRIDDEN",
        reviewer=request.reviewer,
        comment=request.comment,
    )

    db.commit()
    db.refresh(exception)

    return exception