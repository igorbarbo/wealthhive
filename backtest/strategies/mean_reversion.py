"""
Mean Reversion strategy
"""

from typing import Dict, List

from backtest.engine.execution_handler import Signal
from backtest.strategies.base_strategy import BaseStrategy


class MeanReversionStrategy(BaseStrategy):
    """
    Bollinger Bands mean reversion
    Buy when price touches lower band
    Sell when price touches upper band
    """
    
    def __init__(
        self,
        lookback_period: int = 20,
        std_dev: float = 2.0,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.lookback_period = lookback_period
        self.std_dev = std_dev
    
    def on_bar(self, timestamp, bar_data: Dict) -> List[Signal]:
        """Generate mean reversion signals"""
        signals = []
        
        for symbol in bar_data.columns.levels[0]:
            try:
                prices = self.data[symbol]["close"].loc[:timestamp]
                
                if len(prices) < self.lookback_period:
                    continue
                
                # Calculate Bollinger Bands
                ma = prices.rolling(self.lookback_period).mean().iloc[-1]
                std = prices.rolling(self.lookback_period).std().iloc[-1]
                
                upper_band = ma + (std * self.std_dev)
                lower_band = ma - (std * self.std_dev)
                
                current_price = bar_data[symbol]["close"]
                
                # Buy at lower band
                if current_price <= lower_band:
                    signals.append(Signal(
                        symbol=symbol,
                        direction="buy",
                        quantity=100,
                    ))
                
                # Sell at upper band
                elif current_price >= upper_band:
                    signals.append(Signal(
                        symbol=symbol,
                        direction="sell",
                        quantity=100,
                    ))
            
            except Exception as e:
                print(f"Error processing {symbol}: {e}")
        
        return signals
