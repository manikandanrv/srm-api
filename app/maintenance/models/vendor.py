"""
Vendor management model.
"""

import uuid
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models.base import BaseModel


class Vendor(BaseModel):
    """
    Supplier/vendor management.

    Tracks vendors for procurement with rating and category info.
    """

    __tablename__ = "vendors"

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )

    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Contact info
    contact_person: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Tax info
    gst_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    pan_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Categories they supply
    categories: Mapped[Optional[list]] = mapped_column(
        JSONB, nullable=True
    )  # ['plumbing', 'electrical']

    # Terms and rating
    payment_terms: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    rating: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<Vendor(code={self.code}, name={self.name})>"
