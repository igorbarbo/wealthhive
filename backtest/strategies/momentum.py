"""
Momentum strategy
"""

from typing import Dict, List

from backtest.engine.execution_handler import Signal
from backtest.strategies.base_strategy import BaseStrategy


class MomentumStrategy(BaseStrategy):
    """
    Price momentum strategy
    Buy when price momentum is positive and strong
    """
    
    def __init__(
        self,
        lookback_period: int = 20,
        threshold: float = 0.05,  # 5% momentum threshold
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.lookback_period = lookback_period
        self.threshold = threshold
    
    def on_bar(self, timestamp, bar_data: Dict) -> List[Signal]:
        """Generate momentum signals"""
        signals = []
        
        for symbol in bar_data.columns.levels[0]:
            try:
                prices = self.data[symbol]["close"].loc[:timestamp]
                
                if len(prices) < self.lookback_period:
                    continue
                
                # Calculate momentum
                current_price = prices.iloc[-1]
                past_price = prices.iloc[-self.lookback_period]
                momentum = (current_price - past_price) / past_price
                
                # Generate signal
                if momentum > self.threshold:
                    signals.append(Signal(
                        symbol=symbol,
                        direction="buy",
                        quantity=100,
                    ))
                elif momentum < -self.threshold:
                    signals.append(Signal(
                        symbol=symbol,
                        direction="sell",
                        quantity=100,
                    ))
            
            except Exception as e:
                print(f"Error processing {symbol}: {e}")
        
        return signals
