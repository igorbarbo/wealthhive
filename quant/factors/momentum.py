"""
Momentum factor
"""

import pandas as pd


class MomentumFactor:
    """
    Calculate momentum factor
    """
    
    def calculate(
        self,
        prices: pd.DataFrame,
        lookback: int = 12,  # 12 months
        skip: int = 1,  # Skip most recent month (reversal)
    ) -> pd.Series:
        """
        Calculate momentum score
        
        Standard momentum: return over past 12 months excluding most recent month
        """
        # Calculate returns
        returns = prices.pct_change()
        
        # Skip recent month
        if skip > 0:
            recent_returns = returns.iloc[-skip:]
            returns = returns.iloc[:-skip]
        
        # Calculate cumulative return over lookback period
        momentum = (1 + returns).rolling(window=lookback).apply(lambda x: x.prod()) - 1
        
        return momentum.iloc[-1]
    
    def rank_assets(
        self,
        prices: pd.DataFrame,
        n_quantiles: int = 10,
    ) -> pd.DataFrame:
        """
        Rank assets by momentum into quantiles
        """
        momentum = self.calculate(prices)
        
        # Rank
        ranks = momentum.rank(ascending=False)
        
        # Assign quantiles
        quantiles = pd.qcut(ranks, n_quantiles, labels=False, duplicates="drop")
        
        return pd.DataFrame({
            "momentum": momentum,
            "rank": ranks,
            "quantile": quantiles,
        })
      
