"""
Farm equipment API endpoints.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def list_equipment():
    """List all farm equipment."""
    return {"items": [], "total": 0}


@router.get("/{equipment_id}")
async def get_equipment(equipment_id: str):
    """Get a specific equipment item."""
    return {"message": "Not implemented"}


@router.put("/{equipment_id}/status")
async def update_equipment_status(equipment_id: str):
    """Update equipment status."""
    return {"message": "Not implemented"}
