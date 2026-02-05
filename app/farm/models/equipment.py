"""
Farm equipment model.
"""

import uuid
from datetime import date
from typing import Optional

from sqlalchemy import Boolean, Date, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models.base import BaseModel


class EquipmentStatus(str):
    """Equipment operational status."""

    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    RETIRED = "retired"


class EquipmentCategory(str):
    """Equipment categories."""

    IRRIGATION = "irrigation"
    CULTIVATION = "cultivation"
    TRANSPORT = "transport"
    TOOLS = "tools"
    STORAGE = "storage"


class Equipment(BaseModel):
    """
    Farm equipment and tools tracking.

    Includes irrigation equipment, cultivation tools, and transport vehicles.
    """

    __tablename__ = "farm_equipment"

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )

    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    name_tamil: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Status and location
    status: Mapped[str] = mapped_column(
        String(50), default=EquipmentStatus.AVAILABLE, nullable=False
    )
    current_location_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id"), nullable=True
    )
    assigned_to: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # Maintenance tracking
    purchase_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    last_maintenance_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    next_maintenance_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Specifications
    specifications: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<Equipment(code={self.code}, name={self.name}, status={self.status})>"
