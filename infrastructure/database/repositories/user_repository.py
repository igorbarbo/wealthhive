"""
User repository implementation
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from core.entities.user import User
from core.repositories.user_repository import IUserRepository
from infrastructure.database.models.user import UserModel


class UserRepository(IUserRepository):
    """User repository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user = result.scalar_one_or_none()
        return user.to_entity() if user else None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        user = result.scalar_one_or_none()
        return user.to_entity() if user else None
    
    async def create(self, email: str, password: str, full_name: str) -> User:
        """Create new user"""
        user = UserModel(
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
        )
        self.session.add(user)
        await self.session.flush()
        return user.to_entity()
    
    async def update(self, user_id: UUID, **kwargs) -> User:
        """Update user"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user = result.scalar_one()
        
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        
        await self.session.flush()
        return user.to_entity()
    
    async def delete(self, user_id: UUID) -> None:
        """Delete user"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user = result.scalar_one()
        await self.session.delete(user)
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users"""
        result = await self.session.execute(
            select(UserModel).offset(skip).limit(limit)
        )
        users = result.scalars().all()
        return [u.to_entity() for u in users]
