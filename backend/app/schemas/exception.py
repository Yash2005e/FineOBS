from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ExceptionResponse(BaseModel):
    id: int

    payment_id: str
    order_id: str | None
    settlement_id: str | None

    exception_type: str

    payment_amount: float | None
    settlement_amount: float | None
    difference_amount: float | None

    confidence: float | None
    explanation: str | None

    status: str

    reviewer: str | None
    reviewer_comment: str | None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class ExceptionActionRequest(BaseModel):
    reviewer: str
    comment: str | None = None