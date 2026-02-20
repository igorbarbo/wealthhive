"""
Backtest SQLAlchemy model
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, JSON, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID


class BacktestModel:
    """Backtest database model"""
    __tablename__ = "backtests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=True)
    
    strategy_name = Column(String(100), nullable=False)
    start_date = Column(String(10), nullable=False)  # YYYY-MM-DD
    end_date = Column(String(10), nullable=False)
    initial_capital = Column(Numeric(15, 2), nullable=False)
    parameters = Column(JSON, default=dict, nullable=False)
    
    # Results
    final_capital = Column(Numeric(15, 2), nullable=True)
    total_return = Column(Numeric(15, 2), nullable=True)
    total_return_percent = Column(Numeric(10, 4), nullable=True)
    sharpe_ratio = Column(Numeric(10, 4), nullable=True)
    sortino_ratio = Column(Numeric(10, 4), nullable=True)
    max_drawdown = Column(Numeric(10, 4), nullable=True)
    calmar_ratio = Column(Numeric(10, 4), nullable=True)
    win_rate = Column(Numeric(5, 4), nullable=True)
    profit_factor = Column(Numeric(10, 4), nullable=True)
    
    # Detailed data
    trades = Column(JSON, default=list, nullable=True)  # List of trades
    equity_curve = Column(JSON, default=list, nullable=True)  # Daily equity values
    
    status = Column(String(20), default="pending", nullable=False)  # pending, running, completed, failed
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
  
