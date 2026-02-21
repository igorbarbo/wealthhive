"""
Yahoo Finance WebSocket client
"""

import asyncio

import yfinance as yf


class YahooWebSocketClient:
    """
    Client for Yahoo Finance streaming (simulated via polling)
    """
    
    def __init__(self):
        self.subscriptions = set()
        self.callbacks = []
        self.running = False
    
    async def connect(self):
        """Start streaming"""
        self.running = True
        asyncio.create_task(self._stream())
    
    async def _stream(self):
        """Stream data"""
        while self.running:
            for symbol in self.subscriptions:
                try:
                    ticker = yf.Ticker(symbol)
                    data = ticker.fast_info
                    
                    message = {
                        "symbol": symbol,
                        "price": data.last_price,
                        "change": data.last_price - data.previous_close,
                        "timestamp": asyncio.get_event_loop().time(),
                    }
                    
                    for callback in self.callbacks:
                        await callback(message)
                
                except Exception as e:
                    print(f"Error fetching {symbol}: {e}")
            
            await asyncio.sleep(5)  # Poll every 5 seconds
    
    async def subscribe(self, symbols: list):
        """Subscribe to symbols"""
        self.subscriptions.update(symbols)
    
    async def unsubscribe(self, symbols: list):
        """Unsubscribe from symbols"""
        self.subscriptions.difference_update(symbols)
    
    def add_callback(self, callback):
        """Add callback"""
        self.callbacks.append(callback)
    
    async def close(self):
        """Stop streaming"""
        self.running = False
