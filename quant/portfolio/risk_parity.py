"""
Risk Parity portfolio construction
"""

from typing import Dict, List

import numpy as np
from scipy.optimize import minimize


class RiskParityOptimizer:
    """
    Risk parity optimization
    Allocate such that each asset contributes equally to portfolio risk
    """
    
    def optimize(
        self,
        symbols: List[str],
        cov_matrix: np.ndarray = None,
    ) -> Dict:
        """
        Optimize risk parity portfolio
        
        Args:
            symbols: Asset symbols
            cov_matrix: Covariance matrix
        """
        n_assets = len(symbols)
        
        if cov_matrix is None:
            cov_matrix = np.eye(n_assets) * 0.04
        
        # Risk budgeting: equal risk contribution
        target_risk = 1.0 / n_assets
        
        # Objective: minimize sum of squared differences from target
        def objective(weights):
            port_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            
            # Marginal risk contribution
            marginal = np.dot(cov_matrix, weights) / port_risk
            
            # Risk contribution
            risk_contrib = weights * marginal
            
            # Sum of squared differences from target
            return np.sum((risk_contrib - target_risk) ** 2)
        
        # Constraints
        constraints = [{"type": "eq", "fun": lambda x: np.sum(x) - 1}]
        bounds = tuple((0.01, 0.5) for _ in range(n_assets))  # Min 1%, max 50%
        
        # Initial guess
        x0 = np.ones(n_assets) / n_assets
        
        # Optimize
        result = minimize(
            objective,
            x0,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
        )
        
        optimal_weights = result.x
        
        # Calculate metrics
        port_risk = np.sqrt(np.dot(optimal_weights.T, np.dot(cov_matrix, optimal_weights)))
        marginal = np.dot(cov_matrix, optimal_weights) / port_risk
        risk_contrib = optimal_weights * marginal
        
        return {
            "weights": optimal_weights.tolist(),
            "risk_contributions": risk_contrib.tolist(),
            "portfolio_risk": port_risk,
        }
