"""
Field model for farm block management.
"""

import uuid
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Date, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models.base import BaseModel


class FieldType(str, Enum):
    """Types of farm fields."""

    GRASS_BLOCK = "grass_block"
    HORTICULTURE = "horticulture"
    MIXED = "mixed"
    NURSERY = "nursery"


class IrrigationType(str, Enum):
    """Types of irrigation systems."""

    CANAL = "canal"
    DRIP = "drip"
    SPRINKLER = "sprinkler"
    BOREWELL = "borewell"
    FLOOD = "flood"


class FieldStatus(str, Enum):
    """Field operational status."""

    ACTIVE = "active"
    FALLOW = "fallow"
    PREPARATION = "preparation"
    MAINTENANCE = "maintenance"


class Field(BaseModel):
    """
    Field/block model for farm operations.

    Represents cultivation areas with their properties and current status.
    """

    __tablename__ = "fields"

    location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id"), nullable=False
    )

    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    name_tamil: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    field_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default=FieldType.GRASS_BLOCK.value
    )

    # Physical properties
    area_acres: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    soil_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    irrigation_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Current cultivation
    current_crop_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("crop_varieties.id"), nullable=True
    )
    current_cycle_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cultivation_cycles.id"), nullable=True
    )

    # Important dates
    last_sowing_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    last_harvest_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    next_harvest_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    last_fertilizer_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Status
    status: Mapped[str] = mapped_column(
        String(50), default=FieldStatus.ACTIVE.value, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Additional data
    extra_data: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    def __repr__(self) -> str:
        return f"<Field(code={self.code}, name={self.name}, status={self.status})>"
