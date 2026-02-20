"""
Base strategy class
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from backtest.engine.execution_handler import Signal


class BaseStrategy(ABC):
    """Base class for trading strategies"""
    
    def __init__(self, **kwargs):
        self.parameters = kwargs
        self.data = None
        self.initialized = False
    
    def initialize(self, data: Any):
        """Initialize with historical data"""
        self.data = data
        self.initialized = True
        self.on_init()
    
    def on_init(self):
        """Override for custom initialization"""
        pass
    
    @abstractmethod
    def on_bar(self, timestamp, bar_data: Dict) -> List[Signal]:
        """
        Process new bar and generate signals
        
        Returns:
            List of Signal objects
        """
        pass
    
    def get_parameters(self) -> Dict:
        """Get strategy parameters"""
        return self.parameters
    
    def set_parameters(self, params: Dict):
        """Update parameters"""
        self.parameters.update(params)
