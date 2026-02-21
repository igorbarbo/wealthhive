"""
Performance calculation metrics
"""

from typing import Any, Dict, List

import numpy as np
import pandas as pd


class PerformanceMetrics:
    """Calculate strategy performance metrics"""
    
    @staticmethod
    def calculate_all(
        equity_curve: List[float],
        trades: List[Dict],
    ) -> Dict[str, Any]:
        """Calculate all metrics"""
        returns = pd.Series(equity_curve).pct_change().dropna()
        
        metrics = {
            "sharpe_ratio": PerformanceMetrics.sharpe_ratio(returns),
            "sortino_ratio": PerformanceMetrics.sortino_ratio(returns),
            "max_drawdown": PerformanceMetrics.max_drawdown(equity_curve),
            "calmar_ratio": PerformanceMetrics.calmar_ratio(returns, equity_curve),
            "volatility": returns.std() * np.sqrt(252),
            "total_trades": len(trades),
            "winning_trades": len([t for t in trades if t.get("pnl", 0) > 0]),
            "losing_trades": len([t for t in trades if t.get("pnl", 0) < 0]),
        }
        
        if metrics["total_trades"] > 0:
            metrics["win_rate"] = metrics["winning_trades"] / metrics["total_trades"]
            
            avg_win = np.mean([t["pnl"] for t in trades if t.get("pnl", 0) > 0]) if metrics["winning_trades"] > 0 else 0
            avg_loss = np.mean([t["pnl"] for t in trades if t.get("pnl", 0) < 0]) if metrics["losing_trades"] > 0 else 1
            metrics["profit_factor"] = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        else:
            metrics["win_rate"] = 0
            metrics["profit_factor"] = 0
        
        return metrics
    
    @staticmethod
    def sharpe_ratio(returns: pd.Series, risk_free: float = 0.04) -> float:
        """Annualized Sharpe ratio"""
        excess = returns - risk_free / 252
        if excess.std() == 0:
            return 0
        return np.sqrt(252) * excess.mean() / excess.std()
    
    @staticmethod
    def sortino_ratio(returns: pd.Series, risk_free: float = 0.04) -> float:
        """Sortino ratio"""
        excess = returns - risk_free / 252
        downside = returns[returns < 0]
        if len(downside) == 0 or downside.std() == 0:
            return 0
        return np.sqrt(252) * excess.mean() / downside.std()
    
    @staticmethod
    def max_drawdown(equity_curve: List[float]) -> float:
        """Maximum drawdown"""
        peak = np.maximum.accumulate(equity_curve)
        drawdown = (np.array(equity_curve) - peak) / peak
        return float(np.min(drawdown))
    
    @staticmethod
    def calmar_ratio(returns: pd.Series, equity_curve: List[float]) -> float:
        """Calmar ratio"""
        annual_return = returns.mean() * 252
        max_dd = abs(PerformanceMetrics.max_drawdown(equity_curve))
        return annual_return / max_dd if max_dd > 0 else 0
