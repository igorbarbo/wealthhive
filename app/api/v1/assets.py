"""
Asset management endpoints
"""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_active_user, get_db
from infrastructure.database.repositories.asset_repository import AssetRepository
from infrastructure.external.data_providers.yahoo_finance import YahooFinanceProvider

router = APIRouter()


@router.get("/", response_model=List[dict])
async def list_assets(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    asset_type: str = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """List all assets"""
    asset_repo = AssetRepository(db)
    assets = await asset_repo.get_all(
        skip=skip,
        limit=limit,
        search=search,
        asset_type=asset_type,
    )
    
    return [
        {
            "id": asset.id,
            "symbol": asset.symbol,
            "name": asset.name,
            "asset_type": asset.asset_type,
            "exchange": asset.exchange,
            "currency": asset.currency,
            "sector": asset.sector,
            "industry": asset.industry,
        }
        for asset in assets
    ]


@router.get("/search", response_model=List[dict])
async def search_assets(
    query: str = Query(..., min_length=2),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Search assets by symbol or name"""
    asset_repo = AssetRepository(db)
    assets = await asset_repo.search(query)
    
    return [
        {
            "id": asset.id,
            "symbol": asset.symbol,
            "name": asset.name,
            "asset_type": asset.asset_type,
            "exchange": asset.exchange,
        }
        for asset in assets
    ]


@router.get("/{asset_id}", response_model=dict)
async def get_asset(
    asset_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get asset by ID"""
    asset_repo = AssetRepository(db)
    asset = await asset_repo.get_by_id(asset_id)
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )
    
    return {
        "id": asset.id,
        "symbol": asset.symbol,
        "name": asset.name,
        "asset_type": asset.asset_type,
        "exchange": asset.exchange,
        "currency": asset.currency,
        "sector": asset.sector,
        "industry": asset.industry,
        "market_cap": asset.market_cap,
        "created_at": asset.created_at,
    }


@router.get("/{asset_id}/price", response_model=dict)
async def get_asset_price(
    asset_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get current asset price"""
    asset_repo = AssetRepository(db)
    asset = await asset_repo.get_by_id(asset_id)
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )
    
    # Fetch real-time price
    yahoo = YahooFinanceProvider()
    price_data = await yahoo.get_current_price(asset.symbol)
    
    return {
        "asset_id": asset.id,
        "symbol": asset.symbol,
        "price": price_data.get("price"),
        "change": price_data.get("change"),
        "change_percent": price_data.get("change_percent"),
        "volume": price_data.get("volume"),
        "timestamp": price_data.get("timestamp"),
    }


@router.get("/{asset_id}/history", response_model=dict)
async def get_asset_history(
    asset_id: UUID,
    period: str = "1y",
    interval: str = "1d",
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get asset price history"""
    asset_repo = AssetRepository(db)
    asset = await asset_repo.get_by_id(asset_id)
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )
    
    yahoo = YahooFinanceProvider()
    history = await yahoo.get_history(
        symbol=asset.symbol,
        period=period,
        interval=interval,
    )
    
    return {
        "asset_id": asset.id,
        "symbol": asset.symbol,
        "period": period,
        "interval": interval,
        "data": history,
    }


@router.post("/", response_model=dict)
async def create_asset(
    symbol: str,
    name: str,
    asset_type: str,
    exchange: str = None,
    currency: str = "BRL",
    sector: str = None,
    industry: str = None,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Create new asset"""
    asset_repo = AssetRepository(db)
    
    # Check if asset exists
    existing = await asset_repo.get_by_symbol(symbol)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Asset with this symbol already exists",
        )
    
    asset = await asset_repo.create(
        symbol=symbol,
        name=name,
        asset_type=asset_type,
        exchange=exchange,
        currency=currency,
        sector=sector,
        industry=industry,
    )
    
    return {
        "id": asset.id,
        "symbol": asset.symbol,
        "name": asset.name,
        "message": "Asset created successfully",
    }
