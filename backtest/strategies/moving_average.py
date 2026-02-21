"""
Moving Average Crossover Strategy
"""

from typing import Dict, List

import pandas as pd

from backtest.engine.execution_handler import Signal
from backtest.strategies.base_strategy import BaseStrategy


class MovingAverageStrategy(BaseStrategy):
    """
    Simple Moving Average Crossover
    Buy when short MA crosses above long MA
    Sell when short MA crosses below long MA
    """
    
    def __init__(
        self,
        short_window: int = 20,
        long_window: int = 50,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.short_window = short_window
        self.long_window = long_window
    
    def on_init(self):
        """Pre-calculate moving averages"""
        # Calculate for all symbols
        pass
    
    def on_bar(self, timestamp, bar_data: Dict) -> List[Signal]:
        """Generate signals based on MA crossover"""
        signals = []
        
        for symbol in bar_data.columns.levels[0]:
            try:
                # Get price history up to current bar
                prices = self.data[symbol]["close"].loc[:timestamp]
                
                if len(prices) < self.long_window:
                    continue
                
                # Calculate MAs
                short_ma = prices.rolling(self.short_window).mean().iloc[-1]
                long_ma = prices.rolling(self.long_window).mean().iloc[-1]
                
                prev_short = prices.rolling(self.short_window).mean().iloc[-2]
                prev_long = prices.rolling(self.long_window).mean().iloc[-2]
                
                # Check for crossover
                current_price = bar_data[symbol]["close"]
                
                # Golden cross (buy)
                if prev_short <= prev_long and short_ma > long_ma:
                    signals.append(Signal(
                        symbol=symbol,
                        direction="buy",
                        quantity=100,  # Fixed size for simplicity
                    ))
                
                # Death cross (sell)
                elif prev_short >= prev_long and short_ma < long_ma:
                    signals.append(Signal(
                        symbol=symbol,
                        direction="sell",
                        quantity=100,
                    ))
            
            except Exception as e:
                print(f"Error processing {symbol}: {e}")
        
        return signals
