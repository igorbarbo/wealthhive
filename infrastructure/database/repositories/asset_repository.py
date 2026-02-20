"""
Asset repository implementation
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.entities.asset import Asset
from core.repositories.asset_repository import IAssetRepository
from infrastructure.database.models.asset import AssetModel


class AssetRepository(IAssetRepository):
    """Asset repository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, asset_id: UUID) -> Optional[Asset]:
        """Get asset by ID"""
        result = await self.session.execute(
            select(AssetModel).where(AssetModel.id == asset_id)
        )
        asset = result.scalar_one_or_none()
        return asset.to_entity() if asset else None
    
    async def get_by_symbol(self, symbol: str) -> Optional[Asset]:
        """Get asset by symbol"""
        result = await self.session.execute(
            select(AssetModel).where(AssetModel.symbol == symbol.upper())
        )
        asset = result.scalar_one_or_none()
        return asset.to_entity() if asset else None
    
    async def create(self, **kwargs) -> Asset:
        """Create new asset"""
        asset = AssetModel(**kwargs)
        self.session.add(asset)
        await self.session.flush()
        return asset.to_entity()
    
    async def update(self, asset_id: UUID, **kwargs) -> Asset:
        """Update asset"""
        result = await self.session.execute(
            select(AssetModel).where(AssetModel.id == asset_id)
        )
        asset = result.scalar_one()
        
        for key, value in kwargs.items():
            if hasattr(asset, key) and value is not None:
                setattr(asset, key, value)
        
        await self.session.flush()
        return asset.to_entity()
    
    async def delete(self, asset_id: UUID) -> None:
        """Delete asset"""
        result = await self.session.execute(
            select(AssetModel).where(AssetModel.id == asset_id)
        )
        asset = result.scalar_one()
        await self.session.delete(asset)
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        asset_type: Optional[str] = None,
    ) -> List[Asset]:
        """Get all assets with filtering"""
        query = select(AssetModel)
        
        if asset_type:
            query = query.where(AssetModel.asset_type == asset_type)
        
        if search:
            query = query.where(
                or_(
                    AssetModel.symbol.ilike(f"%{search}%"),
                    AssetModel.name.ilike(f"%{search}%"),
                )
            )
        
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        assets = result.scalars().all()
        return [a.to_entity() for a in assets]
    
    async def search(self, query_str: str) -> List[Asset]:
        """Search assets"""
        result = await self.session.execute(
            select(AssetModel).where(
                or_(
                    AssetModel.symbol.ilike(f"%{query_str}%"),
                    AssetModel.name.ilike(f"%{query_str}%"),
                )
            ).limit(20)
        )
        assets = result.scalars().all()
        return [a.to_entity() for a in assets]
      
