"""
User management API endpoints.
"""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.user import User, UserRole
from app.core.schemas.common import MessageResponse, PaginatedResponse
from app.core.schemas.user import (
    UserCreate,
    UserProfile,
    UserResponse,
    UserUpdate,
)
from app.core.services.auth import get_current_user, require_role
from app.core.services.user import UserService
from app.database import get_db

router = APIRouter()


@router.get("/me", response_model=UserProfile)
async def get_my_profile(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Get the current user's profile.
    """
    return UserProfile(
        id=current_user.id,
        employee_code=current_user.employee_code,
        name=current_user.name,
        name_tamil=current_user.name_tamil,
        phone=current_user.phone,
        email=current_user.email,
        role=current_user.role,
        department=current_user.department,
        preferred_language=current_user.preferred_language,
        org_id=current_user.org_id,
        org_name=current_user.organization.name if current_user.organization else "",
        org_name_tamil=current_user.organization.name_tamil if current_user.organization else None,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
    )


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    data: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Update the current user's profile.

    Note: Role and department can only be changed by admins.
    """
    # Prevent non-admins from changing their own role or department
    if not current_user.is_admin:
        data.role = None
        data.department = None
        data.is_active = None

    user_service = UserService(db)
    user = await user_service.update(current_user.id, data)
    return UserResponse.model_validate(user)


@router.get("", response_model=PaginatedResponse[UserResponse])
async def list_users(
    current_user: Annotated[User, Depends(require_role(UserRole.SUPERVISOR, UserRole.MANAGER, UserRole.ADMIN))],
    db: Annotated[AsyncSession, Depends(get_db)],
    org_id: Optional[UUID] = None,
    department: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    """
    List users with optional filtering.

    Requires supervisor role or higher.
    """
    # Non-admins can only see users in their organization
    if not current_user.is_admin:
        org_id = current_user.org_id

    user_service = UserService(db)
    offset = (page - 1) * page_size
    users, total = await user_service.get_all(
        org_id=org_id,
        department=department,
        role=role,
        is_active=is_active,
        search=search,
        offset=offset,
        limit=page_size,
    )

    return PaginatedResponse.create(
        items=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user: Annotated[User, Depends(require_role(UserRole.SUPERVISOR, UserRole.MANAGER, UserRole.ADMIN))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get a specific user by ID.

    Requires supervisor role or higher.
    """
    user_service = UserService(db)
    user = await user_service.get_by_id(user_id)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")

    # Non-admins can only view users in their organization
    if not current_user.is_admin and user.org_id != current_user.org_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Access denied")

    return UserResponse.model_validate(user)


@router.post("", response_model=UserResponse, status_code=201)
async def create_user(
    data: UserCreate,
    current_user: Annotated[User, Depends(require_role(UserRole.MANAGER, UserRole.ADMIN))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Create a new user.

    Requires manager role or higher.
    """
    # Non-admins can only create users in their organization
    if not current_user.is_admin:
        data.org_id = current_user.org_id

    user_service = UserService(db)
    user = await user_service.create(data)
    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    current_user: Annotated[User, Depends(require_role(UserRole.MANAGER, UserRole.ADMIN))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Update a user.

    Requires manager role or higher.
    """
    user_service = UserService(db)
    user = await user_service.get_by_id(user_id)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")

    # Non-admins can only update users in their organization
    if not current_user.is_admin and user.org_id != current_user.org_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Access denied")

    user = await user_service.update(user_id, data)
    return UserResponse.model_validate(user)


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: UUID,
    current_user: Annotated[User, Depends(require_role(UserRole.ADMIN))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Soft delete a user (set is_active to False).

    Requires admin role.
    """
    user_service = UserService(db)
    await user_service.delete(user_id)
    return MessageResponse(message="User deleted successfully")


@router.post("/{user_id}/reset-pin", response_model=MessageResponse)
async def reset_user_pin(
    user_id: UUID,
    current_user: Annotated[User, Depends(require_role(UserRole.MANAGER, UserRole.ADMIN))],
    db: Annotated[AsyncSession, Depends(get_db)],
    new_pin: str = Query(..., min_length=4, max_length=6, pattern=r"^\d{4,6}$"),
):
    """
    Reset a user's PIN (admin operation).

    Requires manager role or higher.
    """
    user_service = UserService(db)
    user = await user_service.get_by_id(user_id)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")

    # Non-admins can only reset PINs for users in their organization
    if not current_user.is_admin and user.org_id != current_user.org_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Access denied")

    await user_service.reset_pin(user_id, new_pin)
    return MessageResponse(message="PIN reset successfully")
