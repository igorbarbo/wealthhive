"""
Portfolio rebalancing algorithms
"""

from typing import Dict, List, Tuple

import numpy as np


class RebalanceEngine:
    """
    Portfolio rebalancing engine
    """
    
    def __init__(
        self,
        threshold: float = 0.05,  # 5% drift threshold
        max_turnover: float = 0.50,  # Maximum 50% turnover
    ):
        self.threshold = threshold
        self.max_turnover = max_turnover
    
    def check_drift(
        self,
        target_weights: Dict[str, float],
        current_weights: Dict[str, float],
    ) -> Dict[str, float]:
        """
        Calculate weight drift from target
        
        Returns:
            Dict of drift by asset
        """
        all_assets = set(target_weights.keys()) | set(current_weights.keys())
        
        drift = {}
        for asset in all_assets:
            target = target_weights.get(asset, 0)
            current = current_weights.get(asset, 0)
            drift[asset] = abs(current - target)
        
        return drift
    
    def needs_rebalancing(
        self,
        target_weights: Dict[str, float],
        current_weights: Dict[str, float],
    ) -> bool:
        """Check if rebalancing is needed"""
        drift = self.check_drift(target_weights, current_weights)
        return max(drift.values()) > self.threshold
    
    def generate_trades(
        self,
        target_weights: Dict[str, float],
        current_weights: Dict[str, float],
        portfolio_value: float,
        prices: Dict[str, float],
    ) -> List[Dict]:
        """
        Generate rebalancing trades
        
        Returns:
            List of trades to execute
        """
        trades = []
        
        all_assets = set(target_weights.keys()) | set(current_weights.keys())
        
        for asset in all_assets:
            target = target_weights.get(asset, 0)
            current = current_weights.get(asset, 0)
            
            weight_diff = target - current
            
            if abs(weight_diff) > self.threshold:
                # Calculate trade
                value_to_trade = weight_diff * portfolio_value
                price = prices.get(asset, 0)
                
                if price > 0:
                    shares = value_to_trade / price
                    
                    trades.append({
                        "asset": asset,
                        "action": "buy" if weight_diff > 0 else "sell",
                        "shares": abs(shares),
                        "value": abs(value_to_trade),
                        "target_weight": target,
                        "current_weight": current,
                    })
        
        # Sort by value (largest first)
        trades.sort(key=lambda x: x["value"], reverse=True)
        
        # Apply turnover constraint
        total_turnover = sum(t["value"] for t in trades)
        if total_turnover > self.max_turnover * portfolio_value:
            # Scale down
            scale = (self.max_turnover * portfolio_value) / total_turnover
            for trade in trades:
                trade["value"] *= scale
                trade["shares"] *= scale
        
        return trades
    
    def tax_aware_rebalance(
        self,
        target_weights: Dict[str, float],
        current_weights: Dict[str, float],
        portfolio_value: float,
        prices: Dict[str, float],
        tax_lots: Dict[str, List[Dict]],  # Asset -> list of purchase lots
        tax_rate: float = 0.15,
    ) -> List[Dict]:
        """
        Tax-aware rebalancing (harvest losses, defer gains)
        """
        trades = []
        
        # First, identify tax loss harvesting opportunities
        for asset, lots in tax_lots.items():
            current_price = prices.get(asset, 0)
            
            for lot in lots:
                if current_price < lot["purchase_price"]:
                    # Loss harvesting opportunity
                    unrealized_loss = (lot["purchase_price"] - current_price) * lot["shares"]
                    
                    trades.append({
                        "asset": asset,
                        "action": "sell",
                        "sh
