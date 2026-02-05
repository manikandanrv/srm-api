"""
Core module Pydantic schemas for request/response validation.
"""

from app.core.schemas.auth import LoginRequest, LoginResponse, RefreshTokenRequest, TokenData
from app.core.schemas.common import (
    ErrorResponse,
    MessageResponse,
    PaginatedResponse,
    PaginationParams,
)
from app.core.schemas.location import (
    LocationCreate,
    LocationResponse,
    LocationTree,
    LocationUpdate,
)
from app.core.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationUpdate,
)
from app.core.schemas.organization import (
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
)
from app.core.schemas.user import UserCreate, UserProfile, UserResponse, UserUpdate

__all__ = [
    # Common
    "ErrorResponse",
    "MessageResponse",
    "PaginatedResponse",
    "PaginationParams",
    # Auth
    "LoginRequest",
    "LoginResponse",
    "RefreshTokenRequest",
    "TokenData",
    # Organization
    "OrganizationCreate",
    "OrganizationResponse",
    "OrganizationUpdate",
    # User
    "UserCreate",
    "UserResponse",
    "UserUpdate",
    "UserProfile",
    # Location
    "LocationCreate",
    "LocationResponse",
    "LocationUpdate",
    "LocationTree",
    # Notification
    "NotificationCreate",
    "NotificationResponse",
    "NotificationUpdate",
]
