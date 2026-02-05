"""
Organization model for multi-tenant support.
"""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models.base import BaseModel

if TYPE_CHECKING:
    from app.core.models.location import Location
    from app.core.models.user import User


class Organization(BaseModel):
    """
    Organization model for multi-tenant support.

    Supports different ashram departments:
    - farm: NPP Farm operations
    - maintenance: Ashram maintenance
    - both: Access to all modules
    """

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    name_tamil: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="both"
    )  # 'farm', 'maintenance', 'both'
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    settings: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    users: Mapped[list["User"]] = relationship(
        "User", back_populates="organization", lazy="selectin"
    )
    locations: Mapped[list["Location"]] = relationship(
        "Location", back_populates="organization", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name={self.name}, type={self.type})>"
