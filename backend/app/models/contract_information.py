from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base


class ContractInformation(Base):
    __tablename__ = "contract_information"

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

    client_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    vendor_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    contract_value: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 2),
        nullable=True,
    )

    currency: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )

    payment_terms: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    renewal_terms: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    termination_terms: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    obligations: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    dependencies: Mapped[str | None] = mapped_column(
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