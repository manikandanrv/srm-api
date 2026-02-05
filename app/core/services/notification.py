"""
Notification service for push notifications and alerts.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.notification import (
    Notification,
    NotificationPriority,
    NotificationType,
)
from app.core.schemas.notification import NotificationCount, NotificationCreate


class NotificationService:
    """Notification service for creating and managing notifications."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, notification_id: UUID) -> Optional[Notification]:
        """Get notification by ID."""
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        return result.scalar_one_or_none()

    async def get_user_notifications(
        self,
        user_id: UUID,
        unread_only: bool = False,
        notification_type: Optional[str] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Notification], int]:
        """Get notifications for a user."""
        query = select(Notification).where(Notification.user_id == user_id)

        if unread_only:
            query = query.where(Notification.read_at.is_(None))
        if notification_type:
            query = query.where(Notification.type == notification_type)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering (newest first)
        query = query.offset(offset).limit(limit).order_by(Notification.created_at.desc())
        result = await self.db.execute(query)
        notifications = list(result.scalars().all())

        return notifications, total

    async def get_notification_count(self, user_id: UUID) -> NotificationCount:
        """Get notification counts for a user."""
        # Total count
        total_result = await self.db.execute(
            select(func.count()).where(Notification.user_id == user_id)
        )
        total = total_result.scalar() or 0

        # Unread count
        unread_result = await self.db.execute(
            select(func.count()).where(
                Notification.user_id == user_id,
                Notification.read_at.is_(None),
            )
        )
        unread = unread_result.scalar() or 0

        # Critical unread count
        critical_result = await self.db.execute(
            select(func.count()).where(
                Notification.user_id == user_id,
                Notification.read_at.is_(None),
                Notification.priority == NotificationPriority.CRITICAL.value,
            )
        )
        critical = critical_result.scalar() or 0

        return NotificationCount(total=total, unread=unread, critical=critical)

    async def create(self, data: NotificationCreate) -> Notification:
        """Create a new notification."""
        notification = Notification(
            user_id=data.user_id,
            type=data.type,
            priority=data.priority,
            title=data.title,
            title_tamil=data.title_tamil,
            message=data.message,
            message_tamil=data.message_tamil,
            entity_type=data.entity_type,
            entity_id=data.entity_id,
            action_url=data.action_url,
            audio_url=data.audio_url,
        )

        self.db.add(notification)
        await self.db.flush()
        await self.db.refresh(notification)
        return notification

    async def create_bulk(
        self,
        user_ids: list[UUID],
        notification_type: str,
        priority: str,
        title: str,
        title_tamil: Optional[str] = None,
        message: Optional[str] = None,
        message_tamil: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
    ) -> int:
        """Create notifications for multiple users."""
        notifications = [
            Notification(
                user_id=user_id,
                type=notification_type,
                priority=priority,
                title=title,
                title_tamil=title_tamil,
                message=message,
                message_tamil=message_tamil,
                entity_type=entity_type,
                entity_id=entity_id,
            )
            for user_id in user_ids
        ]

        self.db.add_all(notifications)
        await self.db.flush()
        return len(notifications)

    async def mark_as_read(self, notification_id: UUID, user_id: UUID) -> bool:
        """Mark a notification as read."""
        result = await self.db.execute(
            update(Notification)
            .where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
            .values(read_at=datetime.now(timezone.utc))
        )
        return result.rowcount > 0

    async def mark_all_as_read(self, user_id: UUID) -> int:
        """Mark all notifications as read for a user."""
        result = await self.db.execute(
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.read_at.is_(None),
            )
            .values(read_at=datetime.now(timezone.utc))
        )
        return result.rowcount

    async def mark_as_delivered(self, notification_id: UUID) -> bool:
        """Mark a notification as delivered."""
        result = await self.db.execute(
            update(Notification)
            .where(Notification.id == notification_id)
            .values(delivered_at=datetime.now(timezone.utc))
        )
        return result.rowcount > 0

    async def delete(self, notification_id: UUID, user_id: UUID) -> bool:
        """Delete a notification."""
        notification = await self.get_by_id(notification_id)
        if not notification or notification.user_id != user_id:
            return False

        await self.db.delete(notification)
        await self.db.flush()
        return True

    # Convenience methods for creating specific notification types

    async def send_task_assignment(
        self,
        user_id: UUID,
        task_type: str,
        task_id: UUID,
        task_title: str,
        task_title_tamil: Optional[str] = None,
    ) -> Notification:
        """Send task assignment notification."""
        return await self.create(
            NotificationCreate(
                user_id=user_id,
                type=NotificationType.ASSIGNMENT.value,
                priority=NotificationPriority.HIGH.value,
                title=f"New task assigned: {task_title}",
                title_tamil=f"புதிய பணி ஒதுக்கப்பட்டது: {task_title_tamil or task_title}",
                entity_type=task_type,
                entity_id=task_id,
            )
        )

    async def send_task_reminder(
        self,
        user_id: UUID,
        task_type: str,
        task_id: UUID,
        task_title: str,
        task_title_tamil: Optional[str] = None,
    ) -> Notification:
        """Send task reminder notification."""
        return await self.create(
            NotificationCreate(
                user_id=user_id,
                type=NotificationType.REMINDER.value,
                priority=NotificationPriority.NORMAL.value,
                title=f"Reminder: {task_title}",
                title_tamil=f"நினைவூட்டல்: {task_title_tamil or task_title}",
                entity_type=task_type,
                entity_id=task_id,
            )
        )

    async def send_overdue_alert(
        self,
        user_id: UUID,
        task_type: str,
        task_id: UUID,
        task_title: str,
        task_title_tamil: Optional[str] = None,
    ) -> Notification:
        """Send overdue task alert."""
        return await self.create(
            NotificationCreate(
                user_id=user_id,
                type=NotificationType.ALERT.value,
                priority=NotificationPriority.CRITICAL.value,
                title=f"OVERDUE: {task_title}",
                title_tamil=f"தாமதம்: {task_title_tamil or task_title}",
                entity_type=task_type,
                entity_id=task_id,
            )
        )

    async def send_low_stock_alert(
        self,
        user_id: UUID,
        item_name: str,
        item_name_tamil: Optional[str] = None,
        current_qty: float = 0,
    ) -> Notification:
        """Send low stock alert notification."""
        return await self.create(
            NotificationCreate(
                user_id=user_id,
                type=NotificationType.LOW_STOCK.value,
                priority=NotificationPriority.HIGH.value,
                title=f"Low stock: {item_name} ({current_qty} remaining)",
                title_tamil=f"குறைந்த இருப்பு: {item_name_tamil or item_name} ({current_qty} மீதமுள்ளது)",
            )
        )
