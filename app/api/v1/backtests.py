"""
Backtesting endpoints
"""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_active_user, get_db
from backtest.engine.backtest_engine import BacktestEngine
from infrastructure.message_queue.celery_tasks import run_backtest_task

router = APIRouter()


@router.post("/", response_model=dict)
async def create_backtest(
    portfolio_id: UUID,
    strategy_name: str,
    start_date: str,
    end_date: str,
    initial_capital: float = 100000.0,
    parameters: dict = None,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Create and run backtest"""
    from infrastructure.database.repositories.portfolio_repository import PortfolioRepository
    
    portfolio_repo = PortfolioRepository(db)
    portfolio = await portfolio_repo.get_by_id(portfolio_id)
    
    if not portfolio or portfolio.user_id != UUID(current_user["id"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )
    
    # Create backtest record
    from infrastructure.database.models.backtest import Backtest
    backtest = Backtest(
        user_id=UUID(current_user["id"]),
        portfolio_id=portfolio_id,
        strategy_name=strategy_name,
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital,
        parameters=parameters or {},
        status="pending",
    )
    db.add(backtest)
    await db.commit()
    await db.refresh(backtest)
    
    # Run backtest asynchronously
    run_backtest_task.delay(
        backtest_id=str(backtest.id),
        strategy_name=strategy_name,
        portfolio_id=str(portfolio_id),
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital,
        parameters=parameters or {},
    )
    
    return {
        "id": backtest.id,
        "status": "pending",
        "message": "Backtest queued for execution",
    }


@router.get("/", response_model=List[dict])
async def list_backtests(
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """List all backtests for user"""
    from infrastructure.database.repositories.backtest_repository import BacktestRepository
    
    backtest_repo = BacktestRepository(db)
    backtests = await backtest_repo.get_by_user(UUID(current_user["id"]))
    
    return [
        {
            "id": bt.id,
            "strategy_name": bt.strategy_name,
            "start_date": bt.start_date,
            "end_date": bt.end_date,
            "initial_capital": bt.initial_capital,
            "final_capital": bt.final_capital,
            "total_return": bt.total_return,
            "sharpe_ratio": bt.sharpe_ratio,
            "max_drawdown": bt.max_drawdown,
            "status": bt.status,
            "created_at": bt.created_at,
        }
        for bt in backtests
    ]


@router.get("/{backtest_id}", response_model=dict)
async def get_backtest(
    backtest_id: UUID,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get backtest results"""
    from infrastructure.database.repositories.backtest_repository import BacktestRepository
    
    backtest_repo = BacktestRepository(db)
    backtest = await backtest_repo.get_by_id(backtest_id)
    
    if not backtest or backtest.user_id != UUID(current_user["id"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Backtest not found",
        )
    
    return {
        "id": backtest.id,
        "strategy_name": backtest.strategy_name,
        "start_date": backtest.start_date,
        "end_date": backtest.end_date,
        "initial_capital": backtest.initial_capital,
        "final_capital": backtest.final_capital,
        "total_return": backtest.total_return,
        "total_return_percent": backtest.total_return_percent,
        "sharpe_ratio": backtest.sharpe_ratio,
        "sortino_ratio": backtest.sortino_ratio,
        "max_drawdown": backtest.max_drawdown,
        "calmar_ratio": backtest.calmar_ratio,
        "win_rate": backtest.win_rate,
        "profit_factor": backtest.profit_factor,
        "trades": backtest.trades,
        "equity_curve": backtest.equity_curve,
        "status": backtest.status,
        "created_at": backtest.created_at,
    }


@router.delete("/{backtest_id}", response_model=dict)
async def delete_backtest(
    backtest_id: UUID,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Delete backtest"""
    from infrastructure.database.repositories.backtest_repository import BacktestRepository
    
    backtest_repo = BacktestRepository(db)
    backtest = await backtest_repo.get_by_id(backtest_id)
    
    if not backtest or backtest.user_id != UUID(current_user["id"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Backtest not found",
        )
    
    await backtest_repo.delete(backtest_id)
    return {"message": "Backtest deleted successfully"}
