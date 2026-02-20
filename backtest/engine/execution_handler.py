"""
Order execution simulation
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class Signal:
    """Trading signal"""
    symbol: str
    direction: str  # buy, sell
    quantity: float
    order_type: str = "market"  # market, limit
    limit_price: Optional[float] = None


@dataclass
class Fill:
    """Order fill"""
    symbol: str
    direction: str
    quantity: float
    price: float
    commission: float
    timestamp: Any


class ExecutionHandler:
    """Simulate order execution"""
    
    def __init__(self, commission: float = 0.001, slippage: float = 0.0005):
        self.commission = commission
        self.slippage = slippage
    
    def execute(self, signal: Signal, market_data: Dict) -> Optional[Fill]:
        """Execute signal and return fill"""
        # Get current price
        if signal.order_type == "market":
            base_price = market_data.get("close", 0)
            
            # Apply slippage (worse price for buyer)
            if signal.direction == "buy":
                fill_price = base_price * (1 + self.slippage)
            else:
                fill_price = base_price * (1 - self.slippage)
            
            # Calculate commission
            trade_value = fill_price * signal.quantity
            commission = trade_value * self.commission
            
            return Fill(
                symbol=signal.symbol,
                direction=signal.direction,
                quantity=signal.quantity,
                price=fill_price,
                commission=commission,
                timestamp=market_data.get("timestamp"),
            )
        
        elif signal.order_type == "limit":
            # Check if limit price is hit
            # Simplified - would check high/low
            pass
        
        return None
      
