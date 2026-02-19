"""
Order domain entity
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderStatus(Enum):
    PENDING = "pending"
    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass
class Order:
    """Order entity"""
    portfolio_id: UUID
    asset_id: UUID
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    id: UUID = field(default_factory=uuid4)
    price: Optional[Decimal] = None  # For limit orders
    stop_price: Optional[Decimal] = None  # For stop orders
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: Decimal = field(default_factory=lambda: Decimal("0"))
    avg_fill_price: Optional[Decimal] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    executed_at: Optional[datetime] = None
    notes: Optional[str] = None
    
    @property
    def remaining_quantity(self) -> Decimal:
        """Quantity remaining to be filled"""
        return self.quantity - self.filled_quantity
    
    @property
    def is_filled(self) -> bool:
        """Check if order is completely filled"""
        return self.filled_quantity >= self.quantity
    
    def fill(self, quantity: Decimal, price: Decimal) -> None:
        """Record a fill (partial or complete)"""
        if quantity > self.remaining_quantity:
            raise ValueError("Fill quantity exceeds remaining quantity")
        
        # Update average fill price
        total_value = (self.filled_quantity * (self.avg_fill_price or Decimal("0"))) + (quantity * price)
        self.filled_quantity += quantity
        self.avg_fill_price = total_value / self.filled_quantity
        
        # Update status
        if self.is_filled:
            self.status = OrderStatus.FILLED
            self.executed_at = datetime.utcnow()
        else:
            self.status = OrderStatus.PARTIALLY_FILLED
        
        self.updated_at = datetime.utcnow()
    
    def cancel(self) -> None:
        """Cancel the order"""
        if self.status not in [OrderStatus.PENDING, OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]:
            raise ValueError(f"Cannot cancel order with status {self.status}")
        
        self.status = OrderStatus.CANCELLED
        self.updated_at = datetime.utcnow()
    
    def reject(self, reason: str) -> None:
        """Reject the order"""
        self.status = OrderStatus.REJECTED
        self.notes = reason
        self.updated_at = datetime.utcnow()
      
