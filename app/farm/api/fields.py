"""
Field management API endpoints.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.user import User
from app.core.services.auth import get_current_user
from app.database import get_db
from app.farm.schemas.schedule import FieldResponse
from app.farm.services.schedule import ScheduleService

router = APIRouter()


@router.get("", response_model=list[FieldResponse])
async def list_fields(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    List all farm fields.

    Returns all active fields for task assignment.
    """
    service = ScheduleService(db)
    fields = await service.get_fields(current_user.org_id)

    return [
        {
            "id": f.id,
            "code": f.code,
            "name": f.name,
            "name_tamil": f.name_tamil,
            "area_in_acres": float(f.area_acres) if f.area_acres else None,
            "current_crop": None,  # TODO: Get from current_crop relationship
            "current_crop_tamil": None,
        }
        for f in fields
    ]


@router.get("/{field_id}")
async def get_field(field_id: str):
    """Get a specific field."""
    return {"message": "Not implemented"}


@router.post("")
async def create_field():
    """Create a new field."""
    return {"message": "Not implemented"}


@router.put("/{field_id}")
async def update_field(field_id: str):
    """Update a field."""
    return {"message": "Not implemented"}


@router.get("/{field_id}/history")
async def get_field_history(field_id: str):
    """Get cultivation history for a field."""
    return {"items": [], "total": 0}
