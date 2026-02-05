"""
Notification API endpoints.
"""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.user import User
from app.core.schemas.common import MessageResponse, PaginatedResponse
from app.core.schemas.notification import (
    NotificationCount,
    NotificationListItem,
    NotificationResponse,
)
from app.core.services.auth import get_current_user
from app.core.services.notification import NotificationService
from app.database import get_db

router = APIRouter()


@router.get("", response_model=PaginatedResponse[NotificationListItem])
async def list_notifications(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    unread_only: bool = False,
    notification_type: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    """
    List notifications for the current user.

    - **unread_only**: Only return unread notifications
    - **notification_type**: Filter by type (alert, reminder, etc.)
    """
    notification_service = NotificationService(db)
    offset = (page - 1) * page_size

    notifications, total = await notification_service.get_user_notifications(
        user_id=current_user.id,
        unread_only=unread_only,
        notification_type=notification_type,
        offset=offset,
        limit=page_size,
    )

    return PaginatedResponse.create(
        items=[
            NotificationListItem(
                id=n.id,
                type=n.type,
                priority=n.priority,
                title=n.title,
                title_tamil=n.title_tamil,
                is_read=n.is_read,
                created_at=n.created_at,
            )
            for n in notifications
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/count", response_model=NotificationCount)
async def get_notification_count(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get notification counts for the current user.

    Returns total, unread, and critical counts.
    """
    notification_service = NotificationService(db)
    return await notification_service.get_notification_count(current_user.id)


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get a specific notification by ID.
    """
    notification_service = NotificationService(db)
    notification = await notification_service.get_by_id(notification_id)

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    if notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return NotificationResponse(
        id=notification.id,
        user_id=notification.user_id,
        type=notification.type,
        priority=notification.priority,
        title=notification.title,
        title_tamil=notification.title_tamil,
        message=notification.message,
        message_tamil=notification.message_tamil,
        entity_type=notification.entity_type,
        entity_id=notification.entity_id,
        action_url=notification.action_url,
        audio_url=notification.audio_url,
        delivered_at=notification.delivered_at,
        read_at=notification.read_at,
        is_read=notification.is_read,
        created_at=notification.created_at,
    )


@router.put("/{notification_id}/read", response_model=MessageResponse)
async def mark_as_read(
    notification_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Mark a notification as read.
    """
    notification_service = NotificationService(db)
    success = await notification_service.mark_as_read(notification_id, current_user.id)

    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")

    return MessageResponse(message="Notification marked as read")


@router.put("/read-all", response_model=MessageResponse)
async def mark_all_as_read(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Mark all notifications as read for the current user.
    """
    notification_service = NotificationService(db)
    count = await notification_service.mark_all_as_read(current_user.id)
    return MessageResponse(message=f"{count} notifications marked as read")


@router.delete("/{notification_id}", response_model=MessageResponse)
async def delete_notification(
    notification_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Delete a notification.
    """
    notification_service = NotificationService(db)
    success = await notification_service.delete(notification_id, current_user.id)

    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")

    return MessageResponse(message="Notification deleted")
