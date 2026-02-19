"""
Backtesting service
"""

from typing import Any, Dict, List
from uuid import UUID

import structlog

from backtest.engine.backtest_engine import BacktestEngine
from backtest.strategies.moving_average import MovingAverageStrategy
from backtest.strategies.momentum import MomentumStrategy
from backtest.strategies.mean_reversion import MeanReversionStrategy

logger = structlog.get_logger()


class BacktestService:
    """Backtesting business logic"""
    
    STRATEGIES = {
        "moving_average": MovingAverageStrategy,
        "momentum": MomentumStrategy,
        "mean_reversion": MeanReversionStrategy,
    }
    
    def __init__(self, db_session):
        self.db = db_session
    
    async def run_backtest(
        self,
        strategy_name: str,
        symbols: List[str],
        start_date: str            "hhi": round(hhi, 4),
            "top_5_percent": round(top_5_percent, 2),
        }
