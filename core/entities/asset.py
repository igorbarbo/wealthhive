"""
Asset domain entity
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class Asset:
    """Asset entity (stock, ETF, crypto, etc.)"""
    symbol: str
    name: str
    asset_type: str  # stock, etf, crypto, forex, commodity
    id: UUID = field(default_factory=uuid4)
    exchange: Optional[str] = None
    currency: str = "BRL"
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: str = "BR"
    market_cap: Optional[Decimal] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    # Fundamental data
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    eps: Optional[float] = None
    
    def update_price_data(
        self,
        current_price: Decimal,
        volume: int,
    ) -> None:
        """Update real-time price data"""
        self.updated_at = datetime.utcnow()
        # Would update price history
    
    def update_fundamentals(
        self,
        pe_ratio: Optional[float] = None,
        pb_ratio: Optional[float] = None,
        dividend_yield: Optional[float] = None,
    ) -> None:
        """Update fundamental metrics"""
        if pe_ratio is not None:
            self.pe_ratio = pe_ratio
        if pb_ratio is not None:
            self.pb_ratio = pb_ratio
        if dividend_yield is not None:
            self.dividend_yield = dividend_yield
        self.updated_at = datetime.utcnow()
    
    def deactivate(self) -> None:
        """Deactivate asset (delisted, etc.)"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
