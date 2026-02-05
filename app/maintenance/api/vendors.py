"""
Vendor management API endpoints.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def list_vendors():
    """List all vendors."""
    return {"items": [], "total": 0}


@router.get("/{vendor_id}")
async def get_vendor(vendor_id: str):
    """Get a specific vendor."""
    return {"message": "Not implemented"}


@router.post("")
async def create_vendor():
    """Create a new vendor."""
    return {"message": "Not implemented"}


@router.put("/{vendor_id}")
async def update_vendor(vendor_id: str):
    """Update a vendor."""
    return {"message": "Not implemented"}
