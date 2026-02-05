"""
Audio log model for storing voice recordings and Bhashini transcriptions.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models.base import BaseModel


class AudioLog(BaseModel):
    """
    Audio log model for storing voice recordings and transcriptions.

    Used for:
    - Task voice notes (farm)
    - Job card voice logs (maintenance)
    - Service request voice capture
    - Feedback recordings

    Integrates with Bhashini API for Tamil STT.
    """

    __tablename__ = "audio_logs"

    # User who recorded
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    # Entity reference (polymorphic)
    entity_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # 'farm_task', 'job_card', 'feedback', 'service_request'
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    # Audio file
    audio_url: Mapped[str] = mapped_column(String(500), nullable=False)
    audio_format: Mapped[str] = mapped_column(
        String(20), default="wav", nullable=False
    )  # 'wav', 'mp3', 'ogg'
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Transcription results
    transcript_tamil: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    transcript_english: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[Optional[float]] = mapped_column(nullable=True)

    # Extracted keywords for search/categorization
    keywords: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )  # Extracted keywords and their categories

    # Processing status
    processing_status: Mapped[str] = mapped_column(
        String(50), default="pending", nullable=False
    )  # 'pending', 'processing', 'completed', 'failed'
    processed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    error_message: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    def __repr__(self) -> str:
        return f"<AudioLog(id={self.id}, entity_type={self.entity_type}, status={self.processing_status})>"
