"""
Reporting endpoints
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_active_user, get_db
from infrastructure.message_queue.celery_tasks import generate_report_task

router = APIRouter()


@router.post("/portfolio/{portfolio_id}", response_model=dict)
async def generate_portfolio_report(
    portfolio_id: UUID,
    report_type: str = "full",  # full, performance, risk, tax
    start_date: str = None,
    end_date: str = None,
    format: str = "pdf",  # pdf, excel, json
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Generate portfolio report"""
    from infrastructure.database.repositories.portfolio_repository import PortfolioRepository
    
    portfolio_repo = PortfolioRepository(db)
    portfolio = await portfolio_repo.get_by_id(portfolio_id)
    
    if not portfolio or portfolio.user_id != UUID(current_user["id"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )
    
    task = generate_report_task.delay(
        report_type="portfolio",
        entity_id=str(portfolio_id),
        user_id=current_user["id"],
        start_date=start_date,
        end_date=end_date,
        format=format,
    )
    
    return {
        "task_id": task.id,
        "status": "queued",
        "message": f"Portfolio report generation queued",
        "download_url": f"/api/v1/reports/download/{task.id}",
    }


@router.post("/backtest/{backtest_id}", response_model=dict)
async def generate_backtest_report(
    backtest_id: UUID,
    format: str = "pdf",
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Generate backtest report"""
    from infrastructure.database.repositories.backtest_repository import BacktestRepository
    
    backtest_repo = BacktestRepository(db)
    backtest = await backtest_repo.get_by_id(backtest_id)
    
    if not backtest or backtest.user_id != UUID(current_user["id"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Backtest not found",
        )
    
    task = generate_report_task.delay(
        report_type="backtest",
        entity_id=str(backtest_id),
        user_id=current_user["id"],
        format=format,
    )
    
    return {
        "task_id": task.id,
        "status": "queued",
        "message": "Backtest report generation queued",
    }


@router.get("/download/{task_id}")
async def download_report(
    task_id: str,
    current_user: dict = Depends(get_current_active_user),
) -> Any:
    """Download generated report"""
    from celery.result import AsyncResult
    
    task = AsyncResult(task_id)
    
    if not task.ready():
        return {
            "task_id": task_id,
            "status": task.status,
            "progress": task.info.get("progress", 0) if task.info else 0,
        }
    
    if task.failed():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Report generation failed",
        )
    
    result = task.result
    file_path = result.get("file_path")
    
    # Return file
    def iterfile():
        with open(file_path, "rb") as f:
            yield from f
    
    return StreamingResponse(
        iterfile(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={result.get('filename', 'report.pdf')}"},
    )


@router.get("/status/{task_id}", response_model=dict)
async def get_report_status(
    task_id: str,
    current_user: dict = Depends(get_current_active_user),
) -> Any:
    """Check report generation status"""
    from celery.result import AsyncResult
    
    task = AsyncResult(task_id)
    
    return {
        "task_id": task_id,
        "status": task.status,
        "progress": task.info.get("progress", 0) if task.info else 0,
        "ready": task.ready(),
        "successful": task.successful() if task.ready() else None,
  }
  
