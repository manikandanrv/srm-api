"""
Location model with hierarchical support for:
- Guest House -> Room hierarchy (Maintenance)
- Field -> Block hierarchy (Farm)
"""

import uuid
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models.base import BaseModel

if TYPE_CHECKING:
    from app.core.models.organization import Organization


class LocationType(str, Enum):
    """Types of locations in the system."""

    # Maintenance locations
    GUEST_HOUSE = "guest_house"
    ROOM = "room"
    COMMON_AREA = "common_area"
    UTILITY_ROOM = "utility_room"

    # Farm locations
    FARM = "farm"
    FIELD = "field"
    BLOCK = "block"
    COWSHED = "cowshed"
    WORKER_QUARTERS = "worker_quarters"
    WATER_SOURCE = "water_source"
    STORAGE = "storage"


class Location(BaseModel):
    """
    Hierarchical location model supporting both maintenance and farm domains.

    Hierarchy examples:
    - Maintenance: Organization -> Guest House -> Room
    - Farm: Organization -> Farm -> Field -> Block

    Features:
    - Self-referential parent-child relationship
    - QR code for easy scanning
    - Geographic coordinates (optional)
    - Area measurement
    - Flexible metadata storage
    """

    __tablename__ = "locations"

    # Organization relationship
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )

    # Hierarchy
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id"), nullable=True
    )

    # Identity
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    name_tamil: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)

    # QR Code for scanning
    qr_code: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)

    # Geographic data
    coordinates: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )  # {lat, lng, polygon}
    area_sqm: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Extra data
    extra_data: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    description_tamil: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="locations"
    )
    parent: Mapped[Optional["Location"]] = relationship(
        "Location",
        remote_side="Location.id",
        back_populates="children",
    )
    children: Mapped[list["Location"]] = relationship(
        "Location",
        back_populates="parent",
        lazy="selectin",
    )

    @property
    def full_path(self) -> str:
        """Get full path from root to this location."""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name

    @property
    def is_guest_house(self) -> bool:
        return self.type == LocationType.GUEST_HOUSE.value

    @property
    def is_room(self) -> bool:
        return self.type == LocationType.ROOM.value

    @property
    def is_field(self) -> bool:
        return self.type == LocationType.FIELD.value

    def __repr__(self) -> str:
        return f"<Location(id={self.id}, code={self.code}, name={self.name}, type={self.type})>"
