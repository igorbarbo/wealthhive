"""
Markowitz Modern Portfolio Theory
"""

from typing import Dict, List

import numpy as np
from scipy.optimize import minimize


class MarkowitzOptimizer:
    """Mean-variance optimization"""
    
    def optimize(
        self,
        symbols: List[str],
        expected_returns: np.ndarray = None,
        cov_matrix: np.ndarray = None,
        target_return: float = None,
        target_risk: float = None,
        risk_free_rate: float = 0.04,
    ) -> Dict:
        """
        Optimize portfolio weights
        
        Args:
            symbols: Asset symbols
            expected_returns: Expected annual returns
            cov_matrix: Covariance matrix
            target_return: Target portfolio return (optional)
            target_risk: Target portfolio risk (optional)
            risk_free_rate: Risk-free rate for Sharpe optimization
        
        Returns:
            Optimal weights and portfolio metrics
        """
        n_assets = len(symbols)
        
        # Generate sample data if not provided
        if expected_returns is None:
            expected_returns = np.random.uniform(0.05, 0.15, n_assets)
        
        if cov_matrix is None:
            # Sample covariance matrix
            cov_matrix = np.eye(n_assets) * 0.04  # 20% volatility
        
        # Constraints: weights sum to 1
        constraints = [{"type": "eq", "fun": lambda x: np.sum(x) - 1}]
        
        # Bounds: 0 <= weight <= 1 (no short selling)
        bounds = tuple((0, 1) for _ in range(n_assets))
        
        # Initial guess: equal weights
        x0 = np.array([1 / n_assets] * n_assets)
        
        # Objective function
        if target_return is not None:
            # Minimize risk for target return
            constraints.append({
                "type": "eq",
                "fun": lambda x: np.dot(x, expected_returns) - target_return,
            })
            objective = lambda x: np.sqrt(np.dot(x.T, np.dot(cov_matrix, x)))
        
        elif target_risk is not None:
            # Maximize return for target risk
            def objective(x):
                portfolio_risk = np.sqrt(np.dot(x.T, np.dot(cov_matrix, x)))
                return -np.dot(x, expected_returns) + 1000 * abs(portfolio_risk - target_risk)
        
        else:
            # Maximize Sharpe ratio
            def objective(x):
                port_return = np.dot(x, expected_returns)
                port_risk = np.sqrt(np.dot(x.T, np.dot(cov_matrix, x)))
                return -(port_return - risk_free_rate) / port_risk if port_risk > 0 else 0
        
        # Optimize
        result = minimize(
            objective,
            x0,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
        )
        
        optimal_weights = result.x
        
        # Calculate portfolio metrics
        port_return = np.dot(optimal_weights, expected_returns)
        port_risk = np.sqrt(np.dot(optimal_weights.T, np.dot(cov_matrix, optimal_weights)))
        sharpe = (port_return - risk_free_rate) / port_risk if port_risk > 0 else 0
        
        # Generate efficient frontier
        frontier = self._generate_frontier(expected_returns, cov_matrix, risk_free_rate)
        
        return {
            "weights": optimal_weights.tolist(),
            "symbols": symbols,
            "expected_return": port_return,
            "expected_risk": port_risk,
            "sharpe_ratio": sharpe,
            "efficient_frontier": frontier,
        }
    
    def _generate_frontier(
        self,
        expected_returns: np.ndarray,
        cov_matrix: np.ndarray,
        risk_free_rate: float,
        n_points: int = 50,
    ) -> List[Dict]:
        """Generate efficient frontier points"""
        frontier = []
        
        min_return = np.min(expected_returns)
        max_return = np.max(expected_returns)
        target_returns = np.linspace(min_return, max_return, n_points)
        
        for target in target_returns:
            try:
                result = self.optimize(
                    symbols=[f"asset_{i}" for i in range(len(expected_returns))],
                    expected_returns=expected_returns,
                    cov_matrix=cov_matrix,
                    target_return=target,
                    risk_free_rate=risk_free_rate,
                )
                frontier.append({
                    "return": result["expected_return"],
                    "risk": result["expected_risk"],
                })
            except Exception:
                pass
        
        return frontier
      
