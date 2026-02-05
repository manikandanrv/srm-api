"""
Inventory management models.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models.base import BaseModel


class InventoryCategory(str, Enum):
    """Inventory item categories."""

    PLUMBING = "plumbing"
    ELECTRICAL = "electrical"
    HARDWARE = "hardware"
    TOOLS = "tools"
    CHEMICALS = "chemicals"


class InventoryItem(BaseModel):
    """
    Master inventory catalog.

    Defines all parts and consumables that can be stocked and used.
    """

    __tablename__ = "inventory_items"

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )

    # Identity
    sku: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    name_tamil: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Classification
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    subcategory: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Units
    unit: Mapped[str] = mapped_column(String(20), nullable=False)  # 'piece', 'roll', 'meter', 'kg'
    unit_tamil: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Stocking levels
    criticality: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)
    min_stock_level: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    max_stock_level: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    reorder_point: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    reorder_quantity: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    lead_time_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Pricing
    unit_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)

    # Tracking options
    is_serialized: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<InventoryItem(sku={self.sku}, name={self.name})>"


class StockLevel(BaseModel):
    """
    Per-location inventory levels.

    Tracks quantity of each item at each storage location.
    """

    __tablename__ = "stock_levels"

    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("inventory_items.id"), nullable=False
    )
    location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id"), nullable=False
    )

    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    last_counted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def __repr__(self) -> str:
        return f"<StockLevel(item_id={self.item_id}, qty={self.quantity})>"


class TransactionType(str, Enum):
    """Types of inventory transactions."""

    RECEIPT = "receipt"  # Stock received
    ISSUE = "issue"  # Stock issued to job
    TRANSFER = "transfer"  # Between locations
    ADJUSTMENT = "adjustment"  # Inventory adjustment
    RETURN = "return"  # Returned from job


class InventoryTransaction(BaseModel):
    """
    Audit trail for all inventory movements.

    Every stock change is recorded for traceability.
    """

    __tablename__ = "inventory_transactions"

    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("inventory_items.id"), nullable=False
    )
    location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id"), nullable=False
    )

    transaction_type: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )  # Positive for in, negative for out

    # Reference to source document
    reference_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # 'job_card', 'purchase_order', 'transfer'
    reference_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    unit_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)

    performed_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<InventoryTransaction(item_id={self.item_id}, type={self.transaction_type}, qty={self.quantity})>"
