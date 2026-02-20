"""
ML model evaluation metrics
"""

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    recall_score,
    roc_auc_score,
)


class RegressionMetrics:
    """Regression metrics"""
    
    @staticmethod
    def mse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        return mean_squared_error(y_true, y_pred)
    
    @staticmethod
    def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        return np.sqrt(mean_squared_error(y_true, y_pred))
    
    @staticmethod
    def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        return mean_absolute_error(y_true, y_pred)
    
    @staticmethod
    def mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        return np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    
    @staticmethod
    def r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        return 1 - (ss_res / ss_tot)
    
    @staticmethod
    def directional_accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Accuracy of direction prediction"""
        direction_true = np.sign(np.diff(y_true))
        direction_pred = np.sign(np.diff(y_pred))
        return accuracy_score(direction_true, direction_pred)


class ClassificationMetrics:
    """Classification metrics"""
    
    @staticmethod
    def accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        return accuracy_score(y_true, y_pred)
    
    @staticmethod
    def precision(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        return precision_score(y_true, y_pred, average="weighted")
    
    @staticmethod
    def recall(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        return recall_score(y_true, y_pred, average="weighted")
    
    @staticmethod
    def f1(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        return f1_score(y_true, y_pred, average="weighted")
    
    @staticmethod
    def auc(y_true: np.ndarray, y_prob: np.ndarray) -> float:
        return roc_auc_score(y_true, y_prob, multi_class="ovr")


class FinancialMetrics:
    """Financial-specific metrics"""
    
    @staticmethod
    def sharpe_ratio(returns: np.ndarray, risk_free_rate: float = 0.04) -> float:
        """Annualized Sharpe ratio"""
        excess_returns = returns - risk_free_rate / 252
        return np.sqrt(252) * np.mean(excess_returns) / np.std(excess_returns)
    
    @staticmethod
    def sortino_ratio(returns: np.ndarray, risk_free_rate: float = 0.04) -> float:
        """Sortino ratio (downside risk only)"""
        excess_returns = returns - risk_free_rate / 252
        downside_returns = returns[returns < 0]
        downside_std = np.std(downside_returns) if len(downside_returns) > 0 else 0
        return np.sqrt(252) * np.mean(excess_returns) / downside_std if downside_std > 0 else 0
    
    @staticmethod
    def max_drawdown(equity_curve: np.ndarray) -> float:
        """Maximum drawdown"""
        peak = np.maximum.accumulate(equity_curve)
        drawdown = (equity_curve - peak) / peak
        return np.min(drawdown)
    
    @staticmethod
    def calmar_ratio(returns: np.ndarray, max_dd: float = None) -> float:
        """Calmar ratio (return / max drawdown)"""
        annual_return = np.mean(returns) * 252
        if max_dd is None:
            # Calculate from returns
            equity = np.cumprod(1 + returns)
            max_dd = FinancialMetrics.max_drawdown(equity)
        return annual_return / abs(max_dd) if max_dd != 0 else 0
