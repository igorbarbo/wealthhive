"""
Multi-asset portfolio construction
"""

from typing import Dict, List

import numpy as np


class MultiAssetPortfolio:
    """
    Construct portfolios across multiple asset classes
    """
    
    ASSET_CLASSES = {
        "stocks_br": {"expected_return": 0.12, "volatility": 0.20, "correlation": 0.8},
        "stocks_us": {"expected_return": 0.10, "volatility": 0.18, "correlation": 0.7},
        "bonds": {"expected_return": 0.08, "volatility": 0.08, "correlation": 0.2},
        "reits": {"expected_return": 0.09, "volatility": 0.15, "correlation": 0.6},
        "crypto": {"expected_return": 0.25, "volatility": 0.80, "correlation": 0.1},
        "gold": {"expected_return": 0.06, "volatility": 0.15, "correlation": 0.0},
        "cash": {"expected_return": 0.04, "volatility": 0.01, "correlation": 0.0},
    }
    
    def construct(
        self,
        risk_profile: str,  # conservative, moderate, aggressive
        constraints: Dict[str, tuple] = None,
    ) -> Dict:
        """
        Construct multi-asset portfolio
        
        Args:
            risk_profile: Investor risk profile
            constraints: Min/max weights per asset class
        """
        # Base allocations by risk profile
        base_allocations = {
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
        
        if risk_profile not in base_allocations:
            raise ValueError(f"Unknown risk profile: {risk_profile}")
        
        allocation = base_allocations[risk_profile].copy()
        
        # Apply constraints
        if constraints:
            for asset, (min_w, max_w) in constraints.items():
                if asset in allocation:
                    allocation[asset] = max(min_w, min(max_w, allocation[asset]))
        
        # Normalize
        total = sum(allocation.values())
        allocation = {k: v / total for k, v in allocation.items()}
        
        # Calculate portfolio metrics
        port_return = sum(
            allocation[a] * self.ASSET_CLASSES[a]["expected_return"]
            for a in allocation
        )
        
        # Simplified risk calculation
        port_risk = np.sqrt(sum(
            allocation[a] ** 2 * self.ASSET_CLASSES[a]["volatility"] ** 2
            for a in allocation
        ))
        
        # Sharpe ratio (assuming 4% risk-free)
        sharpe = (port_return - 0.04) / port_risk if port_risk > 0 else 0
        
        return {
            "risk_profile": risk_profile,
            "allocation": allocation,
            "expected_return": port_return,
            "expected_risk": port_risk,
            "sharpe_ratio": sharpe,
        }
    
    def glide_path(
        self,
        current_age: int,
        retirement_age: int,
    ) -> Dict:
        """
        Generate glide path (allocation changes over time)
        """
        years_to_retirement = retirement_age - current_age
        
        if years_to_retirement > 30:
            profile = "aggressive"
        elif years_to_retirement > 15:
            profile = "moderate"
        else:
            profile = "conservative"
        
        return self.construct(profile)
