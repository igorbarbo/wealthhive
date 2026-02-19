"""
Portfolio business logic service
"""

from typing import Any, Dict, List
from uuid import UUID

import structlog

from infrastructure.cache.redis_client import RedisCache
from infrastructure.database.repositories.portfolio_repository import PortfolioRepository

logger = structlog.get_logger()


class PortfolioService:
    """Portfolio business logic"""
    
    def __init
  
    """Portfolio business logic"""
    
    def __init__(self, db_session):
        self.db = db_session
        self.cache = RedisCache()
        self.repo = PortfolioRepository(db_session)
    
    async def calculate_portfolio_value(self, portfolio_id: UUID) -> Dict[str, Any]:
        """Calculate current portfolio value and metrics"""
        portfolio = await self.repo.get_by_id(portfolio_id)
        if not portfolio:
            raise ValueError("Portfolio not found")
        
        from app.services.market_data_service import MarketDataService
        market_service = MarketDataService()
        
        total_value = 0.0
        total_cost = 0.0
        positions_data = []
        
        for position in portfolio.positions:
            # Get current price
            price_data = await market_service.get_price(position.asset.symbol)
            current_price = price_data.get("price", position.avg_price)
            
            market_value = position.quantity * current_price
            cost_basis = position.quantity * position.avg_price
            unrealized_pnl = market_value - cost_basis
            
            total_value += market_value
            total_cost += cost_basis
            
            positions_data.append({
                "asset_id": position.asset_id,
                "symbol": position.asset.symbol,
                "quantity": position.quantity,
                "avg_price": position.avg_price,
                "current_price": current_price,
                "market_value": market_value,
                "unrealized_pnl": unrealized_pnl,
                "return_percent": (unrealized_pnl / cost_basis * 100) if cost_basis > 0 else 0,
            })
        
        total_return = total_value - portfolio.initial_balance
        total_return_percent = (total_return / portfolio.initial_balance * 100) if portfolio.initial_balance > 0 else 0
        
        result = {
            "portfolio_id": portfolio_id,
            "total_value": total_value,
            "initial_balance": portfolio.initial_balance,
            "total_return": total_return,
            "total_return_percent": total_return_percent,
            "positions": positions_data,
            "cash": portfolio.initial_balance - total_cost + sum(p["unrealized_pnl"] for p in positions_data),
        }
        
        # Update portfolio in database
        await self.repo.update_value(
            portfolio_id=portfolio_id,
            total_value=total_value,
            total_return=total_return,
            total_return_percent=total_return_percent,
        )
        
        return result
    
    async def rebalance_portfolio(
        self,
        portfolio_id: UUID,
        target_weights: Dict[str, float],
    ) -> Dict[str, Any]:
        """Generate rebalancing recommendations]:
        """Generate rebalancing recommendations"""
        portfolio = await self.repo.get_by_id(portfolio_id)
        if not portfolio:
            raise ValueError("Portfolio not found")
        
        current = await self.calculate_portfolio_value(portfolio_id)
        total_value = current["total_value"]
        
        recommendations = []
        
        for position in current["positions"]:
            symbol = position["symbol"]
            current_weight = position["market_value"] / total_value if total_value > 0 else 0
            target_weight = target_weights.get(symbol, 0)
            
            weight_diff = target_weight - current_weight
            value_diff = weight_diff * total_value
            
            if abs(weight_diff) > 0.01:  # 1% threshold
                recommendations.append({
                    "symbol": symbol,
                    "current_weight": round(current_weight * 100, 2),
                    "target_weight": round(target_weight * 100, 2),
                    "action": "buy" if weight_diff > 0 else "sell",
                    "value": abs(value_diff),
                    "shares": abs(value_diff / position["current_price"]) if position["current_price"] > 0 else 0,
                })
        
        return {
            "portfolio_id": portfolio_id,
            "total_value": total_value,
            "recommendations": recommendations,
            "expected_turnover": sum(r["value"] for r in recommendations) / 2,
        }
    
    async def get_performance_metrics(self, portfolio_id: UUID) -> Dict[str, Any]:
        """Calculate portfolio performance metrics"""
        from quant.risk.var import VaRCalculator
        from quant.portfolio.markowitz import MarkowitzOptimizer
        
        portfolio = await self.repo.get_by_id(portfolio_id)
        if not portfolio:
            raise ValueError("Portfolio not found")
        
        # Get historical data for calculations
        current = await self.calculate_portfolio_value(portfolio_id)
        
        # Calculate VaR
        var_calc = VaRCalculator()
        var_result = var_calc.calculate(portfolio=portfolio, confidence_level=0.95)
        
        return {
            "portfolio_id": portfolio_id,
            "total_value": current["total_value"],
            "total_return": current["total_return"],
            "total_return_percent": current["total_return_percent"],
            "var_95": var_result.get("var_amount"),
            "var_95_percent": var_result.get("var_percent"),
            "position_count": len(current["positions"]),
            "concentration": self._calculate_concentration(current["positions"]),
        }
    
    def _calculate_concentration(self, positions: List[Dict]) -> Dict[str, float]:
        """Calculate portfolio concentration metrics"""
        if not positions:
            return {"hhi": 0, "top_5_percent": 0}
        
        total_value = sum(p["market_value"] for p in positions)
        weights = [p["market_value"] / total_value for p in positions]
        
        # Herfindahl-Hirschman Index
        hhi = sum(w ** 2 for w in weights)
        
        # Top 5 concentration
        sorted_weights = sorted(weights, reverse=True)
        top_5_percent = sum(sorted_weights[:5]) * 100
        
        return {
            "hhi": round(hhi, 4),
            "top_5_percent": round(top_5_percent, 2),
        }
        
