"""
Procurement workflow models (PR, PO, GRN).
"""

import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models.base import BaseModel


class PRStatus(str, Enum):
    """Purchase Requisition status."""

    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONVERTED = "converted"  # Converted to PO


class POStatus(str, Enum):
    """Purchase Order status."""

    DRAFT = "draft"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    PARTIAL = "partial"  # Partially received
    RECEIVED = "received"
    CLOSED = "closed"


class GRNStatus(str, Enum):
    """Goods Receipt Note status."""

    PENDING = "pending"
    VERIFIED = "verified"
    DISCREPANCY = "discrepancy"


class PurchaseRequisition(BaseModel):
    """
    Purchase Requisition model.

    Initiates procurement workflow, can be auto-generated for low stock items.
    """

    __tablename__ = "purchase_requisitions"

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )

    # Auto-generated number (PR-2024-0001)
    pr_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # Requester
    requested_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(50), default=PRStatus.DRAFT.value, nullable=False
    )
    priority: Mapped[str] = mapped_column(String(20), default="normal", nullable=False)

    # Dates
    required_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Justification
    justification: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Totals
    total_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)

    # Approval
    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<PurchaseRequisition(pr_number={self.pr_number}, status={self.status})>"


class PurchaseRequisitionItem(BaseModel):
    """Line items for Purchase Requisition."""

    __tablename__ = "purchase_requisition_items"

    pr_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("purchase_requisitions.id"), nullable=False
    )
    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("inventory_items.id"), nullable=False
    )

    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    estimated_unit_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), nullable=True
    )

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class PurchaseOrder(BaseModel):
    """
    Purchase Order model.

    Created from approved PRs, sent to vendors.
    """

    __tablename__ = "purchase_orders"

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )

    # Auto-generated number (PO-2024-0001)
    po_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # Source PR (optional)
    pr_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("purchase_requisitions.id"), nullable=True
    )

    # Vendor
    vendor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=False
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(50), default=POStatus.DRAFT.value, nullable=False
    )

    # Dates
    order_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    expected_delivery: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Delivery location
    delivery_location_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id"), nullable=True
    )

    # Amounts
    subtotal: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    tax_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    total_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)

    terms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Creator
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    def __repr__(self) -> str:
        return f"<PurchaseOrder(po_number={self.po_number}, status={self.status})>"


class PurchaseOrderItem(BaseModel):
    """Line items for Purchase Order."""

    __tablename__ = "purchase_order_items"

    po_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("purchase_orders.id"), nullable=False
    )
    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("inventory_items.id"), nullable=False
    )

    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    received_quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=0, nullable=False
    )

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class GoodsReceipt(BaseModel):
    """
    Goods Receipt Note (GRN) for three-way matching.
    """

    __tablename__ = "goods_receipts"

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )

    # Auto-generated number (GRN-2024-0001)
    grn_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # Source PO
    po_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("purchase_orders.id"), nullable=False
    )

    # Receipt details
    received_date: Mapped[date] = mapped_column(Date, nullable=False)
    received_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id"), nullable=False
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(50), default=GRNStatus.PENDING.value, nullable=False
    )

    # Invoice matching
    invoice_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    invoice_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    invoice_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<GoodsReceipt(grn_number={self.grn_number}, status={self.status})>"


class GoodsReceiptItem(BaseModel):
    """Line items for GRN."""

    __tablename__ = "goods_receipt_items"

    grn_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("goods_receipts.id"), nullable=False
    )
    po_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("purchase_order_items.id"), nullable=False
    )
    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("inventory_items.id"), nullable=False
    )

    ordered_quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    received_quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    accepted_quantity: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    rejected_quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=0, nullable=False
    )

    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    condition: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # 'good', 'damaged', 'expired'
