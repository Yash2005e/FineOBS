from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.database import Base


class ExceptionRecord(Base):
    __tablename__ = "exceptions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    payment_id: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )

    order_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    settlement_id: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    exception_type: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )

    payment_amount: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    settlement_amount: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    difference_amount: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    explanation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="OPEN",
        index=True,
    )

    reviewer: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    reviewer_comment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )