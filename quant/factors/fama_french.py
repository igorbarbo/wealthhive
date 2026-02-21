"""
Fama-French factor model
"""

from typing import Dict

import numpy as np
import pandas as pd


class FamaFrenchModel:
    """
    Fama-French 3-factor and 5-factor models
    """
    
    FACTORS_3 = ["market", "smb", "hml"]  # Small-minus-Big, High-minus-Low
    FACTORS_5 = ["market", "smb", "hml", "rmw", "cma"]  # + Profitability, Investment
    
    def __init__(self, model: str = "3factor"):
        self.model = model
        self.factors = self.FACTORS_3 if model == "3factor" else self.FACTORS_5
    
    def regress(
        self,
        returns: pd.Series,
        factor_returns: pd.DataFrame,
    ) -> Dict:
        """
        Run factor regression
        
        Args:
            returns: Asset returns
            factor_returns: Factor returns (market, smb, hml, etc.)
        """
        from sklearn.linear_model import LinearRegression
        
        # Align data
        data = pd.concat([returns, factor_returns], axis=1).dropna()
        
        y = data.iloc[:, 0]  # Asset returns
        X = data.iloc[:, 1:]  # Factor returns
        X = sm.add_constant(X)  # Add intercept (alpha)
        
        # Regression
        model = LinearRegression()
        model.fit(X, y)
        
        # Results
        r_squared = model.score(X, y)
        
        return {
            "alpha": model.intercept_,
            "betas": dict(zip(self.factors, model.coef_[1:])),
            "r_squared": r_squared,
            "model": self.model,
        }
    
    def calculate_factor_exposures(
        self,
        portfolio_returns: pd.Series,
    ) -> Dict:
        """
        Calculate portfolio factor exposures
        """
        # Would fetch factor returns from database
        # Placeholder
        factor_returns = pd.DataFrame(
            np.random.randn(len(portfolio_returns), len(self.factors)),
            columns=self.factors,
            index=portfolio_returns.index,
        )
        
        return self.regress(portfolio_returns, factor_returns)
      
