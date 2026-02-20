"""
Backtesting for ML models
"""

from typing import Dict, List

import numpy as np
import pandas as pd

from ml.evaluation.metrics import FinancialMetrics, RegressionMetrics


class MLBacktester:
    """Backtest ML trading strategy"""
    
    def __init__(self, model, threshold: float = 0.01):
        self.model = model
        self.threshold = threshold  # Minimum prediction confidence to trade
    
    def run(
        self,
        features: pd.DataFrame,
        prices: pd.Series,
        initial_capital: float = 100000,
    ) -> Dict:
        """Run backtest"""
        capital = initial_capital
        position = 0  # 0 = no position, 1 = long, -1 = short
        trades = []
        equity_curve = [capital]
        
        predictions = self.model.predict(features.values)
        
        for i in range(1, len(features)):
            current_price = prices.iloc[i]
            prev_price = prices.iloc[i-1]
            prediction = predictions[i]
            
            # Trading logic
            if abs(prediction) > self.threshold:
                # Signal to trade
                target_position = 1 if prediction > 0 else -1
                
                if target_position != position:
                    # Execute trade
                    if position != 0:
                        # Close existing position
                        pnl = position * (current_price - trades[-1]["price"])
                        capital += pnl
                        trades[-1]["exit_price"] = current_price
                        trades[-1]["pnl"] = pnl
                    
                    # Open new position
                    trades.append({
                        "date": features.index[i],
                        "type": "buy" if target_position == 1 else "sell",
                        "price": current_price,
                        "prediction": prediction,
                    })
                    position = target_position
            
            # Mark to market
            if position != 0:
                unrealized = position * (current_price - trades[-1]["price"])
                equity = capital + unrealized
            else:
                equity = capital
            
            equity_curve.append(equity)
        
        # Close final position
        if position != 0:
            final_price = prices.iloc[-1]
            pnl = position * (final_price - trades[-1]["price"])
            capital += pnl
            trades[-1]["exit_price"] = final_price
            trades[-1]["pnl"] = pnl
        
        # Calculate metrics
        equity_series = pd.Series(equity_curve)
        returns = equity_series.pct_change().dropna()
        
        metrics = {
            "total_return": (capital - initial_capital) / initial_capital,
            "total_trades": len([t for t in trades if "pnl" in t]),
            "winning_trades": len([t for t in trades if t.get("pnl", 0) > 0]),
            "sharpe_ratio": FinancialMetrics.sharpe_ratio(returns),
            "max_drawdown": FinancialMetrics.max_drawdown(equity_series),
            "final_capital": capital,
        }
        
        metrics["win_rate"] = (
            metrics["winning_trades"] / metrics["total_trades"]
            if metrics["total_trades"] > 0 else 0
        )
        
        return {
            "metrics": metrics,
            "trades": trades,
            "equity_curve": equity_curve,
        }
