"""
Notification schemas for push notifications and alerts.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from app.core.models.notification import NotificationPriority, NotificationType
from app.core.schemas.common import BaseSchema


class NotificationBase(BaseSchema):
    """Base notification schema."""

    type: str = Field(default=NotificationType.INFO.value)
    priority: str = Field(default=NotificationPriority.NORMAL.value)
    title: str = Field(..., min_length=1, max_length=200)
    title_tamil: Optional[str] = Field(None, max_length=200)
    message: Optional[str] = None
    message_tamil: Optional[str] = None


class NotificationCreate(NotificationBase):
    """Schema for creating a notification."""

    user_id: UUID
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    action_url: Optional[str] = Field(None, max_length=500)
    audio_url: Optional[str] = Field(None, max_length=500)


class NotificationUpdate(BaseSchema):
    """Schema for updating a notification (marking as read)."""

    read_at: Optional[datetime] = None


class NotificationResponse(NotificationBase):
    """Schema for notification response."""

    id: UUID
    user_id: UUID
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    action_url: Optional[str] = None
    audio_url: Optional[str] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    is_read: bool
    created_at: datetime


class NotificationListItem(BaseSchema):
    """Simplified notification for list views."""

    id: UUID
    type: str
    priority: str
    title: str
    title_tamil: Optional[str] = None
    is_read: bool
    created_at: datetime


class NotificationCount(BaseSchema):
    """Notification count summary."""

    total: int
    unread: int
    critical: int


class BulkNotificationCreate(BaseSchema):
    """Schema for creating notifications for multiple users."""

    user_ids: list[UUID]
    type: str = Field(default=NotificationType.INFO.value)
    priority: str = Field(default=NotificationPriority.NORMAL.value)
    title: str = Field(..., min_length=1, max_length=200)
    title_tamil: Optional[str] = Field(None, max_length=200)
    message: Optional[str] = None
    message_tamil: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
