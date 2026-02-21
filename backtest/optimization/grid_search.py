"""
Grid search optimization
"""

from itertools import product
from typing import Any, Dict, List

import numpy as np


class GridSearchOptimizer:
    """Grid search for strategy parameters"""
    
    def __init__(
        self,
        strategy_class,
        param_grid: Dict[str, List[Any]],
    ):
        self.strategy_class = strategy_class
        self.param_grid = param_grid
    
    async def optimize(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
    ) -> tuple:
        """Run grid search"""
        # Generate all parameter combinations
        keys = list(self.param_grid.keys())
        values = list(self.param_grid.values())
        combinations = list(product(*values))
        
        results = []
        
        for combo in combinations:
            params = dict(zip(keys, combo))
            
            # Create and run backtest
            strategy = self.strategy_class(**params)
            
            from backtest.engine.backtest_engine import BacktestEngine
            engine = BacktestEngine(strategy=strategy)
            
            result = await engine.run(symbols)
            
            results.append({
                "parameters": params,
                "sharpe_ratio": result.get("sharpe_ratio", 0),
                "total_return": result.get("total_return", 0),
                "max_drawdown": result.get("max_drawdown", 0),
            })
        
        # Find best
        best = max(results, key=lambda x: x["sharpe_ratio"])
        
        return best["parameters"], results
      
