"""
Location management API endpoints.
"""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.user import User, UserRole
from app.core.schemas.common import MessageResponse, PaginatedResponse
from app.core.schemas.location import (
    LocationCreate,
    LocationListItem,
    LocationQRLookup,
    LocationResponse,
    LocationTree,
    LocationUpdate,
)
from app.core.services.auth import get_current_user, require_role
from app.core.services.location import LocationService
from app.database import get_db

router = APIRouter()


@router.get("", response_model=PaginatedResponse[LocationListItem])
async def list_locations(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    parent_id: Optional[UUID] = None,
    location_type: Optional[str] = None,
    is_active: Optional[bool] = True,
    search: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
):
    """
    List locations with optional filtering.

    - **parent_id**: Filter by parent location (get children)
    - **location_type**: Filter by type (guest_house, room, field, etc.)
    - **is_active**: Filter by active status
    - **search**: Search by name or code
    """
    location_service = LocationService(db)
    offset = (page - 1) * page_size

    locations, total = await location_service.get_all(
        org_id=current_user.org_id,
        parent_id=parent_id,
        location_type=location_type,
        is_active=is_active,
        search=search,
        offset=offset,
        limit=page_size,
    )

    return PaginatedResponse.create(
        items=[LocationListItem.model_validate(loc) for loc in locations],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/tree", response_model=list[LocationTree])
async def get_location_tree(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    root_id: Optional[UUID] = None,
):
    """
    Get hierarchical location tree.

    - **root_id**: Optional root to start from (default: all root locations)
    """
    location_service = LocationService(db)
    return await location_service.get_tree(current_user.org_id, root_id)


@router.get("/qr/{qr_code}", response_model=LocationQRLookup)
async def lookup_by_qr(
    qr_code: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Look up a location by QR code.

    Returns the location and its parent path for context.
    """
    location_service = LocationService(db)
    location = await location_service.get_by_qr_code(qr_code)

    if not location:
        raise HTTPException(status_code=404, detail="Location not found for QR code")

    if location.org_id != current_user.org_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Get parent path
    parent_path = await location_service.get_parent_path(location.id)

    return LocationQRLookup(
        location=LocationResponse(
            id=location.id,
            org_id=location.org_id,
            parent_id=location.parent_id,
            code=location.code,
            name=location.name,
            name_tamil=location.name_tamil,
            type=location.type,
            qr_code=location.qr_code,
            coordinates=location.coordinates,
            area_sqm=location.area_sqm,
            address=location.address,
            description=location.description,
            description_tamil=location.description_tamil,
            metadata=location.metadata,
            is_active=location.is_active,
            full_path=location.full_path,
            created_at=location.created_at,
            updated_at=location.updated_at,
        ),
        parent_path=[LocationListItem.model_validate(p) for p in parent_path],
    )


@router.get("/{location_id}", response_model=LocationResponse)
async def get_location(
    location_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get a specific location by ID.
    """
    location_service = LocationService(db)
    location = await location_service.get_by_id(location_id)

    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    if location.org_id != current_user.org_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return LocationResponse(
        id=location.id,
        org_id=location.org_id,
        parent_id=location.parent_id,
        code=location.code,
        name=location.name,
        name_tamil=location.name_tamil,
        type=location.type,
        qr_code=location.qr_code,
        coordinates=location.coordinates,
        area_sqm=location.area_sqm,
        address=location.address,
        description=location.description,
        description_tamil=location.description_tamil,
        metadata=location.metadata,
        is_active=location.is_active,
        full_path=location.full_path,
        created_at=location.created_at,
        updated_at=location.updated_at,
    )


@router.post("", response_model=LocationResponse, status_code=201)
async def create_location(
    data: LocationCreate,
    current_user: Annotated[User, Depends(require_role(UserRole.MANAGER, UserRole.ADMIN))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Create a new location.

    Requires manager role or higher.
    """
    # Ensure org_id matches current user's org (unless admin)
    if not current_user.is_admin:
        data.org_id = current_user.org_id

    location_service = LocationService(db)
    location = await location_service.create(data)

    return LocationResponse(
        id=location.id,
        org_id=location.org_id,
        parent_id=location.parent_id,
        code=location.code,
        name=location.name,
        name_tamil=location.name_tamil,
        type=location.type,
        qr_code=location.qr_code,
        coordinates=location.coordinates,
        area_sqm=location.area_sqm,
        address=location.address,
        description=location.description,
        description_tamil=location.description_tamil,
        metadata=location.metadata,
        is_active=location.is_active,
        full_path=location.full_path,
        created_at=location.created_at,
        updated_at=location.updated_at,
    )


@router.put("/{location_id}", response_model=LocationResponse)
async def update_location(
    location_id: UUID,
    data: LocationUpdate,
    current_user: Annotated[User, Depends(require_role(UserRole.MANAGER, UserRole.ADMIN))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Update a location.

    Requires manager role or higher.
    """
    location_service = LocationService(db)
    location = await location_service.get_by_id(location_id)

    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    if not current_user.is_admin and location.org_id != current_user.org_id:
        raise HTTPException(status_code=403, detail="Access denied")

    location = await location_service.update(location_id, data)

    return LocationResponse(
        id=location.id,
        org_id=location.org_id,
        parent_id=location.parent_id,
        code=location.code,
        name=location.name,
        name_tamil=location.name_tamil,
        type=location.type,
        qr_code=location.qr_code,
        coordinates=location.coordinates,
        area_sqm=location.area_sqm,
        address=location.address,
        description=location.description,
        description_tamil=location.description_tamil,
        metadata=location.metadata,
        is_active=location.is_active,
        full_path=location.full_path,
        created_at=location.created_at,
        updated_at=location.updated_at,
    )


@router.delete("/{location_id}", response_model=MessageResponse)
async def delete_location(
    location_id: UUID,
    current_user: Annotated[User, Depends(require_role(UserRole.ADMIN))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Soft delete a location.

    Requires admin role.
    Note: Cannot delete locations with active children.
    """
    location_service = LocationService(db)
    await location_service.delete(location_id)
    return MessageResponse(message="Location deleted successfully")
