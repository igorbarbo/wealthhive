"""
Quantitative finance endpoints
"""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_active_user, get_db
from quant.portfolio.markowitz import MarkowitzOptimizer
from quant.portfolio.black_litterman import BlackLittermanOptimizer
from quant.risk.var import VaRCalculator

router = APIRouter()


@router.post("/optimize/markowitz", response_model=dict)
async def optimize_markowitz(
    asset_ids: List[UUID],
    target_return: float = None,
    target_risk: float = None,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Optimize portfolio using Markowitz mean-variance optimization"""
    from infrastructure.database.repositories.asset_repository import AssetRepository
    
    asset_repo = AssetRepository(db)
    assets = []
    
    for asset_id in asset_ids:
        asset = await asset_repo.get_by_id(asset_id)
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asset {asset_id} not found",
            )
        assets.append(asset)
    
    optimizer = MarkowitzOptimizer()
    result = optimizer.optimize(
        symbols=[a.symbol for a in assets],
        target_return=target_return,
        target_risk=target_risk,
    )
    
    return {
        "method": "markowitz",
        "optimal_weights": result["weights"],
        "expected_return": result["expected_return"],
        "expected_risk": result["expected_risk"],
        "sharpe_ratio": result["sharpe_ratio"],
        "frontier": result["efficient_frontier"],
        "assets": [{"id": a.id, "symbol": a.symbol, "weight": w} for a, w in zip(assets, result["weights"])],
    }


@router.post("/optimize/black-litterman", response_model=dict)
async def optimize_black_litterman(
    asset_ids: List[UUID],
    views: List[dict],  # [{"asset": "PETR4", "return": 0.15, "confidence": 0.7}]
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Optimize using Black-Litterman model with investor views"""
    from infrastructure.database.repositories.asset_repository import AssetRepository
    
    asset_repo = AssetRepository(db)
    assets = []
    
    for asset_id in asset_ids:
        asset = await asset_repo.get_by_id(asset_id)
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asset {asset_id} not found",
            )
        assets.append(asset)
    
    optimizer = BlackLittermanOptimizer()
    result = optimizer.optimize(
        symbols=[a.symbol for a in assets],
        views=views,
    )
    
    return {
        "method": "black_litterman",
        "optimal_weights": result["weights"],
        "expected_return": result["expected_return"],
        "expected_risk": result["expected_risk"],
        "posterior_returns": result["posterior_returns"],
        "assets": [{"id": a.id, "symbol": a.symbol, "weight": w} for a, w in zip(assets, result["weights"])],
    }


@router.post("/risk/var", response_model=dict)
async def calculate_var(
    portfolio_id: UUID,
    confidence_level: float = 0.95,
    time_horizon_days: int = 1,
    method: str = "historical",  # historical, parametric, monte_carlo
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Calculate Value at Risk for portfolio"""
    from infrastructure.database.repositories.portfolio_repository import PortfolioRepository
    
    portfolio_repo = PortfolioRepository(db)
    portfolio = await portfolio_repo.get_by_id(portfolio_id)
    
    if not portfolio or portfolio.user_id != UUID(current_user["id"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )
    
    calculator = VaRCalculator(method=method)
    var_result = calculator.calculate(
        portfolio=portfolio,
        confidence_level=confidence_level,
        time_horizon=time_horizon_days,
    )
    
    return {
        "portfolio_id": portfolio_id,
        "method": method,
        "confidence_level": confidence_level,
        "time_horizon_days": time_horizon_days,
        "var_amount": var_result["var_amount"],
        "var_percent": var_result["var_percent"],
        "portfolio_value": portfolio.total_value,
        "interpretation": f"With {confidence_level*100}% confidence, the portfolio will not lose more than {var_result['var_percent']:.2f}% ({var_result['var_amount']:,.2f}) in the next {time_horizon_days} day(s)",
    }


@router.post("/risk/cvar", response_model=dict)
async def calculate_cvar(
    portfolio_id: UUID,
    confidence_level: float = 0.95,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Calculate Conditional Value at Risk (Expected Shortfall)"""
    from quant.risk.cvar import CVaRCalculator
    from infrastructure.database.repositories.portfolio_repository import PortfolioRepository
    
    portfolio_repo = PortfolioRepository(db)
    portfolio = await portfolio_repo.get_by_id(portfolio_id)
    
    if not portfolio or portfolio.user_id != UUID(current_user["id"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )
    
    calculator = CVaRCalculator()
    cvar_result = calculator.calculate(
        portfolio=portfolio,
        confidence_level=confidence_level,
    )
    
    return {
        "portfolio_id": portfolio_id,
        "confidence_level": confidence_level,
        "cvar_amount": cvar_result["cvar_amount"],
        "cvar_percent": cvar_result["cvar_percent"],
        "interpretation": f"Given that the loss exceeds VaR, the expected loss is {cvar_result['cvar_percent']:.2f}%",
    }


@router.post("/snowball", response_model=dict)
async def snowball_simulation(
    initial_investment: float,
    monthly_contribution: float,
    annual_return_rate: float,
    years: int = 20,
    reinvest_dividends: bool = True,
    dividend_yield: float = 0.04,
    current_user: dict = Depends(get_current_active_user),
) -> Any:
    """Calculate snowball effect (compound growth with contributions)"""
    from quant.portfolio.snowball_simulation import SnowballSimulator
    
    simulator = SnowballSimulator()
    result = simulator.calculate(
        initial_investment=initial_investment,
        monthly_contribution=monthly_contribution,
        annual_return_rate=annual_return_rate,
        years=years,
        reinvest_dividends=reinvest_dividends,
        dividend_yield=dividend_yield,
    )
    
    return {
        "initial_investment": initial_investment,
        "total_contributions": result["total_contributions"],
        "total_dividends": result["total_dividends"],
        "final_value": result["final_value"],
        "total_return": result["total_return"],
        "total_return_percent": result["total_return_percent"],
        "years": years,
        "monthly_breakdown": result["monthly_data"],
        "milestones": result["milestones"],  # When reached 100k, 500k, 1M, etc.
  }
  
