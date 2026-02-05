"""
Authentication API endpoints.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.user import User
from app.core.schemas.auth import (
    ChangePINRequest,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
)
from app.core.schemas.common import MessageResponse
from app.core.services.auth import AuthService, get_current_user
from app.database import get_db

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Authenticate user with employee code and PIN or password.

    - **employee_code**: Unique employee identifier
    - **pin**: 4-6 digit PIN for workers (primary auth method)
    - **password**: Password for admin users (optional)

    Returns access token, refresh token, and user information.
    """
    auth_service = AuthService(db)
    return await auth_service.login(request)


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Refresh access token using a valid refresh token.

    Returns a new access token.
    """
    auth_service = AuthService(db)
    access_token, expires_in = await auth_service.refresh_access_token(
        request.refresh_token
    )
    return RefreshTokenResponse(
        access_token=access_token,
        expires_in=expires_in,
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Logout the current user.

    Note: With JWT, logout is typically handled client-side by discarding tokens.
    This endpoint can be used to invalidate refresh tokens if using a token blacklist.
    """
    # TODO: Implement token blacklist if needed
    return MessageResponse(message="Logged out successfully")


@router.post("/change-pin", response_model=MessageResponse)
async def change_pin(
    request: ChangePINRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Change the current user's PIN.

    Requires the current PIN for verification.
    """
    auth_service = AuthService(db)
    await auth_service.change_pin(
        user_id=current_user.id,
        current_pin=request.current_pin,
        new_pin=request.new_pin,
    )
    return MessageResponse(message="PIN changed successfully")


@router.get("/me")
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Get the current authenticated user's information.
    """
    return {
        "id": current_user.id,
        "employee_code": current_user.employee_code,
        "name": current_user.name,
        "name_tamil": current_user.name_tamil,
        "role": current_user.role,
        "department": current_user.department,
        "org_id": current_user.org_id,
        "org_name": current_user.organization.name if current_user.organization else None,
        "preferred_language": current_user.preferred_language,
    }
