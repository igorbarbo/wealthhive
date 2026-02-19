"""
User repository interface
"""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from core.entities.user import User


class IUserRepository(ABC):
    """Interface for user repository"""
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        pass
    
    @abstractmethod
    async def create(self, email: str, password: str, full_name: str) -> User:
        """Create new user"""
        pass
    
    @abstractmethod
    async def update(self, user_id: UUID, **kwargs) -> User:
        """Update user"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> None:
        """Delete user"""
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all users"""
        pass
