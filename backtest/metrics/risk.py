"""
Risk metrics for backtests
"""

import numpy as np
from scipy import stats


class RiskMetrics:
    """Calculate risk metrics"""
    
    @staticmethod
    def value_at_risk(returns: np.ndarray, confidence: float = 0.95) -> float:
        """Parametric VaR"""
        mean = np.mean(returns)
        std = np.std(returns)
        z_score = stats.norm.ppf(1 - confidence)
        return mean + z_score * std
    
    @staticmethod
    def cvar(returns: np.ndarray, confidence: float = 0.95) -> float:
        """Conditional VaR (Expected Shortfall)"""
        var = RiskMetrics.value_at_risk(returns, confidence)
        return np.mean(returns[returns <= var])
    
    @staticmethod
    def beta(returns: np.ndarray, market_returns: np.ndarray) -> float:
        """Calculate beta"""
        covariance = np.cov(returns, market_returns)[0][1]
        market_variance = np.var(market_returns)
        return covariance / market_variance if market_variance > 0 else 0
    
    @staticmethod
    def alpha(
        returns: np.ndarray,
        market_returns: np.ndarray,
        risk_free: float = 0.04,
    ) -> float:
        """Calculate Jensen's alpha"""
        beta = RiskMetrics.beta(returns, market_returns)
        alpha = np.mean(returns) - (risk_free / 252 + beta * (np.mean(market_returns) - risk_free / 252))
        return alpha * 252  # Annualize
