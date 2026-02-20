"""
Fundamental analysis features
"""

from typing import Any, Dict

import pandas as pd


class FundamentalFeatures:
    """Extract fundamental features"""
    
    @staticmethod
    def calculate_ratios(financials: Dict[str, Any]) -> Dict[str, float]:
        """Calculate financial ratios"""
        ratios = {}
        
        # Valuation ratios
        if "market_cap" in financials and "revenue" in financials:
            ratios["ps_ratio"] = financials["market_cap"] / financials["revenue"]
        
        if "market_cap" in financials and "net_income" in financials:
            ratios["pe_ratio"] = financials["market_cap"] / financials["net_income"]
        
        if "book_value" in financials and "market_cap" in financials:
            ratios["pb_ratio"] = financials["market_cap"] / financials["book_value"]
        
        # Profitability ratios
        if "net_income" in financials and "revenue" in financials:
            ratios["net_margin"] = financials["net_income"] / financials["revenue"]
        
        if "ebitda" in financials and "revenue" in financials:
            ratios["ebitda_margin"] = financials["ebitda"] / financials["revenue"]
        
        # Efficiency ratios
        if "revenue" in financials and "assets" in financials:
            ratios["asset_turnover"] = financials["revenue"] / financials["assets"]
        
        # Leverage ratios
        if "debt" in financials and "equity" in financials:
            ratios["debt_to_equity"] = financials["debt"] / financials["equity"]
        
        return ratios
    
    @staticmethod
    def calculate_growth_rates(
        current: Dict[str, float],
        previous: Dict[str, float],
    ) -> Dict[str, float]:
        """Calculate year-over-year growth rates"""
        growth = {}
        
        metrics = ["revenue", "net_income", "ebitda", "book_value"]
        
        for metric in metrics:
            if metric in current and metric in previous and previous[metric] != 0:
                growth[f"{metric}_growth"] = (
                    (current[metric] - previous[metric]) / abs(previous[metric])
                )
        
        return growth
    
    @staticmethod
    def quality_score(financials: Dict[str, Any]) -> float:
        """Calculate fundamental quality score (0-100)"""
        score = 0
        weights = {
            "pe_ratio": 0.15,  # Lower is better
            "pb_ratio": 0.15,  # Lower is better
            "net_margin": 0.20,  # Higher is better
            "roe": 0.25,  # Higher is better
            "debt_to_equity": 0.15,  # Lower is better
            "revenue_growth": 0.10,  # Higher is better
        }
        
        # P/E ratio score (inverse, optimal around 15)
        pe = financials.get("pe_ratio", 30)
        score += weights["pe_ratio"] * max(0, min(100, (30 - pe) / 30 * 100))
        
        # P/B ratio score (inverse, optimal around 2)
        pb = financials.get("pb_ratio", 5)
        score += weights["pb_ratio"] * max(0, min(100, (5 - pb) / 5 * 100))
        
        # Net margin score (direct, 0-30% range)
        margin = financials.get("net_margin", 0)
        score += weights["net_margin"] * min(100, margin * 100 / 30 * 100)
        
        # ROE score (direct, 0-25% range)
        roe = financials.get("return_on_equity", 0)
        score += weights["roe"] * min(100, roe * 100 / 25 * 100)
        
        # Debt/Equity score (inverse, optimal < 1)
        de = financials.get("debt_to_equity", 2)
        score += weights["debt_to_equity"] * max(0, min(100, (2 - de) / 2 * 100))
        
        # Revenue growth score (direct, 0-30% range)
        growth = financials.get("revenue_growth", 0)
        score += weights["revenue_growth"] * min(100, growth * 100 / 30 * 100)
        
        return round(score, 2)
