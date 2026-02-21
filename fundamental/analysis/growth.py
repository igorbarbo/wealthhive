"""
Growth analysis
"""

from typing import Any, Dict, List

import numpy as np


class GrowthAnalysis:
    """
    Analyze company growth metrics
    """
    
    def calculate_cagr(
        self,
        values: List[float],
        years: int,
    ) -> float:
        """
        Calculate Compound Annual Growth Rate
        """
        if len(values) < 2 or values[0] <= 0:
            return 0
        
        beginning = values[0]
        ending = values[-1]
        
        cagr = (ending / beginning) ** (1 / years) - 1
        return cagr
    
    def analyze_revenue_growth(
        self,
        revenues: List[float],
        years: List[int],
    ) -> Dict[str, Any]:
        """
        Analyze revenue growth trends
        """
        if len(revenues) < 2:
            return {"error": "Insufficient data"}
        
        # Calculate year-over-year growth
        yoy_growth = [
            (revenues[i] - revenues[i-1]) / revenues[i-1]
            for i in range(1, len(revenues))
        ]
        
        # CAGR
        cagr = self.calculate_cagr(revenues, len(revenues) - 1)
        
        # Trend
        recent_growth = np.mean(yoy_growth[-3:]) if len(yoy_growth) >= 3 else np.mean(yoy_growth)
        older_growth = np.mean(yoy_growth[:3]) if len(yoy_growth) >= 6 else np.mean(yoy_growth)
        
        trend = "accelerating" if recent_growth > older_growth else "decelerating"
        
        return {
            "cagr": round(cagr * 100, 2),
            "average_yoy": round(np.mean(yoy_growth) * 100, 2),
            "latest_growth": round(yoy_growth[-1] * 100, 2),
            "trend": trend,
            "consistency": "stable" if np.std(yoy_growth) < 0.1 else "volatile",
            "historical": list(zip(years, revenues, [0] + [g*100 for g in yoy_growth])),
        }
    
    def sustainable_growth_rate(
        self,
        roe: float,
        payout_ratio: float,
    ) -> float:
        """
        Calculate sustainable growth rate
        
        SGR = ROE * (1 - payout_ratio)
        """
        retention_ratio = 1 - payout_ratio
        sgr = roe * retention_ratio
        return sgr
    
    def peg_ratio(
        self,
        pe_ratio: float,
        earnings_growth: float,
    ) -> float:
        """
        Calculate PEG ratio
        
        PEG = PE / Earnings Growth
        < 1 is considered undervalued
        """
        if earnings_growth <= 0:
            return float("inf")
        
        return pe_ratio / (earnings_growth * 100)
    
    def growth_quality_score(
        self,
        revenue_growth: List[float],
        earnings_growth: List[float],
        cash_flow_growth: List[float],
    ) -> Dict[str, Any]:
        """
        Score quality of growth
        
        Quality growth = revenue, earnings, and cash flow growing together
        """
        scores = {}
        
        # Consistency across metrics
        avg_revenue = np.mean(revenue_growth) if revenue_growth else 0
        avg_earnings = np.mean(earnings_growth) if earnings_growth else 0
        avg_cashflow = np.mean(cash_flow_growth) if cash_flow_growth else 0
        
        # Alignment score (all growing similarly)
        growth_rates = [avg_revenue, avg_earnings, avg_cashflow]
        alignment = 1 - (np.std(growth_rates) / (np.mean(growth_rates) + 0.001))
        scores["alignment"] = max(0, alignment) * 100
        
        # Profitability of growth (earnings growing faster than revenue)
        if avg_revenue > 0:
            profit_growth = (avg_earnings - avg_revenue) / avg_revenue
            scores["profitability"] = min(100, max(0, 50 + profit_growth * 100))
        else:
            scores["profitability"] = 50
        
        # Sustainability (cash flow supporting earnings)
        if avg_earnings > 0:
            cash_support = min(1, avg_cashflow / avg_earnings)
            scores["sustainability"] = cash_support * 100
        else:
            scores["sustainability"] = 0
        
        scores["overall"] = np.mean(list(scores.values()))
        
        return scores
      
