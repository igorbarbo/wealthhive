"""
Broadcast utilities
"""

import asyncio
from typing import Any, Dict

import structlog

logger = structlog.get_logger()


class BroadcastManager:
    """
    Manage broadcasting of market data
    """
    
    def __init__(self, connection_manager):
        self.manager = connection_manager
        self.running = False
        self.tasks = []
    
    async def start_price_feed(self, interval: float = 1.0):
        """Start broadcasting price updates"""
        self.running = True
        
        while self.running:
            try:
                # Fetch latest prices
                prices = await self._fetch_prices()
                
                # Broadcast to subscribers
                for symbol, price_data in prices.items():
                    await self.manager.broadcast(
                        {
                            "type": "price_update",
                            "symbol": symbol,
                            "data": price_data,
                            "timestamp": asyncio.get_event_loop().time(),
                        },
                        symbol=symbol,
                    )
                
                await asyncio.sleep(interval)
            
            except Exception as e:
                logger.error("Error in price feed", error=str(e))
                await asyncio.sleep(interval)
    
    async def _fetch_prices(self) -> Dict[str, Any]:
        """Fetch latest prices from data provider"""
        # Would connect to real-time data source
        return {
            "PETR4": {"price": 28.50, "change": 0.02},
            "VALE3": {"price": 68.20, "change": -0.01},
        }
    
    def stop(self):
        """Stop broadcasting"""
        self.running = False
        for task in self.tasks:
            task.cancel()
          
