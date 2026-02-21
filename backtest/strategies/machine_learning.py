"""
ML-based trading strategy
"""

from typing import Dict, List

from backtest.engine.execution_handler import Signal
from backtest.strategies.base_strategy import BaseStrategy


class MachineLearningStrategy(BaseStrategy):
    """
    Strategy using ML predictions
    """
    
    def __init__(
        self,
        model_path: str,
        threshold: float = 0.02,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.model_path = model_path
        self.threshold = threshold
        self.model = None
    
    def on_init(self):
        """Load ML model"""
        from ml.inference.predictor import MLPredictor
        
        self.model = MLPredictor(self.model_path)
    
    def on_bar(self, timestamp, bar_data: Dict) -> List[Signal]:
        """Generate signals from ML predictions"""
        signals = []
        
        for symbol in bar_data.columns.levels[0]:
            try:
                # Get prediction
                # This would need to be adapted for backtest context
                prediction = 0  # Placeholder
                
                if prediction > self.threshold:
                    signals.append(Signal(
                        symbol=symbol,
                        direction="buy",
                        quantity=100,
                    ))
                elif prediction < -self.threshold:
                    signals.append(Signal(
                        symbol=symbol,
                        direction="sell",
                        quantity=100,
                    ))
            
            except Exception as e:
                print(f"Error processing {symbol}: {e}")
        
        return signals
