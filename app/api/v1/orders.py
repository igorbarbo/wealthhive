"""
Order management endpoints
"""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_active_user, get_db
from infrastructure.database.repositories.portfolio_repository import PortfolioRepository
from infrastructure.message_queue.celery_tasks import execute_order_task

router = APIRouter()


@router.get("/", response_model=List[dict])
async def list_orders(
    portfolio_id: UUID = None,
    status: str = None,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """List orders for user"""
    from infrastructure.database.repositories.order_repository import OrderRepository
    
    order_repo = OrderRepository(db)
    
    if portfolio_id:
        # Verify portfolio belongs to user
        portfolio_repo = PortfolioRepository(db)
        portfolio = await portfolio_repo.get_by_id(portfolio_id)
        if not portfolio or portfolio.user_id != UUID(current_user["id"]):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found",
            )
        orders = await order_repo.get_by_portfolio(portfolio_id, status=status)
    else:
        orders = await order_repo.get_by_user(UUID(current_user["id"]), status=status)
    
    return [
        {
            "id": order.id,
            "portfolio_id": order.portfolio_id,
            "asset_id": order.asset_id,
            "order_type": order.order_type,
            "side": order.side,
            "quantity": order.quantity,
            "price": order.price,
            "status": order.status,
            "created_at": order.created_at,
        }
        for order in orders
    ]


@router.post("/", response_model=dict)
async def create_order(
    portfolio_id: UUID,
    asset_id: UUID,
    order_type: str,  # market, limit, stop
    side: str,  # buy, sell
    quantity: float,
    price: float = None,  # Required for limit orders
    stop_price: float = None,  # Required for stop orders
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Create new order"""
    portfolio_repo = PortfolioRepository(db)
    portfolio = await portfolio_repo.get_by_id(portfolio_id)
    
    if not portfolio or portfolio.user_id != UUID(current_user["id"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )
    
    from infrastructure.database.repositories.order_repository import OrderRepository
    order_repo = OrderRepository(db)
    
    order = await order_repo.create(
        portfolio_id=portfolio_id,
        asset_id=asset_id,
        order_type=order_type,
        side=side,
        quantity=quantity,
        price=price,
        stop_price=stop_price,
        status="pending",
    )
    
    # Execute order asynchronously
    execute_order_task.delay(str(order.id))
    
    return {
        "id": order.id,
        "status": order.status,
        "message": "Order created and queued for execution",
    }


@router.get("/{order_id}", response_model=dict)
async def get_order(
    order_id: UUID,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get order by ID"""
    from infrastructure.database.repositories.order_repository import OrderRepository
    
    order_repo = OrderRepository(db)
    order = await order_repo.get_by_id(order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    
    # Verify ownership
    portfolio_repo = PortfolioRepository(db)
    portfolio = await portfolio_repo.get_by_id(order.portfolio_id)
    if portfolio.user_id != UUID(current_user["id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this order",
        )
    
    return {
        "id": order.id,
        "portfolio_id": order.portfolio_id,
        "asset_id": order.asset_id,
        "order_type": order.order_type,
        "side": order.side,
        "quantity": order.quantity,
        "price": order.price,
        "filled_quantity": order.filled_quantity,
        "avg_fill_price": order.avg_fill_price,
        "status": order.status,
        "created_at": order.created_at,
        "updated_at": order.updated_at,
    }


@router.delete("/{order_id}", response_model=dict)
async def cancel_order(
    order_id: UUID,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Cancel pending order"""
    from infrastructure.database.repositories.order_repository import OrderRepository
    
    order_repo = OrderRepository(db)
    order = await order_repo.get_by_id(order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    
    if order.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending orders can be cancelled",
        )
    
    # Verify ownership
    portfolio_repo = PortfolioRepository(db)
    portfolio = await portfolio_repo.get_by_id(order.portfolio_id)
    if portfolio.user_id != UUID(current_user["id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this order",
        )
    
    await order_repo.update_status(order_id, "cancelled")
    return {"message": "Order cancelled successfully"}
