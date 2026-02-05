"""
Farm task and watering schedule models.
"""

import uuid
from datetime import date, datetime, time
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models.base import BaseModel


class TaskType(str, Enum):
    """Types of farm tasks."""

    SOWING = "sowing"
    WATERING = "watering"
    FERTILIZING = "fertilizing"
    PEST_CONTROL = "pest_control"
    WEEDING = "weeding"
    HARVESTING = "harvesting"
    TRANSPORT = "transport"
    SOIL_PREPARATION = "soil_preparation"
    MAINTENANCE = "maintenance"


class TaskStatus(str, Enum):
    """Task execution status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    POSTPONED = "postponed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority levels."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class FarmTask(BaseModel):
    """
    Farm task model for managing daily operations.

    Supports task assignment, tracking, voice logs, and checklist completion.
    """

    __tablename__ = "farm_tasks"

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    field_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fields.id"), nullable=True
    )

    # Task details
    task_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    title_tamil: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description_tamil: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Scheduling
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False)
    scheduled_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Priority
    priority: Mapped[str] = mapped_column(
        String(20), default=TaskPriority.NORMAL.value, nullable=False
    )

    # Assignment
    assigned_to: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    assigned_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    assigned_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Checklist
    checklist_template_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    # Execution tracking
    status: Mapped[str] = mapped_column(
        String(50), default=TaskStatus.PENDING.value, nullable=False
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Postponement
    postpone_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    postponed_to: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Feedback
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    feedback_tamil: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-5

    # Voice logs (references audio_logs table)
    has_voice_notes: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    def __repr__(self) -> str:
        return f"<FarmTask(id={self.id}, type={self.task_type}, status={self.status})>"


class WateringSchedule(BaseModel):
    """
    Watering schedule for automated task generation.

    This is the trial module mentioned in requirements.
    """

    __tablename__ = "watering_schedules"

    field_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fields.id"), nullable=False
    )

    # Schedule
    frequency_days: Mapped[int] = mapped_column(Integer, nullable=False)
    preferred_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)

    # Tracking
    last_watered_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    next_watering_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Method details
    irrigation_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Fertilizer mixing
    includes_fertilizer: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fertilizer_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    fertilizer_quantity: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Assignment
    default_assignee: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<WateringSchedule(field_id={self.field_id}, frequency={self.frequency_days}d)>"
