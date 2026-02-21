"""
Snowball effect (compound growth) simulation
"""

from dataclasses import dataclass
from typing import Dict, List

import numpy as np


@dataclass
class SnowballResult:
    """Snowball simulation result"""
    years: int
    final_value: float
    total_contributions: float
    total_dividends: float
    total_return: float
    monthly_data: List[Dict]


class SnowballSimulator:
    """
    Simulate snowball effect with dividend reinvestment
    """
    
    def calculate(
        self,
        initial_investment: float,
        monthly_contribution: float,
        annual_return_rate: float,
        years: int,
        reinvest_dividends: bool = True,
        dividend_yield: float = 0.04,
        dividend_growth: float = 0.05,
        contribution_growth: float = 0.0,
    ) -> SnowballResult:
        """
        Calculate snowball effect
        
        Args:
            initial_investment: Starting amount
            monthly_contribution: Monthly addition
            annual_return_rate: Expected annual return
            years: Investment horizon
            reinvest_dividends: Whether to reinvest dividends
            dividend_yield: Starting annual dividend yield
            dividend_growth: Annual dividend growth rate
            contribution_growth: Annual contribution growth rate
        """
        balance = initial_investment
        total_contributions = initial_investment
        total_dividends = 0
        monthly_data = []
        
        current_dividend_yield = dividend_yield
        current_contribution = monthly_contribution
        
        for year in range(1, years + 1):
            for month in range(1, 13):
                # Add contribution
                balance += current_contribution
                total_contributions += current_contribution
                
                # Calculate and reinvest dividends
                if reinvest_dividends:
                    monthly_dividend = balance * (current_dividend_yield / 12)
                    total_dividends += monthly_dividend
                    balance += monthly_dividend
                
                # Apply monthly return
                monthly_return = (1 + annual_return_rate) ** (1/12) - 1
                balance *= (1 + monthly_return)
                
                # Record data
                monthly_data.append({
                    "year": year,
                    "month": month,
                    "balance": round(balance, 2),
                    "contributions": round(total_contributions, 2),
                    "dividends": round(total_dividends, 2),
                })
            
            # Annual growth adjustments
            current_dividend_yield *= (1 + dividend_growth)
            current_contribution *= (1 + contribution_growth)
        
        total_return = balance - total_contributions
        
        return SnowballResult(
            years=years,
            final_value=round(balance, 2),
            total_contributions=round(total_contributions, 2),
            total_dividends=round(total_dividends, 2),
            total_return=round(total_return, 2),
            monthly_data=monthly_data,
        )
    
    def compare_scenarios(
        self,
        scenarios: List[Dict],
        years: int,
    ) -> Dict:
        """Compare multiple snowball scenarios"""
        results = []
        
        for scenario in scenarios:
            result = self.calculate(
                initial_investment=scenario.get("initial", 0),
                monthly_contribution=scenario.get("monthly", 0),
                annual_return_rate=scenario.get("return", 0.10),
                years=years,
                reinvest_dividends=scenario.get("reinvest", True),
                dividend_yield=scenario.get("dividend_yield", 0.04),
            )
            results.append({
                "name": scenario.get("name", "Scenario"),
                "final_value": result.final_value,
                "total_contributions": result.total_contributions,
                "total_dividends": result.total_dividends,
            })
        
        return {
            "years": years,
            "scenarios": results,
        }
