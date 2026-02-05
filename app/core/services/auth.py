"""
Authentication service with PIN-based and password authentication.
"""

from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional
from uuid import UUID

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.core.models.user import User, UserRole
from app.core.schemas.auth import LoginRequest, LoginResponse, TokenData
from app.database import get_db

# HTTP Bearer security scheme
security = HTTPBearer()


class AuthService:
    """Authentication service for PIN and password-based authentication."""

    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def hash_pin(pin: str) -> str:
        """Hash a PIN using bcrypt."""
        return bcrypt.hashpw(pin.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def verify_pin(plain_pin: str, hashed_pin: str) -> bool:
        """Verify a PIN against its hash."""
        return bcrypt.checkpw(plain_pin.encode('utf-8'), hashed_pin.encode('utf-8'))

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
        )
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create a JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    @staticmethod
    def decode_token(token: str) -> TokenData:
        """Decode and validate a JWT token."""
        try:
            payload = jwt.decode(
                token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
            )
            return TokenData(
                user_id=UUID(payload["user_id"]),
                employee_code=payload["employee_code"],
                role=payload["role"],
                department=payload["department"],
                org_id=UUID(payload["org_id"]),
                exp=payload.get("exp"),
            )
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            ) from e

    async def get_user_by_employee_code(self, employee_code: str) -> Optional[User]:
        """Get user by employee code with organization loaded."""
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.organization))
            .where(User.employee_code == employee_code)
        )
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID with organization loaded."""
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.organization))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def authenticate_with_pin(
        self, employee_code: str, pin: str
    ) -> Optional[User]:
        """Authenticate user with employee code and PIN."""
        user = await self.get_user_by_employee_code(employee_code)
        if not user or not user.is_active:
            return None
        if not user.pin_hash or not self.verify_pin(pin, user.pin_hash):
            return None
        return user

    async def authenticate_with_password(
        self, employee_code: str, password: str
    ) -> Optional[User]:
        """Authenticate user with employee code and password (admin users)."""
        user = await self.get_user_by_employee_code(employee_code)
        if not user or not user.is_active:
            return None
        if not user.password_hash or not self.verify_password(password, user.password_hash):
            return None
        return user

    async def login(self, request: LoginRequest) -> LoginResponse:
        """Authenticate user and return tokens."""
        user = None

        # Try PIN authentication first
        if request.pin:
            user = await self.authenticate_with_pin(request.employee_code, request.pin)

        # Try password authentication if PIN not provided or failed
        if not user and request.password:
            user = await self.authenticate_with_password(
                request.employee_code, request.password
            )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        # Create token payload
        token_data = {
            "user_id": str(user.id),
            "employee_code": user.employee_code,
            "role": user.role,
            "department": user.department,
            "org_id": str(user.org_id),
        }

        # Generate tokens
        access_token = self.create_access_token(token_data)
        refresh_token = self.create_refresh_token(token_data)

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.access_token_expire_minutes * 60,
            user_id=user.id,
            employee_code=user.employee_code,
            name=user.name,
            name_tamil=user.name_tamil,
            role=user.role,
            department=user.department,
            org_id=user.org_id,
            org_name=user.organization.name if user.organization else "",
        )

    async def refresh_access_token(self, refresh_token: str) -> tuple[str, int]:
        """Refresh an access token using a refresh token."""
        try:
            payload = jwt.decode(
                refresh_token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
            )

            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type",
                )

            # Verify user still exists and is active
            user = await self.get_user_by_id(UUID(payload["user_id"]))
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found or inactive",
                )

            # Create new access token
            token_data = {
                "user_id": str(user.id),
                "employee_code": user.employee_code,
                "role": user.role,
                "department": user.department,
                "org_id": str(user.org_id),
            }
            access_token = self.create_access_token(token_data)

            return access_token, settings.access_token_expire_minutes * 60

        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            ) from e

    async def change_pin(self, user_id: UUID, current_pin: str, new_pin: str) -> bool:
        """Change user's PIN."""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not user.pin_hash or not self.verify_pin(current_pin, user.pin_hash):
            raise HTTPException(status_code=400, detail="Current PIN is incorrect")

        user.pin_hash = self.hash_pin(new_pin)
        await self.db.commit()
        return True


# Dependency to get current user from token
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """FastAPI dependency to get the current authenticated user."""
    token_data = AuthService.decode_token(credentials.credentials)

    auth_service = AuthService(db)
    user = await auth_service.get_user_by_id(token_data.user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive",
        )

    return user


def require_role(*roles: UserRole):
    """
    FastAPI dependency factory to require specific roles.

    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(user: User = Depends(require_role(UserRole.ADMIN))):
            ...
    """

    async def role_checker(
        current_user: Annotated[User, Depends(get_current_user)]
    ) -> User:
        if current_user.role not in [r.value for r in roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return role_checker
