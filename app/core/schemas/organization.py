"""
Organization schemas for CRUD operations.
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import Field

from app.core.schemas.common import BaseSchema


class OrganizationBase(BaseSchema):
    """Base organization schema."""

    name: str = Field(..., min_length=1, max_length=100)
    name_tamil: Optional[str] = Field(None, max_length=100)
    code: str = Field(..., min_length=1, max_length=50)
    type: str = Field(default="both")  # 'farm', 'maintenance', 'both'
    description: Optional[str] = Field(None, max_length=500)


class OrganizationCreate(OrganizationBase):
    """Schema for creating an organization."""

    settings: Optional[dict[str, Any]] = Field(default_factory=dict)


class OrganizationUpdate(BaseSchema):
    """Schema for updating an organization."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    name_tamil: Optional[str] = Field(None, max_length=100)
    type: Optional[str] = None
    description: Optional[str] = Field(None, max_length=500)
    settings: Optional[dict[str, Any]] = None
    is_active: Optional[bool] = None


class OrganizationResponse(OrganizationBase):
    """Schema for organization response."""

    id: UUID
    settings: dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class OrganizationListItem(BaseSchema):
    """Simplified organization schema for list views."""

    id: UUID
    name: str
    name_tamil: Optional[str] = None
    code: str
    type: str
    is_active: bool
