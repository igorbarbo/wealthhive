"""
Monte Carlo simulation for portfolio analysis
"""

from typing import Dict, List

import numpy as np
import pandas as pd


class MonteCarloSimulation:
    """
    Monte Carlo simulation for portfolio optimization and risk analysis
    """
    
    def __init__(
        self,
        n_simulations: int = 10000,
        time_horizon: int = 252,  # Trading days
    ):
        self.n_simulations = n_simulations
        self.time_horizon = time_horizon
    
    def simulate_returns(
        self,
        expected_returns: np.ndarray,
        cov_matrix: np.ndarray,
        weights: np.ndarray,
    ) -> np.ndarray:
        """
        Simulate portfolio returns
        
        Returns:
            Array of shape (n_simulations, time_horizon) with portfolio values
        """
        n_assets = len(weights)
        
        # Generate correlated random returns
        simulated_returns = np.random.multivariate_normal(
            expected_returns,
            cov_matrix,
            (self.n_simulations, self.time_horizon),
        )
        
        # Calculate portfolio returns
        portfolio_returns = np.dot(simulated_returns, weights)
        
        # Calculate cumulative returns
        cumulative_returns = np.cumprod(1 + portfolio_returns, axis=1)
        
        return cumulative_returns
    
    def analyze_distribution(
        self,
        final_values: np.ndarray,
    ) -> Dict:
        """
        Analyze distribution of final portfolio values
        """
        return {
            "mean": np.mean(final_values),
            "median": np.median(final_values),
            "std": np.std(final_values),
            "min": np.min(final_values),
            "max": np.max(final_values),
            "percentile_5": np.percentile(final_values, 5),
            "percentile_95": np.percentile(final_values, 95),
            "prob_profit": np.mean(final_values > 1),
            "prob_double": np.mean(final_values > 2),
            "prob_loss": np.mean(final_values < 1),
        }
    
    def optimize_weights(
        self,
        expected_returns: np.ndarray,
        cov_matrix: np.ndarray,
        objective: str = "sharpe",
    ) -> Dict:
        """
        Find optimal weights using Monte Carlo
        """
        n_assets = len(expected_returns)
        best_score = -np.inf
        best_weights = None
        
        results = []
        
        for _ in range(self.n_simulations):
            # Random weights
            weights = np.random.random(n_assets)
            weights = weights / weights.sum()
            
            # Simulate
            simulated = self.simulate_returns(
                expected_returns,
                cov_matrix,
                weights,
            )
            
            final_values = simulated[:, -1]
            
            # Calculate objective
            if objective == "sharpe":
                mean_return = np.mean(final_values) - 1
                std_return = np.std(final_values)
                score = mean_return / std_return if std_return > 0 else 0
            elif objective == "return":
                score = np.mean(final_values)
            elif objective == "cvar":
                score = -np.percentile(final_values, 5)  # Minimize CVaR
            else:
                score = np.mean(final_values)
            
            results.append({
                "weights": weights,
                "score": score,
                "mean": np.mean(final_values),
                "std": np.std(final_values),
            })
            
            if score > best_score:
                best_score = score
                best_weights = weights
        
        # Return top results
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "best_weights": best_weights,
            "best_score": best_score,
            "top_10": results[:10],
              }
      
