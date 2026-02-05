"""
User service for CRUD operations.
"""

from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.models.user import User
from app.core.schemas.user import UserCreate, UserUpdate
from app.core.services.auth import AuthService


class UserService:
    """User service for CRUD operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.organization))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_employee_code(self, employee_code: str) -> Optional[User]:
        """Get user by employee code."""
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.organization))
            .where(User.employee_code == employee_code)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        org_id: Optional[UUID] = None,
        department: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[User], int]:
        """Get all users with optional filtering."""
        query = select(User).options(selectinload(User.organization))

        # Apply filters
        if org_id:
            query = query.where(User.org_id == org_id)
        if department:
            query = query.where(User.department == department)
        if role:
            query = query.where(User.role == role)
        if is_active is not None:
            query = query.where(User.is_active == is_active)
        if search:
            search_filter = f"%{search}%"
            query = query.where(
                (User.name.ilike(search_filter))
                | (User.employee_code.ilike(search_filter))
                | (User.name_tamil.ilike(search_filter))
            )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination
        query = query.offset(offset).limit(limit).order_by(User.name)
        result = await self.db.execute(query)
        users = list(result.scalars().all())

        return users, total

    async def create(self, data: UserCreate) -> User:
        """Create a new user."""
        # Check if employee code already exists
        existing = await self.get_by_employee_code(data.employee_code)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Employee code '{data.employee_code}' already exists",
            )

        # Hash PIN
        pin_hash = AuthService.hash_pin(data.pin)

        # Hash password if provided
        password_hash = None
        if data.password:
            password_hash = AuthService.hash_password(data.password)

        user = User(
            org_id=data.org_id,
            employee_code=data.employee_code,
            name=data.name,
            name_tamil=data.name_tamil,
            phone=data.phone,
            email=data.email,
            pin_hash=pin_hash,
            password_hash=password_hash,
            role=data.role,
            department=data.department,
            preferred_language=data.preferred_language,
        )

        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update(self, user_id: UUID, data: UserUpdate) -> User:
        """Update an existing user."""
        user = await self.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def delete(self, user_id: UUID) -> bool:
        """Soft delete a user by setting is_active to False."""
        user = await self.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.is_active = False
        await self.db.flush()
        return True

    async def reset_pin(self, user_id: UUID, new_pin: str) -> bool:
        """Reset user's PIN (admin operation)."""
        user = await self.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.pin_hash = AuthService.hash_pin(new_pin)
        await self.db.flush()
        return True

    async def get_users_by_department(
        self, org_id: UUID, department: str
    ) -> list[User]:
        """Get all active users in a department."""
        result = await self.db.execute(
            select(User)
            .where(
                User.org_id == org_id,
                User.department == department,
                User.is_active == True,
            )
            .order_by(User.name)
        )
        return list(result.scalars().all())

    async def get_supervisors(self, org_id: UUID) -> list[User]:
        """Get all supervisors and above in an organization."""
        result = await self.db.execute(
            select(User)
            .where(
                User.org_id == org_id,
                User.role.in_(["supervisor", "manager", "admin"]),
                User.is_active == True,
            )
            .order_by(User.name)
        )
        return list(result.scalars().all())
