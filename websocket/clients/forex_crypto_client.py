"""
Forex and Crypto WebSocket client
"""

import asyncio
import json

import websockets


class ForexCryptoClient:
    """
    Client for Forex and Crypto real-time data
    Supports multiple exchanges
    """
    
    EXCHANGES = {
        "binance": "wss://stream.binance.com:9443/ws",
        "coinbase": "wss://ws-feed.exchange.coinbase.com",
        "forex": "wss://fx-ws.gate.io/v4/ws",  # Example
    }
    
    def __init__(self, exchange: str = "binance"):
        self.exchange = exchange
        self.ws = None
        self.subscriptions = set()
        self.callbacks = []
    
    async def connect(self):
        """Connect to exchange WebSocket"""
        uri = self.EXCHANGES.get(self.exchange)
        if not uri:
            raise ValueError(f"Unknown exchange: {self.exchange}")
        
        self.ws = await websockets.connect(uri)
        asyncio.create_task(self._listen())
        
        # Subscribe to streams
        await self._send_subscriptions()
    
    async def _send_subscriptions(self):
        """Send subscription messages"""
        if self.exchange == "binance":
            # Binance format: symbol@ticker
            streams = [f"{s.lower()}@ticker" for s in self.subscriptions]
            await self.ws.send(json.dumps({
                "method": "SUBSCRIBE",
                "params": streams,
                "id": 1,
            }))
    
    async def _listen(self):
        """Listen for messages"""
        try:
            async for message in self.ws:
                data = json.loads(message)
                await self._handle_message(data)
        except websockets.exceptions.ConnectionClosed:
            await self.reconnect()
    
    async def _handle_message(self, data: dict):
        """Handle message"""
        # Normalize format
        normalized = self._normalize_message(data)
        
        for callback in self.callbacks:
            await callback(normalized)
    
    def _normalize_message(self, data: dict) -> dict:
        """Normalize to common format"""
        if self.exchange == "binance":
            return {
                "symbol": data.get("s"),
                "price": float(data.get("c", 0)),
                "change_24h": float(data.get("P", 0)),
                "volume": float(data.get("v", 0)),
                "timestamp": data.get("E"),
            }
        return data
    
    async def subscribe(self, symbols: list):
        """Subscribe to symbols"""
        self.subscriptions.update(symbols)
        if self.ws:
            await self._send_subscriptions()
    
    def add_callback(self, callback):
        """Add callback"""
        self.callbacks.append(callback)
    
    async def reconnect(self):
        """Reconnect"""
        await asyncio.sleep(5)
        await self.connect()
    
    async def close(self):
        """Close connection"""
        if self.ws:
            await self.ws.close()
