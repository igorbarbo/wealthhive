"""
Portfolio domain entity
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from core.entities.asset import Asset


@dataclass
class Position:
    """Position within a portfolio"""
    asset: Asset
    quantity: Decimal
    avg_price: Decimal
    id: UUID = field(default_factory=uuid4)
    opened_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def cost_basis(self) -> Decimal:
        """Total cost of position"""
        return self.quantity * self.avg_price
    
    def add_shares(self, quantity: Decimal, price: Decimal) -> None:
        """Add shares to position (average down/up)"""
        total_cost = self.cost_basis + (quantity * price)
        total_shares = self.quantity + quantity
        self.avg_price = total_cost / total_shares
        self.quantity = total_shares
        self.updated_at = datetime.utcnow()
    
    def remove_shares(self, quantity: Decimal) -> Decimal:
        """Remove shares from position, return realized P&L"""
        if quantity > self.quantity:
            raise ValueError("Cannot sell more shares than owned")
        
        realized_value = quantity * self.avg_price  # Simplified
        self.quantity -= quantity
        self.updated_at = datetime.utcnow()
        return realized_value


@dataclass
class Portfolio:
    """Portfolio entity"""
    user_id: UUID
    name: str
    id: UUID = field(default_factory=uuid4)
    description: Optional[str] = None
    initial_balance: Decimal = field(default_factory=lambda: Decimal("0"))
    currency: str = "BRL"
    positions: Dict[UUID, Position] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    # Computed fields (updated by service)
    total_value: Optional[Decimal] = None
    total_return: Optional[Decimal] = None
    total_return_percent: Optional[float] = None
    
    def add_position(self, asset: Asset, quantity: Decimal, price: Decimal) -> Position:
        """Add or update position"""
        if asset.id in self.positions:
            self.positions[asset.id].add_shares(quantity, price)
        else:
            self.positions[asset.id] = Position(
                asset=asset,
                quantity=quantity,
                avg_price=price,
            )
        
        self.updated_at = datetime.utcnow()
        return self.positions[asset.id]
    
    def remove_position(self, asset_id: UUID, quantity: Decimal) -> Decimal:
        """Reduce or close position"""
        if asset_id not in self.positions:
            raise ValueError("Position not found")
        
        realized = self.positions[asset_id].remove_shares(quantity)
        
        if self.positions[asset_id].quantity == 0:
            del self.positions[asset_id]
        
        self.updated_at = datetime.utcnow()
        return realized
    
    def calculate_allocation(self) -> Dict[UUID, float]:
        """Calculate current allocation percentages"""
        if not self.total_value or self.total_value == 0:
            return {}
        
        return {
            asset_id: float(pos.cost_basis / self.total_value)
            for asset_id, pos in self.positions.items()
        }
    
    def get_sector_allocation(self) -> Dict[str, float]:
        """Get allocation by sector"""
        sector_values: Dict[str, Decimal] = {}
        
        for pos in self.positions.values():
            sector = pos.asset.sector or "Unknown"
            if sector not in sector_values:
                sector_values[sector] = Decimal("0")
            sector_values[sector] += pos.cost_basis
        
        total = sum(sector_values.values())
        if total == 0:
            return {}
        
        return {
            sector: float(value / total)
            for sector, value in sector_values.items()
        }
