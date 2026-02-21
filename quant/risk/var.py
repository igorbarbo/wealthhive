"""
Value at Risk calculations
"""

from typing import Dict

import numpy as np
from scipy import stats


class VaRCalculator:
    """
    Calculate Value at Risk using different methods
    """
    
    def __init__(self, method: str = "historical"):
        self.method = method  # historical, parametric, monte_carlo
    
    def calculate(
        self,
        portfolio,
        confidence_level: float = 0.95,
        time_horizon: int = 1,
    ) -> Dict:
        """
        Calculate VaR
        
        Args:
            portfolio: Portfolio object
            confidence_level: Confidence level (e.g., 0.95)
            time_horizon: Days ahead to calculate
        """
        # Get historical returns
        returns = self._get_portfolio_returns(portfolio)
        
        if self.method == "historical":
            var = self._historical_var(returns, confidence_level)
        elif self.method == "parametric":
            var = self._parametric_var(returns, confidence_level)
        elif self.method == "monte_carlo":
            var = self._monte_carlo_var(returns, confidence_level)
        else:
            raise ValueError(f"Unknown method: {self.method}")
        
        # Scale to time horizon
        var = var * np.sqrt(time_horizon)
        
        portfolio_value = portfolio.total_value or 0
        
        return {
            "var_amount": var * portfolio_value,
            "var_percent": var * 100,
            "confidence_level": confidence_level,
            "time_horizon_days": time_horizon,
            "method": self.method,
        }
    
    def _get_portfolio_returns(self, portfolio):
        """Get historical portfolio returns"""
        # Would fetch from database or calculate from positions
        # Placeholder: generate random returns
        return np.random.normal(0.001, 0.02, 252)
    
    def _historical_var(self, returns: np.ndarray, confidence: float) -> float:
        """Historical simulation VaR"""
        return np.percentile(returns, (1 - confidence) * 100)
    
    def _parametric_var(self, returns: np.ndarray, confidence: float) -> float:
        """Parametric (variance-covariance) VaR"""
        mean = np.mean(returns)
        std = np.std(returns)
        z_score = stats.norm.ppf(1 - confidence)
        return mean + z_score * std
    
    def _monte_carlo_var(
        self,
        returns: np.ndarray,
        confidence: float,
        simulations: int = 10000,
    ) -> float:
        """Monte Carlo simulation VaR"""
        mean = np.mean(returns)
        std = np.std(returns)
        
        simulated = np.random.normal(mean, std, simulations)
        return np.percentile(simulated, (1 - confidence) * 100)
