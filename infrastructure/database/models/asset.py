"""
Asset SQLAlchemy model
"""

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import Column, DateTime, Numeric, String
from sqlalchemy.dialects.postgresql import UUID

from infrastructure.database.connection import AsyncDatabaseManager


class AssetModel:
    """Asset database model"""
    __tablename__ = "assets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    symbol = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    asset_type = Column(String(50), nullable=False, index=True)  # stock, etf, crypto, etc.
    exchange = Column(String(50), nullable=True)
    currency = Column(String(3), default="BRL", nullable=False)
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    country = Column(String(2), default="BR", nullable=False)
    market_cap = Column(Numeric(20, 2), nullable=True)
    
    # Fundamental data
    pe_ratio = Column(Numeric(10, 2), nullable=True)
    pb_ratio = Column(Numeric(10, 2), nullable=True)
    dividend_yield = Column(Numeric(5, 4), nullable=True)
    eps = Column(Numeric(10, 2), nullable=True)
    
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_entity(self):
        """Convert to domain entity"""
        from core.entities.asset import Asset
        
        return Asset(
            id=self.id,
            symbol=self.symbol,
            name=self.name,
            asset_type=self.asset_type,
            exchange=self.exchange,
            currency=self.currency,
            sector=self.sector,
            industry=self.industry,
            country=self.country,
            market_cap=self.market_cap,
            pe_ratio=float(self.pe_ratio) if self.pe_ratio else None,
            pb_ratio=float(self.pb_ratio) if self.pb_ratio else None,
            dividend_yield=float(self.dividend_yield) if self.dividend_yield else None,
            eps=float(self.eps) if self.eps else None,
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
