"""
User schemas for CRUD operations.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import EmailStr, Field

from app.core.models.user import Department, UserRole
from app.core.schemas.common import BaseSchema


class UserBase(BaseSchema):
    """Base user schema with common fields."""

    name: str = Field(..., min_length=1, max_length=100)
    name_tamil: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=15, pattern=r"^\+?[\d\s-]{10,15}$")
    email: Optional[EmailStr] = None
    role: str = Field(default=UserRole.WORKER.value)
    department: str = Field(default=Department.GENERAL.value)
    preferred_language: str = Field(default="ta", max_length=10)


class UserCreate(UserBase):
    """Schema for creating a new user."""

    employee_code: str = Field(..., min_length=1, max_length=20)
    org_id: UUID
    pin: str = Field(
        ...,
        min_length=4,
        max_length=6,
        pattern=r"^\d{4,6}$",
        description="4-6 digit PIN",
    )
    password: Optional[str] = Field(
        None, min_length=8, description="Password for admin users"
    )


class UserUpdate(BaseSchema):
    """Schema for updating a user."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    name_tamil: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=15)
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    department: Optional[str] = None
    preferred_language: Optional[str] = Field(None, max_length=10)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response."""

    id: UUID
    employee_code: str
    org_id: UUID
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class UserProfile(BaseSchema):
    """Schema for current user profile (self)."""

    id: UUID
    employee_code: str
    name: str
    name_tamil: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    role: str
    department: str
    preferred_language: str
    org_id: UUID
    org_name: str
    org_name_tamil: Optional[str] = None
    is_active: bool
    created_at: datetime


class UserListItem(BaseSchema):
    """Simplified user schema for list views."""

    id: UUID
    employee_code: str
    name: str
    name_tamil: Optional[str] = None
    role: str
    department: str
    is_active: bool


class UserAssignment(BaseSchema):
    """Schema for assigning users to tasks/jobs."""

    user_id: UUID
    name: str
    name_tamil: Optional[str] = None
    employee_code: str
    department: str
