"""
Machine Learning endpoints
"""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.dependencies import get_current_active_user, get_db
from ml.inference.predictor import MLPredictor

router = APIRouter()


@router.get("/models", response_model=List[dict])
async def list_models(
    settings: Settings = Depends(get_settings),
) -> Any:
    """List available ML models"""
    if not settings.ENABLE_ML_PREDICTIONS:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML predictions are disabled",
        )
    
    return [
        {
            "id": "lstm-v1",
            "name": "LSTM Price Predictor",
            "type": "lstm",
            "description": "LSTM neural network for price prediction",
            "features": ["price", "volume", "rsi", "macd"],
        },
        {
            "id": "transformer-v1",
            "name": "Transformer Predictor",
            "type": "transformer",
            "description": "Transformer architecture for time series",
            "features": ["price", "volume", "technical_indicators"],
        },
        {
            "id": "ensemble-v1",
            "name": "Ensemble Model",
            "type": "ensemble",
            "description": "XGBoost + LSTM ensemble",
            "features": ["price", "volume", "fundamentals", "sentiment"],
        },
    ]


@router.post("/predict", response_model=dict)
async def predict(
    asset_id: UUID,
    model_id: str = "lstm-v1",
    horizon_days: int = 5,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Any:
    """Get ML prediction for asset"""
    if not settings.ENABLE_ML_PREDICTIONS:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML predictions are disabled",
        )
    
    from infrastructure.database.repositories.asset_repository import AssetRepository
    
    asset_repo = AssetRepository(db)
    asset = await asset_repo.get_by_id(asset_id)
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )
    
    predictor = MLPredictor(model_id=model_id)
    prediction = await predictor.predict(
        symbol=asset.symbol,
        horizon_days=horizon_days,
    )
    
    return {
        "asset_id": asset_id,
        "asset_symbol": asset.symbol,
        "model_id": model_id,
        "horizon_days": horizon_days,
        "current_price": prediction["current_price"],
        "predicted_prices": prediction["predicted_prices"],
        "confidence_intervals": prediction["confidence_intervals"],
        "direction": prediction["direction"],  # up, down, neutral
        "confidence": prediction["confidence"],
        "generated_at": prediction["generated_at"],
    }


@router.post("/train", response_model=dict)
async def train_model(
    model_id: str,
    asset_ids: List[UUID],
    start_date: str,
    end_date: str,
    current_user: dict = Depends(get_current_active_user),
    settings: Settings = Depends(get_settings),
) -> Any:
    """Trigger model training (async)"""
    if not settings.ENABLE_ML_PREDICTIONS:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML predictions are disabled",
        )
    
    from infrastructure.message_queue.celery_tasks import train_model_task
    
    task = train_model_task.delay(
        model_id=model_id,
        asset_ids=[str(aid) for aid in asset_ids],
        start_date=start_date,
        end_date=end_date,
        user_id=current_user["id"],
    )
    
    return {
        "task_id": task.id,
        "status": "training_started",
        "message": "Model training queued",
    }


@router.get("/sentiment-ml", response_model=dict)
async def get_ml_sentiment(
    asset_id: UUID,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Any:
    """Get ML-based sentiment analysis combining price and news"""
    if not settings.ENABLE_ML_PREDICTIONS:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML predictions are disabled",
        )
    
    from ml.features.feature_engineering import FeatureEngineer
    
    engineer = FeatureEngineer()
    sentiment = await engineer.get_combined_sentiment(asset_id)
    
    return {
        "asset_id": asset_id,
        "technical_sentiment": sentiment["technical"],
        "news_sentiment": sentiment["news"],
        "combined_sentiment": sentiment["combined"],
        "signal_strength": sentiment["strength"],
        "recommendation": sentiment["recommendation"],
    }
