"""
Portfolio repository implementation
"""

from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.entities.portfolio import Portfolio
from core.repositories.portfolio_repository import IPortfolioRepository
from infrastructure.database.models.portfolio import PortfolioModel, PositionModel


class PortfolioRepository(IPortfolioRepository):
    """Portfolio repository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, portfolio_id: UUID) -> Optional[Portfolio]:
        """Get portfolio by ID with positions"""
        result = await self.session.execute(
            select(PortfolioModel)
            .where(PortfolioModel.id == portfolio_id)
        )
        portfolio = result.scalar_one_or_none()
        
        if not portfolio:
            return None
        
        entity = portfolio.to_entity()
        
        # Load positions
        positions_result = await self.session.execute(
            select(PositionModel)
            .where(PositionModel.portfolio_id == portfolio_id)
        )
        positions = positions_result.scalars().all()
        
        # Convert positions to entities (would need asset entities too)
        # entity.positions = {p.asset_id: p.to_entity() for p in positions}
        
        return entity
    
    async def get_by_user_id(self, user_id: UUID) -> List[Portfolio]:
        """Get all portfolios for a user"""
        result = await self.session.execute(
            select(PortfolioModel)
            .where(PortfolioModel.user_id == user_id)
            .order_by(PortfolioModel.created_at.desc())
        )
        portfolios = result.scalars().all()
        return [p.to_entity() for p in portfolios]
    
    async def create(
        self,
        user_id: UUID,
        name: str,
        description: Optional[str],
        initial_balance: Decimal,
    ) -> Portfolio:
        """Create new portfolio"""
        portfolio = PortfolioModel(
            user_id=user_id,
            name=name,
            description=description,
            initial_balance=initial_balance,
        )
        self.session.add(portfolio)
        await self.session.flush()
        return portfolio.to_entity()
    
    async def update(self, portfolio_id: UUID, **kwargs) -> Portfolio:
        """Update portfolio"""
        result = await self.session.execute(
            select(PortfolioModel).where(PortfolioModel.id == portfolio_id)
        )
        portfolio = result.scalar_one()
        
        for key, value in kwargs.items():
            if hasattr(portfolio, key) and value is not None:
                setattr(portfolio, key, value)
        
        await self.session.flush()
        return portfolio.to_entity()
    
    async def delete(self, portfolio_id: UUID) -> None:
        """Delete portfolio"""
        result = await self.session.execute(
            select(PortfolioModel).where(PortfolioModel.id == portfolio_id)
        )
        portfolio = result.scalar_one()
        await self.session.delete(portfolio)
    
    async def add_position(
        self,
        portfolio_id: UUID,
        asset_id: UUID,
        quantity: Decimal,
        price: Decimal,
    ) -> None:
        """Add or update position"""
        # Check if position exists
        result = await self.session.execute(
            select(PositionModel).where(
                PositionModel.portfolio_id == portfolio_id,
                PositionModel.asset_id == asset_id,
            )
        )
        position = result.scalar_one_or_none()
        
        if position:
            # Update existing position (average price)
            total_cost = (position.quantity * position.avg_price) + (quantity * price)
            total_qty = position.quantity + quantity
            position.quantity = total_qty
            position.avg_price = total_cost / total_qty
        else:
            # Create new position
            position = PositionModel(
                portfolio_id=portfolio_id,
                asset_id=asset_id,
                quantity=quantity,
                avg_price=price,
            )
            self.session.add(position)
        
        await self.session.flush()
    
    async def update_value(
        self,
        portfolio_id: UUID,
        total_value: Decimal,
        total_return: Decimal,
        total_return_percent: float,
    ) -> None:
        """Update portfolio value metrics"""
        result = await self.session.execute(
            select(PortfolioModel).where(PortfolioModel.id == portfolio_id)
        )
        portfolio = result.scalar_one()
        
        portfolio.total_value = total_value
        portfolio.total_return = total_return
        portfolio.total_return_percent = Decimal(str(total_return_percent))
        
        await self.session.flush()
      
