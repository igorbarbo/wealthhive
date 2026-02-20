"""
Portfolio SQLAlchemy model
"""

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from infrastructure.database.connection import AsyncDatabaseManager


class PortfolioModel:
    """Portfolio database model"""
    __tablename__ = "portfolios"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    initial_balance = Column(Numeric(15, 2), default=Decimal("0"), nullable=False)
    currency = Column(String(3), default="BRL", nullable=False)
    
    # Computed fields (updated periodically)
    total_value = Column(Numeric(15, 2), nullable=True)
    total_return = Column(Numeric(15, 2), nullable=True)
    total_return_percent = Column(Numeric(7, 4), nullable=True)  # Decimal percentage
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("UserModel", back_populates="portfolios")
    positions = relationship("PositionModel", back_populates="portfolio", cascade="all, delete-orphan")
    orders = relationship("OrderModel", back_populates="portfolio", cascade="all, delete-orphan")
    
    def to_entity(self):
        """Convert to domain entity"""
        from core.entities.portfolio import Portfolio
        
        return Portfolio(
            id=self.id,
            user_id=self.user_id,
            name=self.name,
            description=self.description,
            initial_balance=self.initial_balance,
            currency=self.currency,
            total_value=self.total_value,
            total_return=self.total_return,
            total_return_percent=float(self.total_return_percent) if self.total_return_percent else None,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class PositionModel:
    """Position database model"""
    __tablename__ = "positions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=False, index=True)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=False, index=True)
    quantity = Column(Numeric(15, 8), nullable=False)
    avg_price = Column(Numeric(15, 4), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    portfolio = relationship("PortfolioModel", back_populates="positions")
    asset = relationship("AssetModel")
    
    def to_entity(self, asset_entity=None):
        """Convert to domain entity"""
        from core.entities.portfolio import Position
        
        return Position(
            id=self.id,
            asset=asset_entity,
            quantity=self.quantity,
            avg_price=self.avg_price,
            opened_at=self.created_at,
            updated_at=self.updated_at,
        )
