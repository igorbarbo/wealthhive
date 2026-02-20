"""
Time series cross-validation
"""

from typing import List

import numpy as np
from sklearn.metrics import mean_squared_error


class TimeSeriesCV:
    """Time series cross-validation"""
    
    def __init__(self, n_splits: int = 5, test_size: int = 30):
        self.n_splits = n_splits
        self.test_size = test_size
    
    def split(self, X: np.ndarray):
        """Generate train/test indices"""
        n_samples = len(X)
        indices = np.arange(n_samples)
        
        for i in range(self.n_splits):
            # Calculate split point
            split_point = n_samples - (self.n_splits - i) * self.test_size
            
            if split_point <= self.test_size:
                continue
            
            train_indices = indices[:split_point]
            test_indices = indices[split_point:split_point + self.test_size]
            
            yield train_indices, test_indices
    
    def evaluate(self, model, X: np.ndarray, y: np.ndarray) -> List[dict]:
        """Evaluate model with time series CV"""
        scores = []
        
        for fold, (train_idx, test_idx) in enumerate(self.split(X)):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]
            
            # Train
            model.fit(X_train, y_train)
            
            # Predict
            y_pred = model.predict(X_test)
            
            # Score
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            
            scores.append({
                "fold": fold + 1,
                "train_size": len(train_idx),
                "test_size": len(test_idx),
                "mse": mse,
                "rmse": rmse,
            })
        
        return scores
