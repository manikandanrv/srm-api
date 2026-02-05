"""
Farm workers API endpoints.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.user import User
from app.core.services.auth import get_current_user
from app.database import get_db
from app.farm.schemas.schedule import WorkerResponse
from app.farm.services.schedule import ScheduleService

router = APIRouter()


@router.get("", response_model=list[WorkerResponse])
async def list_farm_workers(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    List all farm workers.

    Returns all active workers in the farm department.
    Used for task assignment dropdowns.
    """
    service = ScheduleService(db)
    workers = await service.get_workers(current_user.org_id)

    return [
        {
            "id": w.id,
            "employee_code": w.employee_code,
            "name": w.name,
            "name_tamil": w.name_tamil,
            "phone": w.phone,
            "role": w.role,
        }
        for w in workers
    ]
