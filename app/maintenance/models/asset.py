"""
Asset and asset category models for maintenance management.
"""

import uuid
from datetime import date
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models.base import BaseModel


class AssetDomain(str, Enum):
    """Asset domains."""

    PLUMBING = "plumbing"
    ELECTRICAL = "electrical"
    HVAC = "hvac"
    GENERAL = "general"


class AssetStatus(str, Enum):
    """Asset operational status."""

    OPERATIONAL = "operational"
    NEEDS_REPAIR = "needs_repair"
    UNDER_REPAIR = "under_repair"
    RETIRED = "retired"


class Criticality(str, Enum):
    """Asset criticality levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AssetCategory(BaseModel):
    """
    Asset category for classification.

    Supports hierarchical categories (e.g., Plumbing > Water Supply > Pumps).
    """

    __tablename__ = "asset_categories"

    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    name_tamil: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    domain: Mapped[str] = mapped_column(String(50), nullable=False)  # AssetDomain
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("asset_categories.id"), nullable=True
    )

    icon_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    default_maintenance_days: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<AssetCategory(code={self.code}, name={self.name}, domain={self.domain})>"


class Asset(BaseModel):
    """
    Asset registry model.

    Tracks all maintainable assets in guest houses including:
    - Plumbing: Pumps, geysers, fixtures
    - Electrical: Fans, lights, distribution boards
    - HVAC: AC units, exhaust fans
    """

    __tablename__ = "assets"

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id"), nullable=False
    )
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("asset_categories.id"), nullable=True
    )

    # Identity
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    name_tamil: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Identification
    qr_code: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)
    serial_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    barcode: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Manufacturer info
    manufacturer: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    model_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Dates
    installation_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    warranty_expiry: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    purchase_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Status
    status: Mapped[str] = mapped_column(
        String(50), default=AssetStatus.OPERATIONAL.value, nullable=False
    )
    criticality: Mapped[str] = mapped_column(
        String(20), default=Criticality.MEDIUM.value, nullable=False
    )

    # Maintenance
    last_maintenance_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    next_maintenance_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    maintenance_interval_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Specifications and extra data
    specifications: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    extra_data: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Description
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<Asset(code={self.code}, name={self.name}, status={self.status})>"
