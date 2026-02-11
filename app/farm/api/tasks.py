"""
Farm task management API endpoints.
"""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.user import User
from app.core.services.auth import get_current_user
from app.database import get_db
from app.farm.schemas.task import (
    FarmTaskCreate,
    FarmTaskListResponse,
    FarmTaskResponse,
    FarmTaskUpdate,
    TaskCompleteRequest,
    TaskPostponeRequest,
    TaskStartRequest,
)
from app.farm.services.task import TaskService

router = APIRouter()


@router.get("/my", response_model=FarmTaskListResponse)
async def get_my_tasks(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of records to return"),
    status: Optional[str] = Query(None, description="Filter by status"),
    include_completed: bool = Query(False, description="Include completed/cancelled tasks"),
):
    """
    Get tasks assigned to current user.
    
    Returns a paginated list of farm tasks assigned to the authenticated user.
    By default, excludes completed and cancelled tasks.
    
    - **skip**: Pagination offset (default: 0)
    - **limit**: Page size (default: 100, max: 200)
    - **status**: Optional status filter (pending, in_progress, completed, etc.)
    - **include_completed**: Include completed/cancelled tasks (default: false)
    """
    service = TaskService(db)
    tasks, total = await service.get_my_tasks(
        org_id=current_user.org_id,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status_filter=status,
        include_completed=include_completed,
    )
    
    return FarmTaskListResponse(
        items=[FarmTaskResponse.model_validate(task) for task in tasks],
        total=total,
    )


@router.get("", response_model=FarmTaskListResponse)
async def list_tasks(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    """List all farm tasks with filtering."""
    # TODO: Implement organization-wide task listing
    # For now, return user's tasks
    service = TaskService(db)
    tasks, total = await service.get_my_tasks(
        org_id=current_user.org_id,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        include_completed=True,
    )
    
    return FarmTaskListResponse(
        items=[FarmTaskResponse.model_validate(task) for task in tasks],
        total=total,
    )


@router.get("/{task_id}", response_model=FarmTaskResponse)
async def get_task(
    task_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a specific task."""
    from uuid import UUID
    
    service = TaskService(db)
    task = await service.get_task_by_id(UUID(task_id))
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.org_id != current_user.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return FarmTaskResponse.model_validate(task)


@router.post("", response_model=FarmTaskResponse)
async def create_task(
    data: FarmTaskCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new task."""
    service = TaskService(db)
    task = await service.create_task(
        org_id=current_user.org_id,
        created_by=current_user.id,
        data=data,
    )
    await db.commit()
    
    return FarmTaskResponse.model_validate(task)


@router.put("/{task_id}", response_model=FarmTaskResponse)
async def update_task(
    task_id: str,
    data: FarmTaskUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update a task."""
    from uuid import UUID
    
    service = TaskService(db)
    task = await service.update_task(UUID(task_id), data)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.org_id != current_user.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    await db.commit()
    return FarmTaskResponse.model_validate(task)


@router.post("/{task_id}/start", response_model=FarmTaskResponse)
async def start_task(
    task_id: str,
    data: TaskStartRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Mark task as started."""
    from uuid import UUID
    
    service = TaskService(db)
    task = await service.start_task(UUID(task_id))
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.org_id != current_user.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    await db.commit()
    return FarmTaskResponse.model_validate(task)


@router.post("/{task_id}/complete", response_model=FarmTaskResponse)
async def complete_task(
    task_id: str,
    data: TaskCompleteRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Mark task as completed."""
    from uuid import UUID
    
    service = TaskService(db)
    task = await service.complete_task(
        UUID(task_id),
        feedback=data.feedback,
        rating=data.rating,
    )
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.org_id != current_user.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    await db.commit()
    return FarmTaskResponse.model_validate(task)


@router.post("/{task_id}/postpone", response_model=FarmTaskResponse)
async def postpone_task(
    task_id: str,
    data: TaskPostponeRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Postpone a task."""
    from uuid import UUID
    
    service = TaskService(db)
    task = await service.postpone_task(
        UUID(task_id),
        postponed_to=data.postponed_to,
        reason=data.postpone_reason,
    )
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.org_id != current_user.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    await db.commit()
    return FarmTaskResponse.model_validate(task)


@router.post("/{task_id}/audio")
async def add_audio_log(task_id: str):
    """Add voice log to task."""
    # TODO: Implement audio log functionality
    return {"message": "Audio log feature coming soon"}
