"""
Day schedule and watering schedule API endpoints.
"""

from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.user import User
from app.core.services.auth import get_current_user
from app.database import get_db
from app.farm.schemas.schedule import (
    DayScheduleCreate,
    DayScheduleResponse,
)
from app.farm.services.schedule import ScheduleService

router = APIRouter()


def _schedule_to_response(schedule) -> dict:
    """Convert schedule model to response dict."""
    if not schedule:
        return None

    return {
        "id": schedule.id,
        "date": schedule.schedule_date,
        "notes": schedule.notes,
        "notes_tamil": schedule.notes_tamil,
        "created_by": schedule.created_by_id,
        "created_by_name": None,  # Could be populated if needed
        "is_published": schedule.is_published,
        "tasks": [
            {
                "id": t.id,
                "description": t.description,
                "description_tamil": t.description_tamil,
                "scheduled_time": t.scheduled_time,
                "category": t.category,
                "field_id": t.field_id,
                "field_name": t.field_name,
                "field_name_tamil": t.field_name_tamil,
                "crop_name": t.crop_name,
                "crop_name_tamil": t.crop_name_tamil,
                "assigned_worker_id": t.assigned_worker_id,
                "assigned_worker_name": t.assigned_worker_name,
                "assigned_worker_name_tamil": t.assigned_worker_name_tamil,
                "priority": t.priority,
                "status": t.status,
                "notes": t.notes,
                "notes_tamil": t.notes_tamil,
                "voice_note_url": t.voice_note_url,
                "completed_at": t.completed_at,
                "has_issues": t.has_issues,
                "issue_type": t.issue_type,
                "issue_description": t.issue_description,
                "issue_description_tamil": t.issue_description_tamil,
                "created_at": t.created_at,
                "updated_at": t.updated_at,
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
                    for u in (t.updates or [])
                ],
            }
            for t in (schedule.tasks or [])
        ],
        "created_at": schedule.created_at,
        "updated_at": schedule.updated_at,
    }


# ============== Day Schedule Endpoints ==============


@router.get("/by-date", response_model=Optional[DayScheduleResponse])
async def get_schedule_by_date(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    target_date: date = Query(..., description="Date to get schedule for"),
):
    """
    Get schedule for a specific date.

    Returns the day schedule with all tasks for the given date.
    """
    service = ScheduleService(db)
    schedule = await service.get_schedule_by_date(current_user.org_id, target_date)

    if not schedule:
        return None

    return _schedule_to_response(schedule)


@router.get("/today", response_model=Optional[DayScheduleResponse])
async def get_today_schedule(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get today's schedule.

    Returns the day schedule with all tasks for today.
    """
    service = ScheduleService(db)
    schedule = await service.get_today_schedule(current_user.org_id)

    if not schedule:
        return None

    return _schedule_to_response(schedule)


@router.get("/tomorrow", response_model=Optional[DayScheduleResponse])
async def get_tomorrow_schedule(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get tomorrow's schedule.

    Returns the day schedule with all tasks for tomorrow.
    """
    service = ScheduleService(db)
    schedule = await service.get_tomorrow_schedule(current_user.org_id)

    if not schedule:
        return None

    return _schedule_to_response(schedule)


@router.get("/range", response_model=list[DayScheduleResponse])
async def get_schedules_in_range(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
):
    """
    Get schedules within a date range.

    Returns all day schedules between start_date and end_date (inclusive).
    """
    service = ScheduleService(db)
    schedules = await service.get_schedules_in_range(
        current_user.org_id, start_date, end_date
    )
    return [_schedule_to_response(s) for s in schedules]


@router.post("", response_model=DayScheduleResponse)
async def create_schedule(
    data: DayScheduleCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Create a new day schedule.

    Supervisors use this to create schedules for specific dates.
    Includes multiple tasks that will be assigned to workers.
    """
    service = ScheduleService(db)
    schedule = await service.create_schedule(
        current_user.org_id, data, current_user
    )
    await db.commit()
    return _schedule_to_response(schedule)


# ============== Watering Schedule Endpoints (Trial Module) ==============


@router.get("/watering")
async def list_watering_schedules():
    """List all watering schedules."""
    return {"items": [], "total": 0}


@router.post("/watering")
async def create_watering_schedule():
    """Create a new watering schedule."""
    return {"message": "Not implemented"}


@router.put("/watering/{schedule_id}")
async def update_watering_schedule(schedule_id: str):
    """Update a watering schedule."""
    return {"message": "Not implemented"}


@router.delete("/watering/{schedule_id}")
async def delete_watering_schedule(schedule_id: str):
    """Delete a watering schedule."""
    return {"message": "Not implemented"}
