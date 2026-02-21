"""
Multi-market factor analysis
"""

from typing import Dict, List

import numpy as np
import pandas as pd


class MarketFactorAnalyzer:
    """
    Analyze factors across multiple markets
    """
    
    MARKETS = ["US", "BR", "EU", "EM", "JP"]
    
    def calculate_market_exposure(
        self,
        portfolio_returns: pd.Series,
        market_returns: Dict[str, pd.Series],
    ) -> Dict[str, float]:
        """
        Calculate exposure to each market
        
        Returns beta to each market index
        """
        exposures = {}
        
        for market, returns in market_returns.items():
            # Align data
            aligned = pd.concat([portfolio_returns, returns], axis=1).dropna()
            
            if len(aligned) > 30:
                # Calculate beta
                cov = aligned.cov().iloc[0, 1]
                var = aligned.iloc[:, 1].var()
                beta = cov / var if var > 0 else 0
                exposures[market] = beta
            else:
                exposures[market] = 0
        
        return exposures
    
    def calculate_currency_exposure(
        self,
        portfolio,
        currency_returns: Dict[str, pd.Series],
    ) -> Dict[str, float]:
        """
        Calculate currency exposure
        """
        # Get currency breakdown of portfolio
        currency_allocation = self._get_currency_allocation(portfolio)
        
        exposures = {}
        for currency, weight in currency_allocation.items():
            if currency in currency_returns:
                # Calculate contribution to return
                exposures[currency] = weight
        
        return exposures
    
    def _get_currency_allocation(self, portfolio) -> Dict[str, float]:
        """Get portfolio allocation by currency"""
        # Simplified
        return {"BRL": 0.7, "USD": 0.3}
    
    def geographic_diversification(self, portfolio) -> Dict:
        """
        Calculate geographic diversification metrics
        """
        # Get geographic breakdown
        geo_breakdown = self._get_geographic_breakdown(portfolio)
        
        # Calculate Herfindahl index
        weights = np.array(list(geo_breakdown.values()))
        hhi = np.sum(weights ** 2)
        
        return {
            "breakdown": geo_breakdown,
            "hhi": hhi,
            "effective_n_countries": 1 / hhi if hhi > 0 else 0,
            "concentration_risk": "high" if hhi > 0.5 else "medium" if hhi > 0.3 else "low",
        }
    
    def _get_geographic_breakdown(self, portfolio) -> Dict[str, float]:
        """Get geographic breakdown of portfolio"""
        # Would use actual position data
        return {"Brazil": 0.7, "USA": 0.2, "Other": 0.1}
