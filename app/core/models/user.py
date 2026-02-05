"""
User model with PIN-based authentication for low-literacy users.
"""

import uuid
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models.base import BaseModel

if TYPE_CHECKING:
    from app.core.models.notification import Notification
    from app.core.models.organization import Organization


class UserRole(str, Enum):
    """User roles for RBAC."""

    WORKER = "worker"
    SUPERVISOR = "supervisor"
    MANAGER = "manager"
    ADMIN = "admin"


class Department(str, Enum):
    """User department/domain."""

    FARM = "farm"
    ELECTRICAL = "electrical"
    PLUMBING = "plumbing"
    GENERAL = "general"


class User(BaseModel):
    """
    User model supporting PIN-based authentication for low-literacy users.

    Features:
    - PIN authentication (4-6 digits) as primary auth method
    - Optional password for admin users
    - Role-based access control
    - Department assignment (farm, electrical, plumbing, general)
    - Tamil name support
    - Voice profile for potential voice recognition
    """

    __tablename__ = "users"

    # Organization relationship
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )

    # Identity
    employee_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    name_tamil: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Authentication
    pin_hash: Mapped[Optional[str]] = mapped_column(
        String(256), nullable=True
    )  # For PIN-based auth
    password_hash: Mapped[Optional[str]] = mapped_column(
        String(256), nullable=True
    )  # For admin users

    # Role and Department
    role: Mapped[str] = mapped_column(
        String(50), nullable=False, default=UserRole.WORKER.value
    )
    department: Mapped[str] = mapped_column(
        String(50), nullable=False, default=Department.GENERAL.value
    )

    # Preferences
    preferred_language: Mapped[str] = mapped_column(
        String(10), default="ta", nullable=False
    )  # Tamil default
    voice_profile_id: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )  # For voice recognition

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="users"
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="user", lazy="selectin"
    )

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN.value

    @property
    def is_supervisor(self) -> bool:
        return self.role in [UserRole.SUPERVISOR.value, UserRole.MANAGER.value, UserRole.ADMIN.value]

    @property
    def can_access_farm(self) -> bool:
        return self.department in [Department.FARM.value, Department.GENERAL.value]

    @property
    def can_access_maintenance(self) -> bool:
        return self.department in [
            Department.ELECTRICAL.value,
            Department.PLUMBING.value,
            Department.GENERAL.value,
        ]

    def __repr__(self) -> str:
        return f"<User(id={self.id}, code={self.employee_code}, name={self.name}, role={self.role})>"
