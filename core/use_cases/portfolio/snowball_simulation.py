"""
Snowball effect simulation use case
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List


@dataclass
class SnowballResult:
    """Result of snowball simulation"""
    final_value: Decimal
    total_contributions: Decimal
    total_dividends: Decimal
    total_return: Decimal
    total_return_percent: float
    monthly_data: List[Dict]
    milestones: List[Dict]


class SnowballSimulationUseCase:
    """Calculate compound growth with dividend reinvestment"""
    
    def execute(
        self,
        initial_investment: Decimal,
        monthly_contribution: Decimal,
        annual_return_rate: float,
        years: int,
        reinvest_dividends: bool = True,
        dividend_yield: float = 0.04,
    ) -> SnowballResult:
        """
        Calculate snowball effect
        
        Args:
            initial_investment: Starting amount
            monthly_contribution: Monthly addition
            annual_return_rate: Expected annual return (e.g., 0.12 for 12%)
            years: Investment horizon
            reinvest_dividends: Whether to reinvest dividends
            dividend_yield: Annual dividend yield
        """
        monthly_rate = annual_return_rate / 12
        monthly_dividend_yield = dividend_yield / 12 if reinvest_dividends else 0
        
        balance = initial_investment
        total_contributions = initial_investment
        total_dividends = Decimal("0")
        monthly_data = []
        milestones = []
        
        milestone_targets = [
            Decimal("100000"),
            Decimal("500000"),
            Decimal("1000000"),
            Decimal("5000000"),
            Decimal("10000000"),
        ]
        milestone_idx = 0
        
        for month in range(1, years * 12 + 1):
            # Add monthly contribution
            balance += monthly_contribution
            total_contributions += monthly_contribution
            
            # Calculate and reinvest dividends
            monthly_dividend = balance * Decimal(str(monthly_dividend_yield))
            total_dividends += monthly_dividend
            balance += monthly_dividend
            
            # Apply capital appreciation
            balance *= Decimal(str(1 + monthly_rate))
            
            # Record monthly data
            monthly_data.append({
                "month": month,
                "year": month // 12,
                "balance": round(balance, 2),
                "contributions": round(total_contributions, 2),
                "dividends": round(total_dividends, 2),
            })
            
            # Check milestones
            while milestone_idx < len(milestone_targets) and balance >= milestone_targets[milestone_idx]:
                milestones.append({
                    "amount": float(milestone_targets[milestone_idx]),
                    "month": month,
                    "year": month / 12,
                })
                milestone_idx += 1
        
        total_return = balance - total_contributions
        total_return_percent = float(total_return / total_contributions * 100) if total_contributions > 0 else 0
        
        return SnowballResult(
            final_value=round(balance, 2),
            total_contributions=round(total_contributions, 2),
            total_dividends=round(total_dividends, 2),
            total_return=round(total_return, 2),
            total_return_percent=round(total_return_percent, 2),
            monthly_data=monthly_data,
            milestones=milestones,
        )
