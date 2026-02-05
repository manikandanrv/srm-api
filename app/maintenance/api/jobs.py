"""
Job card management API endpoints.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def list_jobs():
    """List all job cards with filtering."""
    return {"items": [], "total": 0}


@router.get("/my")
async def get_my_jobs():
    """Get jobs assigned to current user."""
    return {"items": [], "total": 0}


@router.get("/{job_id}")
async def get_job(job_id: str):
    """Get a specific job card."""
    return {"message": "Not implemented"}


@router.post("")
async def create_job():
    """Create a new job card."""
    return {"message": "Not implemented"}


@router.put("/{job_id}")
async def update_job(job_id: str):
    """Update a job card."""
    return {"message": "Not implemented"}


@router.post("/{job_id}/assign")
async def assign_job(job_id: str):
    """Assign technician to job."""
    return {"message": "Not implemented"}


@router.post("/{job_id}/start")
async def start_job(job_id: str):
    """Mark job as started."""
    return {"message": "Not implemented"}


@router.post("/{job_id}/complete")
async def complete_job(job_id: str):
    """Mark job as completed."""
    return {"message": "Not implemented"}


@router.post("/{job_id}/materials")
async def add_job_materials(job_id: str):
    """Add materials used in job."""
    return {"message": "Not implemented"}


@router.post("/{job_id}/audio")
async def add_job_audio(job_id: str):
    """Add voice log to job."""
    return {"message": "Not implemented"}
