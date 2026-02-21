"""
Central optimization wrapper
"""

from typing import Any, Dict, List

import numpy as np

from quant.optimization.genetic import GeneticOptimizer
from quant.optimization.monte_carlo import MonteCarloSimulation
from quant.portfolio.black_litterman import BlackLittermanOptimizer
from quant.portfolio.markowitz import MarkowitzOptimizer
from quant.portfolio.risk_parity import RiskParityOptimizer


class PortfolioOptimizer:
    """
    Central optimizer that selects appropriate method based on requirements
    """
    
    METHODS = {
        "markowitz": MarkowitzOptimizer,
        "black_litterman": BlackLittermanOptimizer,
        "risk_parity": RiskParityOptimizer,
        "genetic": GeneticOptimizer,
        "monte_carlo": MonteCarloSimulation,
    }
    
    def optimize(
        self,
        method: str,
        symbols: List[str],
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Optimize portfolio using specified method
        
        Args:
            method: Optimization method
            symbols: List of asset symbols
            **kwargs: Method-specific parameters
        
        Returns:
            Optimization results
        """
        if method not in self.METHODS:
            raise ValueError(f"Unknown method: {method}. Available: {list(self.METHODS.keys())}")
        
        optimizer_class = self.METHODS[method]
        optimizer = optimizer_class(**kwargs)
        
        if method in ["markowitz", "black_litterman", "risk_parity"]:
            return optimizer.optimize(symbols=symbols, **kwargs)
        elif method == "genetic":
            # Genetic needs fitness function
            fitness_func = kwargs.get("fitness_func")
            n_assets = len(symbols)
            weights, score = optimizer.optimize(n_assets, fitness_func)
            return {
                "weights": weights.tolist(),
                "fitness": score,
                "symbols": symbols,
            }
        elif method == "monte_carlo":
            expected_returns = kwargs.get("expected_returns")
            cov_matrix = kwargs.get("cov_matrix")
            return optimizer.optimize_weights(expected_returns, cov_matrix)
        
        return {}
    
    def compare_methods(
        self,
        symbols: List[str],
        **common_params,
    ) -> Dict[str, Dict]:
        """
        Compare different optimization methods
        """
        results = {}
        
        for method in ["markowitz", "risk_parity"]:
            try:
                result = self.optimize(method, symbols, **common_params)
                results[method] = {
                    "success": True,
                    "result": result,
                }
            except Exception as e:
                results[method] = {
                    "success": False,
                    "error": str(e),
                }
        
        return results
      
