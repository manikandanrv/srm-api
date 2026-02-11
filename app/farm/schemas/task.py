"""
Farm task Pydantic schemas for request/response validation.
"""

from datetime import date, datetime, time
from typing import Optional
from uuid import UUID

from pydantic import Field

from app.core.schemas.common import BaseSchema


# ============== Task Response Schemas ==============


class FarmTaskResponse(BaseSchema):
    """Response schema for farm tasks."""

    id: UUID
    org_id: UUID
    field_id: Optional[UUID] = None
    
    # Task details
    task_type: str
    title: str
    title_tamil: Optional[str] = None
    description: Optional[str] = None
    description_tamil: Optional[str] = None
    
    # Scheduling
    scheduled_date: date
    scheduled_time: Optional[time] = None
    due_date: Optional[date] = None
    
    # Priority
    priority: str
    
    # Assignment
    assigned_to: Optional[UUID] = None
    assigned_by: Optional[UUID] = None
    assigned_at: Optional[datetime] = None
    
    # Checklist
    checklist_template_id: Optional[UUID] = None
    
    # Execution tracking
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Postponement
    postpone_reason: Optional[str] = None
    postponed_to: Optional[date] = None
    
    # Feedback
    feedback: Optional[str] = None
    feedback_tamil: Optional[str] = None
    rating: Optional[int] = None
    
    # Voice logs
    has_voice_notes: bool = False
    
    # Timestamps
    created_at: datetime
    updated_at: datetime


class FarmTaskListResponse(BaseSchema):
    """Paginated response schema for farm tasks list."""

    items: list[FarmTaskResponse]
    total: int


# ============== Task Create/Update Schemas ==============


class FarmTaskCreate(BaseSchema):
    """Schema for creating a farm task."""

    field_id: Optional[UUID] = None
    task_type: str = Field(..., description="Type of farm task")
    title: str = Field(..., min_length=1, max_length=200)
    title_tamil: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    description_tamil: Optional[str] = None
    scheduled_date: date
    scheduled_time: Optional[time] = None
    due_date: Optional[date] = None
    priority: str = "normal"
    assigned_to: Optional[UUID] = None
    checklist_template_id: Optional[UUID] = None


class FarmTaskUpdate(BaseSchema):
    """Schema for updating a farm task."""

    field_id: Optional[UUID] = None
    task_type: Optional[str] = None
    title: Optional[str] = Field(None, max_length=200)
    title_tamil: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    description_tamil: Optional[str] = None
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[time] = None
    due_date: Optional[date] = None
    priority: Optional[str] = None
    assigned_to: Optional[UUID] = None
    checklist_template_id: Optional[UUID] = None


# ============== Task Action Schemas ==============


class TaskStartRequest(BaseSchema):
    """Schema for starting a task."""

    notes: Optional[str] = None


class TaskCompleteRequest(BaseSchema):
    """Schema for completing a task."""

    feedback: Optional[str] = None
    feedback_tamil: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)


class TaskPostponeRequest(BaseSchema):
    """Schema for postponing a task."""

    postponed_to: date
    postpone_reason: Optional[str] = None
