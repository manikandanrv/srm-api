"""
Attachment model for photos, documents, and other files.
"""

import uuid
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models.base import BaseModel


class AttachmentType(str, Enum):
    """Types of attachments."""

    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"


class Attachment(BaseModel):
    """
    Attachment model for photos and documents.

    Used for:
    - Before/after photos on job cards
    - Task evidence photos
    - Equipment photos
    - Documents and manuals
    """

    __tablename__ = "attachments"

    # Entity reference (polymorphic)
    entity_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # 'farm_task', 'job_card', 'asset', etc.
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    # File info
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default=AttachmentType.IMAGE.value
    )
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Metadata
    caption: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    caption_tamil: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Ordering and categorization
    sequence_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_before: Mapped[Optional[bool]] = mapped_column(
        Boolean, nullable=True
    )  # For before/after photos
    category: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # 'evidence', 'documentation', etc.

    # Creator
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Attachment(id={self.id}, entity_type={self.entity_type}, file_name={self.file_name})>"
