"""
Crop variety API endpoints.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def list_crops():
    """List all crop varieties."""
    # TODO: Implement
    return {"items": [], "total": 0}


@router.get("/{crop_id}")
async def get_crop(crop_id: str):
    """Get a specific crop variety."""
    # TODO: Implement
    return {"message": "Not implemented"}
