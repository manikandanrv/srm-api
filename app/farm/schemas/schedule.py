"""
Schedule-related Pydantic schemas for request/response validation.
"""

from datetime import date, datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import Field

from app.core.schemas.common import BaseSchema


class TaskCategory(str, Enum):
    """Categories of farm tasks."""

    WATERING = "watering"
    FERTILIZING = "fertilizing"
    PEST_CONTROL = "pest_control"
    WEEDING = "weeding"
    HARVESTING = "harvesting"
    MAINTENANCE = "maintenance"
    TRANSPORT = "transport"
    OTHER = "other"


class TaskStatus(str, Enum):
    """Task execution status."""

    SCHEDULED = "scheduled"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    HAS_ISSUES = "has_issues"
    OVERDUE = "overdue"


class TaskPriority(str, Enum):
    """Task priority levels."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class IssueType(str, Enum):
    """Types of issues that can be reported."""

    EQUIPMENT_FAILURE = "equipment_failure"
    WEATHER = "weather"
    RESOURCE_SHORTAGE = "resource_shortage"
    SAFETY_CONCERN = "safety_concern"
    OTHER = "other"


# ============== Task Update Schemas ==============


class TaskUpdateResponse(BaseSchema):
    """Response schema for task update records."""

    id: UUID
    task_id: UUID
    worker_id: UUID
    worker_name: str
    status: str
    timestamp: datetime
    notes: Optional[str] = None
    notes_tamil: Optional[str] = None
    voice_note_url: Optional[str] = None
    issue_type: Optional[str] = None
    issue_description: Optional[str] = None
    issue_description_tamil: Optional[str] = None


# ============== Scheduled Task Schemas ==============


class ScheduledTaskBase(BaseSchema):
    """Base schema for scheduled tasks."""

    description_tamil: str = Field(..., min_length=1, max_length=1000)
    description: Optional[str] = Field(None, max_length=1000)
    category: str = Field(default=TaskCategory.OTHER.value)
    priority: str = Field(default=TaskPriority.NORMAL.value)
    notes_tamil: Optional[str] = None
    notes: Optional[str] = None


class ScheduledTaskCreate(ScheduledTaskBase):
    """Schema for creating a scheduled task."""

    scheduled_time: datetime
    field_id: Optional[UUID] = None
    assigned_worker_id: Optional[UUID] = None


class ScheduledTaskUpdate(BaseSchema):
    """Schema for updating a scheduled task."""

    description_tamil: Optional[str] = Field(None, max_length=1000)
    description: Optional[str] = Field(None, max_length=1000)
    scheduled_time: Optional[datetime] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    field_id: Optional[UUID] = None
    assigned_worker_id: Optional[UUID] = None
    notes_tamil: Optional[str] = None
    notes: Optional[str] = None


class ScheduledTaskResponse(BaseSchema):
    """Response schema for scheduled tasks."""

    id: UUID
    description: Optional[str] = None
    description_tamil: str
    scheduled_time: datetime
    category: str
    field_id: Optional[UUID] = None
    field_name: Optional[str] = None
    field_name_tamil: Optional[str] = None
    crop_name: Optional[str] = None
    crop_name_tamil: Optional[str] = None
    assigned_worker_id: Optional[UUID] = None
    assigned_worker_name: Optional[str] = None
    assigned_worker_name_tamil: Optional[str] = None
    priority: str
    status: str
    notes: Optional[str] = None
    notes_tamil: Optional[str] = None
    voice_note_url: Optional[str] = None
    completed_at: Optional[datetime] = None
    has_issues: bool = False
    issue_type: Optional[str] = None
    issue_description: Optional[str] = None
    issue_description_tamil: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    updates: list[TaskUpdateResponse] = []


# ============== Day Schedule Schemas ==============


class DayScheduleCreate(BaseSchema):
    """Schema for creating a day schedule."""

    date: date
    tasks: list[ScheduledTaskCreate]
    notes: Optional[str] = None
    notes_tamil: Optional[str] = None


class DayScheduleResponse(BaseSchema):
    """Response schema for day schedules."""

    id: UUID
    date: date
    notes: Optional[str] = None
    notes_tamil: Optional[str] = None
    created_by: Optional[UUID] = None
    created_by_name: Optional[str] = None
    is_published: bool = True
    tasks: list[ScheduledTaskResponse] = []
    created_at: datetime
    updated_at: datetime


# ============== Task Action Schemas ==============


class TaskStatusUpdateRequest(BaseSchema):
    """Schema for updating task status."""

    status: str = Field(..., description="New status for the task")
    notes: Optional[str] = None
    notes_tamil: Optional[str] = None
    voice_note_url: Optional[str] = None


class TaskCompleteRequest(BaseSchema):
    """Schema for completing a task."""

    notes: Optional[str] = None
    notes_tamil: Optional[str] = None
    voice_note_url: Optional[str] = None


class TaskIssueRequest(BaseSchema):
    """Schema for reporting an issue with a task."""

    issue_type: str = Field(..., description="Type of issue")
    description: Optional[str] = None
    description_tamil: Optional[str] = None
    voice_note_url: Optional[str] = None


# ============== Worker/Field Schemas ==============


class WorkerResponse(BaseSchema):
    """Response schema for farm workers."""

    id: UUID
    employee_code: str
    name: str
    name_tamil: Optional[str] = None
    phone: Optional[str] = None
    role: str


class FieldResponse(BaseSchema):
    """Response schema for farm fields."""

    id: UUID
    code: str
    name: str
    name_tamil: Optional[str] = None
    area_in_acres: Optional[float] = None
    current_crop: Optional[str] = None
    current_crop_tamil: Optional[str] = None


# ============== Query Schemas ==============


class DateRangeQuery(BaseSchema):
    """Query parameters for date range."""

    start_date: date
    end_date: date


class ScheduleListResponse(BaseSchema):
    """Response schema for list of schedules."""

    items: list[DayScheduleResponse]
    total: int
