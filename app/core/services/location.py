"""
Location service for hierarchical location management.
"""

from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.models.location import Location
from app.core.schemas.location import LocationCreate, LocationTree, LocationUpdate


class LocationService:
    """Location service for hierarchical location CRUD operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, location_id: UUID) -> Optional[Location]:
        """Get location by ID with children loaded."""
        result = await self.db.execute(
            select(Location)
            .options(selectinload(Location.children))
            .where(Location.id == location_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, org_id: UUID, code: str) -> Optional[Location]:
        """Get location by organization and code."""
        result = await self.db.execute(
            select(Location).where(
                Location.org_id == org_id,
                Location.code == code,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_qr_code(self, qr_code: str) -> Optional[Location]:
        """Get location by QR code."""
        result = await self.db.execute(
            select(Location)
            .options(selectinload(Location.children))
            .where(Location.qr_code == qr_code)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        org_id: UUID,
        parent_id: Optional[UUID] = None,
        location_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[Location], int]:
        """Get all locations with optional filtering."""
        query = select(Location).where(Location.org_id == org_id)

        # Apply filters
        if parent_id:
            query = query.where(Location.parent_id == parent_id)
        elif parent_id is None and location_type is None:
            # By default, get root locations (no parent)
            query = query.where(Location.parent_id.is_(None))

        if location_type:
            query = query.where(Location.type == location_type)
        if is_active is not None:
            query = query.where(Location.is_active == is_active)
        if search:
            search_filter = f"%{search}%"
            query = query.where(
                (Location.name.ilike(search_filter))
                | (Location.code.ilike(search_filter))
                | (Location.name_tamil.ilike(search_filter))
            )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = query.offset(offset).limit(limit).order_by(Location.code)
        result = await self.db.execute(query)
        locations = list(result.scalars().all())

        return locations, total

    async def get_tree(self, org_id: UUID, root_id: Optional[UUID] = None) -> list[LocationTree]:
        """Get location tree structure."""
        # Get root locations or start from specified root
        if root_id:
            root_location = await self.get_by_id(root_id)
            if not root_location:
                return []
            roots = [root_location]
        else:
            result = await self.db.execute(
                select(Location)
                .options(selectinload(Location.children))
                .where(
                    Location.org_id == org_id,
                    Location.parent_id.is_(None),
                    Location.is_active == True,
                )
                .order_by(Location.code)
            )
            roots = list(result.scalars().all())

        async def build_tree(location: Location) -> LocationTree:
            """Recursively build tree structure."""
            # Fetch children if not already loaded
            if not location.children:
                result = await self.db.execute(
                    select(Location)
                    .options(selectinload(Location.children))
                    .where(
                        Location.parent_id == location.id,
                        Location.is_active == True,
                    )
                    .order_by(Location.code)
                )
                children = list(result.scalars().all())
            else:
                children = [c for c in location.children if c.is_active]

            child_trees = []
            for child in children:
                child_tree = await build_tree(child)
                child_trees.append(child_tree)

            return LocationTree(
                id=location.id,
                code=location.code,
                name=location.name,
                name_tamil=location.name_tamil,
                type=location.type,
                children=child_trees,
            )

        return [await build_tree(root) for root in roots]

    async def get_parent_path(self, location_id: UUID) -> list[Location]:
        """Get the path from root to the specified location."""
        path = []
        current = await self.get_by_id(location_id)

        while current:
            path.insert(0, current)
            if current.parent_id:
                result = await self.db.execute(
                    select(Location).where(Location.id == current.parent_id)
                )
                current = result.scalar_one_or_none()
            else:
                break

        return path

    async def create(self, data: LocationCreate) -> Location:
        """Create a new location."""
        # Check if code already exists in org
        existing = await self.get_by_code(data.org_id, data.code)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Location code '{data.code}' already exists in this organization",
            )

        # Verify parent exists if specified
        if data.parent_id:
            parent = await self.get_by_id(data.parent_id)
            if not parent:
                raise HTTPException(status_code=404, detail="Parent location not found")
            if parent.org_id != data.org_id:
                raise HTTPException(
                    status_code=400,
                    detail="Parent location belongs to different organization",
                )

        # Check QR code uniqueness
        if data.qr_code:
            existing_qr = await self.get_by_qr_code(data.qr_code)
            if existing_qr:
                raise HTTPException(
                    status_code=400,
                    detail=f"QR code '{data.qr_code}' already exists",
                )

        location = Location(
            org_id=data.org_id,
            parent_id=data.parent_id,
            code=data.code,
            name=data.name,
            name_tamil=data.name_tamil,
            type=data.type,
            qr_code=data.qr_code,
            coordinates=data.coordinates,
            area_sqm=data.area_sqm,
            address=data.address,
            description=data.description,
            description_tamil=data.description_tamil,
            metadata=data.metadata or {},
        )

        self.db.add(location)
        await self.db.flush()
        await self.db.refresh(location)
        return location

    async def update(self, location_id: UUID, data: LocationUpdate) -> Location:
        """Update a location."""
        location = await self.get_by_id(location_id)
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")

        # Check QR code uniqueness if changing
        if data.qr_code and data.qr_code != location.qr_code:
            existing_qr = await self.get_by_qr_code(data.qr_code)
            if existing_qr:
                raise HTTPException(
                    status_code=400,
                    detail=f"QR code '{data.qr_code}' already exists",
                )

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(location, field, value)

        await self.db.flush()
        await self.db.refresh(location)
        return location

    async def delete(self, location_id: UUID) -> bool:
        """Soft delete a location."""
        location = await self.get_by_id(location_id)
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")

        # Check if location has active children
        result = await self.db.execute(
            select(func.count()).where(
                Location.parent_id == location_id,
                Location.is_active == True,
            )
        )
        child_count = result.scalar() or 0
        if child_count > 0:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete location with active children",
            )

        location.is_active = False
        await self.db.flush()
        return True

    async def get_guest_houses(self, org_id: UUID) -> list[Location]:
        """Get all guest houses in an organization."""
        result = await self.db.execute(
            select(Location)
            .where(
                Location.org_id == org_id,
                Location.type == "guest_house",
                Location.is_active == True,
            )
            .order_by(Location.code)
        )
        return list(result.scalars().all())

    async def get_rooms_by_guest_house(self, guest_house_id: UUID) -> list[Location]:
        """Get all rooms in a guest house."""
        result = await self.db.execute(
            select(Location)
            .where(
                Location.parent_id == guest_house_id,
                Location.type == "room",
                Location.is_active == True,
            )
            .order_by(Location.code)
        )
        return list(result.scalars().all())

    async def get_fields(self, org_id: UUID) -> list[Location]:
        """Get all fields for farm module."""
        result = await self.db.execute(
            select(Location)
            .where(
                Location.org_id == org_id,
                Location.type.in_(["field", "block"]),
                Location.is_active == True,
            )
            .order_by(Location.code)
        )
        return list(result.scalars().all())
