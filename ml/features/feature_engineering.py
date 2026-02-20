"""
Main feature engineering pipeline
"""

from typing import Any, Dict, List

import numpy as np
import pandas as pd

from ml.features.fundamental_features import FundamentalFeatures
from ml.features.technical_indicators import TechnicalIndicators


class FeatureEngineer:
    """Feature engineering pipeline"""
    
    def __init__(self):
        self.technical = TechnicalIndicators()
        self.fundamental = FundamentalFeatures()
    
    def create_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create price-based features"""
        features = df.copy()
        
        # Returns
        features["returns"] = df["close"].pct_change()
        features["log_returns"] = np.log(df["close"] / df["close"].shift(1))
        
        # Volatility
        features["volatility_20d"] = features["returns"].rolling(20).std() * np.sqrt(252)
        
        # Price position
        features["price_to_sma20"] = df["close"] / self.technical.sma(df["close"], 20)
        features["price_to_sma50"] = df["close"] / self.technical.sma(df["close"], 50)
        
        # High/Low ratios
        features["high_low_ratio"] = df["high"] / df["low"]
        features["close_to_high"] = df["close"] / df["high"]
        features["close_to_low"] = df["close"] / df["low"]
        
        return features
    
    def create_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create volume-based features"""
        features = df.copy()
        
        # Volume moving averages
        features["volume_sma_20"] = df["volume"].rolling(20).mean()
        features["volume_ratio"] = df["volume"] / features["volume_sma_20"]
        
        # Price-volume relationship
        features["price_volume_trend"] = (
            (df["close"] - df["close"].shift(1)) / df["close"].shift(1)
        ) * df["volume"]
        
        return features
    
    def create_lag_features(self, df: pd.DataFrame, lags: List[int] = None) -> pd.DataFrame:
        """Create lagged features"""
        if lags is None:
            lags = [1, 2, 3, 5, 10, 20]
        
        features = df.copy()
        
        for lag in lags:
            features[f"returns_lag_{lag}"] = df["close"].pct_change(lag)
            features[f"volume_lag_{lag}"] = df["volume"].shift(lag)
        
        return features
    
    def create_target_variable(
        self,
        df: pd.DataFrame,
        horizon: int = 5,
        threshold: float = 0.02,
    ) -> pd.Series:
        """Create target variable for classification"""
        future_returns = df["close"].pct_change(horizon).shift(-horizon)
        
        # Classify: -1 (down), 0 (neutral), 1 (up)
        target = pd.Series(0, index=df.index)
        target[future_returns > threshold] = 1
        target[future_returns < -threshold] = -1
        
        return target
    
    def prepare_features(
        self,
        price_data: pd.DataFrame,
        fundamental_data: Dict = None,
    ) -> pd.DataFrame:
        """Full feature preparation pipeline"""
        # Technical indicators
        df = self.technical.calculate_all(price_data)
        
        # Price features
        df = self.create_price_features(df)
        
        # Volume features
        df = self.create_volume_features(df)
        
        # Lag features
        df = self.create_lag_features(df)
        
        # Add fundamental features if available
        if fundamental_data:
            for key, value in fundamental_data.items():
                df[f"fund_{key}"] = value
        
        # Drop NaN values
        df = df.dropna()
        
        return df
    
    def get_feature_importance(self, model, feature_names: List[str]) -> Dict[str, float]:
        """Get feature importance from trained model"""
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
        elif hasattr(model, "coef_"):
            importances = np.abs(model.coef_[0])
        else:
            return {}
        
        return dict(sorted(
            zip(feature_names, importances),
            key=lambda x: x[1],
            reverse=True,
        ))
