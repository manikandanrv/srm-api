"""
Farm task service layer for business logic.
"""

from datetime import date
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.farm.models.task import FarmTask, TaskStatus
from app.farm.schemas.task import FarmTaskCreate, FarmTaskUpdate


class TaskService:
    """Service for managing farm tasks."""

    def __init__(self, db: AsyncSession):
        """Initialize the task service.

        Args:
            db: Database session
        """
        self.db = db

    async def get_my_tasks(
        self,
        org_id: UUID,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[str] = None,
        include_completed: bool = False,
    ) -> tuple[list[FarmTask], int]:
        """Get tasks assigned to a specific user.

        Args:
            org_id: Organization ID
            user_id: User ID to get tasks for
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            status_filter: Optional status to filter by
            include_completed: Whether to include completed/cancelled tasks

        Returns:
            Tuple of (list of tasks, total count)
        """
        # Build base query
        conditions = [
            FarmTask.org_id == org_id,
            FarmTask.assigned_to == user_id,
        ]

        # Filter by status if provided
        if status_filter:
            conditions.append(FarmTask.status == status_filter)
        elif not include_completed:
            # By default, exclude completed and cancelled tasks
            conditions.append(
                FarmTask.status.notin_([TaskStatus.COMPLETED.value, TaskStatus.CANCELLED.value])
            )

        # Count query
        count_query = select(FarmTask).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = len(count_result.scalars().all())

        # Data query with pagination and ordering
        query = (
            select(FarmTask)
            .where(and_(*conditions))
            .order_by(
                # Order by: urgent/high priority first, then by scheduled date
                FarmTask.priority.desc(),
                FarmTask.scheduled_date.asc(),
            )
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(query)
        tasks = result.scalars().all()

        return list(tasks), total

    async def get_task_by_id(self, task_id: UUID) -> Optional[FarmTask]:
        """Get a specific task by ID.

        Args:
            task_id: Task ID

        Returns:
            Task if found, None otherwise
        """
        query = select(FarmTask).where(FarmTask.id == task_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_task(
        self, org_id: UUID, created_by: UUID, data: FarmTaskCreate
    ) -> FarmTask:
        """Create a new farm task.

        Args:
            org_id: Organization ID
            created_by: User creating the task
            data: Task creation data

        Returns:
            Created task
        """
        task = FarmTask(
            org_id=org_id,
            field_id=data.field_id,
            task_type=data.task_type,
            title=data.title,
            title_tamil=data.title_tamil,
            description=data.description,
            description_tamil=data.description_tamil,
            scheduled_date=data.scheduled_date,
            scheduled_time=data.scheduled_time,
            due_date=data.due_date,
            priority=data.priority,
            assigned_to=data.assigned_to,
            assigned_by=created_by if data.assigned_to else None,
            checklist_template_id=data.checklist_template_id,
            status=TaskStatus.PENDING.value,
        )
        self.db.add(task)
        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def update_task(self, task_id: UUID, data: FarmTaskUpdate) -> Optional[FarmTask]:
        """Update a farm task.

        Args:
            task_id: Task ID to update
            data: Update data

        Returns:
            Updated task if found, None otherwise
        """
        task = await self.get_task_by_id(task_id)
        if not task:
            return None

        # Update fields if provided
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def start_task(self, task_id: UUID) -> Optional[FarmTask]:
        """Mark a task as started.

        Args:
            task_id: Task ID

        Returns:
            Updated task if found, None otherwise
        """
        task = await self.get_task_by_id(task_id)
        if not task:
            return None

        from app.core.utils.timezone import get_utc_now

        task.status = TaskStatus.IN_PROGRESS.value
        task.started_at = get_utc_now()  # Store in UTC, displayed as IST in frontend

        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def complete_task(
        self, task_id: UUID, feedback: Optional[str] = None, rating: Optional[int] = None
    ) -> Optional[FarmTask]:
        """Mark a task as completed.

        Args:
            task_id: Task ID
            feedback: Optional feedback
            rating: Optional rating (1-5)

        Returns:
            Updated task if found, None otherwise
        """
        task = await self.get_task_by_id(task_id)
        if not task:
            return None

        from app.core.utils.timezone import get_utc_now

        task.status = TaskStatus.COMPLETED.value
        task.completed_at = get_utc_now()  # Store in UTC, displayed as IST in frontend
        if feedback:
            task.feedback = feedback
        if rating:
            task.rating = rating

        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def postpone_task(
        self, task_id: UUID, postponed_to: date, reason: Optional[str] = None
    ) -> Optional[FarmTask]:
        """Postpone a task to a future date.

        Args:
            task_id: Task ID
            postponed_to: New date to postpone to
            reason: Optional reason for postponement

        Returns:
            Updated task if found, None otherwise
        """
        task = await self.get_task_by_id(task_id)
        if not task:
            return None

        task.status = TaskStatus.POSTPONED.value
        task.postponed_to = postponed_to
        task.postpone_reason = reason

        await self.db.flush()
        await self.db.refresh(task)
        return task
