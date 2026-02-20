"""
Model inference for production
"""

from typing import Any, Dict

import numpy as np

from ml.features.feature_engineering import FeatureEngineer


class MLPredictor:
    """Production ML predictor"""
    
    def __init__(self, model_id: str = "ensemble-v1"):
        self.model_id = model_id
        self.model = None
        self.feature_engineer = FeatureEngineer()
        self._load_model()
    
    def _load_model(self):
        """Load model from registry"""
        from ml.inference.model_registry import ModelRegistry
        
        registry = ModelRegistry()
        self.model = registry.load(self.model_id)
    
    async def predict(
        self,
        symbol: str,
        horizon_days: int = 5,
    ) -> Dict[str, Any]:
        """Generate prediction"""
        # Fetch recent data
        # This would call market data service
        recent_data = await self._fetch_recent_data(symbol)
        
        # Engineer features
        features = self.feature_engineer.prepare_features(recent_data)
        X = features.values[-1:]  # Last row
        
        # Predict
        if hasattr(self.model, "predict"):
            prediction = self.model.predict(X)[0]
        else:
            prediction = 0
        
        # Generate price path
        current_price = recent_data["close"].iloc[-1]
        predicted_prices = self._generate_price_path(
            current_price,
            prediction,
            horizon_days,
        )
        
        # Confidence intervals
        confidence = self._calculate_confidence(X)
        
        return {
            "current_price": round(current_price, 2),
            "predicted_prices": [round(p, 2) for p in predicted_prices],
            "confidence_intervals": self._calculate_intervals(
                predicted_prices,
                confidence,
            ),
            "direction": "up" if prediction > 0.02 else "down" if prediction < -0.02 else "neutral",
            "confidence": round(confidence, 2),
            "generated_at": str(np.datetime64("now")),
        }
    
    async def _fetch_recent_data(self, symbol: str):
        """Fetch recent market data"""
        from app.services.market_data_service import MarketDataService
        
        service = MarketDataService()
        data = await service.get_historical(symbol, period="3mo", interval="1d")
        return data
    
    def _generate_price_path(
        self,
        current_price: float,
        expected_return: float,
        days: int,
    ) -> list:
        """Generate predicted price path"""
        daily_return = expected_return / days
        prices = [current_price]
        
        for _ in range(days):
            next_price = prices[-1] * (1 + daily_return)
            prices.append(next_price)
        
        return prices[1:]  # Exclude current
    
    def _calculate_confidence(self, X: np.ndarray) -> float:
        """Calculate prediction confidence"""
        # Based on model uncertainty or feature distance from training
        return 0.75  # Placeholder
    
    def _calculate_intervals(self, prices: list, confidence: float) -> list:
        """Calculate confidence intervals"""
        intervals = []
        width = (1 - confidence) * 0.5
        
        for price in prices:
            lower = price * (1 - width)
            upper = price * (1 + width)
            intervals.append({
                "lower": round(lower, 2),
                "upper": round(upper, 2),
            })
        
        return intervals
