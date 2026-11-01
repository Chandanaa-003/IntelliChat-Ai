from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin
from app.core.security import get_password_hash, verify_password


class AuthService:
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Fetch user by email address."""
        stmt = select(User).where(User.email == email.lower().strip())
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
        """Fetch user by primary key ID."""
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def register_user(db: AsyncSession, user_in: UserRegister) -> User:
        """Register a new user with hashed password."""
        existing = await AuthService.get_by_email(db, user_in.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email address already exists.",
            )

        hashed_password = get_password_hash(user_in.password)
        new_user = User(
            email=user_in.email.lower().strip(),
            username=user_in.username.strip(),
            hashed_password=hashed_password,
            is_active=True,
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user

    @staticmethod
    async def authenticate_user(db: AsyncSession, credentials: UserLogin) -> User:
        """Authenticate user credentials and return user model."""
        user = await AuthService.get_by_email(db, credentials.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive.",
            )

        return user
