"""
Portfolio backtesting with rebalancing
"""

from typing import Any, Dict, List

import numpy as np
import pandas as pd


class PortfolioBacktester:
    """Backtest portfolio strategies with rebalancing"""
    
    def __init__(
        self,
        weights: Dict[str, float],
        rebalance_frequency: str = "M",  # M=monthly, Q=quarterly, Y=yearly
        transaction_cost: float = 0.001,
    ):
        self.target_weights = weights
        self.rebalance_frequency = rebalance_frequency
        self.transaction_cost = transaction_cost
    
    def run(
        self,
        price_data: pd.DataFrame,
    ) -> Dict[str, Any]:
        """
        Run portfolio backtest
        
        Args:
            price_data: DataFrame with price history for each asset
        """
        # Calculate returns
        returns = price_data.pct_change().dropna()
        
        # Determine rebalance dates
        if self.rebalance_frequency == "M":
            rebalance_dates = returns.resample("M").last().index
        elif self.rebalance_frequency == "Q":
            rebalance_dates = returns.resample("Q").last().index
        else:
            rebalance_dates = returns.resample("Y").last().index
        
        # Initialize
        portfolio_value = 1.0
        current_weights = pd.Series(self.target_weights)
        values = [portfolio_value]
        dates = [returns.index[0]]
        
        for date in returns.index[1:]:
            # Apply returns
            daily_return = np.dot(current_weights, returns.loc[date])
            portfolio_value *= (1 + daily_return)
            
            # Update weights (drift)
            current_weights = current_weights * (1 + returns.loc[date])
            current_weights = current_weights / current_weights.sum()
            
            # Rebalance if needed
            if date in rebalance_dates:
                # Calculate turnover
                turnover = np.sum(np.abs(current_weights - pd.Series(self.target_weights)))
                
                # Apply transaction costs
                cost = turnover * self.transaction_cost
                portfolio_value *= (1 - cost)
                
                # Reset to target weights
                current_weights = pd.Series(self.target_weights)
            
            values.append(portfolio_value)
            dates.append(date)
        
        # Calculate metrics
        equity_curve = pd.Series(values, index=dates)
        total_return = equity_curve.iloc[-1] - 1
        
        return {
            "total_return": total_return,
            "annualized_return": (1 + total_return) ** (252 / len(returns)) - 1,
            "volatility": returns.mean() * 252,  # Simplified
            "sharpe_ratio": (returns.mean() * 252) / (returns.std() * np.sqrt(252)),
            "max_drawdown": self._max_drawdown(equity_curve),
            "equity_curve": equity_curve.tolist(),
            "turnover": turnover,
        }
    
    def _max_drawdown(self, equity_curve: pd.Series) -> float:
        """Calculate maximum drawdown"""
        peak = equity_curve.expanding().max()
        drawdown = (equity_curve - peak) / peak
        return drawdown.min()
