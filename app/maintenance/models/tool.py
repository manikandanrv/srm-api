"""
Tool tracking models for check-in/check-out management.
"""

import uuid
from datetime import date, datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models.base import BaseModel


class ToolStatus(str, Enum):
    """Tool status."""

    AVAILABLE = "available"
    CHECKED_OUT = "checked_out"
    DAMAGED = "damaged"
    CALIBRATION = "calibration"
    RETIRED = "retired"


class Tool(BaseModel):
    """
    Serialized tool tracking.

    High-value tools like drills, multimeters, wrenches are tracked individually.
    """

    __tablename__ = "tools"

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )

    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    name_tamil: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    category: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # 'plumbing', 'electrical', 'general'

    # Status and location
    status: Mapped[str] = mapped_column(
        String(50), default=ToolStatus.AVAILABLE.value, nullable=False
    )
    current_location_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id"), nullable=True
    )

    # Check-out tracking
    checked_out_to: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    checked_out_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Calibration tracking
    last_calibration_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    next_calibration_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Purchase info
    purchase_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    specifications: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<Tool(code={self.code}, name={self.name}, status={self.status})>"


class ToolTransaction(BaseModel):
    """
    Tool check-in/check-out log.
    """

    __tablename__ = "tool_transactions"

    tool_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tools.id"), nullable=False
    )

    transaction_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # 'check_out', 'check_in', 'damage_report'

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    from_location_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id"), nullable=True
    )
    to_location_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id"), nullable=True
    )

    job_card_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_cards.id"), nullable=True
    )

    condition_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<ToolTransaction(tool_id={self.tool_id}, type={self.transaction_type})>"
