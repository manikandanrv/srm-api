"""
Crop variety and cultivation cycle models.
"""

import uuid
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models.base import BaseModel


class CropCategory(str, Enum):
    """Categories of fodder crops."""

    MULTI_CUT_GRASS = "multi_cut_grass"
    SINGLE_CUT_LEGUME = "single_cut_legume"
    COVER_CROP = "cover_crop"


class GrowthType(str, Enum):
    """Growth duration type."""

    LONG_TERM = "long_term"  # Perennial, multi-year
    SHORT_TERM = "short_term"  # Annual, single season


class CropVariety(BaseModel):
    """
    Crop variety master data.

    Includes grass varieties (Super Napier, CO-4, CO-5) and legumes (Cowpea, Hedge Lucerne).
    """

    __tablename__ = "crop_varieties"

    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    name_tamil: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    category: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # CropCategory value
    growth_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # GrowthType value

    # Harvest timing
    first_harvest_days: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )  # Days to first harvest
    subsequent_harvest_days: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )  # Days between harvests
    lifespan_years: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(3, 1), nullable=True
    )  # For perennial crops

    # Growing requirements
    water_requirement: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # 'low', 'medium', 'high'
    soil_type_preferred: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    optimal_temperature: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Nutritional information
    nutrition_profile: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )  # {protein_pct, fiber_pct, etc.}

    # Display
    icon_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description_tamil: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<CropVariety(code={self.code}, name={self.name}, category={self.category})>"


class CultivationCycle(BaseModel):
    """
    Track complete cultivation cycles for each field.

    A cycle starts with sowing and ends when the crop is removed or dies.
    """

    __tablename__ = "cultivation_cycles"

    field_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fields.id"), nullable=False
    )
    crop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("crop_varieties.id"), nullable=False
    )

    cycle_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    sowing_date: Mapped[date] = mapped_column(Date, nullable=False)
    expected_first_harvest: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    actual_first_harvest: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Cycle status
    status: Mapped[str] = mapped_column(
        String(50), default="active", nullable=False
    )  # 'active', 'completed', 'failed'
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_reason: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True
    )  # Why cycle ended

    # Yield tracking
    total_harvests: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_yield_kg: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=0, nullable=False
    )

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<CultivationCycle(field_id={self.field_id}, crop_id={self.crop_id}, status={self.status})>"
