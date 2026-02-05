"""
Location schemas for hierarchical location management.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from pydantic import Field

from app.core.models.location import LocationType
from app.core.schemas.common import BaseSchema


class LocationBase(BaseSchema):
    """Base location schema."""

    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    name_tamil: Optional[str] = Field(None, max_length=100)
    type: str = Field(...)  # LocationType value
    description: Optional[str] = Field(None, max_length=500)
    description_tamil: Optional[str] = Field(None, max_length=500)


class LocationCreate(LocationBase):
    """Schema for creating a location."""

    org_id: UUID
    parent_id: Optional[UUID] = None
    qr_code: Optional[str] = Field(None, max_length=100)
    coordinates: Optional[dict[str, Any]] = None  # {lat, lng, polygon}
    area_sqm: Optional[Decimal] = Field(None, ge=0)
    address: Optional[str] = Field(None, max_length=500)
    metadata: Optional[dict[str, Any]] = Field(default_factory=dict)


class LocationUpdate(BaseSchema):
    """Schema for updating a location."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    name_tamil: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    description_tamil: Optional[str] = Field(None, max_length=500)
    qr_code: Optional[str] = Field(None, max_length=100)
    coordinates: Optional[dict[str, Any]] = None
    area_sqm: Optional[Decimal] = Field(None, ge=0)
    address: Optional[str] = Field(None, max_length=500)
    metadata: Optional[dict[str, Any]] = None
    is_active: Optional[bool] = None


class LocationResponse(LocationBase):
    """Schema for location response."""

    id: UUID
    org_id: UUID
    parent_id: Optional[UUID] = None
    qr_code: Optional[str] = None
    coordinates: Optional[dict[str, Any]] = None
    area_sqm: Optional[Decimal] = None
    address: Optional[str] = None
    metadata: dict[str, Any]
    is_active: bool
    full_path: str
    created_at: datetime
    updated_at: datetime


class LocationListItem(BaseSchema):
    """Simplified location schema for list views."""

    id: UUID
    code: str
    name: str
    name_tamil: Optional[str] = None
    type: str
    parent_id: Optional[UUID] = None
    qr_code: Optional[str] = None
    is_active: bool


class LocationTree(BaseSchema):
    """Location with nested children for tree view."""

    id: UUID
    code: str
    name: str
    name_tamil: Optional[str] = None
    type: str
    children: list["LocationTree"] = []

    class Config:
        from_attributes = True


# Update forward reference
LocationTree.model_rebuild()


class LocationQRLookup(BaseSchema):
    """Response for QR code lookup."""

    location: LocationResponse
    parent_path: list[LocationListItem]  # Path from root to this location


class GuestHouseInfo(BaseSchema):
    """Guest house specific information."""

    id: UUID
    code: str
    name: str
    name_tamil: Optional[str] = None
    room_count: int
    utility_profile: Optional[str] = None


class RoomInfo(BaseSchema):
    """Room specific information."""

    id: UUID
    code: str
    name: str
    name_tamil: Optional[str] = None
    guest_house_id: UUID
    guest_house_name: str
    floor: Optional[str] = None
    has_ac: bool = False


class FieldInfo(BaseSchema):
    """Field specific information for farm module."""

    id: UUID
    code: str
    name: str
    name_tamil: Optional[str] = None
    area_acres: Optional[Decimal] = None
    soil_type: Optional[str] = None
    irrigation_type: Optional[str] = None
    current_crop: Optional[str] = None
