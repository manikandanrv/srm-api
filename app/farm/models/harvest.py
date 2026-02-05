"""
Harvest tracking model.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models.base import BaseModel


class QualityRating(str):
    """Harvest quality ratings."""

    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class Harvest(BaseModel):
    """
    Harvest record for tracking yield and quality.

    Links to field, cultivation cycle, and optionally the harvesting task.
    """

    __tablename__ = "harvests"

    field_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fields.id"), nullable=False
    )
    cycle_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cultivation_cycles.id"), nullable=True
    )
    task_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("farm_tasks.id"), nullable=True
    )

    # Harvest details
    harvest_date: Mapped[date] = mapped_column(Date, nullable=False)
    harvest_number: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )  # Which harvest in the cycle

    # Yield
    yield_kg: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    area_harvested_acres: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 2), nullable=True
    )

    # Quality
    quality_rating: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    moisture_content: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2), nullable=True
    )

    # Transport/Delivery
    destination: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )  # Where it was sent
    transport_vehicle: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Receipt confirmation
    received_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    received_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    receipt_confirmed: Mapped[bool] = mapped_column(
        default=False, nullable=False
    )

    # Workers involved
    harvested_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Harvest(field_id={self.field_id}, date={self.harvest_date}, yield={self.yield_kg}kg)>"
