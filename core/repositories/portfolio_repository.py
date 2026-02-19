"""
Portfolio repository interface
"""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from core.entities.portfolio import Portfolio


class IPortfolioRepository(ABC):
    """Interface for portfolio repository"""
    
    @abstractmethod
    async def get_by_id(self, portfolio_id: UUID) -> Optional[Portfolio]:
        """Get portfolio by ID"""
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> List[Portfolio]:
        """Get all portfolios for a user"""
        pass
    
    @abstractmethod
    async def create(
        self,
        user_id: UUID,
        name: str,
        description: Optional[str],
        initial_balance: Decimal,
    ) -> Portfolio:
        """Create new portfolio"""
        pass
    
    @abstractmethod
    async def update(self, portfolio_id: UUID, **kwargs) -> Portfolio:
        """Update portfolio"""
        pass
    
    @abstractmethod
    async def delete(self, portfolio_id: UUID) -> None:
        """Delete portfolio"""
        pass
    
    @abstractmethod
    async def add_position(
        self,
        portfolio_id: UUID,
        asset_id: UUID,
        quantity: Decimal,
        price: Decimal,
    ) -> None:
        """Add position to portfolio"""
        pass
    
    @abstractmethod
    async def update_value(
        self,
        portfolio_id: UUID,
        total_value: Decimal,
        total_return: Decimal,
        total_return_percent: float,
    ) -> None:
        """Update portfolio value metrics"""
        pass
