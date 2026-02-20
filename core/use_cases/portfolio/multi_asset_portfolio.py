"""
Multi-asset portfolio construction use case
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List
from uuid import UUID


@dataclass
class AssetAllocation:
    """Asset allocation result"""
    asset_id: UUID
    symbol: str
    asset_class: str
    weight: float
    value: Decimal
    expected_return: float
    expected_risk: float


class MultiAssetPortfolioUseCase:
    """Construct multi-asset portfolio (stocks, bonds, crypto, etc.)"""
    
    ASSET_CLASSES = {
        "stocks_br": {"return": 0.12, "risk": 0.20, "correlation": 0.8},
        "stocks_us": {"return": 0.10, "risk": 0.18, "correlation": 0.7},
        "bonds": {"return": 0.08, "risk": 0.08, "correlation": 0.2},
        "reits": {"return": 0.09, "risk": 0.15, "correlation": 0.6},
        "crypto": {"return": 0.25, "risk": 0.80, "correlation": 0.1},
        "gold": {"return": 0.06, "risk": 0.15, "correlation": 0.0},
        "cash": {"return": 0.04, "risk": 0.01, "correlation": 0.0},
    }
    
    def execute(
        self,
        total_value: Decimal,
        risk_profile: str,  # conservative, moderate, aggressive
        constraints: Dict[str, tuple] = None,
    ) -> Dict:
        """
        Construct multi-asset portfolio
        
        Args:
            total_value: Total investment amount
            risk_profile: Investor risk profile
            constraints: Min/max constraints per asset class {class: (min, max)}
        """
        # Default allocations by risk profile
        profiles = {
            "conservative": {
                "stocks_br": 0.15,
                "stocks_us": 0.10,
                "bonds": 0.50,
                "reits": 0.10,
                "crypto": 0.00,
                "gold": 0.10,
                "cash": 0.05,
            },
            "moderate": {
                "stocks_br": 0.25,
                "stocks_us": 0.20,
                "bonds": 0.30,
                "reits": 0.10,
                "crypto": 0.05,
                "gold": 0.05,
                "cash": 0.05,
            },
            "aggressive": {
                "stocks_br": 0.35,
                "stocks_us": 0.30,
                "bonds": 0.10,
                "reits": 0.10,
                "crypto": 0.10,
                "gold": 0.00,
                "cash": 0.05,
            },
        }
        
        if risk_profile not in profiles:
            raise ValueError(f"Unknown risk profile: {risk_profile}")
        
        allocation = profiles[risk_profile]
        
        # Apply constraints if provided
        if constraints:
            allocation = self._apply_constraints(allocation, constraints)
        
        # Normalize to ensure sum = 1
        total_weight = sum(allocation.values())
        allocation = {k: v / total_weight for k, v in allocation.items()}
        
        # Calculate portfolio metrics
        portfolio_return = sum(
            allocation[cls] * self.ASSET_CLASSES[cls]["return"]
            for cls in allocation
        )
        
        # Simplified risk calculation (would use covariance matrix)
        portfolio_risk = sum(
            allocation[cls] * self.ASSET_CLASSES[cls]["risk"]
            for cls in allocation
        ) / len(allocation)  # Simplified
        
        allocations = []
        for asset_class, weight in allocation.items():
            if weight > 0:
                allocations.append({
                    "asset_class": asset_class,
                    "weight": round(weight * 100, 2),
                    "value": round(total_value * Decimal(str(weight)), 2),
                    "expected_return": round(self.ASSET_CLASSES[asset_class]["return"] * 100, 2),
                    "expected_risk": round(self.ASSET_CLASSES[asset_class]["risk"] * 100, 2),
                })
        
        return {
            "risk_profile": risk_profile,
            "total_value": total_value,
            "expected_annual_return": round(portfolio_return * 100, 2),
            "expected_annual_risk": round(portfolio_risk * 100, 2),
            "sharpe_ratio": round((portfolio_return - 0.04) / portfolio_risk, 2),  # Assuming 4% risk-free
            "allocations": allocations,
            "diversification_score": self._calculate_diversification(allocation),
        }
    
    def _apply_constraints(
        self,
        allocation: Dict[str, float],
        constraints: Dict[str, tuple],
    ) -> Dict[str, float]:
        """Apply min/max constraints to allocation"""
        result = allocation.copy()
        
        for asset_class, (min_val, max_val) in constraints.items():
            if asset_class in result:
                result[asset_class] = max(min_val, min(max_val, result[asset_class]))
        
        return result
    
    def _calculate_diversification(self, allocation: Dict[str, float]) -> float:
        """Calculate diversification score (0-100)"""
        # Herfindahl-Hirschman Index inverse
        hhi = sum(w ** 2 for w in allocation.values())
        # Normalize: lower HHI = higher diversification
        score = (1 - hhi) * 100
        return round(score, 2)
