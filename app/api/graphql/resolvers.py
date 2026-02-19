"""
GraphQL Resolvers
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.graphql.schema import Asset, BacktestResult, Portfolio, User
from infrastructure.database.repositories.asset_repository import AssetRepository
from infrastructure.database.repositories.portfolio_repository import PortfolioRepository
from infrastructure.database.repositories.user_repository import UserRepository


class UserResolver:
    """User resolvers"""
    
    @staticmethod
    async def get_me(db: AsyncSession, user_id: UUID) -> Optional[User]:
        repo = UserRepository(db)
        user = await repo.get_by_id(user_id)
        if not user:
            return None
        
        return User(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
        )


class AssetResolver:
    """Asset resolvers"""
    
    @staticmethod
    async def get_all(db: AsyncSession, search: Optional[str] = None) -> List[Asset]:
        repo = AssetRepository(db)
        assets = await repo.get_all(search=search)
        
        return [
            Asset(
                id=a.id,
                symbol=a.symbol,
                name=a.name,
                asset_type=a.asset_type,
                exchange=a.exchange,
                currency=a.currency,
                sector=a.sector,
                industry=a.industry,
                current_price=None,  # Would fetch from cache/real-time
            )
            for a in assets
        ]
    
    @staticmethod
    async def get_by_id(db: AsyncSession, asset_id: UUID) -> Optional[Asset]:
        repo = AssetRepository(db)
        a = await repo.get_by_id(asset_id)
        if not a:
            return None
        
        return Asset(
            id=a.id,
            symbol=a.symbol,
            name=a.name,
            asset_type=a.asset_type,
            exchange=a.exchange,
            currency=a.currency,
            sector=a.sector,
            industry=a.industry,
            current_price=None,
        )


class PortfolioResolver:
    """Portfolio resolvers"""
    
    @staticmethod
    async def get_all(db: AsyncSession, user_id: UUID) -> List[Portfolio]:
        repo = PortfolioRepository(db)
        portfolios = await repo.get_by_user_id(user_id)
        
        return [
            Portfolio(
                id=p.id,
                name=p.name,
                description=p.description,
                total_value=p.total_value or 0.0,
                total_return=p.total_return or 0.0,
                total_return_percent=p.total_return_percent or 0.0,
                positions=[],  # Would fetch separately
            )
            for p in portfolios
        ]
