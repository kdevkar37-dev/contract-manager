from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base


class DecisionScore(Base):
    __tablename__ = "decision_scores"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    contract_id: Mapped[int] = mapped_column(
        ForeignKey("contracts.id"),
        unique=True,
        nullable=False,
        index=True,
    )

    score: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 4),
        nullable=True,
    )

    financial_score: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 4),
        nullable=True,
    )

    risk_score: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 4),
        nullable=True,
    )

    contract_value_score: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 4),
        nullable=True,
    )

    financial_weight: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
    )

    risk_weight: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
    )

    contract_value_weight: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
    )

    assumptions: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    explanation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )