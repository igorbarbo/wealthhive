"""
Hyperparameter optimization
"""

from typing import Any, Dict, List

import numpy as np
import optuna
from sklearn.model_selection import cross_val_score


class HyperparameterTuner:
    """Optimize model hyperparameters"""
    
    def __init__(self, model_class, param_distributions: Dict[str, Any]):
        self.model_class = model_class
        self.param_distributions = param_distributions
    
    def objective(self, trial: optuna.Trial, X: np.ndarray, y: np.ndarray) -> float:
        """Optuna objective function"""
        # Sample parameters
        params = {}
        for param_name, param_config in self.param_distributions.items():
            if param_config["type"] == "int":
                params[param_name] = trial.suggest_int(
                    param_name,
                    param_config["low"],
                    param_config["high"],
                )
            elif param_config["type"] == "float":
                params[param_name] = trial.suggest_float(
                    param_name,
                    param_config["low"],
                    param_config["high"],
                    log=param_config.get("log", False),
                )
            elif param_config["type"] == "categorical":
                params[param_name] = trial.suggest_categorical(
                    param_name,
                    param_config["choices"],
                )
        
        # Create and evaluate model
        model = self.model_class(**params)
        scores = cross_val_score(model, X, y, cv=3, scoring="neg_mean_squared_error")
        
        return -scores.mean()  # Minimize MSE
    
    def optimize(
        self,
        X: np.ndarray,
        y: np.ndarray,
        n_trials: int = 100,
        timeout: int = 3600,
    ) -> Dict[str, Any]:
        """Run hyperparameter optimization"""
        study = optuna.create_study(direction="minimize")
        
        study.optimize(
            lambda trial: self.objective(trial, X, y),
            n_trials=n_trials,
            timeout=timeout,
            show_progress_bar=True,
        )
        
        return {
            "best_params": study.best_params,
            "best_score": study.best_value,
            "n_trials": len(study.trials),
            "optimization_history": [
                {"trial": t.number, "value": t.value, "params": t.params}
                for t in study.trials
            ],
        }
      
