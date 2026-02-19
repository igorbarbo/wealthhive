"""
Portfolio management endpoints
"""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_active_user, get_db
from infrastructure.database.repositories.portfolio_repository import PortfolioRepository

router = APIRouter()


@router.get("/", response_model=List[dict])
async def list_portfolios(
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """List all portfolios for current user"""
    portfolio_repo = PortfolioRepository(db)
    portfolios = await portfolio_repo.get_by_user_id(UUID(current_user["id"]))
    
    return [
        {
            "id": portfolio.id,
            "name": portfolio.name,
            "description": portfolio.description,
            "total_value": portfolio.total_value,
            "total_return": portfolio.total_return,
            "total_return_percent": portfolio.total_return_percent,
            "created_at": portfolio.created_at,
        }
        for portfolio in portfolios
    ]


@router.post("/", response_model=dict)
async def create_portfolio(
    name: str,
    description: str = None,
    initial_balance: float = 0.0,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Create new portfolio"""
    portfolio_repo = PortfolioRepository(db)
    
    portfolio = await portfolio_repo.create(
        user_id=UUID(current_user["id"]),
        name=name,
        description=description,
        initial_balance=initial_balance,
    )
    
    return {
        "id": portfolio.id,
        "name": portfolio.name,
        "description": portfolio.description,
        "initial_balance": portfolio.initial_balance,
        "message": "Portfolio created successfully",
    }


@router.get("/{portfolio_id}", response_model=dict)
async def get_portfolio(
    portfolio_id: UUID,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get portfolio by ID"""
    portfolio_repo = PortfolioRepository(db)
    portfolio = await portfolio_repo.get_by_id(portfolio_id)
    
    if not portfolio or portfolio.user_id != UUID(current_user["id"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )
    
    return {
        "id": portfolio.id,
        "name": portfolio.name,
        "description": portfolio.description,
        "initial_balance": portfolio.initial_balance,
        "total_value": portfolio.total_value,
        "total_return": portfolio.total_return,
        "total_return_percent": portfolio.total_return_percent,
        "positions": [
            {
                "asset_id": pos.asset_id,
                "asset_symbol": pos.asset_symbol,
                "quantity": pos.quantity,
                "avg_price": pos.avg_price,
                "current_price": pos.current_price,
                "market_value": pos.market_value,
                "unrealized_pnl": pos.unrealized_pnl,
            }
            for pos in portfolio.positions
        ],
        "created_at": portfolio.created_at,
    }


@router.put("/{portfolio_id}", response_model=dict)
async def update_portfolio(
    portfolio_id: UUID,
    name: str = None,
    description: str = None,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Update portfolio"""
    portfolio_repo = PortfolioRepository(db)
    portfolio = await portfolio_repo.get_by_id(portfolio_id)
    
    if not portfolio or portfolio.user_id != UUID(current_user["id"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )
    
    updated = await portfolio_repo.update(
        portfolio_id=portfolio_id,
        name=name,
        description=description,
    )
    
    return {
        "id": updated.id,
        "name": updated.name,
        "message": "Portfolio updated successfully",
    }


@router.delete("/{portfolio_id}", response_model=dict)
async def delete_portfolio(
    portfolio_id: UUID,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Delete portfolio"""
    portfolio_repo = PortfolioRepository(db)
    portfolio = await portfolio_repo.get_by_id(portfolio_id)
    
    if not portfolio or portfolio.user_id != UUID(current_user["id"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )
    
    await portfolio_repo.delete(portfolio_id)
    return {"message": "Portfolio deleted successfully"}


@router.post("/{portfolio_id}/positions", response_model=dict)
async def add_position(
    portfolio_id: UUID,
    asset_id: UUID,
    quantity: float,
    price: float,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Add position to portfolio"""
    portfolio_repo = PortfolioRepository(db)
    portfolio = await portfolio_repo.get_by_id(portfolio_id)
    
    if not portfolio or portfolio.user_id != UUID(current_user["id"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )
    
    position = await portfolio_repo.add_position(
        portfolio_id=portfolio_id,
        asset_id=asset_id,
        quantity=quantity,
        price=price,
    )
    
    return {
        "id": position.id,
        "asset_id": position.asset_id,
        "quantity": position.quantity,
        "avg_price": position.avg_price,
        "message": "Position added successfully",
    }
