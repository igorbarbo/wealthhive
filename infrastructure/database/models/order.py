"""
Order SQLAlchemy model
"""

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID

from core.entities.order import OrderSide, OrderStatus, OrderType


class OrderModel:
    """Order database model"""
    __tablename__ = "orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=False, index=True)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=False, index=True)
    
    side = Column(Enum(OrderSide), nullable=False)
    order_type = Column(Enum(OrderType), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False, index=True)
    
    quantity = Column(Numeric(15, 8), nullable=False)
    price = Column(Numeric(15, 4), nullable=True)  # For limit orders
    stop_price = Column(Numeric(15, 4), nullable=True)  # For stop orders
    
    filled_quantity = Column(Numeric(15, 8), default=Decimal("0"), nullable=False)
    avg_fill_price = Column(Numeric(15, 4), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    executed_at = Column(DateTime, nullable=True)
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    portfolio = relationship("PortfolioModel", back_populates="orders")
    asset = relationship("AssetModel")
    
    def to_entity(self):
        """Convert to domain entity"""
        from core.entities.order import Order
        
        return Order(
            id=self.id,
            portfolio_id=self.portfolio_id,
            asset_id=self.asset_id,
            side=self.side,
            order_type=self.order_type,
            status=self.status,
            quantity=self.quantity,
            price=self.price,
            stop_price=self.stop_price,
            filled_quantity=self.filled_quantity,
            avg_fill_price=self.avg_fill_price,
            created_at=self.created_at,
            updated_at=self.updated_at,
            executed_at=self.executed_at,
            notes=self.notes,
        )
