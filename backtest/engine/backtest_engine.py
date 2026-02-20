"""
Main backtesting engine
"""

from typing import Any, Dict, List

import pandas as pd

from backtest.engine.execution_handler import ExecutionHandler
from backtest.engine.portfolio_handler import PortfolioHandler


class BacktestEngine:
    """
    Event-driven backtesting engine
    """
    
    def __init__(
        self,
        strategy,
        initial_capital: float = 100000.0,
        commission: float = 0.001,  # 0.1%
        slippage: float = 0.0005,   # 0.05%
        start_date: str = None,
        end_date: str = None,
    ):
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.start_date = start_date
        self.end_date = end_date
        
        self.execution_handler = ExecutionHandler(commission, slippage)
        self.portfolio_handler = PortfolioHandler(initial_capital)
        
        self.events = []
        self.results = {}
    
    async def run(self, symbols: List[str]) -> Dict[str, Any]:
        """Run backtest"""
        print(f"Starting backtest for {symbols}")
        
        # Load data
        data = await self._load_data(symbols)
        
        # Initialize strategy
        self.strategy.initialize(data)
        
        # Event loop
        for timestamp in data.index:
            # Update market data
            current_data = data.loc[timestamp]
            
            # Generate signals
            signals = self.strategy.on_bar(timestamp, current_data)
            
            # Execute signals
            for signal in signals:
                fill = self.execution_handler.execute(signal, current_data)
                if fill:
                    self.portfolio_handler.update(fill)
            
            # Update portfolio value
            self.portfolio_handler.mark_to_market(timestamp, current_data)
        
        # Calculate results
        self.results = self._calculate_metrics()
        
        return self.results
    
    async def _load_data(self, symbols: List[str]) -> pd.DataFrame:
        """Load historical data"""
        from infrastructure.external.data_providers.yahoo_finance import YahooFinanceProvider
        
        provider = YahooFinanceProvider()
        
        all_data = {}
        for symbol in symbols:
            hist = await provider.get_history(
                symbol,
                period="5y" if not self.start_date else None,
            )
            all_data[symbol] = hist
        
        # Combine into DataFrame
        df = pd.concat(all_data, axis=1)
        return df
    
    def _calculate_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics"""
        from backtest.metrics.performance import PerformanceMetrics
        
        equity_curve = self.portfolio_handler.equity_curve
        trades = self.portfolio_handler.trades
        
        metrics = PerformanceMetrics.calculate_all(equity_curve, trades)
        
        return {
            "initial_capital": self.initial_capital,
            "final_capital": equity_curve[-1],
            "total_return": (equity_curve[-1] - self.initial_capital) / self.initial_capital,
            **metrics,
            "trades": trades,
            "equity_curve": equity_curve,
        }
