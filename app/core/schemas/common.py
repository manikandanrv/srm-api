"""
Common Pydantic schemas used across the application.
"""

from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class ErrorResponse(BaseSchema):
    """Standard error response schema."""

    detail: str
    error_code: Optional[str] = None
    field_errors: Optional[dict[str, list[str]]] = None


class MessageResponse(BaseSchema):
    """Simple message response schema."""

    message: str
    success: bool = True


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(
        default=20, ge=1, le=100, description="Number of items per page"
    )
    sort_by: Optional[str] = Field(default=None, description="Field to sort by")
    sort_order: str = Field(
        default="desc", pattern="^(asc|desc)$", description="Sort order"
    )

    @property
    def offset(self) -> int:
        """Calculate offset for database query."""
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseSchema, Generic[T]):
    """Paginated response wrapper for list endpoints."""

    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(
        cls, items: list[T], total: int, page: int, page_size: int
    ) -> "PaginatedResponse[T]":
        """Create a paginated response."""
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )


class IDResponse(BaseSchema):
    """Response with just an ID."""

    id: str


class StatusResponse(BaseSchema):
    """Status update response."""

    id: str
    status: str
    message: Optional[str] = None


class BulkOperationResult(BaseSchema):
    """Result of a bulk operation."""

    success_count: int
    failure_count: int
    errors: list[dict[str, Any]] = []


class TamilText(BaseSchema):
    """Schema for bilingual text (English + Tamil)."""

    text: str
    text_tamil: Optional[str] = None
