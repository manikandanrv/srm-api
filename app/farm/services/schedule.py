"""
Schedule service for farm task scheduling operations.
"""

from datetime import date, datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.models.user import Department, User
from app.farm.models.field import Field
from app.farm.models.schedule import DaySchedule, ScheduledTask, TaskUpdate
from app.farm.schemas.schedule import (
    DayScheduleCreate,
    ScheduledTaskCreate,
    ScheduledTaskUpdate,
    TaskCompleteRequest,
    TaskIssueRequest,
    TaskStatusUpdateRequest,
)


class ScheduleService:
    """Service for schedule and task operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============== Day Schedule Operations ==============

    async def get_schedule_by_date(
        self, org_id: UUID, schedule_date: date
    ) -> Optional[DaySchedule]:
        """Get schedule for a specific date."""
        result = await self.db.execute(
            select(DaySchedule)
            .options(selectinload(DaySchedule.tasks).selectinload(ScheduledTask.updates))
            .where(
                and_(
                    DaySchedule.org_id == org_id,
                    DaySchedule.schedule_date == schedule_date,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_today_schedule(self, org_id: UUID) -> Optional[DaySchedule]:
        """Get today's schedule."""
        today = date.today()
        return await self.get_schedule_by_date(org_id, today)

    async def get_tomorrow_schedule(self, org_id: UUID) -> Optional[DaySchedule]:
        """Get tomorrow's schedule."""
        tomorrow = date.today() + timedelta(days=1)
        return await self.get_schedule_by_date(org_id, tomorrow)

    async def get_schedules_in_range(
        self, org_id: UUID, start_date: date, end_date: date
    ) -> list[DaySchedule]:
        """Get schedules within a date range."""
        result = await self.db.execute(
            select(DaySchedule)
            .options(selectinload(DaySchedule.tasks).selectinload(ScheduledTask.updates))
            .where(
                and_(
                    DaySchedule.org_id == org_id,
                    DaySchedule.schedule_date >= start_date,
                    DaySchedule.schedule_date <= end_date,
                )
            )
            .order_by(DaySchedule.schedule_date)
        )
        return list(result.scalars().all())

    async def create_schedule(
        self,
        org_id: UUID,
        data: DayScheduleCreate,
        created_by: User,
    ) -> DaySchedule:
        """Create a new day schedule with tasks."""
        # Check if schedule already exists for this date
        existing = await self.get_schedule_by_date(org_id, data.date)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Schedule already exists for {data.date}",
            )

        # Create the day schedule
        schedule = DaySchedule(
            org_id=org_id,
            schedule_date=data.date,
            notes=data.notes,
            notes_tamil=data.notes_tamil,
            created_by_id=created_by.id,
        )
        self.db.add(schedule)
        await self.db.flush()

        # Create tasks for this schedule
        for task_data in data.tasks:
            task = await self._create_task(
                org_id=org_id,
                schedule_id=schedule.id,
                data=task_data,
            )
            self.db.add(task)

        await self.db.flush()
        await self.db.refresh(schedule)

        # Re-fetch with relationships
        return await self.get_schedule_by_date(org_id, data.date)

    # ============== Task Operations ==============

    async def get_task_by_id(self, task_id: UUID) -> Optional[ScheduledTask]:
        """Get a task by ID."""
        result = await self.db.execute(
            select(ScheduledTask)
            .options(selectinload(ScheduledTask.updates))
            .where(ScheduledTask.id == task_id)
        )
        return result.scalar_one_or_none()

    async def get_tasks_for_date(
        self, org_id: UUID, target_date: date
    ) -> list[ScheduledTask]:
        """Get all tasks for a specific date."""
        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = datetime.combine(target_date, datetime.max.time())

        result = await self.db.execute(
            select(ScheduledTask)
            .options(selectinload(ScheduledTask.updates))
            .where(
                and_(
                    ScheduledTask.org_id == org_id,
                    ScheduledTask.scheduled_time >= start_of_day,
                    ScheduledTask.scheduled_time <= end_of_day,
                )
            )
            .order_by(ScheduledTask.scheduled_time)
        )
        return list(result.scalars().all())

    async def get_tasks_for_worker(
        self, org_id: UUID, worker_id: UUID, target_date: date
    ) -> list[ScheduledTask]:
        """Get tasks assigned to a specific worker for a date."""
        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = datetime.combine(target_date, datetime.max.time())

        result = await self.db.execute(
            select(ScheduledTask)
            .options(selectinload(ScheduledTask.updates))
            .where(
                and_(
                    ScheduledTask.org_id == org_id,
                    ScheduledTask.assigned_worker_id == worker_id,
                    ScheduledTask.scheduled_time >= start_of_day,
                    ScheduledTask.scheduled_time <= end_of_day,
                )
            )
            .order_by(ScheduledTask.scheduled_time)
        )
        return list(result.scalars().all())

    async def get_my_today_tasks(
        self, org_id: UUID, user_id: UUID
    ) -> list[ScheduledTask]:
        """Get current user's tasks for today."""
        return await self.get_tasks_for_worker(org_id, user_id, date.today())

    async def create_task(
        self, org_id: UUID, data: ScheduledTaskCreate
    ) -> ScheduledTask:
        """Create a standalone scheduled task."""
        task = await self._create_task(org_id=org_id, schedule_id=None, data=data)
        self.db.add(task)
        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def _create_task(
        self,
        org_id: UUID,
        schedule_id: Optional[UUID],
        data: ScheduledTaskCreate,
    ) -> ScheduledTask:
        """Internal method to create a task."""
        # Get field info if field_id provided
        field_name = None
        field_name_tamil = None
        crop_name = None
        crop_name_tamil = None

        if data.field_id:
            field = await self._get_field(data.field_id)
            if field:
                field_name = field.name
                field_name_tamil = field.name_tamil
                # TODO: Get crop info from field's current cultivation

        # Get worker info if assigned
        worker_name = None
        worker_name_tamil = None

        if data.assigned_worker_id:
            worker = await self._get_user(data.assigned_worker_id)
            if worker:
                worker_name = worker.name
                worker_name_tamil = worker.name_tamil

        return ScheduledTask(
            org_id=org_id,
            schedule_id=schedule_id,
            description=data.description,
            description_tamil=data.description_tamil,
            scheduled_time=data.scheduled_time,
            category=data.category,
            field_id=data.field_id,
            field_name=field_name,
            field_name_tamil=field_name_tamil,
            crop_name=crop_name,
            crop_name_tamil=crop_name_tamil,
            assigned_worker_id=data.assigned_worker_id,
            assigned_worker_name=worker_name,
            assigned_worker_name_tamil=worker_name_tamil,
            priority=data.priority,
            notes=data.notes,
            notes_tamil=data.notes_tamil,
            status="scheduled",
        )

    async def update_task(
        self, task_id: UUID, data: ScheduledTaskUpdate
    ) -> ScheduledTask:
        """Update a scheduled task."""
        task = await self.get_task_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        update_data = data.model_dump(exclude_unset=True)

        # Handle field update
        if "field_id" in update_data and update_data["field_id"]:
            field = await self._get_field(update_data["field_id"])
            if field:
                update_data["field_name"] = field.name
                update_data["field_name_tamil"] = field.name_tamil

        # Handle worker update
        if "assigned_worker_id" in update_data and update_data["assigned_worker_id"]:
            worker = await self._get_user(update_data["assigned_worker_id"])
            if worker:
                update_data["assigned_worker_name"] = worker.name
                update_data["assigned_worker_name_tamil"] = worker.name_tamil

        for field, value in update_data.items():
            setattr(task, field, value)

        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def update_task_status(
        self,
        task_id: UUID,
        data: TaskStatusUpdateRequest,
        user: User,
    ) -> ScheduledTask:
        """Update task status with notes."""
        task = await self.get_task_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Update task status
        task.status = data.status
        if data.notes:
            task.notes = data.notes
        if data.notes_tamil:
            task.notes_tamil = data.notes_tamil
        if data.voice_note_url:
            task.voice_note_url = data.voice_note_url

        # Create update record
        update = TaskUpdate(
            task_id=task_id,
            worker_id=user.id,
            worker_name=user.name_tamil or user.name,
            status=data.status,
            timestamp=datetime.utcnow(),
            notes=data.notes,
            notes_tamil=data.notes_tamil,
            voice_note_url=data.voice_note_url,
        )
        self.db.add(update)

        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def complete_task(
        self,
        task_id: UUID,
        data: TaskCompleteRequest,
        user: User,
    ) -> ScheduledTask:
        """Mark a task as completed."""
        task = await self.get_task_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        task.status = "completed"
        task.completed_at = datetime.utcnow()
        if data.notes:
            task.notes = data.notes
        if data.notes_tamil:
            task.notes_tamil = data.notes_tamil
        if data.voice_note_url:
            task.voice_note_url = data.voice_note_url

        # Create update record
        update = TaskUpdate(
            task_id=task_id,
            worker_id=user.id,
            worker_name=user.name_tamil or user.name,
            status="completed",
            timestamp=datetime.utcnow(),
            notes=data.notes,
            notes_tamil=data.notes_tamil,
            voice_note_url=data.voice_note_url,
        )
        self.db.add(update)

        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def report_task_issue(
        self,
        task_id: UUID,
        data: TaskIssueRequest,
        user: User,
    ) -> ScheduledTask:
        """Report an issue with a task."""
        task = await self.get_task_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        task.status = "has_issues"
        task.has_issues = True
        task.issue_type = data.issue_type
        task.issue_description = data.description
        task.issue_description_tamil = data.description_tamil
        if data.voice_note_url:
            task.voice_note_url = data.voice_note_url

        # Create update record
        update = TaskUpdate(
            task_id=task_id,
            worker_id=user.id,
            worker_name=user.name_tamil or user.name,
            status="has_issues",
            timestamp=datetime.utcnow(),
            issue_type=data.issue_type,
            issue_description=data.description,
            issue_description_tamil=data.description_tamil,
            voice_note_url=data.voice_note_url,
        )
        self.db.add(update)

        await self.db.flush()
        await self.db.refresh(task)
        return task

    # ============== Workers and Fields ==============

    async def get_workers(self, org_id: UUID) -> list[User]:
        """Get all farm workers in the organization."""
        result = await self.db.execute(
            select(User)
            .where(
                and_(
                    User.org_id == org_id,
                    User.department == Department.FARM.value,
                    User.is_active == True,
                )
            )
            .order_by(User.name)
        )
        return list(result.scalars().all())

    async def get_fields(self, org_id: UUID) -> list[Field]:
        """Get all active fields in the organization's location."""
        # Note: This assumes fields are linked via location_id
        # You may need to adjust based on your data model
        result = await self.db.execute(
            select(Field)
            .where(Field.is_active == True)
            .order_by(Field.name)
        )
        return list(result.scalars().all())

    # ============== Helper Methods ==============

    async def _get_field(self, field_id: UUID) -> Optional[Field]:
        """Get field by ID."""
        result = await self.db.execute(
            select(Field).where(Field.id == field_id)
        )
        return result.scalar_one_or_none()

    async def _get_user(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
