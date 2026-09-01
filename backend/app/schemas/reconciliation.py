from pydantic import BaseModel
from typing import Optional


class ReconciliationResult(BaseModel):
    payment_id: str
    order_id: Optional[str] = None
    settlement_id: Optional[str] = None

    status: str
    exception_type: str

    payment_amount: float
    settlement_amount: Optional[float] = None
    difference_amount: Optional[float] = None

    confidence: float
    explanation: str