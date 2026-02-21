"""
Value and Quality factors
"""

from typing import Dict

import pandas as pd


class ValueFactor:
    """
    Value factor calculations
    """
    
    def calculate_pe(self, price: float, earnings: float) -> float:
        """Price-to-Earnings ratio"""
        return price / earnings if earnings > 0 else float("inf")
    
    def calculate_pb(self, price: float, book_value: float) -> float:
        """Price-to-Book ratio"""
        return price / book_value if book_value > 0 else float("inf")
    
    def calculate_ps(self, price: float, sales: float) -> float:
        """Price-to-Sales ratio"""
        return price / sales if sales > 0 else float("inf")
    
    def calculate_evebitda(
        self,
        market_cap: float,
        debt: float,
        cash: float,
        ebitda: float,
    ) -> float:
        """Enterprise Value to EBITDA"""
        ev = market_cap + debt - cash
        return ev / ebitda if ebitda > 0 else float("inf")
    
    def composite_value_score(
        self,
        metrics: Dict[str, float],
    ) -> float:
        """
        Calculate composite value score
        
        Combines multiple value metrics into single score
        """
        # Rank each metric (lower is better for value)
        pe_score = 1 / metrics.get("pe", 100) if metrics.get("pe", 0) > 0 else 0
        pb_score = 1 / metrics.get("pb", 100) if metrics.get("pb", 0) > 0 else 0
        ps_score = 1 / metrics.get("ps", 100) if metrics.get("ps", 0) > 0 else 0
        dividend_score = metrics.get("dividend_yield", 0)
        
        # Weighted average
        weights = {"pe": 0.3, "pb": 0.3, "ps": 0.2, "dividend": 0.2}
        
        score = (
            weights["pe"] * pe_score +
            weights["pb"] * pb_score +
            weights["ps"] * ps_score +
            weights["dividend"] * dividend_score
        )
        
        return score


class QualityFactor:
    """
    Quality factor calculations
    """
    
    def calculate_roe(self, net_income: float, equity: float) -> float:
        """Return on Equity"""
        return net_income / equity if equity > 0 else 0
    
    def calculate_roa(self, net_income: float, assets: float) -> float:
        """Return on Assets"""
        return net_income / assets if assets > 0 else 0
    
    def calculate_profitability(
        self,
        metrics: Dict[str, float],
    ) -> float:
        """
        Calculate profitability score
        """
        roe = metrics.get("roe", 0)
        roa = metrics.get("roa", 0)
        margin = metrics.get("net_margin", 0)
        
        # Normalize and combine
        score = (roe * 0.4 + roa * 0.3 + margin * 0.3)
        
        return score
    
    def calculate_earnings_quality(
        self,
        net_income: float,
        operating_cash_flow: float,
    ) -> float:
        """
        Earnings quality: accruals ratio
        """
        accruals = net_income - operating_cash_flow
        return 1 - abs(accruals / net_income) if net_income != 0 else 0
