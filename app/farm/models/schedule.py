"""
Daily schedule and task update models for farm operations.
"""

import uuid
from datetime import date, datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models.base import BaseModel


class IssueType(str, Enum):
    """Types of issues that can be reported for tasks."""

    EQUIPMENT_FAILURE = "equipment_failure"
    WEATHER = "weather"
    RESOURCE_SHORTAGE = "resource_shortage"
    SAFETY_CONCERN = "safety_concern"
    OTHER = "other"


class DaySchedule(BaseModel):
    """
    Daily schedule model for grouping tasks.

    Represents a supervisor-created schedule for a specific date
    containing multiple scheduled tasks.
    """

    __tablename__ = "day_schedules"

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )

    # Schedule date
    schedule_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes_tamil: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Created by (supervisor)
    created_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # Status
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    tasks: Mapped[list["ScheduledTask"]] = relationship(
        "ScheduledTask", back_populates="schedule", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<DaySchedule(date={self.schedule_date}, tasks={len(self.tasks) if self.tasks else 0})>"


class ScheduledTask(BaseModel):
    """
    Individual scheduled task within a day schedule.

    Represents a task assigned to a worker for a specific time.
    """

    __tablename__ = "scheduled_tasks"

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )

    # Link to day schedule
    schedule_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("day_schedules.id"), nullable=True
    )

    # Task details
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description_tamil: Mapped[str] = mapped_column(Text, nullable=False)

    # Scheduling
    scheduled_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    # Category/Type
    category: Mapped[str] = mapped_column(String(50), nullable=False)

    # Field assignment
    field_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fields.id"), nullable=True
    )
    field_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    field_name_tamil: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Crop info
    crop_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    crop_name_tamil: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Worker assignment
    assigned_worker_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    assigned_worker_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    assigned_worker_name_tamil: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Priority
    priority: Mapped[str] = mapped_column(String(20), default="normal", nullable=False)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="scheduled", nullable=False)

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes_tamil: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Voice note
    voice_note_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Completion tracking
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Issue tracking
    has_issues: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    issue_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    issue_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    issue_description_tamil: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    schedule: Mapped[Optional["DaySchedule"]] = relationship(
        "DaySchedule", back_populates="tasks"
    )
    updates: Mapped[list["TaskUpdate"]] = relationship(
        "TaskUpdate", back_populates="task", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<ScheduledTask(id={self.id}, category={self.category}, status={self.status})>"


class TaskUpdate(BaseModel):
    """
    Task update/response log from workers.

    Tracks status changes, notes, and voice recordings for task updates.
    """

    __tablename__ = "task_updates"

    # Link to task
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scheduled_tasks.id"), nullable=False
    )

    # Worker info
    worker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    worker_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Update details
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes_tamil: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Voice note
    voice_note_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Issue reporting
    issue_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    issue_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    issue_description_tamil: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    task: Mapped["ScheduledTask"] = relationship(
        "ScheduledTask", back_populates="updates"
    )

    def __repr__(self) -> str:
        return f"<TaskUpdate(task_id={self.task_id}, status={self.status})>"
