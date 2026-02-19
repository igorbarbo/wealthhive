"""
Asset repository interface
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from core.entities.asset import Asset


class IAssetRepository(ABC):
    """Interface for asset repository"""
    
    @abstractmethod
    async def get_by_id(self, asset_id: UUID) -> Optional[Asset]:
        """Get asset by ID"""
        pass
    
    @abstractmethod
    async def get_by_symbol(self, symbol: str) -> Optional[Asset]:
        """Get asset by symbol"""
        pass
    
    @abstractmethod
    async def create(self, **kwargs) -> Asset:
        """Create new asset"""
        pass
    
    @abstractmethod
    async def update(self, asset_id: UUID, **kwargs) -> Asset:
        """Update asset"""
        pass
    
    @abstractmethod
    async def delete(self, asset_id: UUID) -> None:
        """Delete asset"""
        pass
    
    @abstractmethod
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        asset_type: Optional[str] = None,
    ) -> List[Asset]:
        """Get all assets with optional filtering"""
        pass
    
    @abstractmethod
    async def search(self, query: str) -> List[Asset]:
        """Search assets by symbol or name"""
        pass
