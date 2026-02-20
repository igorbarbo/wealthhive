"""
Data management for backtesting
"""

from typing import Any, Dict, List

import pandas as pd


class DataHandler:
    """Manage data for backtests"""
    
    def __init__(self):
        self.data: Dict[str, pd.DataFrame] = {}
        self.current_idx = 0
    
    def load_data(
        self,
        symbol: str,
        data: pd.DataFrame,
    ):
        """Load data for symbol"""
        self.data[symbol] data.sort_index()
    
    def get_latest_bars(
        self,
        symbol: str,
        n: int = 1,
    ) -> pd.DataFrame:
        """Get last n bars"""
        if symbol not in self.data:
            return pd.DataFrame()
        
        return self.data[symbol].iloc[-n:]
    
    def update_bars(self):
        """Move to next bar"""
        self.current_idx += 1
    
    def get_current_data(self) -> Dict[str, pd.Series]:
        """Get current bar for all symbols"""
        current = {}
        for symbol, df in self.data.items():
            if self.current_idx < len(df):
                current[symbol] = df.iloc[self.current_idx]
        return current
      
