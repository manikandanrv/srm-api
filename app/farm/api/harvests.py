"""
Harvest tracking API endpoints.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def list_harvests():
    """List all harvests."""
    return {"items": [], "total": 0}


@router.post("")
async def record_harvest():
    """Record a new harvest."""
    return {"message": "Not implemented"}


@router.get("/stats")
async def get_harvest_stats():
    """Get harvest statistics."""
    return {"message": "Not implemented"}


@router.get("/{harvest_id}")
async def get_harvest(harvest_id: str):
    """Get a specific harvest record."""
    return {"message": "Not implemented"}
