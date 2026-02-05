"""
Job card (work order) model for maintenance management.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models.base import BaseModel


class JobType(str, Enum):
    """Types of maintenance jobs."""

    CORRECTIVE = "corrective"  # Fix a reported issue
    PREVENTIVE = "preventive"  # Scheduled maintenance
    EMERGENCY = "emergency"  # Urgent repair
    INSPECTION = "inspection"  # Routine inspection


class JobStatus(str, Enum):
    """Job card status."""

    OPEN = "open"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class JobPriority(str, Enum):
    """Job priority levels."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class JobCard(BaseModel):
    """
    Job card / work order model.

    Central record for maintenance activities including:
    - Issue reporting (voice-enabled)
    - Technician assignment
    - Work execution tracking
    - Parts consumption
    - Time tracking (MTTR calculation)
    """

    __tablename__ = "job_cards"

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )

    # Auto-generated job number (JC-2024-0001)
    job_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # Asset and location
    asset_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assets.id"), nullable=True
    )
    location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id"), nullable=False
    )

    # Job details
    job_type: Mapped[str] = mapped_column(String(50), nullable=False)
    priority: Mapped[str] = mapped_column(
        String(20), default=JobPriority.NORMAL.value, nullable=False
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    title_tamil: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description_tamil: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Reporting
    reported_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    reported_via: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # 'app', 'phone', 'walk_in'
    audio_request_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )  # Voice request audio

    # Assignment
    assigned_to: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    assigned_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Status tracking
    status: Mapped[str] = mapped_column(
        String(50), default=JobStatus.OPEN.value, nullable=False
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Resolution
    resolution: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolution_tamil: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolution_audio_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )  # Voice resolution audio
    root_cause: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Metrics
    mttr_minutes: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )  # Mean Time To Repair

    # Cost tracking
    labor_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    parts_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    total_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)

    def __repr__(self) -> str:
        return f"<JobCard(job_number={self.job_number}, status={self.status})>"


class JobCardMaterial(BaseModel):
    """
    Materials/parts consumed in job execution.

    Links job cards to inventory items for tracking consumption.
    """

    __tablename__ = "job_card_materials"

    job_card_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_cards.id"), nullable=False
    )
    inventory_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("inventory_items.id"), nullable=False
    )

    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    unit_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)

    # Who issued the material
    issued_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    notes: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    def __repr__(self) -> str:
        return f"<JobCardMaterial(job_card_id={self.job_card_id}, qty={self.quantity})>"
