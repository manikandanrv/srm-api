"""
Scheduled task management API endpoints.
"""

from datetime import date
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.user import User
from app.core.services.auth import get_current_user
from app.database import get_db
from app.farm.schemas.schedule import (
    ScheduledTaskCreate,
    ScheduledTaskResponse,
    ScheduledTaskUpdate,
    TaskCompleteRequest,
    TaskIssueRequest,
    TaskStatusUpdateRequest,
)
from app.farm.services.schedule import ScheduleService

router = APIRouter()


def _task_to_response(task) -> dict:
    """Convert task model to response dict."""
    return {
        "id": task.id,
        "description": task.description,
        "description_tamil": task.description_tamil,
        "scheduled_time": task.scheduled_time,
        "category": task.category,
        "field_id": task.field_id,
        "field_name": task.field_name,
        "field_name_tamil": task.field_name_tamil,
        "crop_name": task.crop_name,
        "crop_name_tamil": task.crop_name_tamil,
        "assigned_worker_id": task.assigned_worker_id,
        "assigned_worker_name": task.assigned_worker_name,
        "assigned_worker_name_tamil": task.assigned_worker_name_tamil,
        "priority": task.priority,
        "status": task.status,
        "notes": task.notes,
        "notes_tamil": task.notes_tamil,
        "voice_note_url": task.voice_note_url,
        "completed_at": task.completed_at,
        "has_issues": task.has_issues,
        "issue_type": task.issue_type,
        "issue_description": task.issue_description,
        "issue_description_tamil": task.issue_description_tamil,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "updates": [
            {
                "id": u.id,
                "task_id": u.task_id,
                "worker_id": u.worker_id,
                "worker_name": u.worker_name,
                "status": u.status,
                "timestamp": u.timestamp,
                "notes": u.notes,
                "notes_tamil": u.notes_tamil,
                "voice_note_url": u.voice_note_url,
                "issue_type": u.issue_type,
                "issue_description": u.issue_description,
                "issue_description_tamil": u.issue_description_tamil,
            }
            for u in (task.updates or [])
        ],
    }


@router.get("", response_model=list[ScheduledTaskResponse])
async def list_scheduled_tasks(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    target_date: Optional[date] = Query(None, description="Filter by date"),
    worker_id: Optional[UUID] = Query(None, description="Filter by worker"),
):
    """
    List scheduled tasks with optional filtering.

    - **target_date**: Filter tasks for a specific date
    - **worker_id**: Filter tasks assigned to a specific worker
    """
    service = ScheduleService(db)

    if target_date:
        if worker_id:
            tasks = await service.get_tasks_for_worker(
                current_user.org_id, worker_id, target_date
            )
        else:
            tasks = await service.get_tasks_for_date(current_user.org_id, target_date)
    else:
        # Default to today
        tasks = await service.get_tasks_for_date(current_user.org_id, date.today())

    return [_task_to_response(t) for t in tasks]


@router.get("/my", response_model=list[ScheduledTaskResponse])
async def get_my_today_tasks(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get current user's tasks for today.

    Returns all tasks assigned to the authenticated user for today.
    """
    service = ScheduleService(db)
    tasks = await service.get_my_today_tasks(current_user.org_id, current_user.id)
    return [_task_to_response(t) for t in tasks]


@router.get("/today", response_model=list[ScheduledTaskResponse])
async def get_today_tasks(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get all tasks for today.

    Returns all scheduled tasks for today in the organization.
    """
    service = ScheduleService(db)
    tasks = await service.get_tasks_for_date(current_user.org_id, date.today())
    return [_task_to_response(t) for t in tasks]


@router.get("/{task_id}", response_model=ScheduledTaskResponse)
async def get_scheduled_task(
    task_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a specific scheduled task by ID."""
    service = ScheduleService(db)
    task = await service.get_task_by_id(task_id)

    if not task:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Task not found")

    return _task_to_response(task)


@router.post("", response_model=ScheduledTaskResponse)
async def create_scheduled_task(
    data: ScheduledTaskCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Create a new scheduled task.

    Creates a standalone scheduled task (not part of a day schedule).
    """
    service = ScheduleService(db)
    task = await service.create_task(current_user.org_id, data)
    await db.commit()
    return _task_to_response(task)


@router.put("/{task_id}", response_model=ScheduledTaskResponse)
async def update_scheduled_task(
    task_id: UUID,
    data: ScheduledTaskUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update a scheduled task."""
    service = ScheduleService(db)
    task = await service.update_task(task_id, data)
    await db.commit()
    return _task_to_response(task)


@router.patch("/{task_id}/update", response_model=ScheduledTaskResponse)
async def update_task_status(
    task_id: UUID,
    data: TaskStatusUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Update task status.

    Workers use this to update the status of their assigned tasks.
    """
    service = ScheduleService(db)
    task = await service.update_task_status(task_id, data, current_user)
    await db.commit()
    return _task_to_response(task)


@router.patch("/{task_id}/complete", response_model=ScheduledTaskResponse)
async def complete_task(
    task_id: UUID,
    data: TaskCompleteRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Mark a task as completed.

    Workers use this to mark their tasks as done.
    """
    service = ScheduleService(db)
    task = await service.complete_task(task_id, data, current_user)
    await db.commit()
    return _task_to_response(task)


@router.post("/{task_id}/issue", response_model=ScheduledTaskResponse)
async def report_task_issue(
    task_id: UUID,
    data: TaskIssueRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Report an issue with a task.

    Workers use this to report problems preventing task completion.
    Issue types: equipment_failure, weather, resource_shortage, safety_concern, other
    """
    service = ScheduleService(db)
    task = await service.report_task_issue(task_id, data, current_user)
    await db.commit()
    return _task_to_response(task)
