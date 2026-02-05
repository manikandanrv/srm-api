"""
Authentication schemas for PIN-based and password login.
"""

from typing import Optional
from uuid import UUID

from pydantic import Field

from app.core.schemas.common import BaseSchema


class LoginRequest(BaseSchema):
    """Login request with PIN or password."""

    employee_code: str = Field(
        ..., min_length=1, max_length=20, description="Employee code for identification"
    )
    pin: Optional[str] = Field(
        None,
        min_length=4,
        max_length=6,
        pattern=r"^\d{4,6}$",
        description="4-6 digit PIN for authentication",
    )
    password: Optional[str] = Field(
        None, min_length=6, description="Password for admin users"
    )


class BiometricLoginRequest(BaseSchema):
    """Biometric login request."""

    employee_code: str = Field(..., min_length=1, max_length=20)
    biometric_token: str = Field(
        ..., description="Device-generated biometric verification token"
    )
    device_id: str = Field(..., description="Unique device identifier")


class TokenData(BaseSchema):
    """Data encoded in JWT token."""

    user_id: UUID
    employee_code: str
    role: str
    department: str
    org_id: UUID
    exp: Optional[int] = None


class LoginResponse(BaseSchema):
    """Login response with tokens and user info."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # Seconds until access token expires

    # User info for immediate use
    user_id: UUID
    employee_code: str
    name: str
    name_tamil: Optional[str] = None
    role: str
    department: str
    org_id: UUID
    org_name: str


class RefreshTokenRequest(BaseSchema):
    """Refresh token request."""

    refresh_token: str = Field(..., description="Refresh token from login")


class RefreshTokenResponse(BaseSchema):
    """Refresh token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class ChangePINRequest(BaseSchema):
    """Request to change PIN."""

    current_pin: str = Field(
        ..., min_length=4, max_length=6, pattern=r"^\d{4,6}$"
    )
    new_pin: str = Field(
        ..., min_length=4, max_length=6, pattern=r"^\d{4,6}$"
    )


class ChangePasswordRequest(BaseSchema):
    """Request to change password (admin users)."""

    current_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=8)


class ResetPINRequest(BaseSchema):
    """Admin request to reset user PIN."""

    user_id: UUID
    new_pin: str = Field(
        ..., min_length=4, max_length=6, pattern=r"^\d{4,6}$"
    )
