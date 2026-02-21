"""
Black-Litterman model for portfolio optimization
"""

from typing import Dict, List

import numpy as np
from scipy.linalg import inv


class BlackLittermanOptimizer:
    """
    Black-Litterman portfolio optimization
    Combines market equilibrium with investor views
    """
    
    def optimize(
        self,
        symbols: List[str],
        market_weights: np.ndarray = None,
        cov_matrix: np.ndarray = None,
        views: List[Dict] = None,
        view_confidences: List[float] = None,
        risk_aversion: float = 2.5,
        tau: float = 0.05,
    ) -> Dict:
        """
        Black-Litterman optimization
        
        Args:
            symbols: Asset symbols
            market_weights: Market capitalization weights
            cov_matrix: Covariance matrix
            views: List of views [{"asset": "AAPL", "return": 0.15, "confidence": 0.7}]
            view_confidences: Confidence in each view
            risk_aversion: Risk aversion parameter
            tau: Uncertainty scaling parameter
        """
        n_assets = len(symbols)
        
        # Default to equal weights if no market weights provided
        if market_weights is None:
            market_weights = np.ones(n_assets) / n_assets
        
        if cov_matrix is None:
            cov_matrix = np.eye(n_assets) * 0.04
        
        # Implied equilibrium returns (reverse optimization)
        pi = risk_aversion * np.dot(cov_matrix, market_weights)
        
        if not views:
            # No views, use market equilibrium
            optimal_weights = market_weights
        else:
            # Build views matrix P and vector Q
            P, Q = self._build_views_matrix(views, n_assets, symbols)
            
            # View uncertainty
            omega = np.diag([tau * (1 - v["confidence"]) for v in views]) if views else np.eye(1)
            
            # Black-Litterman formula
            # Posterior expected returns
            tau_sigma = tau * cov_matrix
            
            try:
                middle_term = inv(np.dot(np.dot(P, tau_sigma), P.T) + omega)
                posterior_returns = pi + np.dot(
                    np.dot(np.dot(tau_sigma, P.T), middle_term),
                    (Q - np.dot(P, pi)),
                )
                
                # Posterior covariance (optional, usually keep original)
                # posterior_cov = cov_matrix + tau_sigma - np.dot(...)
                
                optimal_weights = self._optimize_weights(
                    posterior_returns,
                    cov_matrix,
                    risk_aversion,
                )
            except np.linalg.LinAlgError:
                # Fallback to equilibrium
                optimal_weights = market_weights
                posterior_returns = pi
        
        # Calculate portfolio metrics
        port_return = np.dot(optimal_weights, pi if not views else posterior_returns)
        port_risk = np.sqrt(np.dot(optimal_weights.T, np.dot(cov_matrix, optimal_weights)))
        
        return {
            "weights": optimal_weights.tolist(),
            "posterior_returns": posterior_returns.tolist() if views else pi.tolist(),
            "prior_returns": pi.tolist(),
            "expected_return": port_return,
            "expected_risk": port_risk,
        }
    
    def _build_views_matrix(
        self,
        views: List[Dict],
        n_assets: int,
        symbols: List[str],
    ) -> tuple:
        """Build views matrix P and returns vector Q"""
        n_views = len(views)
        P = np.zeros((n_views, n_assets))
        Q = np.zeros(n_views)
        
        symbol_to_idx = {s: i for i, s in enumerate(symbols)}
        
        for i, view in enumerate(views):
            asset_idx = symbol_to_idx.get(view["asset"])
            if asset_idx is not None:
                P[i, asset_idx] = 1
                Q[i] = view["return"]
        
        return P, Q
    
    def _optimize_weights(
        self,
        expected_returns: np.ndarray,
        cov_matrix: np.ndarray,
        risk_aversion: float,
    ) -> np.ndarray:
        """Optimize weights given returns and covariance"""
        # Simple quadratic optimization
        n = len(expected_returns)
        
        # Unconstrained optimal (can be negative)
        weights = np.dot(inv(cov_matrix), expected_returns) / risk_aversion
        
        # Normalize to sum to 1 (simplified)
        weights = weights / np.sum(np.abs(weights))
        
        # Ensure non-negative (no short selling)
        weights = np.maximum(weights, 0)
        weights = weights / np.sum(weights)
        
        return weights
