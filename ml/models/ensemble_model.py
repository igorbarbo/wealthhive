"""
Ensemble model combining multiple predictors
"""

from typing import Dict, List

import numpy as np
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor


class EnsembleModel:
    """Ensemble of multiple models"""
    
    def __init__(self):
        self.models = {}
        self.weights = {}
    
    def add_model(self, name: str, model, weight: float = 1.0):
        """Add model to ensemble"""
        self.models[name] = model
        self.weights[name] = weight
    
    def fit(self, X: np.ndarray, y: np.ndarray):
        """Train all models"""
        for name, model in self.models.items():
            print(f"Training {name}...")
            if hasattr(model, "fit"):
                model.fit(X, y)
    
    def predict(self, X: np.ndarray) -> Dict[str, np.ndarray]:
        """Get predictions from all models"""
        predictions = {}
        
        for name, model in self.models.items():
            if hasattr(model, "predict"):
                predictions[name] = model.predict(X)
        
        # Weighted ensemble prediction
        total_weight = sum(self.weights.values())
        ensemble_pred = np.zeros(len(X))
        
        for name, pred in predictions.items():
            weight = self.weights[name] / total_weight
            ensemble_pred += weight * pred
        
        predictions["ensemble"] = ensemble_pred
        
        return predictions
    
    def get_confidence(self, X: np.ndarray) -> float:
        """Get prediction confidence based on model agreement"""
        preds = self.predict(X)
        
        # Remove ensemble from calculation
        individual_preds = [p for name, p in preds.items() if name != "ensemble"]
        
        if len(individual_preds) < 2:
            return 1.0
        
        # Calculate standard deviation across models
        stacked = np.stack(individual_preds, axis=0)
        std = np.std(stacked, axis=0)
        
        # Confidence is inverse of disagreement
        confidence = 1 / (1 + np.mean(std))
        
        return confidence


def create_default_ensemble() -> EnsembleModel:
    """Create default ensemble with sklearn models"""
    ensemble = EnsembleModel()
    
    ensemble.add_model(
        "random_forest",
        RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42),
        weight=0.3,
    )
    
    ensemble.add_model(
        "gradient_boosting",
        GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42),
        weight=0.4,
    )
    
    # LSTM would be added here with weight 0.3
    
    return ensemble
