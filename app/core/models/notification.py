"""
Notification model for push notifications and alerts with Tamil voice support.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models.base import BaseModel

if TYPE_CHECKING:
    from app.core.models.user import User


class NotificationType(str, Enum):
    """Types of notifications."""

    ALERT = "alert"  # Urgent alerts
    REMINDER = "reminder"  # Task reminders
    ESCALATION = "escalation"  # Overdue task escalation
    INFO = "info"  # Informational
    ASSIGNMENT = "assignment"  # Task/job assignment
    STATUS_UPDATE = "status_update"  # Status changes
    LOW_STOCK = "low_stock"  # Inventory alerts


class NotificationPriority(str, Enum):
    """Notification priority levels."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class Notification(BaseModel):
    """
    Notification model with Tamil voice support.

    Features:
    - Multi-language support (title and message in Tamil)
    - Pre-rendered audio URL for Tamil voice playback
    - Entity linking for deep navigation
    - Read/delivery tracking
    """

    __tablename__ = "notifications"

    # Recipient
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    # Type and priority
    type: Mapped[str] = mapped_column(
        String(50), nullable=False, default=NotificationType.INFO.value
    )
    priority: Mapped[str] = mapped_column(
        String(20), nullable=False, default=NotificationPriority.NORMAL.value
    )

    # Content
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    title_tamil: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    message_tamil: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Pre-rendered Tamil audio for voice playback
    audio_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Entity reference for deep linking
    entity_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # 'farm_task', 'job_card', etc.
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    # Action URL for mobile navigation
    action_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Delivery tracking
    delivered_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notifications")

    @property
    def is_read(self) -> bool:
        return self.read_at is not None

    @property
    def is_delivered(self) -> bool:
        return self.delivered_at is not None

    @property
    def is_critical(self) -> bool:
        return self.priority == NotificationPriority.CRITICAL.value

    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, type={self.type}, user_id={self.user_id})>"
