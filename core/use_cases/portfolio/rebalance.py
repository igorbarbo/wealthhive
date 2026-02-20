"""
Portfolio rebalancing use case
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List
from uuid import UUID


@dataclass
class RebalanceRecommendation:
    """Rebalancing recommendation"""
    asset_id: UUID
    symbol: str
    current_weight: float
    target_weight: float
    action: str  # buy, sell, hold
    value_difference: Decimal
    shares_to_trade: Decimal


class RebalanceUseCase:
    """Generate portfolio rebalancing recommendations"""
    
    def __init__(self, portfolio_repository, asset_repository):
        self.portfolio_repo = portfolio_repository
        self.asset_repo = asset_repository
    
    async def execute(
        self,
        portfolio_id: UUID,
        target_weights: Dict[UUID, float],
        threshold: float = 0.05,  # 5% drift threshold
    ) -> Dict:
        """
        Generate rebalancing recommendations
        
        Args:
            portfolio_id: Portfolio to rebalance
            target_weights: Target allocation {asset_id: weight}
            threshold: Minimum drift to trigger rebalancing
        """
        portfolio = await self.portfolio_repo.get_by_id(portfolio_id)
        if not portfolio:
            raise ValueError("Portfolio not found")
        
        # Calculate current weights
        total_value = portfolio.total_value or Decimal("0")
        if total_value == 0:
            return {"error": "Portfolio has no value"}
        
        current_weights = {}
        recommendations = []
        total_drift = 0
        
        for asset_id, position in portfolio.positions.items():
            current_weight = float(position.cost_basis / total_value)
            current_weights[asset_id] = current_weight
            
            target_weight = target_weights.get(asset_id, 0)
            drift = abs(current_weight - target_weight)
            total_drift += drift
            
            if drift > threshold:
                value_diff = Decimal(str(target_weight - current_weight)) * total_value
                
                # Get current price
                asset = await self.asset_repo.get_by_id(asset_id)
                current_price = position.cost_basis / position.quantity if position.quantity > 0 else Decimal("1")
                
                shares = abs(value_diff / current_price) if current_price > 0 else Decimal("0")
                
                recommendations.append(RebalanceRecommendation(
                    asset_id=asset_id,
                    symbol=asset.symbol if asset else "Unknown",
                    current_weight=round(current_weight * 100, 2),
                    target_weight=round(target_weight * 100, 2),
                    action="buy" if value_diff > 0 else "sell",
                    value_difference=abs(value_diff),
                    shares_to_trade=round(shares, 4),
                ))
        
        # Check for new assets to add
        for asset_id, target_weight in target_weights.items():
            if asset_id not in current_weights and target_weight > 0:
                asset = await self.asset_repo.get_by_id(asset_id)
                # Would need current price from market data
                value_diff = Decimal(str(target_weight)) * total_value
                
                recommendations.append(RebalanceRecommendation(
                    asset_id=asset_id,
                    symbol=asset.symbol if asset else "Unknown",
                    current_weight=0,
                    target_weight=round(target_weight * 100, 2),
                    action="buy",
                    value_difference=value_diff,
                    shares_to_trade=Decimal("0"),  # Would calculate based on price
                ))
        
        return {
            "portfolio_id": portfolio_id,
            "total_value": total_value,
            "total_drift": round(total_drift * 100, 2),
            "needs_rebalancing": len(recommendations) > 0,
            "recommendations": recommendations,
            "expected_turnover": sum(r.value_difference for r in recommendations) / 2,
            "estimated_fees": sum(r.value_difference for r in recommendations) * Decimal("0.001"),  # 0.1% fee estimate
        }
      
