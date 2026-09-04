from typing import Literal

from pydantic import BaseModel, Field


class AIVerificationDecision(BaseModel):
    decision: Literal[
        "AUTO_RECONCILE",
        "HUMAN_REVIEW",
        "UNRESOLVED",
    ]

    exception_type: Literal[
        "none",
        "amount_mismatch",
        "missing_settlement",
        "duplicate_settlement",
        "settlement_delay",
        "reference_mismatch",
        "insufficient_evidence",
    ]

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    explanation: str

    evidence: list[str]

    recommended_action: str