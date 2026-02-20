"""
Model training orchestrator
"""

from typing import Any, Dict, List

import numpy as np
from sklearn.model_selection import TimeSeriesSplit

from ml.features.feature_engineering import FeatureEngineer
from ml.models.ensemble_model import create_default_ensemble
from ml.models.lstm_model import LSTMPredictor


class ModelTrainer:
    """Orchestrate model training"""
    
    def __init__(self, model_type: str = "ensemble"):
        self.model_type = model_type
        self.model = None
        self.feature_engineer = FeatureEngineer()
        self.metrics = {}
    
    def prepare_data(
        self,
        price_data: np.ndarray,
        target_horizon: int = 5,
    ) -> tuple:
        """Prepare training data"""
        # Create features
        features_df = self.feature_engineer.prepare_features(price_data)
        
        # Create target
        target = self.feature_engineer.create_target_variable(
            price_data,
            horizon=target_horizon,
        )
        
        # Align features and target
        features_df = features_df.loc[target.index]
        target = target.loc[features_df.index]
        
        X = features_df.values
        y = target.values
        
        return X, y, features_df.columns.tolist()
    
    def train(
        self,
        price_data: np.ndarray,
        validation_split: float = 0.2,
    ) -> Dict[str, Any]:
        """Train model"""
        X, y, feature_names = self.prepare_data(price_data)
        
        # Time series split for validation
        split_idx = int(len(X) * (1 - validation_split))
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        if self.model_type == "ensemble":
            self.model = create_default_ensemble()
            self.model.fit(X_train, y_train)
            
            # Validation metrics
            val_preds = self.model.predict(X_val)
            self.metrics = self._calculate_metrics(y_val, val_preds["ensemble"])
            
        elif self.model_type == "lstm":
            # Reshape for LSTM [samples, timesteps, features]
            seq_length = 60
            self.model = LSTMPredictor(
                input_size=X.shape[1],
                seq_length=seq_length,
            )
            
            train_loader = self.model.prepare_data(X_train, y_train)
            losses = self.model.train(train_loader, epochs=50)
            
            self.metrics = {"final_loss": losses[-1]}
        
        return {
            "model_type": self.model_type,
            "metrics": self.metrics,
            "feature_names": feature_names,
            "training_samples": len(X_train),
            "validation_samples": len(X_val),
        }
    
    def _calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Calculate regression metrics"""
        mse = np.mean((y_true - y_pred) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(y_true - y_pred))
        
        # Directional accuracy
        direction_true = np.sign(np.diff(y_true))
        direction_pred = np.sign(np.diff(y_pred))
        directional_accuracy = np.mean(direction_true == direction_pred)
        
        return {
            "mse": mse,
            "rmse": rmse,
            "mae": mae,
            "directional_accuracy": directional_accuracy,
        }
    
    def save(self, path: str):
        """Save model"""
        import pickle
        
        with open(path, "wb") as f:
            pickle.dump({
                "model": self.model,
                "metrics": self.metrics,
                "model_type": self.model_type,
            }, f)
    
    def load(self, path: str):
        """Load model"""
        import pickle
        
        with open(path, "rb") as f:
            data = pickle.load(f)
            self.model = data["model"]
            self.metrics = data["metrics"]
            self.model_type = data["model_type"]
          
