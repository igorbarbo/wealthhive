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
        start_date: str,
        end_date: str,
        initial_capital: float,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Run backtest with specified strategy"""
        if strategy_name not in self.STRATEGIES:
            raise ValueError(f"Unknown strategy: {strategy_name}")
        
        strategy_class = self.STRATEGIES[strategy_name]
        strategy = strategy_class(**parameters)
        
        engine = BacktestEngine(
            strategy=strategy,
            initial_capital=initial_capital,
            start_date=start_date,
            end_date=end_date,
        )
        
        logger.info(
            "Starting backtest",
            strategy=strategy_name,
            symbols=symbols,
            start=start_date,
            end=end_date,
        )
        
        result = await engine.run(symbols)
        
        logger.info(
            "Backtest completed",
            total_return=result["total_return"],
            sharpe=result["sharpe_ratio"],
        )
        
        return result
    
    async def optimize_strategy(
        self,
        strategy_name: str,
        symbols: List[str],
        start_date: str,
        end_date: str,
        param_grid: Dict[str, List[Any]],
    ) -> Dict[str, Any]:
        """Run grid search optimization"""
        from backtest.optimization.grid_search import GridSearchOptimizer
        
        optimizer = GridSearchOptimizer(
            strategy_class=self.STRATEGIES[strategy_name],
            param_grid=param_grid,
        )
        
        best_params, results = await optimizer.optimize(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
        )
        
        return {
            "best_parameters": best_params,
            "best_sharpe": max(r["sharpe_ratio"] for r in results),
            "all_results": results[:10],  # Top 10
        }
    
    async def walk_forward_analysis(
        self,
        strategy_name: str,
        symbols: List[str],
        startIES[strategy_name],
            param_grid=param_grid,
        )
        
        best_params, results = await optimizer.optimize(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
        )
        
        return {
            "best_parameters": best_params,
            "best_sharpe": max(r["sharpe_ratio"] for r in results),
            "all_results": results[:10],  # Top 10
        }
    
    async def walk_forward_analysis(
        self,
        strategy_name: str,
        symbols: List[str],
        start_date: str,
        end_date: str,
        train_size: int = 252,
        test_size: int = 63,
    ) -> Dict[str, Any]:
        """Run walk-forward optimization"""
        from backtest.optimization.walk_forward import WalkForwardOptimizer
        
        optimizer = WalkForwardOptimizer(
            strategy_class=self.STRATEGIES[strategy_name],
            train_size=train_size,
            test_size=test_size,
        )
        
        results = await optimizer.run(
            symbols=symbols,
            start_date=start_date,
            end=test_size,
        )
        
        results = await optimizer.run(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
        )
        
        return {
            "periods": len(results),
            "avg_train_return": sum(r["train_return"] for r in results) / len(results),
            "avg_test_return": sum(r["test_return"] for r in results) / len(results),
            "results": results,
        }
        
