"""
Portfolio tracking during backtest
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Position:
    """Backtest position"""
    symbol: str
    quantity: float
    avg_price: float


@dataclass
class Trade:
    """Completed trade"""
    symbol: str
    entry_date: Any
    exit_date: Any
    entry_price: float
    exit_price: float
    quantity: float
    pnl: float


class PortfolioHandler:
    """Track portfolio during backtest"""
    
    def __init__(self, initial_capital: float):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.equity_curve: List[float] = [initial_capital]
        self.current_equity = initial_capital
    
    def update(self, fill):
        """Update portfolio with fill"""
        symbol = fill.symbol
        
        if fill.direction == "buy":
            # Update or create position
            if symbol in self.positions:
                pos = self.positions[symbol]
                total_cost = pos.quantity * pos.avg_price + fill.quantity * fill.price
                total_qty = pos.quantity + fill.quantity
                pos.avg_price = total_cost / total_qty
                pos.quantity = total_qty
            else:
                self.positions[symbol] = Position(
                    symbol=symbol,
                    quantity=fill.quantity,
                    avg_price=fill.price,
                )
            
            # Deduct cash
            self.cash -= (fill.price * fill.quantity + fill.commission)
        
        else:  # sell
            if symbol in self.positions:
                pos = self.positions[symbol]
                
                # Record trade
                if pos.quantity == fill.quantity:
                    # Complete exit
                    pnl = (fill.price - pos.avg_price) * fill.quantity - fill.commission
                    self.trades.append(Trade(
                        symbol=symbol,
                        entry_date=None,  # Would track
                        exit_date=fill.timestamp,
                        entry_price=pos.avg_price,
                        exit_price=fill.price,
                        quantity=fill.quantity,
                        pnl=pnl,
                    ))
                    del self.positions[symbol]
                else:
                    # Partial exit
                    pos.quantity -= fill.quantity
                
                # Add cash
                self.cash += (fill.price * fill.quantity - fill.commission)
    
    def mark_to_market(self, timestamp, market_data):
        """Update portfolio value with current prices"""
        position_value = 0
        
        for symbol, position in self.positions.items():
            current_price = market_data.get((symbol, "close"), position.avg_price)
            position_value += position.quantity * current_price
        
        self.current_equity = self.cash + position_value
        self.equity_curve.append(self.current_equity)
