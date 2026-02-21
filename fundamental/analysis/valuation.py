"""
Valuation models
"""

from typing import Any, Dict


class ValuationModels:
    """
    Various valuation models
    """
    
    @staticmethod
    def dcf(
        free_cash_flow: float,
        growth_rate: float,
        discount_rate: float,
        terminal_growth: float,
        years: int = 5,
    ) -> Dict[str, float]:
        """
        Discounted Cash Flow valuation
        
        Args:
            free_cash_flow: Current FCF
            growth_rate: Growth rate for projection period
            discount_rate: WACC / discount rate
            terminal_growth: Perpetual growth rate
            years: Projection years
        """
        # Project FCF
        fcf_projections = []
        for year in range(1, years + 1):
            fcf = free_cash_flow * ((1 + growth_rate) ** year)
            pv = fcf / ((1 + discount_rate) ** year)
            fcf_projections.append({
                "year": year,
                "fcf": fcf,
                "pv": pv,
            })
        
        # Terminal value
        terminal_fcf = fcf_projections[-1]["fcf"] * (1 + terminal_growth)
        terminal_value = terminal_fcf / (discount_rate - terminal_growth)
        terminal_pv = terminal_value / ((1 + discount_rate) ** years)
        
        # Enterprise value
        enterprise_value = sum(p["pv"] for p in fcf_projections) + terminal_pv
        
        return {
            "projections": fcf_projections,
            "terminal_value": terminal_value,
            "terminal_pv": terminal_pv,
            "enterprise_value": enterprise_value,
            "wacc": discount_rate,
            "growth_assumption": growth_rate,
        }
    
    @staticmethod
    def graham_number(eps: float, book_value_per_share: float) -> float:
        """
        Graham's number for intrinsic value
        """
        return (22.5 * eps * book_value_per_share) ** 0.5
    
    @staticmethod
    def dividend_discount_model(
        dividend: float,
        growth_rate: float,
        required_return: float,
    ) -> float:
        """
        Gordon Growth Model
        """
        if required_return <= growth_rate:
            return float("inf")
        
        return dividend * (1 + growth_rate) / (required_return - growth_rate)
    
    @staticmethod
    def residual_income_model(
        book_value: float,
        eps: float,
        cost_of_equity: float,
    ) -> float:
        """
        Residual Income Model
        """
        residual_income = eps - (book_value * cost_of_equity)
        return book_value + (residual_income / cost_of_equity)
      
